# Cuneiform Detector

Cuneiform Detector is a web application for semantic segmentation of cuneiform tablets using deep learning.

## Project Structure

```
cuneiform-detector/
│
├── backend/ # FastAPI backend
│ ├── app.py # Main FastAPI app
│ ├── requirements.txt # Python dependencies
│ ├── venv/ # Python virtual environment (not included in repo)
│ └── U_net_weights.pth (semantic segmentation model weights)
│
├── frontend/ # React frontend
│ ├── package.json # JavaScript dependencies
│ └── ... # Frontend components
│
├── .gitattributes
├── package-lock.json
├── run_app.{sh|bat} # Launch script (Linux or Windows)
├── virtual_environment_setup.{sh|bat} # Script to set up environment 
└── README.md # This file
```

## Requirements

- Python 3.9+ installed
- Node.js 18+ + npm installed
- (Recommended) Use a virtual environment for Python

---

## Setup

### Executable files on Linux

In a terminal
```
chmod +x virtual_environment_setup.sh
chmod +x run_app.sh
```

### Backend (Python)

Open a terminal and run the setup script:

* On Windows:
```
virtual_environment_setup.bat
```
* On Linux/macOs
```
./virtual_environment_setup.sh
```
This will:

* Create a virtual environment in backend/venv/
* Install the required Python packages from requirements.txt

### Frontend

Install the JavaScript dependencies in the frontend.
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

This script runs the backend (uvicorn) and the frontend.

The FastAPI backend will run on http://127.0.0.1:8000
The Vite frontend runs on http://localhost:5173/cuneiform-detector/


## License:
The model was trained on electronic Babylonian Library data and is therefore under the license CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike 4.0 International). 

This project is open-source.

List of tablets used for training the model:
1848,0720.115
1848,0720.116
1848,0720.117
1848,0720.119
1848,1104.280
1848,1104.282
1848,1104.283
1867,0402.1
1879,0708.100
1879,0708.114
1879,0708.116
1879,0708.121
1879,0708.123
1879,0708.124
1879,0708.127
1879,0708.150
1879,0708.151
1879,0708.153
1879,0708.20
1879,0708.256
1879,0708.257
1879,0708.271
1879,0708.312
1879,0708.313
1879,0708.328
1879,0708.340
1879,0708.347
1879,0708.348
1879,0708.63
1879,0708.73
1879,0708.77
1879,0708.95
1880,0719.100
1880,0719.103
1880,0719.108
1880,0719.113
1880,0719.114
1880,0719.137
1880,0719.153
1880,0719.154
1880,0719.160
1880,0719.174
1880,0719.176
1880,0719.19
1880,0719.191
1880,0719.197
1880,0719.27
1880,0719.275
1880,0719.336
1880,0719.338
1880,0719.34
1880,0719.35
1880,0719.40
1880,0719.45
1880,0719.46
1880,0719.55
1880,0719.58
1880,0719.59
1880,0719.61
1880,0719.62
1880,0719.63
1880,0719.65
1880,0719.66
1880,0719.69
1880,0719.72
1880,0719.74
1880,0719.77
1880,0719.78
1880,0719.79
1880,0719.88
1880,0719.91
1880,0719.98
BM.128893
BM.128894
BM.128904
BM.128907
BM.128917
BM.128918
BM.128955
BM.128957
BM.128968
BM.128969
BM.128971
BM.128972
BM.128973
BM.128985
BM.128986
BM.128993.1
 

Tablets : ebL editions, accessed on June 17th, 2025.
