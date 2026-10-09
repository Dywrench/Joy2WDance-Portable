
@echo off
setlocal EnableExtensions
title Joy2WDance - Setup

set "BASE=%~dp0"
set "ROOT=%BASE%joydance"
set "J2W=%BASE%Joy2Win"
set "VENV=%ROOT%\.venv"
set "PYTHON=%VENV%\Scripts\python.exe"

echo.
echo ==========================================
echo       Joy2WDance Portable Setup
echo ==========================================
echo.

if not exist "%ROOT%\requirements.txt" (
    echo [ERROR] Missing joydance\requirements.txt
    pause
    exit /b 1
)

if not exist "%J2W%\requirements.txt" (
    echo [ERROR] Missing Joy2Win\requirements.txt
    pause
    exit /b 1
)

if not exist "%ROOT%\dance.py" (
    echo [ERROR] Missing joydance\dance.py
    pause
    exit /b 1
)

echo [1/4] Checking Python 3.10...

py -3.10 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python 3.10 was not found.
    echo.
    echo Install Python 3.10 for Windows from:
    echo https://www.python.org/downloads/release/python-31011/
    echo.
    echo During installation, enable "Add Python to PATH".
    echo Then run this setup again.
    pause
    exit /b 1
)

if not exist "%PYTHON%" (
    echo.
    echo [2/4] Creating virtual environment...
    py -3.10 -m venv "%VENV%"
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Existing virtual environment found. Keeping it.
)

echo.
echo [3/4] Installing JoyDance dependencies...
"%PYTHON%" -m pip install -r "%ROOT%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] JoyDance dependencies could not be installed.
    pause
    exit /b 1
)

echo.
echo [4/4] Installing Joy2Win dependencies...
"%PYTHON%" -m pip install -r "%J2W%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Joy2Win dependencies could not be installed.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo       Setup completed successfully!
echo ==========================================
echo.
echo Next, run Launcher_Portable.bat.
echo Make sure vJoy is installed and configured.
echo.
pause
endlocal