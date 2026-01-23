"""
Camera Capture - Video recording using OpenCV.
"""
import cv2
import time
import threading
from pathlib import Path
from typing import Optional, Callable
import numpy as np


class CameraCapture:
    """Handles webcam capture and video recording."""
    
    def __init__(self, output_path: Path, camera_index: int = 0):
        self.output_path = output_path
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_callback: Optional[Callable] = None
        self.fps_callback: Optional[Callable] = None
        self.current_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        self.fps = 30.0
        self.actual_fps = 0.0
    
    def set_frame_callback(self, callback: Callable) -> None:
        """Set callback function to process each frame."""
        self.frame_callback = callback
    
    def set_fps_callback(self, callback: Callable) -> None:
        """Set callback function to report FPS."""
        self.fps_callback = callback
    
    def start(self) -> bool:
        """Start the camera capture and recording."""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Get camera properties
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        
        # Initialize video writer (use mp4v codec for compatibility)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(
            str(self.output_path),
            fourcc,
            self.fps,
            (width, height)
        )
        
        if not self.writer.isOpened():
            print("Error: Could not initialize video writer")
            self.cap.release()
            return False
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return True
    
    def _capture_loop(self) -> None:
        """Main capture loop running in separate thread."""
        frame_count = 0
        start_time = time.time()
        fps_update_interval = 1.0  # Update FPS every second
        
        while self.is_running:
            ret, frame = self.cap.read()
            
            if not ret:
                continue
            
            # Store current frame thread-safely
            with self.frame_lock:
                self.current_frame = frame.copy()
            
            # Write frame to video file
            self.writer.write(frame)
            frame_count += 1
            
            # Process frame through callback
            if self.frame_callback:
                self.frame_callback(frame, time.time())
            
            # Calculate and report FPS
            elapsed = time.time() - start_time
            if elapsed >= fps_update_interval:
                self.actual_fps = frame_count / elapsed
                if self.fps_callback:
                    self.fps_callback(self.actual_fps)
                frame_count = 0
                start_time = time.time()
            
            # Small delay to prevent CPU overload
            time.sleep(0.001)
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the most recent frame thread-safely."""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def stop(self) -> None:
        """Stop the camera capture and release resources."""
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.writer:
            self.writer.release()
        
        if self.cap:
            self.cap.release()
    
    def get_fps(self) -> float:
        """Get the current actual FPS."""
        return self.actual_fps
