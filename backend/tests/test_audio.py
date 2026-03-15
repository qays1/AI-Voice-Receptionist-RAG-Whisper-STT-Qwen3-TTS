import pytest
import os
from app.stt.whisper_stt import stt_service
from app.tts.qwen_tts import tts_service
from app.core.config import settings

def test_tts_generation():
    """
    TEST: Verify that the TTS service produces a valid audio file.
    """
    text = "Hello, this is a test of the Nova Voice interaction system."
    output_path = tts_service.generate_speech(text)
    
    assert os.path.exists(output_path)
    assert output_path.endswith(".mp3")
    # File should not be empty
    assert os.path.getsize(output_path) > 1000 
    
    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)

@pytest.mark.skip(reason="Requires a valid sample wav file")
def test_stt_transcription():
    """
    TEST: Verify transcription accuracy.
    """
    pass
