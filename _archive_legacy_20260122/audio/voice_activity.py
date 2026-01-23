"""
Voice Activity Detection - Energy-based voice vs silence detection.
"""
import numpy as np
import threading
from pathlib import Path
from typing import Dict, Any

from storage.json_writer import JsonWriter


class VoiceActivityDetector:
    """Detects voice activity using energy threshold (RMS)."""
    
    # Energy threshold for voice detection (RMS)
    ENERGY_THRESHOLD = 0.02
    
    def __init__(self, log_path: Path, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.json_writer = JsonWriter(log_path)
        
        # Statistics tracking
        self.total_frames = 0
        self.voice_frames = 0
        self.rms_values = []
        self.lock = threading.Lock()
    
    def process_chunk(self, audio_chunk: np.ndarray, frames: int) -> bool:
        """
        Process an audio chunk and detect if voice is present.
        
        Returns:
            True if voice is detected in this chunk
        """
        # Calculate RMS (Root Mean Square) energy
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        
        # Detect voice
        voice_detected = rms > self.ENERGY_THRESHOLD
        
        with self.lock:
            self.total_frames += frames
            if voice_detected:
                self.voice_frames += frames
            self.rms_values.append(rms)
        
        return voice_detected
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get voice activity statistics."""
        with self.lock:
            # Calculate speaking duration
            total_duration = self.total_frames / self.sample_rate
            speaking_duration = self.voice_frames / self.sample_rate
            
            # Calculate average volume in dB
            if self.rms_values:
                avg_rms = np.mean(self.rms_values)
                # Convert RMS to dB (avoid log of zero)
                if avg_rms > 0:
                    avg_volume_db = 20 * np.log10(avg_rms)
                else:
                    avg_volume_db = -100.0
            else:
                avg_volume_db = -100.0
            
            return {
                "voice_detected": speaking_duration > 0,
                "total_speaking_time_sec": round(speaking_duration, 2),
                "total_duration_sec": round(total_duration, 2),
                "average_volume": round(avg_volume_db, 2)
            }
    
    def save_log(self) -> None:
        """Save voice activity summary to JSON file."""
        stats = self.get_statistics()
        self.json_writer.write_single(stats)
    
    def reset(self) -> None:
        """Reset all statistics."""
        with self.lock:
            self.total_frames = 0
            self.voice_frames = 0
            self.rms_values = []
