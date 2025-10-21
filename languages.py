# Taalbestanden voor MakkelijkPdf
# Language files for MakkelijkPdf

LANGUAGES = {
    "nl": {
        "app_title": "MakkelijkPdf - PDF naar Afbeelding Converter",
        "select_pdf": "Selecteer PDF",
        "select_output": "Selecteer Output Map",
        "convert": "Converteer",
        "new_conversion": "Nieuwe Conversie",
        "preview": "Preview",
        "statistics": "Statistieken",
        "settings": "Instellingen",
        "help": "Help",
        "about": "Over",
        "theme": "Thema",
        "language": "Taal",
        "format": "Formaat",
        "dpi": "DPI",
        "quality": "Kwaliteit",
        "converting": "Converteren...",
        "success": "Conversie voltooid!",
        "error": "Fout",
        "warning": "Waarschuwing",
        "info": "Info",
        "pages": "Pagina's",
        "size": "Grootte",
        "resolution": "Resolutie",
        "conversion_time": "Conversie tijd",
        "files_created": "Bestanden aangemaakt",
        "total_size": "Totale grootte",
        "file_menu": "Bestand",
        "settings_menu": "Instellingen",
        "help_menu": "Help",
        "open_pdf": "Open PDF",
        "open_output": "Open Output Map",
        "exit": "Afsluiten",
        "general_settings": "Algemene Instellingen",
        "conversion_settings": "Conversie Instellingen",
        "ui_settings": "UI Instellingen",
        "advanced_settings": "Geavanceerde Instellingen",
        "save_settings": "Instellingen Opslaan",
        "load_settings": "Instellingen Laden",
        "export_settings": "Instellingen Exporteren",
        "import_settings": "Instellingen Importeren",
        "reset_settings": "Instellingen Resetten",
        "documentation": "Documentatie",
        "check_updates": "Controleer Updates",
        "version": "Versie",
        "build": "Build",
        "date": "Datum",
        "codename": "Codenaam"
    },
    "en": {
        "app_title": "MakkelijkPdf - PDF to Image Converter",
        "select_pdf": "Select PDF",
        "select_output": "Select Output Folder",
        "convert": "Convert",
        "new_conversion": "New Conversion",
        "preview": "Preview",
        "statistics": "Statistics",
        "settings": "Settings",
        "help": "Help",
        "about": "About",
        "theme": "Theme",
        "language": "Language",
        "format": "Format",
        "dpi": "DPI",
        "quality": "Quality",
        "converting": "Converting...",
        "success": "Conversion completed!",
        "error": "Error",
        "warning": "Warning",
        "info": "Info",
        "pages": "Pages",
        "size": "Size",
        "resolution": "Resolution",
        "conversion_time": "Conversion time",
        "files_created": "Files created",
        "total_size": "Total size",
        "file_menu": "File",
        "settings_menu": "Settings",
        "help_menu": "Help",
        "open_pdf": "Open PDF",
        "open_output": "Open Output Folder",
        "exit": "Exit",
        "general_settings": "General Settings",
        "conversion_settings": "Conversion Settings",
        "ui_settings": "UI Settings",
        "advanced_settings": "Advanced Settings",
        "save_settings": "Save Settings",
        "load_settings": "Load Settings",
        "export_settings": "Export Settings",
        "import_settings": "Import Settings",
        "reset_settings": "Reset Settings",
        "documentation": "Documentation",
        "check_updates": "Check Updates",
        "version": "Version",
        "build": "Build",
        "date": "Date",
        "codename": "Codename"
    }
}

def get_text(key, language="nl"):
    """Haal tekst op voor de huidige taal"""
    return LANGUAGES.get(language, LANGUAGES["nl"]).get(key, key)

def get_available_languages():
    """Krijg lijst van beschikbare talen"""
    return list(LANGUAGES.keys())

def get_language_name(lang_code):
    """Krijg naam van taal"""
    names = {
        "nl": "Nederlands",
        "en": "English"
    }
    return names.get(lang_code, lang_code)
