import os
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..core.config import settings

class RAGEngine:
    def __init__(self):
        # Use local disk for Qdrant if no URL is provided, allowing for Docker-less dev
        if os.getenv("TESTING") == "true":
            self.client = QdrantClient(":memory:")
            print("Using in-memory Qdrant for testing")
        elif not settings.QDRANT_URL or settings.QDRANT_URL == "local":
            storage_path = os.path.join(os.getcwd(), "backend/data/qdrant_local")
            os.makedirs(storage_path, exist_ok=True)
            self.client = QdrantClient(path=storage_path)
            print(f"Using local Qdrant storage at {storage_path}")
        else:
            self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
            
        # Initialize Embeddings
        use_openrouter = settings.OPENROUTER_API_KEY and (not settings.effective_openai_key)
        
        if use_openrouter:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                model="openai/text-embedding-3-small"
            )
        else:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.effective_openai_key or "none"
            )
        
        self.collection_name = "user_knowledge"
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    def ingest_file(self, file_path: str, user_id: int):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in [".doc", ".docx"]:
            loader = UnstructuredWordDocumentLoader(file_path)
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE, 
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(documents)
        
        texts = [chunk.page_content for chunk in chunks]
        all_vectors = []
        BATCH_SIZE = 100
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i+BATCH_SIZE]
            vectors = self.embeddings.embed_documents(batch)
            all_vectors.extend(vectors)
        
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, all_vectors)):
            point_id = abs(hash(f"{file_path}_{i}_{user_id}")) % (10**15)
            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "content": chunk.page_content,
                    "metadata": chunk.metadata,
                    "user_id": user_id
                }
            ))
        
        for i in range(0, len(points), BATCH_SIZE):
            self.client.upsert(
                collection_name=self.collection_name,
                points=points[i:i+BATCH_SIZE]
            )
        
        return len(chunks)

    def retrieve(self, query: str, user_id: int) -> List[dict]:
        query_vector = self.embeddings.embed_query(query)
        
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=settings.RETRIEVAL_TOP_K,
        ).points
        
        return [{"content": res.payload["content"], "score": getattr(res, 'score', 0)} 
                for res in search_result if getattr(res, 'score', 1.0) >= settings.SIMILARITY_THRESHOLD]

rag_engine = RAGEngine()
