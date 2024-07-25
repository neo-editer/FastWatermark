@echo off
setlocal

REM Check if the virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo The virtual environment does not exist. Please create the virtual environment first.
    pause
    exit /b 1
)

REM Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo The requirements.txt file does not exist in the current directory.
    pause
    exit /b 1
)

REM Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Confirm successful installation
if %errorlevel% neq 0 (
    echo There was an error installing the dependencies.
    pause
    exit /b 1
)

echo Dependencies were installed successfully.
pause
endlocal
