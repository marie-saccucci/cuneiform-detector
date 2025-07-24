# Cuneiform Detector

Cuneiform Detector is a web application for semantic segmentation of cuneiform tablets using deep learning.

## Project Structure

```
cuneiform-detector/
│
├── backend/ # FastAPI backend
│ ├── app.py # Main FastAPI app
│ ├── requirements.txt # Python dependencies
│ ├── Procfile # For deployment (optional)
│ ├── venv/ # Python virtual environment (not included in repo)
│ └── virtual_environment_setup.{sh|bat} # Script to set up environment
│
├── frontend/ # React frontend
│ ├── package.json # JavaScript dependencies
│ └── ... # Frontend components
│
├── run_app.{sh|bat} # Launch script (Linux or Windows)
└── README.md # This file
```

## Requirements

- Python 3.9+ installed
- Node.js + npm installed
- (Recommended) Use a virtual environment for Python

---

## Setup

### Backend (Python)

Open a terminal and run the setup script:

* On Windows:
```
backend\virtual_environment_setup.bat
```
* On Linux/macOs
```
./backend/virtual_environment_setup.sh
```
This will:

* Create a virtual environment in backend/venv/
* Install the required Python packages from requirements.txt

### Frontend

Install the java scripts dependencies in the frontend.
```
cd frontend
npm install
cd ..
```

## Running the Application

To start both the backend and the frontend:
* On Windows:
```
run_app.bat
```
* On Linux/macOS:
```
./run_app.sh
```

The FastAPI backend will run on http://127.0.0.1:8000

The React frontend will run on http://localhost:3000


## License:
The model was trained on electronic Babylonian Library data and is therefore under the license CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike 4.0 International). 

This project is open-source.