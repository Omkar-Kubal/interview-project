# Signal Capture MVP

A local-only, offline demo system that captures visual and audio behavioral signals from users using a webcam and microphone.

## Features

- **Camera-based detection**
  - Face presence detection per frame
  - Eye blink detection (EAR-based)
  - Eye direction classification (left/right/center)
  - Head movement intensity (low/medium/high)
  - Video recording to MP4

- **Audio-based detection**
  - Voice activity detection (energy threshold)
  - Speaking duration tracking
  - Average volume measurement
  - Audio recording to WAV

- **Per-user session isolation**
  - Unique folder per user
  - JSON-based logging
  - Session metadata

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Enter your User ID when prompted
2. Press `s` to start recording
3. Press `q` in the video window to stop and save

## Output Files

All outputs are saved to `data/user_<id>/`:

| File | Description |
|------|-------------|
| `video.mp4` | Recorded video stream |
| `audio.wav` | Recorded audio stream |
| `face_log.json` | Per-frame face detection data |
| `audio_log.json` | Voice activity summary |
| `session_meta.json` | Session metadata |

### face_log.json format

```json
[
  {
    "frame_timestamp": 0.033,
    "face_present": true,
    "eye_direction": "center",
    "blink": false,
    "head_movement": "low"
  }
]
```

### audio_log.json format

```json
{
  "voice_detected": true,
  "total_speaking_time_sec": 38.5,
  "total_duration_sec": 120.0,
  "average_volume": -20.3
}
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
├── data/                   # Output directory
│   └── user_<id>/          # Per-user data
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8+
- Webcam
- Microphone
- No internet connection required

## Tech Stack

- OpenCV - Video capture and recording
- MediaPipe Face Mesh - Facial landmark detection
- SoundDevice - Audio capture
- SciPy - WAV file handling
