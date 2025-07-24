#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Activating virtual environment
source backend/venv/bin/activate

# Running backend (FastAPI + Uvicorn) in background
uvicorn backend.app:app --reload &

# Running frontend
cd frontend
npm run dev

# Wait for all background jobs (like uvicorn)
wait