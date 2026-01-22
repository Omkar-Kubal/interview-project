"""
Signal Capture MVP - Main Entry Point
Captures camera + microphone signals for behavioral analysis.

Usage:
    python main.py

Controls:
    - Enter User ID when prompted
    - Press 's' to start session
    - Press 'q' to stop session and save data
"""
import sys
import time
import signal
import cv2

from storage.session_manager import SessionManager
from camera.camera_capture import CameraCapture
from camera.face_logger import FaceLogger
from audio.audio_capture import AudioCapture
from audio.voice_activity import VoiceActivityDetector


class SignalCaptureMVP:
    """Main application for signal capture demo."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.camera: CameraCapture = None
        self.face_logger: FaceLogger = None
        self.audio: AudioCapture = None
        self.vad: VoiceActivityDetector = None
        self.is_running = False
    
    def setup_session(self, user_id: str) -> bool:
        """Initialize session with user ID."""
        # Create session directory
        session_dir = self.session_manager.create_session(user_id)
        print(f"Session directory: {session_dir}")
        
        # Initialize camera capture
        self.camera = CameraCapture(
            output_path=self.session_manager.get_video_path()
        )
        
        # Initialize face logger
        self.face_logger = FaceLogger(
            log_path=self.session_manager.get_face_log_path()
        )
        
        # Initialize audio capture
        self.audio = AudioCapture(
            output_path=self.session_manager.get_audio_path()
        )
        
        # Initialize voice activity detector
        self.vad = VoiceActivityDetector(
            log_path=self.session_manager.get_audio_log_path()
        )
        
        return True
    
    def start(self) -> bool:
        """Start the capture session."""
        print("\nStarting capture session...")
        
        # Start session timing
        self.session_manager.start_session()
        self.face_logger.start()
        
        # Set up callbacks
        self.camera.set_frame_callback(self._on_frame)
        self.camera.set_fps_callback(self._on_fps)
        self.audio.set_chunk_callback(self._on_audio_chunk)
        
        # Start camera capture
        if not self.camera.start():
            print("Error: Failed to start camera")
            return False
        
        # Start audio capture
        if not self.audio.start():
            print("Warning: Failed to start audio capture")
        
        self.is_running = True
        print("Capture started! Press 'q' in the video window to stop.\n")
        
        return True
    
    def _on_frame(self, frame, timestamp: float) -> None:
        """Callback for each video frame."""
        # Process frame through face logger
        entry = self.face_logger.process_frame(frame, timestamp)
        self.session_manager.increment_frame_count()
        
        # Print status occasionally
        if self.session_manager.frame_count % 30 == 0:
            face_status = "✓" if entry["face_present"] else "✗"
            print(f"\rFrame {self.session_manager.frame_count}: "
                  f"Face:{face_status} Eye:{entry['eye_direction']:6} "
                  f"Head:{entry['head_movement']:6} Blink:{entry['blink']}", end="")
    
    def _on_fps(self, fps: float) -> None:
        """Callback for FPS updates."""
        self.session_manager.record_fps(fps)
    
    def _on_audio_chunk(self, chunk, frames: int) -> None:
        """Callback for each audio chunk."""
        self.vad.process_chunk(chunk, frames)
    
    def run_display_loop(self) -> None:
        """Run the display loop for live preview."""
        while self.is_running:
            frame = self.camera.get_current_frame()
            
            if frame is not None:
                # Add status overlay
                cv2.putText(frame, "Recording... Press 'q' to stop",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, (0, 255, 0), 2)
                
                # Show FPS
                fps_text = f"FPS: {self.camera.get_fps():.1f}"
                cv2.putText(frame, fps_text,
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, (0, 255, 0), 2)
                
                cv2.imshow("Signal Capture MVP", frame)
            
            # Check for quit key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.is_running = False
                break
            
            time.sleep(0.01)
        
        cv2.destroyAllWindows()
    
    def stop(self) -> None:
        """Stop the capture session and save all data."""
        print("\n\nStopping capture session...")
        self.is_running = False
        
        # Stop camera
        if self.camera:
            self.camera.stop()
            print("Video saved.")
        
        # Stop audio
        if self.audio:
            self.audio.stop()
            print("Audio saved.")
        
        # Save face log
        if self.face_logger:
            self.face_logger.stop()
            print("Face log saved.")
        
        # Save audio log
        if self.vad:
            self.vad.save_log()
            stats = self.vad.get_statistics()
            print(f"Audio log saved. Speaking time: {stats['total_speaking_time_sec']}s")
        
        # End session and save metadata
        self.session_manager.end_session()
        print("Session metadata saved.")
        
        print(f"\n✓ All files saved to: {self.session_manager.session_dir}")


def main():
    """Main entry point."""
    print("=" * 50)
    print("  SIGNAL CAPTURE MVP")
    print("  Behavioral Signal Recording System")
    print("=" * 50)
    
    # Get user ID
    user_id = input("\nEnter User ID: ").strip()
    if not user_id:
        print("Error: User ID cannot be empty")
        sys.exit(1)
    
    # Create application
    app = SignalCaptureMVP()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nInterrupt received, stopping...")
        app.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Setup and start session
    print(f"\nSetting up session for user: {user_id}")
    app.setup_session(user_id)
    
    print("\nPress 's' to start recording, or 'q' to quit...")
    
    while True:
        key = input().strip().lower()
        if key == 's':
            break
        elif key == 'q':
            print("Exiting without recording.")
            sys.exit(0)
        else:
            print("Press 's' to start or 'q' to quit.")
    
    # Start capture
    if app.start():
        # Run display loop
        app.run_display_loop()
    
    # Stop and save
    app.stop()
    
    print("\n✓ Session complete!")


if __name__ == "__main__":
    main()
