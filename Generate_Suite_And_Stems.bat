@echo off
title Four Seasons House - Suite + orchestral stems
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found in PATH. Install Python or add it to PATH, then try again.
    pause
    exit /b 1
)

echo Installing/updating project (quiet)...
python -m pip install -e . -q

echo Running generator ^(full suites + stem MIDI files^)...
python generate_midis.py --export-orchestral-stems
if errorlevel 1 (
    echo.
    echo If import failed, run once: pip install -e .
    pause
    exit /b 1
)

echo.
echo Done. Main MIDIs: output\
echo Stem MIDIs:      output\stems\^<suite_name^>\
explorer output
pause
