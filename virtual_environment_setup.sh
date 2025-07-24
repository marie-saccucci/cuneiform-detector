#!/bin/bash
cd backend
echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing requirements..."
# Install CPU version of torch separately
python -m pip install torch==2.1.0+cpu torchvision==0.16.0+cpu torchaudio==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install -r requirements.txt

echo
echo "Virtual environment setup complete!"
echo "To activate it later, run: source venv/bin/activate"
