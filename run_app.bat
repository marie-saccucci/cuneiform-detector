@echo off
REM Activating virtual environment
call venv\Scripts\activate

REM Runnning backend (FastAPI + uvicorn)
start /b uvicorn backend.app:app --reload

REM running frontend
start "" "npm" "run" "--prefix" "frontend"

pause