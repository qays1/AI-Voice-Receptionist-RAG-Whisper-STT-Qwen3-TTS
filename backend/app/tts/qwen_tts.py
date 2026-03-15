import os
import uuid
from gtts import gTTS
from ..core.config import settings

class TTSService:
    def __init__(self):
        pass

    def generate_speech(self, text: str, voice_id: str = "en") -> str:
        """
        Generates audio from text and returns the file path.
        """
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(settings.TTS_OUTPUT_DIR, filename)
        
        print(f"DEBUG: Generating real audio for: {text[:50]}...")
        
        # Using gTTS to generate actual speech
        try:
            tts = gTTS(text=text, lang=voice_id)
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"TTS Error: {e}")
            # Fallback empty file to prevent crash
            with open(output_path, "wb") as f:
                f.write(b"")
            return output_path

tts_service = TTSService()
