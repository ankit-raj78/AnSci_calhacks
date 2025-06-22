#!/bin/bash

echo "🧪 Testing Frontend-Backend Connection..."

# Test if backend is running
echo "Testing backend connection..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is responding"
    echo "Response: $(curl -s http://localhost:8000/)"
else
    echo "❌ Backend is not responding on http://localhost:8000"
    echo "Make sure to start the backend first: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
fi

echo ""

# Test if frontend is running
echo "Testing frontend connection..."
if curl -s http://localhost:3000/ > /dev/null; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding on http://localhost:3000"
    echo "Make sure to start the frontend first: cd frontend && npm run dev"
fi

echo ""
echo "🔗 Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs" 