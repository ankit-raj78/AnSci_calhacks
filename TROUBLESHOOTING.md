# AnSci Troubleshooting Guide

## Issues Fixed

### ✅ 1. JSX Syntax Error
**Problem**: Missing closing `</span>` tag in frontend landing page
**Error**: `Unexpected token 'div'. Expected jsx identifier`
**Solution**: Added missing closing span tag in `frontend/app/page.tsx`

### ✅ 2. Missing ffmpeg
**Problem**: Audio processing failed due to missing ffmpeg
**Error**: `[Errno 2] No such file or directory: 'ffmpeg'`
**Solution**: Installed ffmpeg via Homebrew
```bash
brew install ffmpeg
```

### ✅ 3. Asyncio Event Loop Conflict
**Problem**: LMNT TTS asyncio calls conflicting with FastAPI's event loop
**Error**: `asyncio.run() cannot be called from a running event loop`
**Solution**: Updated `backend/ansci/audio.py` to handle existing event loops properly:
- Detect if already in an event loop
- Use ThreadPoolExecutor to run async code in a separate thread
- Added proper error handling and cleanup

### ✅ 4. CORS Configuration
**Problem**: Frontend couldn't connect to backend API
**Solution**: Added CORS middleware to FastAPI backend allowing localhost:3000

### ✅ 5. Frontend-Backend Integration
**Problem**: Frontend was using mock data instead of real API calls
**Solution**: 
- Created `frontend/lib/api.ts` service for backend communication
- Updated frontend app page with real file upload functionality
- Added drag-and-drop file upload
- Integrated actual animation generation workflow

## Current Status

### ✅ **Working Features**:
- Frontend running on http://localhost:3000
- Backend API running on http://localhost:8000
- File upload functionality
- CORS properly configured
- ffmpeg installed for audio processing
- Asyncio conflicts resolved
- Error handling improved

### 🔧 **Audio Generation**:
- LMNT TTS integration fixed for event loop conflicts
- System TTS fallback working
- Silent audio fallback for cases where TTS fails
- ffmpeg processing for audio duration matching

## Testing

### Test Connection
```bash
./test-connection.sh
```

### Start Development Environment
```bash
./start-dev.sh
```

### Manual Testing
1. Upload a PDF file through the frontend
2. Select animation scope
3. Generate animation
4. Check backend logs for processing status

## Common Issues

### Issue: "Frontend not responding"
**Solution**: Make sure Node.js dependencies are installed
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

### Issue: "Backend not responding" 
**Solution**: Ensure Python environment is set up
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue: Audio generation fails
**Possible causes**:
1. Missing LMNT_API_KEY environment variable
2. ffmpeg not installed
3. Asyncio conflicts

**Solutions**:
1. Set LMNT_API_KEY in environment
2. Install ffmpeg: `brew install ffmpeg`
3. The asyncio fixes should handle most conflicts

### Issue: File upload errors
**Check**:
1. File is a valid PDF
2. Backend CORS is configured
3. API endpoint is accessible

## Environment Variables

Required in backend:
```
LMNT_API_KEY=your_lmnt_api_key_here
```

## API Endpoints

- `GET /` - Backend health check
- `POST /api/create-animation` - Upload PDF and generate animation
- `GET /videos/{filename}` - Serve generated videos
- `GET /docs` - API documentation

## Debugging

### Backend Logs
Check terminal running the backend for detailed processing logs

### Frontend Network
Use browser developer tools to inspect API calls

### Audio Processing
Look for ffmpeg-related errors in backend logs

### File Permissions
Ensure output directories are writable 