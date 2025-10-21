@echo off
title MakkelijkPdf Installatie
color 0A

echo.
echo ============================================================
echo                MAKKELIJKPDF INSTALLATIE
echo ============================================================
echo                PDF naar afbeelding converter
echo                Eenvoudige installatie voor Windows
echo ============================================================
echo.

REM Controleer Python
echo [1/4] Controleer Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo FOUT: Python niet gevonden!
    echo.
    echo Download Python van: https://python.org
    echo Installeer Python en probeer opnieuw.
    echo.
    pause
    exit /b 1
)
echo    Python gevonden!

REM Start Python wizard
echo.
echo [2/4] Start installatie wizard...
python setup_wizard.py

if errorlevel 1 (
    echo.
    echo FOUT: De installatie wizard kon niet worden voltooid.
    echo Controleer de foutmeldingen hierboven.
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Installatie voltooid!
echo.
echo [4/4] Maak desktop shortcut...

REM Maak eenvoudige desktop shortcut
set "currentDir=%~dp0"
set "desktop=%USERPROFILE%\Desktop"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\MakkelijkPdf.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '""%currentDir%main.py""'; $Shortcut.WorkingDirectory = '%currentDir%'; $Shortcut.Description = 'MakkelijkPdf - PDF Converter'; $Shortcut.Save()}" >nul 2>&1

echo    Desktop shortcut gemaakt!

echo.
echo ============================================================
echo                    INSTALLATIE VOLTOOID!
echo ============================================================
echo    MakkelijkPdf is geinstalleerd en klaar voor gebruik
echo    Desktop shortcut is gemaakt
echo    Je kunt nu MakkelijkPdf gebruiken!
echo ============================================================
echo.

REM Vraag of gebruiker wil starten
set /p start="Wil je MakkelijkPdf nu starten? (j/n): "
if /i "%start%"=="j" (
    echo.
    echo Start MakkelijkPdf...
    start "" "python" "main.py"
) else if /i "%start%"=="ja" (
    echo.
    echo Start MakkelijkPdf...
    start "" "python" "main.py"
)

echo.
echo Bedankt voor het gebruiken van MakkelijkPdf!
pause
