@echo off
title Four Seasons House - MIDI generator
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found in PATH. Install Python or add it to PATH, then try again.
    pause
    exit /b 1
)

echo Installing/updating project (quiet)...
python -m pip install -e . -q

echo Running generator...
python generate_midis.py
if errorlevel 1 (
    echo.
    echo If import failed, run once: pip install -e .
    pause
    exit /b 1
)

echo.
echo Done. Files are in the output folder.
explorer output
pause
