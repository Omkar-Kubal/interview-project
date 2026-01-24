"""
Audio Capture - Microphone recording using SoundDevice.
"""
import numpy as np
import sounddevice as sd
import threading
from pathlib import Path
from typing import Optional, Callable, List
from scipy.io import wavfile


class AudioCapture:
    """Handles microphone capture and audio recording to WAV."""
    
    def __init__(self, output_path: Path, sample_rate: int = 44100, channels: int = 1):
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.audio_buffer: List[np.ndarray] = []
        self.buffer_lock = threading.Lock()
        self.chunk_callback: Optional[Callable] = None
        self.stream: Optional[sd.InputStream] = None
    
    def set_chunk_callback(self, callback: Callable) -> None:
        """Set callback function to process each audio chunk."""
        self.chunk_callback = callback
    
    def start(self) -> bool:
        """Start the audio capture and recording."""
        try:
            self.is_running = True
            self.audio_buffer = []
            
            # Create input stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                callback=self._audio_callback,
                blocksize=1024
            )
            
            self.stream.start()
            return True
            
        except Exception as e:
            print(f"Error starting audio capture: {e}")
            self.is_running = False
            return False
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """Callback for audio stream - runs in audio thread."""
        if not self.is_running:
            return
        
        # Store audio data
        with self.buffer_lock:
            self.audio_buffer.append(indata.copy())
        
        # Process through callback for voice activity detection
        if self.chunk_callback:
            self.chunk_callback(indata, frames, status)
    
    def get_buffer_copy(self) -> np.ndarray:
        """Get a copy of the current audio buffer."""
        with self.buffer_lock:
            if self.audio_buffer:
                return np.concatenate(self.audio_buffer)
            return np.array([])
    
    def stop(self) -> None:
        """Stop the audio capture and save to file."""
        self.is_running = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        # Save audio to WAV file
        self._save_audio()
    
    def _save_audio(self) -> None:
        """Save recorded audio to WAV file."""
        with self.buffer_lock:
            if not self.audio_buffer:
                print("Warning: No audio data to save")
                return
            
            # Concatenate all audio chunks
            audio_data = np.concatenate(self.audio_buffer)
            
            # Convert float32 [-1, 1] to int16 for WAV
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Ensure mono audio is 1D
            if audio_int16.ndim > 1:
                audio_int16 = audio_int16.flatten()
            
            # Save to WAV file
            wavfile.write(str(self.output_path), self.sample_rate, audio_int16)
