# AI Interview - Signal Capture Stage

A multimodal candidate behavioral signal capture system — Stage 1 of an AI-powered hiring pipeline.

## Overview

This system captures visual and audio behavioral signals during candidate interviews:
- **Video recording** with face, eye, and head tracking
- **Audio recording** with voice activity detection
- **Session integrity monitoring**
- **Per-candidate data isolation**

> **Note:** This is the Signal Capture Stage. Evaluation and scoring are handled in subsequent stages.

## Features

### Active in This Stage
- ✅ Face presence detection
- ✅ Eye blink detection (EAR-based)
- ✅ Eye direction tracking (left/right/center)
- ✅ Head movement intensity (low/medium/high)
- ✅ Voice activity detection
- ✅ Video + audio recording
- ✅ Session integrity signals

### Disabled in Demo (Future Stages)
- ○ Speech-to-text
- ○ Answer relevance scoring
- ○ Behavioral analysis
- ○ Composite candidate scoring

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Enter Candidate ID when prompted
2. Press `s` to start interview capture
3. Press `q` in the video window to stop and save

## Output Files

All outputs are saved to `data/user_<candidate_id>/`:

| File | Description |
|------|-------------|
| `video.mp4` | Interview video recording |
| `audio.wav` | Interview audio recording |
| `face_log.json` | Per-frame behavioral signals |
| `audio_log.json` | Voice activity summary |
| `session_meta.json` | Interview capture metadata |

## Candidate Lifecycle

```
[■ Capture] → [○ Analysis] → [○ Review] → [○ Shortlist]
     ↑
  You are here
```

## Project Structure

```
project_root/
├── main.py                 # Entry point
├── camera/
│   ├── camera_capture.py   # Video recording
│   ├── eye_tracking.py     # MediaPipe eye detection
│   ├── head_movement.py    # Head movement tracking
│   └── face_logger.py      # Face log aggregation
├── audio/
│   ├── audio_capture.py    # WAV recording
│   └── voice_activity.py   # Voice activity detection
├── storage/
│   ├── session_manager.py  # Session lifecycle
│   └── json_writer.py      # JSON utilities
├── ui/
│   ├── overlay.py          # Interview context panels
│   └── styles.py           # UI styling
├── data/                   # Output directory
├── doc/                    # Documentation
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8+
- Webcam
- Microphone
- No internet connection required

## Tech Stack

- **OpenCV** — Video capture and recording
- **MediaPipe Face Mesh** — Facial landmark detection
- **SoundDevice** — Audio capture
- **SciPy** — WAV file handling
