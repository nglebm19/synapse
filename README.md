# Synapse — YouTube-to-transcript+summary

Local-first, full‑stack app that converts YouTube videos into transcripts and smart summaries using self‑hosted models optimized for Apple Silicon.

## Overview

This monorepo contains:

- `backend/`: FastAPI service for video processing, transcription (Whisper), and summarization (DistilBART)
- `study-synapse/`: React + TypeScript + Vite frontend (port 8080)

Helpful docs:

- [`PROJECT_ARCHITECTURE.md`](./PROJECT_ARCHITECTURE.md)
- [`LOCAL_MODEL_GUIDE.md`](./LOCAL_MODEL_GUIDE.md)
- [`FIXED_PORTS.md`](./FIXED_PORTS.md)

## Requirements

- Python 3.11
- Node.js 20.x and npm
- ffmpeg installed on your system (e.g., `brew install ffmpeg` on macOS)

## Quick Start

### Backend (FastAPI)

1. Install dependencies and activate venv
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment (optional)
   - Create `backend/.env` if you want to override defaults (see `LOCAL_MODEL_GUIDE.md`)
3. Run the server (uses `backend/run_server.sh`)
   ```bash
   ./run_server.sh
   ```
4. Access
   - API: `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`
   - Health: `http://localhost:8000/api/health`

Key backend files:

- `backend/app/main.py` — FastAPI app and CORS
- `backend/app/api/video_processing.py` — Processing endpoints
- `backend/app/models/model_manager.py` — Whisper + DistilBART
- `backend/app/services/youtube_service.py` — YouTube download/extract
- `backend/app/database/database.py` — SQLite models and ops

### Frontend (Vite + React + TS)

1. Install dependencies
   ```bash
   cd study-synapse
   npm i
   ```
2. Configure environment (Supabase + API URL)
   Create `study-synapse/.env`:
   ```bash
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_API_BASE_URL=http://localhost:8000/api
   ```
3. Start the dev server
   ```bash
   npm run dev
   ```
4. Access the app
   - Frontend: `http://localhost:8080/`

See `study-synapse/src/services/api.ts` for the API base URL usage.

## Ports

- Frontend: `http://localhost:8080/`
- Backend: `http://localhost:8000/`
- Backend API: `http://localhost:8000/api/`

Details in [`FIXED_PORTS.md`](./FIXED_PORTS.md).

## Testing

Backend tests:
```bash
cd backend
source venv/bin/activate
pytest
```

Frontend lint:
```bash
cd study-synapse
npm run lint
```

## Repository Structure

```
.
├── backend/
│   ├── app/
│   ├── models/
│   ├── temp/
│   ├── requirements.txt
│   ├── run_server.sh
│   └── venv/
├── study-synapse/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── PROJECT_ARCHITECTURE.md
├── LOCAL_MODEL_GUIDE.md
└── FIXED_PORTS.md
```

## License

MIT


