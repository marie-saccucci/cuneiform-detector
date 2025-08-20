@echo off
cd backend
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
python -m pip install -r requirements.txt

echo.
echo Virtual environment setup complete!
echo To activate it later, run: venv\Scripts\activate
pause