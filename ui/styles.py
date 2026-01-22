"""
UI Styles - Color and font definitions for demo overlay.
"""

class Colors:
    """Muted, scientific color palette."""
    
    # Primary colors (neutral greys)
    BACKGROUND = (30, 30, 35)       # Dark grey
    PANEL_BG = (45, 45, 50)         # Slightly lighter
    BORDER = (70, 70, 75)           # Border grey
    
    # Text colors
    TEXT_PRIMARY = (220, 220, 220)  # Off-white
    TEXT_SECONDARY = (150, 150, 155) # Muted grey
    TEXT_DISABLED = (90, 90, 95)    # Very muted
    
    # Accent colors (minimal usage)
    ACCENT_ACTIVE = (100, 180, 100)  # Muted green for active
    ACCENT_INACTIVE = (80, 80, 85)   # Grey for inactive
    ACCENT_WARNING = (180, 140, 80)  # Muted amber
    
    # Status colors
    STATUS_YES = (100, 180, 100)     # Green
    STATUS_NO = (180, 100, 100)      # Red


class Fonts:
    """Font size definitions."""
    
    TITLE = 0.6
    HEADING = 0.5
    BODY = 0.45
    SMALL = 0.4
    
    THICKNESS_NORMAL = 1
    THICKNESS_BOLD = 2
