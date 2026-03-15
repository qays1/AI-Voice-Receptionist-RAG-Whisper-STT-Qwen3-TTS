# AI Voice Receptionist Platform

A production-ready foundation for an AI-powered receptionist using RAG (Retrieval Augmented Generation), Speech-to-Text (Whisper), and Text-to-Speech (Qwen3).

## Features
- 🎙️ **Voice Interaction**: Record directly in the browser.
- 📚 **Knowledge Base (RAG)**: Ingest PDF, TXT, and DOCX files.
- 🧠 **Anti-Hallucination**: High-precision retrieval ensuring answers only come from your data.
- 🔊 **Natural TTS**: Conversational audio responses.
- 🏢 **Multi-tenant Ready**: Designed with `business_id` logic from the start.

## Tech Stack
- **Backend**: Python, FastAPI, LangChain
- **Database**: PostgreSQL (SQLAlchemy/SQLModel)
- **Vector Store**: Qdrant
- **AI Models**: GPT-4 (LLM), Whisper (STT), Qwen3 (TTS)
- **Frontend**: Vanilla HTML/JS/CSS (Premium UI)

## Setup Instructions

### 1. Infrastructure
Run the database and vector store (using Docker Compose V2):
```bash
docker compose up -d
```
*Note: If you have an older version, you may need `docker-compose up -d`.*

### 2. Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Configure Environment:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add either OPENAI_API_KEY or OPENROUTER_API_KEY
   ```
   *If using OpenRouter, specify your model in `OPENROUTER_MODEL` (e.g., `anthropic/claude-3-opus`).*
4. Start the server:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

### 3. Frontend Setup
Simply open `frontend/index.html` in any modern browser.

## Usage
1. **Upload Knowledge**: Use the bottom section to upload a PDF/TXT describing your business (e.g., hours of operation, services).
2. **Interact**: Click the microphone button, ask a question (e.g., "What are your opening hours?"), and click stop.
3. **Listen**: Nova will transcribe your voice, find the answer in your files, and speak the response back to you.

## Project Structure
- `/backend/app/rag`: Retrieval logic and vector store management.
- `/backend/app/services`: Orchestrates the AI flow.
- `/backend/app/stt`: Speech-To-Text processing.
- `/backend/app/tts`: Text-To-Speech generation.
- `/frontend`: Modern browser-based interface.
