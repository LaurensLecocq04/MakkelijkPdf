@echo off
echo MakkelijkPdf - PDF naar afbeelding converter
echo ============================================
echo.

REM Controleer of Python geïnstalleerd is
python --version >nul 2>&1
if errorlevel 1 (
    echo FOUT: Python is niet geïnstalleerd of niet gevonden in PATH
    echo Installeer Python van https://python.org
    pause
    exit /b 1
)

REM Controleer of requirements geïnstalleerd zijn
echo Controleer dependencies...
pip show pdf2image >nul 2>&1
if errorlevel 1 (
    echo Installeer dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo FOUT: Kon dependencies niet installeren
        pause
        exit /b 1
    )
)

REM Controleer poppler installatie
echo Controleer poppler installatie...
pdftoppm -h >nul 2>&1
if errorlevel 1 (
    echo WAARSCHUWING: Poppler niet gevonden!
    echo.
    echo Automatische poppler installatie...
    echo Downloaden van poppler...
    
    REM Download poppler
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip' -OutFile 'poppler.zip'"
    if errorlevel 1 (
        echo FOUT: Kon poppler niet downloaden
        echo Installeer handmatig van: https://github.com/oschwartz10612/poppler-windows/releases/
        pause
        exit /b 1
    )
    
    REM Uitpakken
    powershell -Command "Expand-Archive -Path 'poppler.zip' -DestinationPath 'C:\poppler' -Force"
    if errorlevel 1 (
        echo FOUT: Kon poppler niet uitpakken
        pause
        exit /b 1
    )
    
    REM PATH instellen
    powershell -Command "[Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\poppler\poppler-23.08.0\Library\bin', 'User')"
    
    REM Cleanup
    del poppler.zip
    
    echo Poppler succesvol geïnstalleerd!
    echo Herstart PowerShell voor volledige functionaliteit.
    echo.
) else (
    echo Poppler gevonden - alles OK!
)

REM Start de GUI applicatie
echo Start MakkelijkPdf...
python main.py

pause
