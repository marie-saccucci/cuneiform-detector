#!/bin/bash
cd backend
echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing requirements..."
python -m pip install -r requirements.txt

echo
echo "Virtual environment setup complete!"
echo "To activate it later, run: source venv/bin/activate"
