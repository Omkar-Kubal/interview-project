import mediapipe as mp
import cv2
import numpy as np

try:
    print("Initializing FaceMesh (WITHOUT refine_landmarks)...")
    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
finally:
    if 'face_mesh' in locals():
        face_mesh.close()
