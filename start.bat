@echo off
echo MakkelijkPdf - PDF naar afbeelding converter
echo ============================================
echo.

REM Controleer Python
python --version >nul 2>&1
if errorlevel 1 (
    echo FOUT: Python niet gevonden!
    echo Installeer Python van: https://python.org
    pause
    exit /b 1
)

REM Probeer gewoon te starten
echo Start MakkelijkPdf...
python main.py

REM Als het niet werkt, toon foutmelding
if errorlevel 1 (
    echo.
    echo FOUT: Applicatie kon niet starten!
    echo.
    echo Mogelijke oplossingen:
    echo 1. Run eerst: install.bat
    echo 2. Installeer dependencies: pip install pdf2image Pillow customtkinter setuptools
    echo 3. Installeer Poppler handmatig
    echo.
    pause
)
