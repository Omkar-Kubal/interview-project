# Signal Capture Frontend

Web-based interface for the AI Interview Signal Capture system. This module provides the Candidate Interaction Layer for initiating and monitoring interview capture sessions.

## Architecture

```
signal-capture-frontend/
├── pages/
│   ├── index.html           # Landing page (Candidate ID entry)
│   ├── capture.html         # Live capture page (camera/mic)
│   └── summary.html         # Session complete summary
├── scripts/
│   ├── session.js           # API calls (start/stop)
│   ├── media.js             # Camera + mic lifecycle
│   ├── signals.js           # WebSocket handling
│   └── ui.js                # DOM utilities
├── styles/                  # CSS (uses Tailwind CDN)
├── config.js                # Configuration
└── public/assets/           # Static assets
```

## User Flow

1. **Landing Page** (`/`)
   - Enter Candidate ID
   - Click "Begin Capture"
   - No camera access yet

2. **Live Capture Page** (`/capture`)
   - Camera/mic permission requested
   - Live video feed displayed
   - Real-time signal telemetry
   - Click "End Session" when done

3. **Summary Page** (`/summary`)
   - View session statistics
   - Start new session

## Running

The frontend is served by the backend. Start the backend server:

```bash
cd signal-capture-backend
python -m uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000` in your browser.

## Key Design Decisions

### Camera Access Timing

Camera and microphone permissions are requested **only** on the capture page, not the landing page. This ensures:
- Clean UX flow
- No surprise permission popups
- Professional demo experience

### Modular JavaScript

Scripts are split by function, not by page:
- `session.js` - All API calls
- `media.js` - MediaDevices API handling
- `signals.js` - WebSocket management
- `ui.js` - DOM utilities

## Demo vs Product

This is a **demo frontend**. In production:
- Would use a build system (Vite, Next.js)
- TypeScript for type safety
- Component framework (React, Vue)
- Proper bundling and minification

---

*This demo captures raw signals only. No AI analysis, scoring, or hiring decisions are performed.*
