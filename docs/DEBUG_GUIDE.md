# 🔧 Synapse Debugging Guide

## Quick Connection Test

### 1. Test Backend Health
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy",...}
```

### 2. Test Frontend Access
Open browser: http://localhost:5173
- Look for "Backend: Online/Offline" indicator
- Open browser console (F12) for error messages

## 🐛 Common Bug Locations

### Frontend Issues

#### A. API Service (`src/services/api.ts`)
**Check lines 5, 15-30:**
- API_BASE_URL must match backend port
- Request headers and error handling
- CORS issues show here first

#### B. Health Check (`src/pages/Index.tsx`) 
**Check lines 20-35:**
- useEffect hook for health checking
- Error handling in checkBackendHealth()
- State management for backendStatus

#### C. Browser Console Errors
**Open Developer Tools (F12) → Console:**
- CORS errors: `Access-Control-Allow-Origin`
- Network errors: `Failed to fetch`
- Connection refused: `ERR_CONNECTION_REFUSED`

### Backend Issues

#### A. CORS Configuration (`backend/app/main.py`)
**Check lines 44-50:**
- allow_origins must include frontend URL
- Should have: `"http://localhost:5173"`

#### B. Server Startup (`backend/app/main.py`)
**Check lines 80-90:**
- Host and port configuration
- Lifespan events for model loading

#### C. Health Endpoint (`backend/app/api/health.py`)
**Check lines 25-45:**
- Model manager availability
- Response format matching frontend expectations

## 🔍 Step-by-Step Debugging

### Step 1: Check Browser Console
1. Open http://localhost:5173
2. Press F12 → Console tab
3. Look for red error messages
4. Common errors:
   - `CORS policy` → Backend CORS issue
   - `Failed to fetch` → Backend not running
   - `ERR_CONNECTION_REFUSED` → Wrong port/URL

### Step 2: Test API Manually
```bash
# Test each endpoint:
curl http://localhost:8000/
curl http://localhost:8000/api/health
curl http://localhost:8000/docs  # API documentation
```

### Step 3: Check Server Logs
**Backend logs show:**
- Model loading status
- Request/response details
- Error stack traces

**Frontend logs show:**
- API call attempts
- State changes
- Component render issues

## 🚨 Emergency Fixes

### Fix 1: CORS Issues
If you see CORS errors in browser console:

**Edit `backend/app/main.py` lines 44-50:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary fix - allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Fix 2: Port Conflicts
If ports are taken:

**Backend (change port 8000):**
```bash
# In backend/.env
PORT=8001
```

**Frontend (update API URL):**
```typescript
// In src/services/api.ts
const API_BASE_URL = 'http://localhost:8001/api';
```

### Fix 3: Model Loading Issues
If backend health shows models not loaded:

```bash
cd backend
rm -rf models/  # Clear model cache
python -m app.main  # Restart to re-download
```

## 📊 Debug Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Browser console shows no CORS errors
- [ ] API health endpoint returns 200
- [ ] Backend logs show "All models loaded successfully"
- [ ] Frontend shows "Backend: Online & Ready"

## 🆘 Get Help

If still stuck, check these files for the exact error:
1. Browser Console (F12)
2. Backend terminal output
3. `src/services/api.ts` - API calls
4. `backend/app/main.py` - CORS settings
5. `src/pages/Index.tsx` - Health checking logic

