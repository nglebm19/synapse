# Synapse Backend

AI-powered video lecture processing backend optimized for Apple M1 Pro with self-hosted models.

## Features

- 🎥 YouTube video audio extraction
- 🎤 Speech-to-text transcription using Whisper
- 📝 Intelligent summarization using DistilBART
- ⚡ Optimized for Apple M1 Pro with Metal Performance Shaders
- 🔄 Async processing with job queue
- 📊 SQLite database for job tracking
- 🌐 FastAPI REST API

## Models Used

- **Whisper Small** (244MB) - Speech-to-text transcription
- **DistilBART CNN 12-6** (306MB) - Text summarization
- **Total Model Size**: ~550MB
- **RAM Usage**: ~2-3GB during processing

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# For bash/zsh:
source venv/bin/activate
# For fish:
source venv/bin/activate.fish

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Database URL (SQLite by default)
- Model cache directory
- Processing limits

### 3. Run the Server

```bash
# Development mode with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/health

## API Endpoints

### Video Processing

```bash
# Process a YouTube video
POST /api/process-video
{
  "video_url": "https://youtube.com/watch?v=...",
  "user_id": "optional-user-id"
}

# Check job status
GET /api/job-status/{job_id}

# Get results
GET /api/job-results/{job_id}

# Get user jobs
GET /api/jobs?user_id={user_id}
```

### Health Checks

```bash
# General health
GET /api/health

# Model status
GET /api/health/models

# Readiness probe
GET /api/health/ready
```

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # AI model management
│   │   └── model_manager.py # Whisper & BART integration
│   ├── services/            # Business logic
│   │   └── youtube_service.py # YouTube processing
│   ├── api/                 # API routes
│   │   ├── health.py        # Health endpoints
│   │   └── video_processing.py # Main API
│   ├── database/            # Database models
│   │   └── database.py      # SQLAlchemy models
│   └── utils/               # Utilities
├── models/                  # Cached AI models
├── temp/                    # Temporary files
└── requirements.txt         # Dependencies
```

## Performance Optimization

### Apple M1 Pro Optimizations

- **Metal Performance Shaders**: Automatic GPU acceleration
- **Unified Memory**: Efficient memory usage
- **Model Caching**: Models loaded once at startup
- **Async Processing**: Non-blocking API responses

### Processing Times (Estimates)

| Video Length | Processing Time | Memory Usage |
|-------------|----------------|--------------|
| 5 minutes   | ~1-2 minutes   | ~2GB RAM     |
| 15 minutes  | ~3-5 minutes   | ~2.5GB RAM   |
| 30 minutes  | ~6-10 minutes  | ~3GB RAM     |
| 1 hour      | ~12-20 minutes | ~3.5GB RAM   |

## Development

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Database Management

```bash
# Create tables (automatic on startup)
# Check database with:
sqlite3 synapse.db ".tables"
```

### Model Management

Models are automatically downloaded on first use and cached in the `models/` directory:

- First startup: ~2-5 minutes (downloading models)
- Subsequent startups: ~30-60 seconds (loading cached models)

### Monitoring

Monitor logs for:
- Model loading status
- Processing progress
- Error messages
- Performance metrics

## Troubleshooting

### Common Issues

1. **Models not loading**: Check internet connection and disk space
2. **Out of memory**: Reduce `MAX_CONCURRENT_JOBS` in `.env`
3. **YouTube download fails**: Update `yt-dlp` package
4. **Slow processing**: Ensure M1 optimizations are working (check logs for "mps" device)

### Logs

Check logs for detailed information:
```bash
# View logs in real-time
tail -f app.log

# Check startup logs
grep "Model Manager" app.log
```

## Production Deployment

For production deployment:

1. **Environment**: Set `ENVIRONMENT=production` in `.env`
2. **Database**: Switch to PostgreSQL for better performance
3. **Monitoring**: Add proper logging and monitoring
4. **Scaling**: Consider Redis for job queue in multi-instance setup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

This project is licensed under the MIT License.

