"""
UI Overlay - Rendering panels for AI Interview demo.
"""
import cv2
import numpy as np
from typing import Dict, Any, Optional
from .styles import Colors, Fonts


class OverlayRenderer:
    """Renders overlay panels on video frames."""
    
    def __init__(self, frame_width: int, frame_height: int):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Interview context (static demo values)
        self.interview_context = {
            "type": "Technical Screening (Demo)",
            "role": "Backend Engineer",
            "stage": "Initial Screening",
            "question": "1 of 3",
            "mode": "Video + Audio"
        }
        
        # Integrity signals (updated during capture)
        self.integrity_signals = {
            "face_continuous": True,
            "multiple_faces": False,
            "audio_interruptions": False
        }
        
        # Tracking state
        self.face_present_count = 0
        self.total_frame_count = 0
        self.multiple_face_detected = False
    
    def update_integrity(self, face_present: bool, face_count: int = 1) -> None:
        """Update integrity signals based on frame data."""
        self.total_frame_count += 1
        if face_present:
            self.face_present_count += 1
        
        # Face continuously present if >90% of frames have face
        if self.total_frame_count > 0:
            presence_ratio = self.face_present_count / self.total_frame_count
            self.integrity_signals["face_continuous"] = presence_ratio > 0.9
        
        # Multiple faces detection
        if face_count > 1:
            self.multiple_face_detected = True
        self.integrity_signals["multiple_faces"] = self.multiple_face_detected
    
    def render_full_overlay(self, frame: np.ndarray, signal_data: Dict[str, Any]) -> np.ndarray:
        """Render all overlay panels on frame."""
        # Create extended canvas for side panels
        panel_width = 320
        canvas_width = self.frame_width + panel_width
        canvas = np.zeros((self.frame_height, canvas_width, 3), dtype=np.uint8)
        canvas[:] = Colors.BACKGROUND
        
        # Place video frame on left
        canvas[0:self.frame_height, 0:self.frame_width] = frame
        
        # Draw side panel
        panel_x = self.frame_width
        self._draw_panel_background(canvas, panel_x, 0, panel_width, self.frame_height)
        
        # Render interview context
        y_offset = self._draw_interview_context(canvas, panel_x + 10, 10)
        
        # Render signal capture status
        y_offset = self._draw_signal_status(canvas, panel_x + 10, y_offset + 20, signal_data)
        
        # Render integrity signals
        y_offset = self._draw_integrity_signals(canvas, panel_x + 10, y_offset + 20)
        
        # Render lifecycle indicator at bottom
        self._draw_lifecycle_indicator(canvas, panel_x + 10, self.frame_height - 100)
        
        # Render disabled evaluation preview
        self._draw_evaluation_preview(canvas, panel_x + 10, y_offset + 20)
        
        # Draw title bar on video
        self._draw_title_bar(canvas)
        
        return canvas
    
    def _draw_panel_background(self, canvas: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        """Draw panel background with border."""
        cv2.rectangle(canvas, (x, y), (x + w, y + h), Colors.PANEL_BG, -1)
        cv2.line(canvas, (x, y), (x, y + h), Colors.BORDER, 2)
    
    def _draw_title_bar(self, canvas: np.ndarray) -> None:
        """Draw main title on video."""
        title = "AI INTERVIEW - SIGNAL CAPTURE STAGE"
        cv2.rectangle(canvas, (0, 0), (self.frame_width, 35), Colors.PANEL_BG, -1)
        cv2.putText(canvas, title, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 
                    Fonts.HEADING, Colors.TEXT_PRIMARY, Fonts.THICKNESS_BOLD)
    
    def _draw_interview_context(self, canvas: np.ndarray, x: int, y: int) -> int:
        """Draw interview context panel. Returns y position after panel."""
        # Header
        cv2.putText(canvas, "INTERVIEW CONTEXT", (x, y + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, Fonts.BODY, Colors.TEXT_PRIMARY, Fonts.THICKNESS_BOLD)
        cv2.line(canvas, (x, y + 28), (x + 200, y + 28), Colors.BORDER, 1)
        
        # Context items
        items = [
            ("Type:", self.interview_context["type"]),
            ("Role:", self.interview_context["role"]),
            ("Stage:", self.interview_context["stage"]),
            ("Question:", self.interview_context["question"]),
            ("Mode:", self.interview_context["mode"])
        ]
        
        y_pos = y + 50
        for label, value in items:
            cv2.putText(canvas, label, (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                        Fonts.SMALL, Colors.TEXT_SECONDARY, Fonts.THICKNESS_NORMAL)
            cv2.putText(canvas, value, (x + 70, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                        Fonts.SMALL, Colors.TEXT_PRIMARY, Fonts.THICKNESS_NORMAL)
            y_pos += 22
        
        return y_pos
    
    def _draw_signal_status(self, canvas: np.ndarray, x: int, y: int, signal_data: Dict[str, Any]) -> int:
        """Draw signal capture status. Returns y position after panel."""
        # Header
        cv2.putText(canvas, "SIGNAL CAPTURE", (x, y + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, Fonts.BODY, Colors.TEXT_PRIMARY, Fonts.THICKNESS_BOLD)
        cv2.line(canvas, (x, y + 28), (x + 200, y + 28), Colors.BORDER, 1)
        
        # Status items
        face_icon = "+" if signal_data.get("face_present", False) else "-"
        face_color = Colors.STATUS_YES if signal_data.get("face_present", False) else Colors.STATUS_NO
        
        y_pos = y + 50
        
        # Face status
        cv2.putText(canvas, f"Face: [{face_icon}]", (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    Fonts.SMALL, face_color, Fonts.THICKNESS_NORMAL)
        
        # Eye direction
        eye_dir = signal_data.get("eye_direction", "unknown")
        cv2.putText(canvas, f"Eye: {eye_dir}", (x + 100, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    Fonts.SMALL, Colors.TEXT_PRIMARY, Fonts.THICKNESS_NORMAL)
        y_pos += 22
        
        # Head movement
        head_mov = signal_data.get("head_movement", "unknown")
        cv2.putText(canvas, f"Head: {head_mov}", (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    Fonts.SMALL, Colors.TEXT_PRIMARY, Fonts.THICKNESS_NORMAL)
        
        # Blink
        blink = "Yes" if signal_data.get("blink", False) else "No"
        cv2.putText(canvas, f"Blink: {blink}", (x + 100, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    Fonts.SMALL, Colors.TEXT_PRIMARY, Fonts.THICKNESS_NORMAL)
        y_pos += 22
        
        # Voice
        voice = signal_data.get("voice_active", False)
        voice_text = "Active" if voice else "Silent"
        voice_color = Colors.STATUS_YES if voice else Colors.TEXT_SECONDARY
        cv2.putText(canvas, f"Voice: {voice_text}", (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    Fonts.SMALL, voice_color, Fonts.THICKNESS_NORMAL)
        
        return y_pos + 20
    
    def _draw_integrity_signals(self, canvas: np.ndarray, x: int, y: int) -> int:
        """Draw session integrity signals. Returns y position after panel."""
        # Header
        cv2.putText(canvas, "SESSION INTEGRITY", (x, y + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, Fonts.BODY, Colors.TEXT_PRIMARY, Fonts.THICKNESS_BOLD)
        cv2.line(canvas, (x, y + 28), (x + 200, y + 28), Colors.BORDER, 1)
        
        y_pos = y + 50
        
        # Integrity items
        items = [
            ("Face continuous:", self.integrity_signals["face_continuous"]),
            ("Multiple faces:", self.integrity_signals["multiple_faces"]),
            ("Audio interrupts:", self.integrity_signals["audio_interruptions"])
        ]
        
        for label, value in items:
            # For multiple faces and interrupts, True is bad
            if "Multiple" in label or "interrupt" in label:
                color = Colors.STATUS_NO if value else Colors.STATUS_YES
                text = "Yes" if value else "No"
            else:
                color = Colors.STATUS_YES if value else Colors.STATUS_NO
                text = "Yes" if value else "No"
            
            cv2.putText(canvas, label, (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                        Fonts.SMALL, Colors.TEXT_SECONDARY, Fonts.THICKNESS_NORMAL)
            cv2.putText(canvas, text, (x + 160, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                        Fonts.SMALL, color, Fonts.THICKNESS_NORMAL)
            y_pos += 22
        
        return y_pos
    
    def _draw_evaluation_preview(self, canvas: np.ndarray, x: int, y: int) -> None:
        """Draw disabled evaluation pipeline preview."""
        # Header (greyed out)
        cv2.putText(canvas, "EVALUATION PIPELINE", (x, y + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, Fonts.BODY, Colors.TEXT_DISABLED, Fonts.THICKNESS_NORMAL)
        cv2.putText(canvas, "(Disabled in Demo)", (x + 5, y + 38), 
                    cv2.FONT_HERSHEY_SIMPLEX, Fonts.SMALL, Colors.TEXT_DISABLED, Fonts.THICKNESS_NORMAL)
        
        y_pos = y + 58
        
        # Disabled items
        items = [
            "Speech-to-text",
            "Answer relevance",
            "Behavioral analysis",
            "Composite score"
        ]
        
        for item in items:
            cv2.putText(canvas, f"o {item}", (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                        Fonts.SMALL, Colors.TEXT_DISABLED, Fonts.THICKNESS_NORMAL)
            cv2.putText(canvas, "[Not active]", (x + 160, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                        Fonts.SMALL, Colors.TEXT_DISABLED, Fonts.THICKNESS_NORMAL)
            y_pos += 20
    
    def _draw_lifecycle_indicator(self, canvas: np.ndarray, x: int, y: int) -> None:
        """Draw candidate lifecycle strip."""
        # Header
        cv2.putText(canvas, "CANDIDATE LIFECYCLE", (x, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, Fonts.SMALL, Colors.TEXT_SECONDARY, Fonts.THICKNESS_NORMAL)
        
        # Stages
        stages = ["Capture", "Analysis", "Review", "Shortlist"]
        stage_x = x
        
        for i, stage in enumerate(stages):
            if i == 0:
                # Active stage
                color = Colors.ACCENT_ACTIVE
                prefix = "[*"
                suffix = "]"
            else:
                # Inactive stages
                color = Colors.TEXT_DISABLED
                prefix = "[ "
                suffix = "]"
            
            text = f"{prefix} {stage} {suffix}"
            cv2.putText(canvas, text, (stage_x, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 
                        Fonts.SMALL, color, Fonts.THICKNESS_NORMAL)
            
            # Arrow between stages
            if i < len(stages) - 1:
                stage_x += 75
                cv2.putText(canvas, ">", (stage_x - 10, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 
                            Fonts.SMALL, Colors.TEXT_DISABLED, Fonts.THICKNESS_NORMAL)
