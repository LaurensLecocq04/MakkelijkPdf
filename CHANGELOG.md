# Changelog

Alle belangrijke wijzigingen aan dit project worden gedocumenteerd in dit bestand.

Het formaat is gebaseerd op [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
en dit project volgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Gepland voor v1.1.0
- Drag & Drop ondersteuning voor PDF bestanden
- Preview functionaliteit voor PDF pagina's
- Instellingen opslaan en laden
- Conversie statistieken (tijd, bestandsgrootte)
- Verbeterde error handling

## [1.0.0] - 2025-10-21

### Toegevoegd
- Initial release van MakkelijkPdf
- Modern GUI interface met CustomTkinter
- Command line interface voor batch conversie
- PDF naar PNG/JPG/TIFF conversie functionaliteit
- Aanpasbare DPI instellingen (150-600 DPI)
- Progress tracking tijdens conversie
- Automatische poppler installatie voor Windows
- Cross-platform ondersteuning (Windows, macOS, Linux)
- Batch conversie van meerdere PDF bestanden
- Recursieve verwerking van subdirectories
- Uitgebreide error handling en gebruikersfeedback
- Versie management systeem
- Uitgebreide documentatie en installatie scripts

### Technische Details
- Python 3.7+ ondersteuning
- pdf2image voor PDF conversie
- Pillow voor afbeelding verwerking
- CustomTkinter voor moderne GUI
- Poppler als PDF rendering engine
- Threading voor niet-blokkerende conversie

### Bestanden
- `main.py` - GUI applicatie
- `cli.py` - Command line interface
- `version.py` - Versie management
- `requirements.txt` - Python dependencies
- `start.bat` - Windows start script
- `install.sh` - Linux/macOS installatie script
- `README.md` - Uitgebreide documentatie

## [0.1.0] - 2025-10-21

### Toegevoegd
- Project initiatie
- Basis project structuur
- Eerste concepten en planning

---

## Versie Nummering

Dit project gebruikt [Semantic Versioning](https://semver.org/):

- **MAJOR** versie voor incompatibele API wijzigingen
- **MINOR** versie voor nieuwe functionaliteit (achterwaarts compatibel)
- **PATCH** versie voor bug fixes (achterwaarts compatibel)

## Release Types

- **Stable** - Productie klaar, volledig getest
- **Beta** - Feature compleet, maar mogelijk bugs
- **Alpha** - Vroege ontwikkeling, experimenteel
- **RC** - Release Candidate, bijna klaar voor release
