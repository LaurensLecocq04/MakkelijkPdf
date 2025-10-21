#!/bin/bash

echo "MakkelijkPdf - PDF naar afbeelding converter"
echo "============================================"
echo

# Controleer of Python geïnstalleerd is
if ! command -v python3 &> /dev/null; then
    echo "FOUT: Python3 is niet geïnstalleerd"
    echo "Installeer Python3 van https://python.org"
    echo "Of gebruik Homebrew: brew install python"
    exit 1
fi

# Controleer Python versie
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python versie: $python_version"

# Controleer of requirements geïnstalleerd zijn
echo "Controleer dependencies..."
if ! python3 -c "import pdf2image" &> /dev/null; then
    echo "Installeer dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "FOUT: Kon dependencies niet installeren"
        echo "Probeer: pip3 install --user -r requirements.txt"
        exit 1
    fi
fi

# Controleer poppler installatie
echo "Controleer poppler installatie..."
if ! command -v pdftoppm &> /dev/null; then
    echo "WAARSCHUWING: Poppler niet gevonden!"
    echo ""
    echo "Installeer poppler met Homebrew:"
    echo "  brew install poppler"
    echo ""
    echo "Als je Homebrew niet hebt:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  brew install poppler"
    echo ""
    echo "Na installatie, herstart Terminal en probeer opnieuw."
    exit 1
else
    echo "Poppler gevonden - alles OK!"
fi

# Start de GUI applicatie
echo "Start MakkelijkPdf..."
python3 main.py
