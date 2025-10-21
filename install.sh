#!/bin/bash

echo "MakkelijkPdf - Installatie Script"
echo "================================="
echo

# Controleer Python versie
echo "Controleer Python installatie..."
if ! command -v python3 &> /dev/null; then
    echo "FOUT: Python3 is niet geïnstalleerd"
    echo "Installeer Python3 van https://python.org"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python versie: $python_version"

# Controleer pip
if ! command -v pip3 &> /dev/null; then
    echo "FOUT: pip3 is niet geïnstalleerd"
    exit 1
fi

# Installeer dependencies
echo "Installeer Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "FOUT: Kon dependencies niet installeren"
    exit 1
fi

# Controleer poppler installatie
echo "Controleer poppler installatie..."
if ! command -v pdftoppm &> /dev/null; then
    echo "WAARSCHUWING: Poppler is niet geïnstalleerd"
    echo "Installeer poppler voor jouw systeem:"
    
    # Detecteer besturingssysteem
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS: brew install poppler"
        echo ""
        echo "Als je Homebrew niet hebt geïnstalleerd:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "  brew install poppler"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  Ubuntu/Debian: sudo apt-get install poppler-utils"
        echo "  CentOS/RHEL: sudo yum install poppler-utils"
    else
        echo "  Windows: Download van https://github.com/oschwartz10612/poppler-windows/releases/"
    fi
    echo ""
    echo "Na installatie van poppler, herstart je terminal en probeer opnieuw."
else
    echo "Poppler gevonden - alles OK!"
fi

echo ""
echo "Installatie voltooid!"
echo "Start de applicatie met: python3 main.py"
echo "Of gebruik het CLI script: python3 cli.py --help"
echo ""
echo "Voor meer informatie, zie README.md"
