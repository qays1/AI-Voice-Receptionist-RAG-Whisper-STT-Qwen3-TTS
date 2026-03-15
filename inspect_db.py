import os
import sys
from sqlmodel import Session, create_engine, select

# Add current directory to path
sys.path.append(os.getcwd())
from backend.app.models.models import User, KnowledgeFile

def inspect_db():
    # Use absolute path from .env or current config
    db_path = os.path.join(os.getcwd(), "backend/data/database.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return

    engine = create_engine(f"sqlite:///{db_path}")
    
    print("\n=== Registered Users ===")
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        for u in users:
            print(f"ID: {u.id} | Username: {u.username} | Joined: {u.created_at}")
            
    print("\n=== Uploaded Files ===")
    with Session(engine) as session:
        files = session.exec(select(KnowledgeFile)).all()
        for f in files:
            print(f"User ID: {f.user_id} | Filename: {f.filename} | Status: {f.status}")
    print("=" * 25)

if __name__ == "__main__":
    inspect_db()
