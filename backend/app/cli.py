"""
AI Interview - Signal Capture Stage
Main Entry Point for candidate behavioral signal capture (CLI mode).

Usage:
    python -m app.cli

Controls:
    - Enter Candidate ID when prompted
    - Press 's' to start interview capture
    - Press 'q' to stop and save data
"""
import sys
import time
import signal
import cv2

from app.session.session_manager import SessionManager
from app.capture.camera.camera_capture import CameraCapture
from app.capture.camera.face_logger import FaceLogger
from app.capture.audio.audio_capture import AudioCapture
from app.capture.audio.voice_activity import VoiceActivityDetector
from app.ui.overlay import OverlayRenderer



class AIInterviewCapture:
    """Main application for AI Interview signal capture."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.camera: CameraCapture = None
        self.face_logger: FaceLogger = None
        self.audio: AudioCapture = None
        self.vad: VoiceActivityDetector = None
        self.overlay: OverlayRenderer = None
        self.is_running = False
        self.current_signal_data = {}
        self.voice_active = False
    
    def setup_session(self, candidate_id: str) -> bool:
        """Initialize interview capture session."""
        # Create session directory
        session_dir = self.session_manager.create_session(candidate_id)
        print(f"Interview capture directory: {session_dir}")
        
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
        """Start the interview capture."""
        print("\nStarting interview capture...")
        
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
        
        # Initialize overlay renderer after camera starts
        # Default to 640x480 if we can't get actual dimensions
        frame = self.camera.get_current_frame()
        if frame is not None:
            h, w = frame.shape[:2]
        else:
            w, h = 640, 480
        self.overlay = OverlayRenderer(w, h)
        
        # Start audio capture
        if not self.audio.start():
            print("Warning: Failed to start audio capture")
        
        self.is_running = True
        print("Interview capture started! Press 'q' in the video window to stop.\n")
        
        return True
    
    def _on_frame(self, frame, timestamp: float) -> None:
        """Callback for each video frame."""
        # Process frame through face logger
        entry = self.face_logger.process_frame(frame, timestamp)
        self.session_manager.increment_frame_count()
        
        # Store current signal data for overlay
        self.current_signal_data = {
            "face_present": entry["face_present"],
            "eye_direction": entry["eye_direction"],
            "head_movement": entry["head_movement"],
            "blink": entry["blink"],
            "voice_active": self.voice_active
        }
        
        # Update integrity signals
        if self.overlay:
            self.overlay.update_integrity(entry["face_present"])
        
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
        self.voice_active = self.vad.process_chunk(chunk, frames)
    
    def run_display_loop(self) -> None:
        """Run the display loop with full overlay UI."""
        while self.is_running:
            frame = self.camera.get_current_frame()
            
            if frame is not None and self.overlay is not None:
                # Render full overlay UI
                display_frame = self.overlay.render_full_overlay(frame, self.current_signal_data)
                
                # Show FPS in title bar area
                fps_text = f"FPS: {self.camera.get_fps():.1f}"
                cv2.putText(display_frame, fps_text,
                           (self.overlay.frame_width - 100, 25), cv2.FONT_HERSHEY_SIMPLEX,
                           0.45, (150, 150, 150), 1)
                
                cv2.imshow("AI Interview - Signal Capture Stage", display_frame)
            elif frame is not None:
                # Fallback if overlay not ready
                cv2.imshow("AI Interview - Signal Capture Stage", frame)
            
            # Check for quit key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.is_running = False
                break
            
            time.sleep(0.01)
        
        cv2.destroyAllWindows()
    
    def stop(self) -> None:
        """Stop the interview capture and save all data."""
        print("\n\nStopping interview capture...")
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
        print("Interview metadata saved.")
        
        print(f"\n✓ All files saved to: {self.session_manager.session_dir}")


def main():
    """Main entry point."""
    print("=" * 55)
    print("  AI INTERVIEW - SIGNAL CAPTURE STAGE")
    print("  Multimodal Candidate Behavioral Analysis")
    print("=" * 55)
    
    # Get candidate ID
    candidate_id = input("\nEnter Candidate ID: ").strip()
    if not candidate_id:
        print("Error: Candidate ID cannot be empty")
        sys.exit(1)
    
    # Create application
    app = AIInterviewCapture()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nInterrupt received, stopping interview capture...")
        app.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Setup and start session
    print(f"\nSetting up interview capture for candidate: {candidate_id}")
    app.setup_session(candidate_id)
    
    print("\nPress 's' to start interview capture, or 'q' to quit...")
    
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
    
    print("\n✓ Interview capture complete!")


if __name__ == "__main__":
    main()
