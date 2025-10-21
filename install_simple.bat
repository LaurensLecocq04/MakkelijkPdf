@echo off
echo MakkelijkPdf - Eenvoudige Installatie
echo ====================================
echo.

echo Installeer Python packages...
pip install pdf2image Pillow customtkinter setuptools

echo.
echo Installeer Poppler...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip' -OutFile 'poppler.zip'"
powershell -Command "Expand-Archive -Path 'poppler.zip' -DestinationPath 'C:\poppler' -Force"
powershell -Command "[Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\poppler\poppler-23.08.0\Library\bin', 'User')"
del poppler.zip

echo.
echo KLAAR! Start met: python main.py
pause
