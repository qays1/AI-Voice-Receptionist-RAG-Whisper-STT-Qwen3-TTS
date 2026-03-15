import os
import shutil
import asyncio
from uuid import uuid4
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from sqlmodel import Session, select
from ..services.receptionist import receptionist_service
from ..rag.engine import rag_engine
from ..core.config import settings
from ..core.db import get_session
from ..models.models import User, KnowledgeFile

router = APIRouter()

# --- Auth / User Management ---

@router.post("/login")
async def login(username: str = Form(...), db: Session = Depends(get_session)):
    """
    Simple sign-in: creates user if they don't exist and returns their ID.
    This fulfills the requirement of capturing user names and isolation.
    """
    statement = select(User).where(User.username == username)
    user = db.exec(statement).first()
    
    if not user:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return {"user_id": user.id, "username": user.username}

# --- Interactions ---

@router.post("/interaction")
async def voice_interaction(
    audio: UploadFile = File(...),
    user_id: int = Form(...)
):
    os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)
    file_path = os.path.join(settings.RECORDINGS_DIR, f"{uuid4()}.wav")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    
    try:
        result = await receptionist_service.process_voice_interaction(file_path, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_interaction(
    text: str = Form(...),
    user_id: int = Form(...)
):
    try:
        result = await receptionist_service.process_text_interaction(text, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_session)
):
    # Verify user exists
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    temp_dir = "backend/data/temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Step 1: Ingest into RAG (Vector DB) with user isolation
        chunks_count = await asyncio.to_thread(rag_engine.ingest_file, file_path, user_id)
        
        # Step 2: Save to SQL for tracking
        knowledge = KnowledgeFile(user_id=user_id, filename=file.filename)
        db.add(knowledge)
        db.commit()
        
        return {"status": "success", "chunks_processed": chunks_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
