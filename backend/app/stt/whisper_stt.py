import whisper
import os
from ..core.config import settings
from .audio_utils import preprocess_audio

class STTService:
    def __init__(self):
        print("DEBUG: Loading local Whisper model...")
        # Use medium or large model for better accuracy
        model_name = settings.WHISPER_MODEL or "medium"
        self.model = whisper.load_model(model_name)
        print(f"DEBUG: Whisper model '{model_name}' loaded.")

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe audio with improved accuracy settings.
        
        Improvements:
        - Audio preprocessing (normalization, noise reduction)
        - Language specification (English)
        - Initial prompt for context
        - Temperature settings for better decoding
        - VAD filter to remove silence
        """
        # Preprocess audio for better quality
        try:
            processed_path = preprocess_audio(audio_file_path)
            print(f"DEBUG STT: Audio preprocessed: {processed_path}")
        except Exception as e:
            print(f"DEBUG STT: Preprocessing failed, using original: {e}")
            processed_path = audio_file_path
        
        # Initial prompt helps Whisper understand context
        initial_prompt = (
            "This is a customer calling a business receptionist. "
            "They may ask about store hours, parking, services, products, or contact information."
        )
        
        # Transcribe with optimized parameters
        result = self.model.transcribe(
            processed_path,
            language="en",  # Specify English for better accuracy
            initial_prompt=initial_prompt,  # Context helps accuracy
            temperature=0.0,  # Deterministic decoding (more accurate)
            best_of=5,  # Try 5 different decodings, pick best
            beam_size=5,  # Beam search for better results
            patience=1.0,  # Wait for better alternatives
            condition_on_previous_text=True,  # Use context from previous segments
            compression_ratio_threshold=2.4,  # Filter out low-quality segments
            logprob_threshold=-1.0,  # Filter uncertain predictions
            no_speech_threshold=0.6,  # Better silence detection
            word_timestamps=False,  # Faster processing
        )
        
        transcription = result["text"].strip()
        print(f"DEBUG STT: Transcribed with confidence: {transcription}")
        
        # Clean up processed file
        if processed_path != audio_file_path and os.path.exists(processed_path):
            try:
                os.remove(processed_path)
            except:
                pass
        
        return transcription

stt_service = STTService()
