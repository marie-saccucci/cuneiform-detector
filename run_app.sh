#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

cd backend

# Activating virtual environment
source venv/bin/activate

# Running backend (FastAPI + Uvicorn) in background
uvicorn app:app --reload &

# Running frontend
cd ..\frontend 
npm run dev

# Wait for all background jobs (like uvicorn)
wait