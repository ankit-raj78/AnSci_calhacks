#!/bin/bash

echo "🚀 Starting AnSci development environment..."

# Check if necessary dependencies are installed
echo "📦 Checking backend dependencies..."
cd backend
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv .venv
fi

source .venv/bin/activate
pip install -e .

echo "🌐 Starting backend service (FastAPI)..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend
echo "📦 Checking frontend dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --legacy-peer-deps
fi

echo "🎨 Starting frontend service (Next.js)..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Development environment started!"
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend: http://localhost:8000"
echo "📖 Backend API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait 