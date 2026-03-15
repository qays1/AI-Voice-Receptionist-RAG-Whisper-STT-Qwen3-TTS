from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from ..rag.engine import rag_engine
from ..stt.whisper_stt import stt_service
from ..tts.qwen_tts import tts_service
from ..core.config import settings

class ReceptionistService:
    def __init__(self):
        if settings.OPENROUTER_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENROUTER_MODEL,
                openai_api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                temperature=0
            )
        else:
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0
            )
        self.system_prompt = (
            "You are Nova, a professional and welcoming AI Voice Receptionist. "
            "Your goal is to provide specific business help based ONLY on the provided knowledge. "
            "\n\nEXPERIENCE GUIDELINES:\n"
            "1. Be polite but extremely concise (1-2 sentences max).\n"
            "2. If you don't have an answer, say: 'I don't have that specific detail in my knowledge base yet, but I can certainly take a message for the team.'\n"
            "3. Do not mention 'context' or 'text'. Just answer the user like a human receptionist would."
        )   

    async def process_voice_interaction(self, audio_file_path: str, user_id: int):
        transcript = stt_service.transcribe(audio_file_path)
        context_chunks = rag_engine.retrieve(transcript, user_id)
        
        if not context_chunks:
            response_text = "I don't have that specific detail in my knowledge base yet, but I can certainly take a message for the team."
        else:
            context_text = "\n\n".join([c["content"] for c in context_chunks])
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"KNOWLEDGE CONTEXT:\n{context_text}\n\nUSER QUESTION: {transcript}")
            ]
            response = self.llm.invoke(messages)
            response_text = response.content

        audio_response_path = tts_service.generate_speech(response_text)
        
        return {
            "transcript": transcript,
            "response_text": response_text,
            "audio_url": audio_response_path,
            "sources": [c["content"] for c in context_chunks] if context_chunks else []
        }

    async def process_text_interaction(self, text: str, user_id: int):
        context_chunks = rag_engine.retrieve(text, user_id)
        
        if not context_chunks:
            response_text = "I don't have that specific detail in my knowledge base yet, but I can certainly take a message for the team."
        else:
            context_text = "\n\n".join([c["content"] for c in context_chunks])
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"KNOWLEDGE CONTEXT:\n{context_text}\n\nUSER QUESTION: {text}")
            ]
            response = self.llm.invoke(messages)
            response_text = response.content

        return {
            "response_text": response_text,
            "sources": [c["content"] for c in context_chunks] if context_chunks else []
        }

receptionist_service = ReceptionistService()
