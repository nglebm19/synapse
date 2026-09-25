# Synapse — YouTube-to-transcript+summary

Local-first, full‑stack app that converts YouTube videos into transcripts and smart summaries using self‑hosted models optimized for Apple Silicon.

## Overview

This monorepo contains:

- `backend/`: FastAPI service for video processing, transcription (Whisper), and summarization (DistilBART)
- `frontend/`: React + TypeScript + Vite frontend (port 8080)

Helpful docs:

- [`docs/PROJECT_ARCHITECTURE.md`](./docs/PROJECT_ARCHITECTURE.md)
- [`docs/LOCAL_MODEL_GUIDE.md`](./docs/LOCAL_MODEL_GUIDE.md)
- [`docs/RECOMMENDED_MODELS_M1_PRO.md`](./docs/RECOMMENDED_MODELS_M1_PRO.md)
- [`docs/DEBUG_GUIDE.md`](./docs/DEBUG_GUIDE.md)
- [`docs/DATABASE_STATUS.md`](./docs/DATABASE_STATUS.md)

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
   - Create `backend/.env` if you want to override defaults (see `docs/LOCAL_MODEL_GUIDE.md`)
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
   cd frontend
   npm i
   ```
2. Start the dev server
   ```bash
   npm run dev
   ```
3. Access the app
   - Frontend: `http://localhost:8080/`

Configuration is currently hardcoded (no `.env` is read):

- Backend API URL: `API_BASE_URL` in `frontend/src/services/api.ts` (`http://localhost:8000/api`)
- Supabase URL and anon key: `frontend/src/integrations/supabase/client.ts`
- Supabase schema: `frontend/supabase/migrations/`

## Ports

- Frontend: `http://localhost:8080/`
- Backend: `http://localhost:8000/`
- Backend API: `http://localhost:8000/api/`

Details in [`docs/FIXED_PORTS.md`](./docs/FIXED_PORTS.md).

## Testing

There is no automated test suite yet.

Backend smoke check (imports, model loading, database):
```bash
cd backend
source venv/bin/activate
python scripts/test_system.py
```

Frontend lint:
```bash
cd frontend
npm run lint
```

## Repository Structure

```
.
├── backend/             FastAPI service
│   ├── app/
│   │   ├── api/         Routes (health, video processing)
│   │   ├── database/    SQLite models and operations
│   │   ├── models/      ModelManager (Whisper + DistilBART)
│   │   └── services/    YouTube download/extract
│   ├── scripts/         Manual checks (test_system.py)
│   ├── models/          Local model cache (git-ignored)
│   ├── requirements.txt
│   └── run_server.sh
├── frontend/            React + TypeScript + Vite app
│   ├── src/
│   ├── public/
│   ├── supabase/        Supabase config and migrations
│   ├── package.json
│   └── vite.config.ts
└── docs/                Architecture, model, and debugging guides
```

## License

MIT
