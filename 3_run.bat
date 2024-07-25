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

REM Check if app.py exists
if not exist "app.py" (
    echo The file app.py does not exist in the current directory.
    pause
    exit /b 1
)

REM Run the app.py script
echo Running app.py...
python app.py

REM Confirm successful execution
if %errorlevel% neq 0 (
    echo There was an error running the app.py script.
    pause
    exit /b 1
)

endlocal
