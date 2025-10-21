@echo off
title MakkelijkPdf - Eenvoudige Installatie
color 0A

echo.
echo  ███╗   ███╗ █████╗ ██╗  ██╗██╗  ██╗     ██████╗ ███████╗██╗
echo  ████╗ ████║██╔══██╗██║ ██╔╝██║ ██╔╝    ██╔═══██╗██╔════╝██║
echo  ██╔████╔██║███████║█████╔╝ █████╔╝     ██║   ██║█████╗  ██║
echo  ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔═██╗     ██║   ██║██╔══╝  ██║
echo  ██║ ╚═╝ ██║██║  ██║██║  ██╗██║  ██╗    ╚██████╔╝██║     ██║
echo  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝     ╚═════╝ ╚═╝     ╚═╝
echo.
echo           Eenvoudige Windows Installatie
echo ================================================
echo.

REM Controleer Python
echo [1/4] Controleer Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python niet gevonden!
    echo.
    echo 📥 Download Python van: https://python.org/downloads/
    echo    ☑️ Zorg dat je "Add Python to PATH" aanvinkt!
    echo.
    start https://python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python OK!

REM Installeer dependencies
echo [2/4] Installeer Python packages...
echo    📦 pdf2image, Pillow, customtkinter, setuptools...
python -m pip install --upgrade pip --quiet
python -m pip install pdf2image Pillow customtkinter setuptools --quiet
if errorlevel 1 (
    echo ❌ Installatie mislukt!
    echo.
    echo 🔧 Probeer handmatig:
    echo    python -m pip install pdf2image Pillow customtkinter setuptools
    echo.
    pause
    exit /b 1
)
echo ✅ Python packages OK!

REM Controleer Poppler
echo [3/4] Controleer Poppler...
pdftoppm -h >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Poppler niet gevonden - installeren...
    
    echo    📥 Downloaden...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip' -OutFile 'poppler.zip' -UseBasicParsing } catch { exit 1 }"
    
    if not exist poppler.zip (
        echo ❌ Download mislukt!
        echo 📥 Download handmatig: https://github.com/oschwartz10612/poppler-windows/releases/
        pause
        exit /b 1
    )
    
    echo    📦 Uitpakken...
    powershell -Command "try { Expand-Archive -Path 'poppler.zip' -DestinationPath 'C:\poppler' -Force } catch { exit 1 }"
    
    echo    ⚙️  PATH instellen...
    powershell -Command "[Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\poppler\poppler-23.08.0\Library\bin', 'User')"
    
    del poppler.zip
    echo ✅ Poppler geïnstalleerd!
) else (
    echo ✅ Poppler OK!
)

REM Test installatie
echo [4/4] Test installatie...
python -c "import pdf2image, PIL, customtkinter; print('✅ Alles werkt!')" 2>nul
if errorlevel 1 (
    echo ❌ Test mislukt!
    echo 🔧 Er is iets mis met de installatie.
    pause
    exit /b 1
)

echo.
echo ================================================
echo           🎉 INSTALLATIE VOLTOOID! 🎉
echo ================================================
echo.
echo 🚀 Start MakkelijkPdf:
echo    python main.py
echo.
echo 📁 Of gebruik: start.bat
echo.
echo 💡 Tip: Herstart PowerShell voor volledige functionaliteit
echo.
pause
