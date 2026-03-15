# AI Voice Receptionist — RAG + Whisper STT + TTS

A production-ready AI receptionist platform. Callers speak naturally, 
get instant answers from your business documents — no hallucinations.

## How it works
1. Visitor records voice in browser
2. Whisper transcribes with noise preprocessing
3. Qdrant retrieves relevant chunks from ingested docs
4. GPT-4 answers strictly from knowledge base
5. TTS speaks the response back

## Tech Stack
- **LLM**: GPT-4 / OpenRouter
- **STT**: Whisper (local, optimized beam search)
- **Vector Store**: Qdrant
- **Embeddings**: OpenAI text-embedding-3-small
- **Backend**: FastAPI + LangChain
- **TTS**: gTTS
- **Infra**: Docker, PostgreSQL

## Key Features
- Anti-hallucination guardrails
- Multi-tenant architecture (business_id isolation)
- Audio preprocessing (noise reduction, 16kHz resampling)
- Batched embedding ingestion (100 chunks/batch)
- Similarity threshold filtering

## Setup
```bash
docker compose up -d
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```
