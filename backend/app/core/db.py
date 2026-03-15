from sqlmodel import create_engine, SQLModel, Session
from .config import settings
import os

# Create data directory if it doesn't exist
os.makedirs("backend/data", exist_ok=True)

sqlite_url = settings.DATABASE_URL
# For SQLite, we need to allow multi-threaded access
connect_args = {"check_same_thread": False} if sqlite_url.startswith("sqlite") else {}

engine = create_engine(sqlite_url, connect_args=connect_args)

def init_db():
    from ..models.models import User, Conversation, KnowledgeFile # Ensure models are loaded
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
