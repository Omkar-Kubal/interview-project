"""
Capture Session - Wrapper for existing capture modules with thread-safe signal access.
"""
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from app.session.session_manager import SessionManager
from app.capture.camera.camera_capture import CameraCapture
from app.capture.camera.face_logger import FaceLogger
from app.capture.audio.audio_capture import AudioCapture
from app.capture.audio.voice_activity import VoiceActivityDetector
from app.persistence.repository import save_session



class CaptureSession:
    """Manages a capture session with thread-safe signal access."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.camera: Optional[CameraCapture] = None
        self.face_logger: Optional[FaceLogger] = None
        self.audio: Optional[AudioCapture] = None
        self.vad: Optional[VoiceActivityDetector] = None
        
        self.is_running = False
        self.candidate_id: Optional[str] = None
        self.start_time: Optional[float] = None
        
        # Current signal state (thread-safe)
        self._signal_lock = threading.Lock()
        self._current_signals: Dict[str, Any] = {
            "face_detected": False,
            "eye_direction": "unknown",
            "head_movement": "unknown",
            "blink": False,
            "voice_activity": "silent"
        }
        
        # Integrity tracking
        self._face_present_count = 0
        self._total_frame_count = 0
        self._multiple_faces_detected = False
        self._multiple_faces_latch = False
        self._audio_interruptions = False
    
    def setup(self, candidate_id: str) -> str:
        """Initialize session for candidate."""
        self.candidate_id = candidate_id
        session_dir = self.session_manager.create_session(candidate_id)
        
        # Initialize camera
        self.camera = CameraCapture(
            output_path=self.session_manager.get_video_path()
        )
        
        # Initialize face logger
        self.face_logger = FaceLogger(
            log_path=self.session_manager.get_face_log_path()
        )
        
        # Initialize audio
        self.audio = AudioCapture(
            output_path=self.session_manager.get_audio_path()
        )
        
        # Initialize VAD
        self.vad = VoiceActivityDetector(
            log_path=self.session_manager.get_audio_log_path()
        )
        
        return str(session_dir)
    
    def start(self) -> bool:
        """Start capture session."""
        self.session_manager.start_session()
        self.face_logger.start()
        self.start_time = time.time()
        
        # Set callbacks
        self.camera.set_frame_callback(self._on_frame)
        self.camera.set_fps_callback(self._on_fps)
        self.audio.set_chunk_callback(self._on_audio_chunk)
        
        # Start camera
        if not self.camera.start():
            return False
        
        # Start audio
        self.audio.start()
        
        self.is_running = True
        return True
    
    def _on_frame(self, frame, timestamp: float) -> None:
        """Process each frame."""
        entry = self.face_logger.process_frame(frame, timestamp)
        
        # DEBUG LOGGING => Check if faces are being detected
        if self._total_frame_count % 30 == 0:  # Log every ~1 second
            print(f"[DEBUG] Frame {self._total_frame_count}: Face Present? {entry.get('face_present')} | Signals: {entry}")
            
        self.session_manager.increment_frame_count()
        
        # Update tracking
        self._total_frame_count += 1
        if entry["face_present"]:
            self._face_present_count += 1
            
        # Update integrity (instantaneous for live demo)
        multiple_faces = entry.get("multiple_faces", False)
        self._multiple_faces_detected = multiple_faces
        
        # Update latch for persistence
        if multiple_faces:
            self._multiple_faces_latch = True
        
        # Update signals thread-safely
        with self._signal_lock:
            self._current_signals["face_detected"] = entry["face_present"]
            self._current_signals["eye_direction"] = entry["eye_direction"]
            self._current_signals["head_movement"] = entry["head_movement"]
            self._current_signals["blink"] = entry["blink"]
    
    def _on_fps(self, fps: float) -> None:
        """Record FPS."""
        self.session_manager.record_fps(fps)
    
    def _on_audio_chunk(self, chunk, frames: int, status) -> None:
        """Process audio chunk."""
        if status:
            self._audio_interruptions = True
            
        voice_active = self.vad.process_chunk(chunk, frames)
        
        with self._signal_lock:
            self._current_signals["voice_activity"] = "active" if voice_active else "silent"
    
    def get_current_frame(self) -> Optional[any]:
        """Get current video frame (if available)."""
        if self.camera:
            return self.camera.get_current_frame()
        return None

    def get_current_signals(self) -> Dict[str, Any]:
        """Get current signal state (thread-safe)."""
        with self._signal_lock:
            signals = self._current_signals.copy()
        
        # Add integrity and timing
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Calculate integrity
        face_continuous = True
        if self._total_frame_count > 0:
            presence_ratio = self._face_present_count / self._total_frame_count
            face_continuous = presence_ratio > 0.9
        
        signals["integrity"] = {
            "face_continuous": face_continuous,
            "multiple_faces": self._multiple_faces_detected,
            "audio_interruptions": self._audio_interruptions
        }
        signals["elapsed_sec"] = round(elapsed)
        
        return signals
    
    def stop(self) -> Dict[str, Any]:
        """Stop capture and return summary."""
        self.is_running = False
        duration = time.time() - self.start_time if self.start_time else 0
        
        # Stop camera
        if self.camera:
            self.camera.stop()
        
        # Stop audio
        if self.audio:
            self.audio.stop()
        
        # Save logs
        if self.face_logger:
            self.face_logger.stop()
        
        if self.vad:
            self.vad.save_log()
        
        # End session
        self.session_manager.end_session()
        
        # Save to database
        try:
            session_data = {
                "session_id": self.session_manager.session_id,
                "candidate_id": self.candidate_id,
                "role": "Sr. Machine Learning Engineer",  # Hardcoded for demo
                "started_at": self.session_manager.session_start,
                "ended_at": self.session_manager.session_end,
                "video_path": str(self.session_manager.get_video_path()),
                "audio_path": str(self.session_manager.get_audio_path()),
                "multiple_faces_detected": self._multiple_faces_latch,
                "audio_interruptions_detected": self._audio_interruptions
            }
            save_session(session_data)
        except Exception as e:
            print(f"Error saving session to DB: {e}")
        
        return {
            "candidate_id": self.candidate_id,
            "duration_sec": round(duration, 1)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary."""
        session_dir = self.session_manager.session_dir
        
        return {
            "candidate_id": self.candidate_id,
            "session_start": self.session_manager.session_start.isoformat() if self.session_manager.session_start else None,
            "session_end": self.session_manager.session_end.isoformat() if self.session_manager.session_end else None,
            "duration_sec": round((self.session_manager.session_end - self.session_manager.session_start).total_seconds()) if self.session_manager.session_end and self.session_manager.session_start else 0,
            "fps_avg": round(sum(self.session_manager.fps_samples) / len(self.session_manager.fps_samples), 1) if self.session_manager.fps_samples else 0,
            "artifacts": {
                "video": str(session_dir / "video.mp4") if session_dir else None,
                "audio": str(session_dir / "audio.wav") if session_dir else None,
                "face_log": str(session_dir / "face_log.json") if session_dir else None,
                "audio_log": str(session_dir / "audio_log.json") if session_dir else None
            }
        }


# Global session instance
_current_session: Optional[CaptureSession] = None


def get_session() -> Optional[CaptureSession]:
    """Get current session."""
    return _current_session


def create_session() -> CaptureSession:
    """Create new session."""
    global _current_session
    _current_session = CaptureSession()
    return _current_session


def clear_session() -> None:
    """Clear current session."""
    global _current_session
    _current_session = None
