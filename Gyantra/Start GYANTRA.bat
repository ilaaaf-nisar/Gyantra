@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo GYANTRA's Python environment was not found.
    echo Run this from the project folder after setting up .venv.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "import webview" >nul 2>nul
if errorlevel 1 (
    echo Installing GYANTRA's desktop window dependency...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Could not install the desktop dependency.
        pause
        exit /b 1
    )
)

".venv\Scripts\pythonw.exe" app.py
