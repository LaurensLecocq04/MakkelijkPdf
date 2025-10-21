#!/usr/bin/env python3
"""
MakkelijkPdf - Eenvoudige PDF naar afbeelding converter
"""

import os
import sys
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
from version import get_version_string, get_version_info, check_for_updates
from settings import SettingsManager
from settings_window import SettingsWindow
from languages import get_text, get_available_languages, get_language_name

# Voeg poppler pad toe aan PATH (cross-platform)
import platform
if platform.system() == "Windows":
    poppler_path = r"C:\poppler\poppler-23.08.0\Library\bin"
elif platform.system() == "Darwin":  # macOS
    poppler_path = "/opt/homebrew/bin"  # Homebrew ARM
    if not os.path.exists(poppler_path):
        poppler_path = "/usr/local/bin"  # Homebrew Intel
elif platform.system() == "Linux":
    poppler_path = "/usr/bin"  # System poppler
else:
    poppler_path = ""

if poppler_path and poppler_path not in os.environ["PATH"]:
    os.environ["PATH"] = poppler_path + os.pathsep + os.environ["PATH"]

class MakkelijkPdfApp:
    def __init__(self):
        # Laad instellingen
        self.settings = SettingsManager()
        
        # Stel taal in
        self.current_language = self.settings.get("general", "language", "nl")
        
        # Configureer CustomTkinter
        theme = self.settings.get("general", "theme", "system")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # Maak hoofdvenster
        self.root = ctk.CTk()
        version_string = get_version_string()
        self.root.title(f"MakkelijkPdf - PDF Converter v{version_string}")
        
        # Venster grootte uit instellingen
        width = self.settings.get("ui", "window_width", 1000)
        height = self.settings.get("ui", "window_height", 800)
        self.root.geometry(f"{width}x{height}")
        
        # Variabelen
        self.input_file = None
        # Standaard output map naar Downloads
        default_output = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_folder = default_output
        self.conversion_stats = {
            "start_time": None,
            "end_time": None,
            "pages_converted": 0,
            "total_size": 0,
            "files_created": []
        }
        
        # Instellingen venster
        self.settings_window = None
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_menu(self):
        """Zet menu systeem op"""
        # Maak menu bar
        menubar = ctk.CTkFrame(self.root, height=30)
        menubar.pack(fill="x", padx=10, pady=(10, 0))
        
        # Bestand menu
        file_button = ctk.CTkButton(
            menubar,
            text="Bestand",
            command=self.show_file_menu,
            width=80,
            height=25
        )
        file_button.pack(side="left", padx=5, pady=2)
        self.file_button = file_button
        
        # Instellingen menu
        settings_button = ctk.CTkButton(
            menubar,
            text="Instellingen",
            command=self.show_settings,
            width=80,
            height=25
        )
        settings_button.pack(side="left", padx=5, pady=2)
        self.settings_button = settings_button
        
        # Help menu
        help_button = ctk.CTkButton(
            menubar,
            text="Help",
            command=self.show_help_menu,
            width=80,
            height=25
        )
        help_button.pack(side="left", padx=5, pady=2)
        self.help_button = help_button
        
        # Spacer
        spacer = ctk.CTkLabel(menubar, text="")
        spacer.pack(side="left", fill="x", expand=True)
        
        # Thema switcher
        current_theme = self.settings.get("general", "theme", "system")
        # Bepaal icoon op basis van huidige instelling
        if current_theme == "light":
            theme_icon = "🌙"  # Toon maan voor dark mode
        elif current_theme == "dark":
            theme_icon = "☀️"  # Toon zon voor light mode
        else:  # system
            theme_icon = "🌙"  # Default naar dark mode
        
        self.theme_button = ctk.CTkButton(
            menubar,
            text=theme_icon,
            command=self.toggle_theme,
            width=30,
            height=25
        )
        self.theme_button.pack(side="right", padx=5, pady=2)
        
        # Taal wissel knop
        language_icon = "🇬🇧" if self.current_language == "nl" else "🇳🇱"
        self.language_button = ctk.CTkButton(
            menubar,
            text=language_icon,
            command=self.toggle_language,
            width=30,
            height=25
        )
        self.language_button.pack(side="right", padx=5, pady=2)
        
    def setup_ui(self):
        """Zet de gebruikersinterface op"""
        # Hoofdframe
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel sectie
        title_frame = ctk.CTkFrame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="MakkelijkPdf", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)
        self.title_label = title_label
        
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="Converteer PDF bestanden naar afbeeldingen", 
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 10))
        self.subtitle_label = subtitle_label
        
        # Hoofdcontent frame (2 kolommen)
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Linker kolom - Input en instellingen
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Rechter kolom - Preview en statistieken
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Input bestand sectie
        input_frame = ctk.CTkFrame(left_frame)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        pdf_label = ctk.CTkLabel(input_frame, text="PDF Bestand:", font=ctk.CTkFont(weight="bold"))
        pdf_label.pack(anchor="w", padx=10, pady=(10, 5))
        self.pdf_label = pdf_label
        
        self.input_label = ctk.CTkLabel(input_frame, text="Geen bestand geselecteerd", text_color="gray")
        self.input_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        input_button = ctk.CTkButton(
            input_frame, 
            text="Selecteer PDF", 
            command=self.select_input_file
        )
        input_button.pack(anchor="w", padx=10, pady=(0, 10))
        self.input_button = input_button
        
        # Output folder sectie
        output_frame = ctk.CTkFrame(left_frame)
        output_frame.pack(fill="x", padx=10, pady=10)
        
        output_label_title = ctk.CTkLabel(output_frame, text="Output Map:", font=ctk.CTkFont(weight="bold"))
        output_label_title.pack(anchor="w", padx=10, pady=(10, 5))
        self.output_label_title = output_label_title
        
        # Toon standaard Downloads map
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_label = ctk.CTkLabel(output_frame, text=f"📁 {downloads_path}", text_color="white")
        self.output_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        output_button = ctk.CTkButton(
            output_frame, 
            text="Selecteer Output Map", 
            command=self.select_output_folder
        )
        output_button.pack(anchor="w", padx=10, pady=(0, 10))
        self.output_button = output_button
        
        # Conversie opties
        options_frame = ctk.CTkFrame(left_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        options_label = ctk.CTkLabel(options_frame, text="Conversie Opties:", font=ctk.CTkFont(weight="bold"))
        options_label.pack(anchor="w", padx=10, pady=(10, 5))
        self.options_label = options_label
        
        # DPI instelling
        dpi_frame = ctk.CTkFrame(options_frame)
        dpi_frame.pack(fill="x", padx=10, pady=5)
        
        dpi_label = ctk.CTkLabel(dpi_frame, text="DPI (kwaliteit):")
        dpi_label.pack(side="left", padx=10, pady=10)
        self.dpi_label = dpi_label
        
        default_dpi = self.settings.get("conversion", "default_dpi", 300)
        self.dpi_var = ctk.StringVar(value=str(default_dpi))
        dpi_menu = ctk.CTkOptionMenu(
            dpi_frame,
            variable=self.dpi_var,
            values=["150", "200", "300", "400", "600"],
            width=100
        )
        dpi_menu.pack(side="left", padx=10, pady=10)
        self.dpi_menu = dpi_menu
        
        # Formaat selectie
        format_frame = ctk.CTkFrame(options_frame)
        format_frame.pack(fill="x", padx=10, pady=5)
        
        format_label = ctk.CTkLabel(format_frame, text="Output Formaat:")
        format_label.pack(side="left", padx=10, pady=10)
        self.format_label = format_label
        default_format = self.settings.get("conversion", "default_format", "PNG")
        self.format_var = ctk.StringVar(value=default_format)
        format_menu = ctk.CTkOptionMenu(
            format_frame, 
            variable=self.format_var,
            values=["PNG", "JPG", "JPEG", "TIFF", "BMP"]
        )
        format_menu.pack(side="left", padx=10, pady=10)
        
        # Conversie knop
        self.convert_button = ctk.CTkButton(
            left_frame, 
            text="Start Conversie", 
            command=self.start_conversion,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.convert_button.pack(pady=20)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(left_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(left_frame, text="Klaar voor conversie")
        self.status_label.pack(pady=(0, 10))
        
        # Preview sectie (rechter kolom)
        if self.settings.get("ui", "show_preview", True):
            self.setup_preview(right_frame)
        
        # Statistieken sectie
        if self.settings.get("ui", "show_stats", True):
            self.setup_stats(right_frame)
    
    def setup_preview(self, parent):
        """Zet preview sectie op"""
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(preview_frame, text="Preview", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        # Preview frame met scrollbar
        self.preview_container = ctk.CTkScrollableFrame(preview_frame, width=200, height=300)
        self.preview_container.pack(pady=10)
        
        # Preview label
        self.preview_label = ctk.CTkLabel(
            self.preview_container, 
            text="Selecteer een PDF voor preview",
            wraplength=180
        )
        self.preview_label.pack(pady=20)
        
        # Preview info
        self.preview_info = ctk.CTkLabel(
            self.preview_container,
            text="",
            font=ctk.CTkFont(size=10)
        )
        self.preview_info.pack(pady=5)
    
    def update_preview(self):
        """Update preview met PDF informatie"""
        if not hasattr(self, 'preview_label'):
            return
            
        if self.input_file and os.path.exists(self.input_file):
            try:
                # Probeer PDF informatie te lezen (alleen eerste pagina voor snelheid)
                pages = convert_from_path(
                    self.input_file, 
                    dpi=50, 
                    first_page=1, 
                    last_page=1, 
                    poppler_path=poppler_path
                )
                
                if pages and len(pages) > 0:
                    page = pages[0]
                    
                    # Toon PDF informatie
                    file_size = os.path.getsize(self.input_file)
                    file_size_mb = file_size / (1024 * 1024)
                    
                    # Probeer totaal aantal pagina's te krijgen
                    try:
                        all_pages = convert_from_path(self.input_file, dpi=1, poppler_path=poppler_path)
                        total_pages = len(all_pages) if all_pages else 1
                    except:
                        total_pages = 1
                    
                    info_text = f"""📄 PDF Informatie:

Bestand: {os.path.basename(self.input_file)}
Pagina's: {total_pages} pagina(s)
Grootte: {file_size_mb:.1f} MB
Resolutie: {page.width}x{page.height} px
Modus: {page.mode}

Klik 'Start Conversie' om te beginnen."""
                    
                    self.preview_label.configure(text=info_text)
                    self.preview_info.configure(text="✅ PDF geladen en klaar voor conversie")
                else:
                    self.preview_label.configure(text="❌ Kon PDF niet lezen")
                    self.preview_info.configure(text="Controleer of het een geldig PDF bestand is")
                    
            except Exception as e:
                error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
                self.preview_label.configure(text=f"❌ Fout bij lezen PDF:\n{error_msg}")
                self.preview_info.configure(text="Probeer een ander PDF bestand")
        else:
            self.preview_label.configure(text="Selecteer een PDF voor preview")
            self.preview_info.configure(text="")
    
    def setup_stats(self, parent):
        """Zet statistieken sectie op"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        stats_title = ctk.CTkLabel(stats_frame, text="Statistieken", font=ctk.CTkFont(weight="bold"))
        stats_title.pack(pady=10)
        self.stats_title = stats_title
        
        # Stats labels
        self.stats_labels = {}
        stats_info = [
            ("Pagina's:", "pages"),
            ("Tijd:", "time"),
            ("Bestandsgrootte:", "size"),
            ("Bestanden:", "files")
        ]
        
        for label_text, key in stats_info:
            frame = ctk.CTkFrame(stats_frame)
            frame.pack(fill="x", padx=10, pady=2)
            
            label = ctk.CTkLabel(frame, text=label_text)
            label.pack(side="left", padx=5)
            self.stats_labels[key] = label
            
            value_label = ctk.CTkLabel(frame, text="0")
            value_label.pack(side="right", padx=5)
            self.stats_labels[f"{key}_value"] = value_label
    
    def show_file_menu(self):
        """Toon bestand menu"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("Bestand Menu")
        menu.geometry("200x150")
        menu.transient(self.root)
        menu.grab_set()
        
        # Menu items
        ctk.CTkButton(menu, text="Nieuw", command=lambda: self.new_conversion()).pack(pady=5)
        ctk.CTkButton(menu, text="Open PDF", command=self.select_input_file).pack(pady=5)
        ctk.CTkButton(menu, text="Open Output Map", command=self.open_output_folder).pack(pady=5)
        ctk.CTkButton(menu, text="Sluiten", command=menu.destroy).pack(pady=5)
    
    def show_help_menu(self):
        """Toon help menu"""
        menu = ctk.CTkToplevel(self.root)
        menu.title("Help Menu")
        menu.geometry("200x150")
        menu.transient(self.root)
        menu.grab_set()
        
        # Menu items
        ctk.CTkButton(menu, text="Over", command=self.show_about).pack(pady=5)
        ctk.CTkButton(menu, text="Documentatie", command=self.show_documentation).pack(pady=5)
        ctk.CTkButton(menu, text="Updates", command=self.check_updates).pack(pady=5)
        ctk.CTkButton(menu, text="Sluiten", command=menu.destroy).pack(pady=5)
    
    def show_settings(self):
        """Toon instellingen venster"""
        try:
            if self.settings_window is None:
                self.settings_window = SettingsWindow(self.root, self.settings)
            self.settings_window.show()
        except Exception as e:
            print(f"Fout bij openen instellingen: {e}")
            messagebox.showerror("Fout", f"Kon instellingen niet openen: {e}")
    
    def toggle_theme(self):
        """Wissel tussen licht en donker thema"""
        # Haal huidige thema op uit instellingen (betrouwbaarder)
        current_theme = self.settings.get("general", "theme", "system")
        
        # Bepaal nieuw thema op basis van huidige instelling
        if current_theme == "light":
            new_theme = "dark"
            new_icon = "☀️"
        elif current_theme == "dark":
            new_theme = "light"
            new_icon = "🌙"
        else:  # system of onbekend
            new_theme = "dark"
            new_icon = "☀️"
        
        # Pas thema toe
        ctk.set_appearance_mode(new_theme)
        self.settings.set("general", "theme", new_theme)
        
        # Update knop icoon
        self.theme_button.configure(text=new_icon)
        
        # Toon bevestiging
        self.status_label.configure(text=f"{get_text('theme', self.current_language)} gewijzigd naar {new_theme}")
        
        # Forceer volledige UI update
        self.update_theme_colors()
        
        # Toon bericht
        messagebox.showinfo(
            f"{get_text('theme', self.current_language)} Gewijzigd", 
            f"{get_text('theme', self.current_language)} is gewijzigd naar {new_theme}.\n\n"
            "De wijziging is direct zichtbaar!"
        )
    
    def toggle_language(self):
        """Wissel tussen Nederlands en Engels"""
        # Bepaal nieuwe taal
        if self.current_language == "nl":
            new_language = "en"
            new_icon = "🇳🇱"
        else:
            new_language = "nl"
            new_icon = "🇬🇧"
        
        # Sla nieuwe taal op
        self.current_language = new_language
        self.settings.set("general", "language", new_language)
        
        # Update knop icoon
        self.language_button.configure(text=new_icon)
        
        # Update UI teksten direct
        self.update_ui_language()
        
        # Toon bevestiging
        if self.current_language == "nl":
            self.status_label.configure(text=f"{get_text('language', self.current_language)} gewijzigd naar {get_language_name(self.current_language)}")
        else:
            self.status_label.configure(text=f"{get_text('language', self.current_language)} changed to {get_language_name(self.current_language)}")
        
        # Toon bericht
        if self.current_language == "nl":
            messagebox.showinfo(
                f"{get_text('language', self.current_language)} Gewijzigd", 
                f"{get_text('language', self.current_language)} is gewijzigd naar {get_language_name(self.current_language)}.\n\n"
                "De wijziging is direct zichtbaar!"
            )
        else:
            messagebox.showinfo(
                f"{get_text('language', self.current_language)} Changed", 
                f"{get_text('language', self.current_language)} changed to {get_language_name(self.current_language)}.\n\n"
                "The change is immediately visible!"
            )
    
    def update_ui_language(self):
        """Update alle UI teksten naar de huidige taal"""
        try:
            # Update venster titel
            version_string = get_version_string()
            self.root.title(f"{get_text('app_title', self.current_language)} v{version_string}")
            
            # Update titel en subtitle
            if hasattr(self, 'title_label'):
                self.title_label.configure(text="MakkelijkPdf")
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.configure(text="Converteer PDF bestanden naar afbeeldingen" if self.current_language == "nl" else "Convert PDF files to images")
            
            # Update sectie labels
            if hasattr(self, 'pdf_label'):
                self.pdf_label.configure(text="PDF Bestand:" if self.current_language == "nl" else "PDF File:")
            if hasattr(self, 'output_label_title'):
                self.output_label_title.configure(text="Output Map:" if self.current_language == "nl" else "Output Folder:")
            if hasattr(self, 'options_label'):
                self.options_label.configure(text="Conversie Opties:" if self.current_language == "nl" else "Conversion Options:")
            if hasattr(self, 'dpi_label'):
                self.dpi_label.configure(text="DPI (kwaliteit):" if self.current_language == "nl" else "DPI (quality):")
            if hasattr(self, 'format_label'):
                self.format_label.configure(text="Output Formaat:" if self.current_language == "nl" else "Output Format:")
            
            # Update knoppen en labels
            if hasattr(self, 'input_button'):
                self.input_button.configure(text=get_text('select_pdf', self.current_language))
            if hasattr(self, 'output_button'):
                self.output_button.configure(text=get_text('select_output', self.current_language))
            if hasattr(self, 'convert_button'):
                self.convert_button.configure(text=get_text('convert', self.current_language))
            
            # Update andere knoppen
            if hasattr(self, 'new_conversion_button'):
                self.new_conversion_button.configure(text=get_text('new_conversion', self.current_language))
            
            # Update menu knoppen
            if hasattr(self, 'file_button'):
                self.file_button.configure(text="Bestand" if self.current_language == "nl" else "File")
            if hasattr(self, 'settings_button'):
                self.settings_button.configure(text="Instellingen" if self.current_language == "nl" else "Settings")
            if hasattr(self, 'help_button'):
                self.help_button.configure(text="Help" if self.current_language == "nl" else "Help")
            
            # Update preview en stats labels
            if hasattr(self, 'preview_label'):
                self.preview_label.configure(text=get_text('preview', self.current_language))
            if hasattr(self, 'stats_label'):
                self.stats_label.configure(text=get_text('statistics', self.current_language))
            
            # Update statistieken titel en labels
            if hasattr(self, 'stats_title'):
                self.stats_title.configure(text="Statistieken" if self.current_language == "nl" else "Statistics")
            
            # Update statistieken labels
            if hasattr(self, 'stats_labels'):
                stats_translations = {
                    "pages": "Pagina's:" if self.current_language == "nl" else "Pages:",
                    "time": "Tijd:" if self.current_language == "nl" else "Time:",
                    "size": "Bestandsgrootte:" if self.current_language == "nl" else "File Size:",
                    "files": "Bestanden:" if self.current_language == "nl" else "Files:"
                }
                
                for key, translation in stats_translations.items():
                    if key in self.stats_labels:
                        self.stats_labels[key].configure(text=translation)
            
            # Update input label
            if hasattr(self, 'input_label'):
                if self.input_file:
                    self.input_label.configure(text=f"📄 {os.path.basename(self.input_file)}")
                else:
                    self.input_label.configure(text="Geen bestand geselecteerd" if self.current_language == "nl" else "No file selected")
            
            # Update output label
            if hasattr(self, 'output_label'):
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                self.output_label.configure(text=f"📁 {downloads_path}")
            
            # Update status
            self.status_label.configure(text="Klaar voor conversie" if self.current_language == "nl" else "Ready for conversion")
            
        except Exception as e:
            print(f"Fout bij updaten UI taal: {e}")
    
    def restart_application(self):
        """Herstart de applicatie"""
        import sys
        import os
        import subprocess
        
        # Sluit huidige venster
        self.root.destroy()
        
        # Start nieuwe instantie
        python = sys.executable
        try:
            subprocess.Popen([python, sys.argv[0]])
        except Exception as e:
            print(f"Fout bij herstarten: {e}")
            # Fallback: probeer os.execl
            os.execl(python, python, *sys.argv)
    
    def update_theme_colors(self):
        """Update alle UI kleuren voor het nieuwe thema"""
        try:
            # Forceer volledige UI refresh
            self.root.update()
            self.root.update_idletasks()
            
            # Update venster titel
            version_string = get_version_string()
            self.root.title(f"{get_text('app_title', self.current_language)} v{version_string}")
            
            # Update alle widgets recursief
            self.update_widget_colors(self.root)
                        
        except Exception as e:
            print(f"Thema update fout: {e}")
            # Als er een fout is, gewoon doorgaan
    
    def update_widget_colors(self, widget):
        """Update kleuren van widget en alle kinderen"""
        try:
            # Update huidige widget
            if hasattr(widget, 'configure'):
                widget.update()
            
            # Update alle kinderen
            for child in widget.winfo_children():
                self.update_widget_colors(child)
                
        except Exception:
            pass
    
    def new_conversion(self):
        """Start nieuwe conversie"""
        self.input_file = None
        # Behoud Downloads als standaard output map
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_folder = downloads_path
        
        self.input_label.configure(text="Geen bestand geselecteerd", text_color="gray")
        self.output_label.configure(text=f"📁 {downloads_path}", text_color="white")
        self.progress_bar.set(0)
        self.status_label.configure(text="Klaar voor conversie")
        
        # Reset preview
        if hasattr(self, 'preview_label'):
            self.preview_label.configure(text="Selecteer een PDF voor preview")
        if hasattr(self, 'preview_info'):
            self.preview_info.configure(text="")
        
        # Reset statistieken
        self.conversion_stats = {
            "start_time": None,
            "end_time": None,
            "pages_converted": 0,
            "total_size": 0,
            "files_created": []
        }
        self.update_stats()
    
    def open_output_folder(self):
        """Open output map"""
        if self.output_folder and os.path.exists(self.output_folder):
            import platform
            if platform.system() == "Darwin":  # macOS
                os.system(f"open '{self.output_folder}'")
            elif platform.system() == "Windows":
                os.startfile(self.output_folder)
            else:  # Linux
                os.system(f"xdg-open '{self.output_folder}'")
        else:
            messagebox.showwarning("Waarschuwing", "Geen output map geselecteerd")
    
    def show_documentation(self):
        """Toon documentatie"""
        messagebox.showinfo("Documentatie", "Zie README.md voor volledige documentatie")
    
    def check_updates(self):
        """Controleer op updates"""
        update_info = check_for_updates()
        if update_info["update_available"]:
            messagebox.showinfo("Update Beschikbaar", f"Versie {update_info['latest_version']} is beschikbaar!")
        else:
            messagebox.showinfo("Geen Updates", "Je gebruikt de nieuwste versie!")
    
    def update_stats(self):
        """Update statistieken weergave"""
        if hasattr(self, 'stats_labels'):
            self.stats_labels["pages"].configure(text=str(self.conversion_stats["pages_converted"]))
            
            if self.conversion_stats["start_time"] and self.conversion_stats["end_time"]:
                duration = self.conversion_stats["end_time"] - self.conversion_stats["start_time"]
                self.stats_labels["time"].configure(text=f"{duration:.1f}s")
            else:
                self.stats_labels["time"].configure(text="0s")
            
            size_mb = self.conversion_stats["total_size"] / (1024 * 1024)
            self.stats_labels["size"].configure(text=f"{size_mb:.1f} MB")
            self.stats_labels["files"].configure(text=str(len(self.conversion_stats["files_created"])))
        
    def select_input_file(self):
        """Selecteer input PDF bestand"""
        file_path = filedialog.askopenfilename(
            title="Selecteer PDF bestand",
            filetypes=[("PDF bestanden", "*.pdf"), ("Alle bestanden", "*.*")]
        )
        
        if file_path:
            self.input_file = file_path
            filename = os.path.basename(file_path)
            self.input_label.configure(text=filename, text_color="white")
            
            # Update preview
            if hasattr(self, 'update_preview'):
                self.update_preview()
            
    def select_output_folder(self):
        """Selecteer output map"""
        # Start in Downloads map als standaard
        initial_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        folder_path = filedialog.askdirectory(
            title="Selecteer output map",
            initialdir=initial_dir
        )
        
        if folder_path:
            self.output_folder = folder_path
            self.output_label.configure(text=f"📁 {folder_path}", text_color="white")
            
    def start_conversion(self):
        """Start de conversie in een aparte thread"""
        if not self.input_file:
            messagebox.showerror("Fout", "Selecteer eerst een PDF bestand!")
            return
            
        if not self.output_folder:
            messagebox.showerror("Fout", "Selecteer eerst een output map!")
            return
            
        # Start conversie in aparte thread
        thread = threading.Thread(target=self.convert_pdf)
        thread.daemon = True
        thread.start()
        
    def convert_pdf(self):
        """Converteer PDF naar afbeeldingen"""
        try:
            # Reset statistieken
            self.conversion_stats = {
                "start_time": time.time(),
                "end_time": None,
                "pages_converted": 0,
                "total_size": 0,
                "files_created": []
            }
            
            self.convert_button.configure(state="disabled")
            self.status_label.configure(text="Conversie gestart...")
            self.progress_bar.set(0)
            
            # Lees PDF
            self.status_label.configure(text="PDF wordt gelezen...")
            pages = convert_from_path(
                self.input_file, 
                dpi=int(self.dpi_var.get()),
                first_page=None,
                last_page=None,
                poppler_path=poppler_path
            )
            
            total_pages = len(pages)
            filename_base = Path(self.input_file).stem
            output_format = self.format_var.get().lower()
            quality = self.settings.get("conversion", "quality", 95)
            
            # Converteer elke pagina
            for i, page in enumerate(pages):
                self.status_label.configure(text=f"Pagina {i+1} van {total_pages} wordt geconverteerd...")
                
                # Bepaal output bestandsnaam
                if total_pages == 1:
                    output_filename = f"{filename_base}.{output_format}"
                else:
                    output_filename = f"{filename_base}_pagina_{i+1:03d}.{output_format}"
                
                output_path = os.path.join(self.output_folder, output_filename)
                
                # Sla afbeelding op
                if output_format in ['jpg', 'jpeg']:
                    # Converteer naar RGB voor JPG
                    if page.mode == 'RGBA':
                        page = page.convert('RGB')
                    page.save(output_path, 'JPEG', quality=quality)
                else:
                    page.save(output_path, output_format.upper())
                
                # Update statistieken
                self.conversion_stats["pages_converted"] += 1
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    self.conversion_stats["total_size"] += file_size
                    self.conversion_stats["files_created"].append(output_path)
                
                # Update progress
                progress = (i + 1) / total_pages
                self.progress_bar.set(progress)
                
                # Update statistieken weergave
                self.update_stats()
            
            # Voltooi statistieken
            self.conversion_stats["end_time"] = time.time()
            self.update_stats()
            
            self.status_label.configure(text=f"Conversie voltooid! {total_pages} pagina('s) geconverteerd.")
            
            # Auto-open output folder als ingesteld
            if self.settings.get("conversion", "auto_open_output", False):
                self.open_output_folder()
            
            messagebox.showinfo("Succes", f"Conversie voltooid!\n{total_pages} pagina('s) geconverteerd naar {self.output_folder}")
            
        except Exception as e:
            self.status_label.configure(text="Fout opgetreden tijdens conversie")
            messagebox.showerror("Fout", f"Er is een fout opgetreden:\n{str(e)}")
            
        finally:
            self.convert_button.configure(state="normal")
            
    def show_about(self):
        """Toon over venster met versie informatie"""
        version_info = get_version_info()
        update_info = check_for_updates()
        
        about_text = f"""MakkelijkPdf - PDF Converter

Versie: {version_info['major']}.{version_info['minor']}.{version_info['patch']}
Build: {version_info['build']}
Datum: {version_info['date']}
Codename: {version_info['codename']}

Een eenvoudige en gebruiksvriendelijke applicatie voor het converteren van PDF bestanden naar afbeeldingen.

Features:
• PDF naar PNG/JPG/TIFF conversie
• Batch conversie functionaliteit
• Modern GUI interface
• Command line interface
• Cross-platform ondersteuning

GitHub: https://github.com/LaurensLecocq04/MakkelijkPdf
Licentie: MIT

© 2024 Laurens Lecocq"""
        
        messagebox.showinfo("Over MakkelijkPdf", about_text)
            
    def run(self):
        """Start de applicatie"""
        self.root.mainloop()

def main():
    """Hoofdfunctie"""
    app = MakkelijkPdfApp()
    app.run()

if __name__ == "__main__":
    main()
