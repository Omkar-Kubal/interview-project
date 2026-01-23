"""
Face Logger - Aggregates face detection data and writes to JSON.
"""
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import numpy as np

from .eye_tracking import EyeTracker
from .head_movement import HeadMovementTracker
from app.session.json_writer import JsonWriter


class FaceLogger:
    """Aggregates face detection data from eye and head trackers."""
    
    def __init__(self, log_path: Path):
        self.eye_tracker = EyeTracker()
        self.head_tracker = HeadMovementTracker()
        self.json_writer = JsonWriter(log_path)
        self.session_start: Optional[float] = None
    
    def start(self) -> None:
        """Initialize logging session."""
        self.session_start = time.time()
        self.json_writer.clear()
    
    def process_frame(self, frame: np.ndarray, timestamp: float) -> dict:
        """
        Process a frame through all trackers and log the result.
        
        Returns:
            Dictionary containing the logged data
        """
        # Get eye tracking data
        face_present_eye, blink, eye_direction = self.eye_tracker.process_frame(frame)
        
        # Get head movement data
        face_present_head, head_movement = self.head_tracker.process_frame(frame)
        
        # Face is present if either tracker detects it
        face_present = face_present_eye or face_present_head
        
        # Calculate relative timestamp
        if self.session_start:
            relative_time = timestamp - self.session_start
        else:
            relative_time = 0.0
        
        # Create log entry (convert numpy bools to Python bools for JSON)
        entry = {
            "frame_timestamp": round(relative_time, 3),
            "face_present": bool(face_present),
            "eye_direction": eye_direction if face_present else "unknown",
            "blink": bool(blink) if face_present else False,
            "head_movement": head_movement if face_present else "unknown"
        }
        
        # Append to log
        self.json_writer.append(entry)
        
        return entry
    
    def stop(self) -> None:
        """Stop logging and write all data to file."""
        self.json_writer.flush()
        self.eye_tracker.close()
        self.head_tracker.close()
