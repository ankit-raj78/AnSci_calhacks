@echo off
echo Setting up Survey Analysis Platform...

REM Backend setup
echo Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install Python dependencies
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    echo # OpenAI API Key for LLM integration > .env
    echo OPENAI_API_KEY=your_openai_api_key_here >> .env
    echo. >> .env
    echo # Flask Configuration >> .env
    echo FLASK_SECRET_KEY=your_secret_key_here >> .env
    echo. >> .env
    echo # Database Configuration (optional, defaults to SQLite^) >> .env
    echo DATABASE_URL=sqlite:///survey_platform.db >> .env
    echo Please edit backend\.env and add your OpenAI API key
)

cd ..

REM Frontend setup
echo Setting up frontend...
cd frontend

REM Install Node dependencies
npm install

cd ..

echo Setup complete!
echo.
echo To start the application:
echo 1. Backend: cd backend ^&^& python app.py
echo 2. Frontend: cd frontend ^&^& npm start
echo.
echo Don't forget to add your OpenAI API key to backend\.env 