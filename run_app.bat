@echo off
REM Activating virtual environment
call backend\venv\Scripts\activate

REM Runnning backend (FastAPI + uvicorn)
start /b uvicorn backend.app:app --reload

REM running frontend
cd frontend 
start "frontend" cmd /k "npm run dev"

pause