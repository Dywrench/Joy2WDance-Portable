
@echo off
setlocal EnableExtensions
title Joy2WDance Portable

set "BASE=%~dp0"
set "ROOT=%BASE%joydance"
set "J2W=%BASE%Joy2Win"
set "PYTHON=%ROOT%\.venv\Scripts\python.exe"

echo.
echo ==========================================
echo       Joy2WDance Portable Launcher
echo ==========================================
echo.

if not exist "%PYTHON%" (
    echo [ERROR] JoyDance Python environment not found.
    echo Please configure the Python environment first.
    pause
    exit /b 1
)

if not exist "%ROOT%\dance.py" (
    echo [ERROR] Missing joydance\dance.py
    pause
    exit /b 1
)

if not exist "%ROOT%\joy2win_bridge.py" (
    echo [ERROR] Missing joydance\joy2win_bridge.py
    pause
    exit /b 1
)

if not exist "%J2W%\main.py" (
    echo [ERROR] Missing Joy2Win\main.py
    pause
    exit /b 1
)

echo [1/3] Starting Joy2Win Bridge...
echo Select option 0 in the Bridge window.
start "Joy2Win Bridge" /D "%ROOT%" cmd /k "set J2W=%J2W%&& "%PYTHON%" "%ROOT%\joy2win_bridge.py""

pause

echo.
echo [2/3] Starting JoyDance...
start "JoyDance" /D "%ROOT%" "%PYTHON%" "%ROOT%\dance.py"

timeout /t 4 /nobreak >nul

echo.
echo [3/3] Opening Melody...
start "" "http://localhost:32623"

echo.
echo Keep the Bridge and JoyDance windows open while playing.
pause
endlocal