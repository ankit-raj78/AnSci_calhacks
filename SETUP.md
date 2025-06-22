# AnSci Development Environment Setup

## Quick Start

### Automatic Start (Recommended)
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Manual Start

#### 1. Start Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# Or on Windows: .venv\Scripts\activate
pip install -e .
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Start Frontend (Next.js)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## Access URLs

- **Frontend App**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

## Features

1. **File Upload**: Upload PDF research papers through the frontend interface
2. **Select Scope**: Choose animation generation scope (High-Level Summary, Core Concepts, Full Walkthrough)
3. **Generate Animation**: Backend processes PDF and generates animation videos
4. **View Results**: Watch generated animations in the frontend

## API Endpoints

- `POST /api/create-animation`: Upload PDF and generate animation
  - Parameters: `file` (PDF file), `scope` (animation scope)
  - Returns: List of animation video URLs

- `GET /videos/{filename}`: Access generated video files

## Troubleshooting

If you encounter dependency issues:
```bash
# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Backend
cd backend
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .
``` 