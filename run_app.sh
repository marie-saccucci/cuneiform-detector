#!/bin/bash

# Activating virtual environment
source backend/venv/bin/activate

# Running backend
uvicorn backend.app:app --reload &

# Running frontend
npm run --prefix frontend

wait