@echo off
setlocal

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

REM Create a virtual environment (venv) in the current folder
echo Creating the virtual environment...
python -m venv venv

REM Check if the virtual environment was created successfully
if exist "venv\Scripts\activate.bat" (
    echo The virtual environment was created successfully.
    echo To activate the virtual environment, run:
    echo call venv\Scripts\activate.bat
) else (
    echo There was an error creating the virtual environment.
    pause
    exit /b 1
)

pause
endlocal

