#!/bin/bash

echo "Setting up Survey Analysis Platform..."

# Backend setup
echo "Setting up backend..."
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install Python dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "# OpenAI API Key for LLM integration" > .env
    echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
    echo "" >> .env
    echo "# Flask Configuration" >> .env
    echo "FLASK_SECRET_KEY=your_secret_key_here" >> .env
    echo "" >> .env
    echo "# Database Configuration (optional, defaults to SQLite)" >> .env
    echo "DATABASE_URL=sqlite:///survey_platform.db" >> .env
    echo "Please edit backend/.env and add your OpenAI API key"
fi

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend

# Install Node dependencies
npm install

cd ..

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && python app.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Don't forget to add your OpenAI API key to backend/.env" 