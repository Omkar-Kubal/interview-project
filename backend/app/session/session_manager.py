"""
Session Manager - Handles user session lifecycle and directory structure.
"""
import os
import json
import uuid
from datetime import datetime
from pathlib import Path


class SessionManager:
    """Manages user sessions including directory creation and metadata."""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.session_id = None
        self.candidate_id = None
        self.application_id = None
        self.session_dir = None
        self.session_start = None
        self.session_end = None
        self.frame_count = 0
        self.fps_samples = []
    
    def create_session(self, candidate_id: str, application_id: int = None) -> Path:
        """Create a new session directory."""
        self.session_id = str(uuid.uuid4())
        self.candidate_id = candidate_id
        self.application_id = application_id
        self.session_dir = self.base_path / "interviews" / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        return self.session_dir
    
    def start_session(self) -> None:
        """Mark the session as started."""
        self.session_start = datetime.now()
        self.frame_count = 0
        self.fps_samples = []
    
    def record_fps(self, fps: float) -> None:
        """Record an FPS sample for averaging."""
        self.fps_samples.append(fps)
    
    def increment_frame_count(self) -> None:
        """Increment the frame counter."""
        self.frame_count += 1
    
    def end_session(self) -> None:
        """Mark the session as ended and write metadata."""
        self.session_end = datetime.now()
        self._write_session_meta()
    
    def _write_session_meta(self) -> None:
        """Write session_meta.json to the session directory."""
        if not self.session_dir:
            return
        
        avg_fps = sum(self.fps_samples) / len(self.fps_samples) if self.fps_samples else 0.0
        
        meta = {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "application_id": self.application_id,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "session_end": self.session_end.isoformat() if self.session_end else None,
            "fps_avg": round(avg_fps, 2),
            "total_frames": self.frame_count,
            "device": "local_laptop"
        }
        
        meta_path = self.session_dir / "session_meta.json"
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
    
    def get_video_path(self) -> Path:
        """Get the path for video.mp4."""
        return self.session_dir / "video.mp4"
    
    def get_audio_path(self) -> Path:
        """Get the path for audio.wav."""
        return self.session_dir / "audio.wav"
    
    def get_face_log_path(self) -> Path:
        """Get the path for face_log.json."""
        return self.session_dir / "face_log.json"
    
    def get_audio_log_path(self) -> Path:
        """Get the path for audio_log.json."""
        return self.session_dir / "audio_log.json"
