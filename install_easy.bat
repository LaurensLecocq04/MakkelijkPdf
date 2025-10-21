@echo off
echo ========================================
echo    MakkelijkPdf - Super Eenvoudige Installatie
echo ========================================
echo.

REM Controleer Python
echo [1/5] Controleer Python installatie...
python --version >nul 2>&1
if errorlevel 1 (
    echo FOUT: Python is niet geïnstalleerd!
    echo.
    echo Download Python van: https://python.org/downloads/
    echo Zorg dat je "Add Python to PATH" aanvinkt tijdens installatie!
    echo.
    pause
    exit /b 1
)
echo ✓ Python gevonden!

REM Controleer pip
echo [2/5] Controleer pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo FOUT: pip is niet geïnstalleerd!
    echo Installeer pip handmatig of herinstalleer Python.
    pause
    exit /b 1
)
echo ✓ pip gevonden!

REM Upgrade pip eerst
echo [3/5] Upgrade pip naar nieuwste versie...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo WAARSCHUWING: Kon pip niet upgraden, maar we gaan door...
)

REM Installeer alle dependencies in één keer
echo [4/5] Installeer alle dependencies...
echo Dit kan even duren...
python -m pip install pdf2image==1.17.0 Pillow==10.2.0 customtkinter==5.2.2 setuptools==69.5.1 --quiet
if errorlevel 1 (
    echo.
    echo FOUT: Kon dependencies niet installeren!
    echo.
    echo Probeer handmatig:
    echo   python -m pip install pdf2image Pillow customtkinter setuptools
    echo.
    pause
    exit /b 1
)
echo ✓ Alle dependencies geïnstalleerd!

REM Controleer poppler
echo [5/5] Controleer Poppler...
pdftoppm -h >nul 2>&1
if errorlevel 1 (
    echo WAARSCHUWING: Poppler niet gevonden!
    echo.
    echo Automatische Poppler installatie...
    
    REM Download poppler
    echo Downloaden van Poppler...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip' -OutFile 'poppler.zip' -UseBasicParsing } catch { Write-Host 'Download mislukt' }"
    
    if not exist poppler.zip (
        echo FOUT: Kon Poppler niet downloaden!
        echo Download handmatig van: https://github.com/oschwartz10612/poppler-windows/releases/
        pause
        exit /b 1
    )
    
    REM Uitpakken
    echo Uitpakken van Poppler...
    powershell -Command "try { Expand-Archive -Path 'poppler.zip' -DestinationPath 'C:\poppler' -Force } catch { Write-Host 'Uitpakken mislukt' }"
    
    if not exist "C:\poppler\poppler-23.08.0\Library\bin\pdftoppm.exe" (
        echo FOUT: Kon Poppler niet uitpakken!
        pause
        exit /b 1
    )
    
    REM PATH instellen
    echo PATH instellen...
    powershell -Command "[Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\poppler\poppler-23.08.0\Library\bin', 'User')"
    
    REM Cleanup
    del poppler.zip
    
    echo ✓ Poppler succesvol geïnstalleerd!
) else (
    echo ✓ Poppler gevonden!
)

echo.
echo ========================================
echo    INSTALLATIE VOLTOOID! 🎉
echo ========================================
echo.
echo Start MakkelijkPdf met:
echo   python main.py
echo.
echo Of gebruik: start.bat
echo.
echo Herstart PowerShell/CMD voor volledige Poppler functionaliteit.
echo.
pause
