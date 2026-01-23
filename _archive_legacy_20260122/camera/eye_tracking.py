"""
Eye Tracking - MediaPipe Face Mesh based eye detection.
Implements Eye Aspect Ratio (EAR) for blink detection and iris tracking for gaze direction.
"""
import numpy as np
from typing import Optional, Tuple, List
import mediapipe as mp


class EyeTracker:
    """Tracks eye blinks and gaze direction using MediaPipe Face Mesh."""
    
    # MediaPipe Face Mesh landmark indices for eyes
    # Left eye landmarks
    LEFT_EYE_OUTER = 33
    LEFT_EYE_INNER = 133
    LEFT_EYE_TOP = 159
    LEFT_EYE_BOTTOM = 145
    LEFT_IRIS_CENTER = 468  # Iris landmarks start at 468
    
    # Right eye landmarks
    RIGHT_EYE_OUTER = 362
    RIGHT_EYE_INNER = 263
    RIGHT_EYE_TOP = 386
    RIGHT_EYE_BOTTOM = 374
    RIGHT_IRIS_CENTER = 473
    
    # Eye corners for gaze calculation
    LEFT_EYE_LEFT_CORNER = 33
    LEFT_EYE_RIGHT_CORNER = 133
    RIGHT_EYE_LEFT_CORNER = 362
    RIGHT_EYE_RIGHT_CORNER = 263
    
    # EAR threshold for blink detection
    EAR_THRESHOLD = 0.21
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,  # Enables iris landmarks
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.prev_ear = 1.0
        self.blink_counter = 0
    
    def process_frame(self, frame: np.ndarray) -> Tuple[bool, bool, str]:
        """
        Process a frame and detect face presence, blinks, and eye direction.
        
        Returns:
            Tuple of (face_present, blink_detected, eye_direction)
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = frame[:, :, ::-1]
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return False, False, "center"
        
        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]
        
        # Calculate Eye Aspect Ratio for both eyes
        left_ear = self._calculate_ear(landmarks, w, h, is_left=True)
        right_ear = self._calculate_ear(landmarks, w, h, is_left=False)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Detect blink
        blink_detected = avg_ear < self.EAR_THRESHOLD and self.prev_ear >= self.EAR_THRESHOLD
        self.prev_ear = avg_ear
        
        # Detect eye direction using iris position
        eye_direction = self._calculate_gaze_direction(landmarks, w, h)
        
        return True, blink_detected, eye_direction
    
    def _calculate_ear(self, landmarks, w: int, h: int, is_left: bool) -> float:
        """
        Calculate Eye Aspect Ratio (EAR).
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        """
        if is_left:
            outer = landmarks[self.LEFT_EYE_OUTER]
            inner = landmarks[self.LEFT_EYE_INNER]
            top = landmarks[self.LEFT_EYE_TOP]
            bottom = landmarks[self.LEFT_EYE_BOTTOM]
        else:
            outer = landmarks[self.RIGHT_EYE_OUTER]
            inner = landmarks[self.RIGHT_EYE_INNER]
            top = landmarks[self.RIGHT_EYE_TOP]
            bottom = landmarks[self.RIGHT_EYE_BOTTOM]
        
        # Convert to pixel coordinates
        outer_pt = np.array([outer.x * w, outer.y * h])
        inner_pt = np.array([inner.x * w, inner.y * h])
        top_pt = np.array([top.x * w, top.y * h])
        bottom_pt = np.array([bottom.x * w, bottom.y * h])
        
        # Calculate distances
        horizontal = np.linalg.norm(outer_pt - inner_pt)
        vertical = np.linalg.norm(top_pt - bottom_pt)
        
        if horizontal == 0:
            return 1.0
        
        ear = vertical / horizontal
        return ear
    
    def _calculate_gaze_direction(self, landmarks, w: int, h: int) -> str:
        """
        Calculate gaze direction based on iris position relative to eye corners.
        Returns: 'left', 'right', or 'center'
        """
        # Get iris centers (landmarks 468-472 for left, 473-477 for right)
        left_iris = landmarks[self.LEFT_IRIS_CENTER]
        right_iris = landmarks[self.RIGHT_IRIS_CENTER]
        
        # Get eye corners
        left_eye_left = landmarks[self.LEFT_EYE_LEFT_CORNER]
        left_eye_right = landmarks[self.LEFT_EYE_RIGHT_CORNER]
        right_eye_left = landmarks[self.RIGHT_EYE_LEFT_CORNER]
        right_eye_right = landmarks[self.RIGHT_EYE_RIGHT_CORNER]
        
        # Calculate horizontal position ratio for left eye
        left_eye_width = left_eye_right.x - left_eye_left.x
        if left_eye_width > 0:
            left_ratio = (left_iris.x - left_eye_left.x) / left_eye_width
        else:
            left_ratio = 0.5
        
        # Calculate horizontal position ratio for right eye
        right_eye_width = right_eye_right.x - right_eye_left.x
        if right_eye_width > 0:
            right_ratio = (right_iris.x - right_eye_left.x) / right_eye_width
        else:
            right_ratio = 0.5
        
        # Average the ratios
        avg_ratio = (left_ratio + right_ratio) / 2.0
        
        # Classify direction
        if avg_ratio < 0.35:
            return "left"
        elif avg_ratio > 0.65:
            return "right"
        else:
            return "center"
    
    def close(self) -> None:
        """Release MediaPipe resources."""
        self.face_mesh.close()
