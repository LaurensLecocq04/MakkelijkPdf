"""
MakkelijkPdf - Versie Informatie
"""

# Versie informatie
VERSION = "1.1.0"
BUILD_DATE = "2025-10-21"
BUILD_NUMBER = "002"

# Versie details
VERSION_INFO = {
    "major": 1,
    "minor": 1,
    "patch": 0,
    "build": BUILD_NUMBER,
    "date": BUILD_DATE,
    "codename": "Enhanced"
}

# Changelog
CHANGELOG = {
    "1.1.0": {
        "date": "2025-10-21",
        "changes": [
            "Enhanced UI met moderne layout",
            "Instellingen systeem geïmplementeerd",
            "Preview functionaliteit toegevoegd",
            "Real-time statistieken tracking",
            "Menu systeem met shortcuts",
            "Thema switcher (licht/donker)",
            "Verbeterde conversie opties",
            "Auto-open output folder optie",
            "Uitgebreide instellingen venster",
            "Export/Import instellingen"
        ],
        "features": [
            "Instellingen management systeem",
            "Preview van PDF pagina's",
            "Conversie statistieken (tijd, grootte, bestanden)",
            "Menu systeem (Bestand, Instellingen, Help)",
            "Thema switching functionaliteit",
            "Uitgebreide conversie opties",
            "Instellingen export/import",
            "Verbeterde UI layout (2 kolommen)",
            "Auto-open output folder",
            "Meer output formaten (BMP toegevoegd)"
        ],
        "fixes": [
            "Verbeterde error handling",
            "Betere progress tracking",
            "Geoptimaliseerde geheugengebruik"
        ],
        "breaking_changes": []
    },
    "1.0.0": {
        "date": "2025-10-21",
        "changes": [
            "Initial release",
            "GUI interface met CustomTkinter",
            "Command line interface",
            "PDF naar PNG/JPG/TIFF conversie",
            "Batch conversie functionaliteit",
            "Automatische poppler installatie",
            "Cross-platform ondersteuning"
        ],
        "features": [
            "Modern GUI interface",
            "CLI voor geavanceerde gebruikers",
            "Aanpasbare DPI instellingen",
            "Progress tracking",
            "Error handling"
        ],
        "fixes": [],
        "breaking_changes": []
    }
}

def get_version_string():
    """Retourneer versie string"""
    return f"{VERSION} (Build {BUILD_NUMBER})"

def get_version_info():
    """Retourneer volledige versie informatie"""
    return VERSION_INFO

def get_changelog():
    """Retourneer changelog"""
    return CHANGELOG

def check_for_updates():
    """Controleer op updates (placeholder voor toekomstige implementatie)"""
    return {
        "current_version": VERSION,
        "latest_version": VERSION,  # In toekomst: check GitHub API
        "update_available": False,
        "update_url": "https://github.com/LaurensLecocq04/MakkelijkPdf/releases"
    }
