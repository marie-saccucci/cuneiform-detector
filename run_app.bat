@echo off
REM Activating virtual environment
cd backend
call venv\Scripts\activate

REM Runnning backend (FastAPI + uvicorn)
start /b uvicorn app:app --reload

REM running frontend
cd ..\frontend 
start "frontend" cmd /k "npm run dev"

pause