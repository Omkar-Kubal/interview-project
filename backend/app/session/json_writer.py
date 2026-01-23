"""
JSON Writer - Thread-safe JSON logging utilities.
"""
import json
import threading
from pathlib import Path
from typing import Any, Dict, List


class JsonWriter:
    """Thread-safe JSON writer for logging face and audio data."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.entries: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def append(self, entry: Dict[str, Any]) -> None:
        """Thread-safe append of an entry to the log."""
        with self.lock:
            self.entries.append(entry)
    
    def flush(self) -> None:
        """Write all entries to the JSON file."""
        with self.lock:
            with open(self.file_path, 'w') as f:
                json.dump(self.entries, f, indent=2)
    
    def write_single(self, data: Dict[str, Any]) -> None:
        """Write a single dictionary as JSON (for audio_log summary)."""
        with self.lock:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def clear(self) -> None:
        """Clear all entries."""
        with self.lock:
            self.entries = []
