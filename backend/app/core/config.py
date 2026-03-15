from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "AI Voice Receptionist"
    DATABASE_URL: str = "sqlite:///backend/data/database.db"
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openai/gpt-4-turbo"
    
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    WHISPER_MODEL: str = "base"
    
    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Storage Paths
    RECORDINGS_DIR: str = "backend/data/recordings"
    TTS_OUTPUT_DIR: str = "backend/data/tts_output"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def effective_openai_key(self) -> str:
        if self.OPENAI_API_KEY and "your_openai_key" not in self.OPENAI_API_KEY:
            return self.OPENAI_API_KEY
        return ""

settings = Settings()
