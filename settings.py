"""
MakkelijkPdf - Instellingen Management
"""

import json
import os
from pathlib import Path

class SettingsManager:
    def __init__(self):
        self.settings_file = Path.home() / ".makkelijkpdf" / "settings.json"
        self.settings_file.parent.mkdir(exist_ok=True)
        self.default_settings = {
            "general": {
                "theme": "system",  # system, light, dark
                "language": "nl",
                "auto_update_check": True,
                "remember_last_folder": True,
                "last_input_folder": "",
                "last_output_folder": ""
            },
            "conversion": {
                "default_dpi": 300,
                "default_format": "PNG",
                "quality": 95,  # For JPEG
                "compression": "none",  # none, fast, best
                "preserve_metadata": True,
                "auto_open_output": False
            },
            "ui": {
                "window_width": 700,
                "window_height": 600,
                "show_preview": True,
                "show_stats": True,
                "compact_mode": False
            },
            "advanced": {
                "thread_count": 0,  # 0 = auto
                "memory_limit": 512,  # MB
                "temp_folder": "",
                "log_level": "INFO"
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Laad instellingen uit bestand"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                # Merge met default settings
                return self._merge_settings(self.default_settings, loaded_settings)
            except Exception as e:
                print(f"Fout bij laden instellingen: {e}")
                return self.default_settings.copy()
        return self.default_settings.copy()
    
    def save_settings(self):
        """Bewaar instellingen naar bestand"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fout bij opslaan instellingen: {e}")
            return False
    
    def get(self, section, key, default=None):
        """Haal instelling op"""
        return self.settings.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """Stel instelling in"""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save_settings()
    
    def reset_to_defaults(self):
        """Reset alle instellingen naar standaard"""
        self.settings = self.default_settings.copy()
        self.save_settings()
    
    def _merge_settings(self, default, loaded):
        """Merge loaded settings met defaults"""
        result = default.copy()
        for section, values in loaded.items():
            if section in result:
                result[section].update(values)
            else:
                result[section] = values
        return result
    
    def get_all_settings(self):
        """Haal alle instellingen op"""
        return self.settings.copy()
    
    def export_settings(self, filepath):
        """Exporteer instellingen naar bestand"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fout bij exporteren instellingen: {e}")
            return False
    
    def import_settings(self, filepath):
        """Importeer instellingen uit bestand"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            self.settings = self._merge_settings(self.default_settings, imported_settings)
            self.save_settings()
            return True
        except Exception as e:
            print(f"Fout bij importeren instellingen: {e}")
            return False
