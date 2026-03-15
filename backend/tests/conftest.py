import pytest
import os
from unittest.mock import patch

# Set TESTING=true before importing anything else
os.environ["TESTING"] = "true"

@pytest.fixture(autouse=True)
def mock_llm():
    """
    Mock ChatOpenAI to avoid actual LLM calls during tests.
    We return a predictable response to verify logic.
    """
    with patch('app.services.receptionist.ChatOpenAI') as mock_chat:
        instance = mock_chat.return_value
        mock_response = MagicMock()
        mock_response.content = "This is a mocked response based on the provided context."
        instance.invoke.return_value = mock_response
        yield instance

@pytest.fixture(autouse=True)
def mock_embeddings():
    """
    Mock OpenAI embeddings to avoid actual API calls.
    """
    with patch('app.rag.engine.OpenAIEmbeddings') as mock_emb_cls:
        instance = mock_emb_cls.return_value
        instance.embed_query.return_value = [0.1] * 1536
        instance.embed_documents.return_value = [[0.1] * 1536]
        yield instance

from unittest.mock import MagicMock
