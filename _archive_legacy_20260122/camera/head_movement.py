"""
Head Movement Tracking - Detects head movement intensity using facial landmarks.
"""
import numpy as np
from typing import Optional, List, Tuple
import mediapipe as mp
from collections import deque


class HeadMovementTracker:
    """Tracks head movement intensity based on landmark position changes."""
    
    # Key landmarks for head tracking (nose tip, forehead, chin)
    NOSE_TIP = 1
    FOREHEAD = 10
    CHIN = 152
    LEFT_CHEEK = 234
    RIGHT_CHEEK = 454
    
    # Movement thresholds (in normalized coordinates)
    LOW_THRESHOLD = 0.005
    MEDIUM_THRESHOLD = 0.015
    
    # History window for smoothing
    HISTORY_SIZE = 5
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.prev_landmarks: Optional[np.ndarray] = None
        self.movement_history: deque = deque(maxlen=self.HISTORY_SIZE)
    
    def process_frame(self, frame: np.ndarray) -> Tuple[bool, str]:
        """
        Process a frame and detect head movement intensity.
        
        Returns:
            Tuple of (face_present, movement_intensity)
            movement_intensity is one of: 'low', 'medium', 'high'
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = frame[:, :, ::-1]
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            self.prev_landmarks = None
            return False, "low"
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Extract key landmark positions
        current_landmarks = self._extract_key_landmarks(landmarks)
        
        if self.prev_landmarks is None:
            self.prev_landmarks = current_landmarks
            return True, "low"
        
        # Calculate movement delta
        delta = self._calculate_movement_delta(current_landmarks, self.prev_landmarks)
        self.movement_history.append(delta)
        
        # Update previous landmarks
        self.prev_landmarks = current_landmarks
        
        # Average movement over history for smoothing
        avg_delta = np.mean(list(self.movement_history))
        
        # Classify movement intensity
        intensity = self._classify_intensity(avg_delta)
        
        return True, intensity
    
    def _extract_key_landmarks(self, landmarks) -> np.ndarray:
        """Extract key landmark positions as numpy array."""
        key_indices = [
            self.NOSE_TIP,
            self.FOREHEAD,
            self.CHIN,
            self.LEFT_CHEEK,
            self.RIGHT_CHEEK
        ]
        
        positions = []
        for idx in key_indices:
            lm = landmarks[idx]
            positions.append([lm.x, lm.y, lm.z])
        
        return np.array(positions)
    
    def _calculate_movement_delta(self, current: np.ndarray, previous: np.ndarray) -> float:
        """Calculate the average movement delta between frames."""
        # Calculate Euclidean distance for each landmark
        deltas = np.linalg.norm(current - previous, axis=1)
        
        # Return average movement
        return np.mean(deltas)
    
    def _classify_intensity(self, delta: float) -> str:
        """Classify movement intensity based on delta value."""
        if delta < self.LOW_THRESHOLD:
            return "low"
        elif delta < self.MEDIUM_THRESHOLD:
            return "medium"
        else:
            return "high"
    
    def close(self) -> None:
        """Release MediaPipe resources."""
        self.face_mesh.close()
