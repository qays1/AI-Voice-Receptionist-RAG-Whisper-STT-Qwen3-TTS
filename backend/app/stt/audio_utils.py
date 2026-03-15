"""
Audio preprocessing utilities to improve STT accuracy.
"""
import numpy as np
from scipy import signal
import soundfile as sf
import os

def preprocess_audio(input_path: str, output_path: str = None) -> str:
    """
    Preprocess audio file to improve STT accuracy.
    
    Steps:
    1. Normalize audio levels
    2. Remove DC offset
    3. Apply noise reduction (simple high-pass filter)
    4. Resample to 16kHz (Whisper's native rate)
    
    Args:
        input_path: Path to input audio file
        output_path: Path to save processed audio (optional)
    
    Returns:
        Path to processed audio file
    """
    # Read audio
    audio, sample_rate = sf.read(input_path)
    
    # Convert stereo to mono if needed
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Remove DC offset
    audio = audio - np.mean(audio)
    
    # Normalize to [-1, 1]
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
    
    # Apply high-pass filter to remove low-frequency noise
    # Cutoff at 80 Hz (removes rumble, hum)
    nyquist = sample_rate / 2
    cutoff = 80 / nyquist
    b, a = signal.butter(4, cutoff, btype='high')
    audio = signal.filtfilt(b, a, audio)
    
    # Resample to 16kHz if needed (Whisper's native rate)
    if sample_rate != 16000:
        num_samples = int(len(audio) * 16000 / sample_rate)
        audio = signal.resample(audio, num_samples)
        sample_rate = 16000
    
    # Save processed audio
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_processed{ext}"
    
    sf.write(output_path, audio, sample_rate)
    
    return output_path
