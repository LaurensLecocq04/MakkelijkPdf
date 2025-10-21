#!/usr/bin/env python3
"""
MakkelijkPdf - Eenvoudige PDF naar afbeelding converter
"""

import os
import sys
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pdf2image import convert_from_path
from PIL import Image
import threading
import time
from datetime import datetime
from version import get_version_string, get_version_info, check_for_updates
from settings import SettingsManager
from settings_window import SettingsWindow
from languages import get_text, get_language_name

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
        
        # Voeg icoontje toe
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
            elif os.path.exists("icon.png"):
                # Voor platforms die geen ICO ondersteunen
                self.root.iconphoto(True, ctk.CTkImage(Image.open("icon.png")))
        except Exception as e:
            print(f"Kon icoontje niet laden: {e}")
        
        # Venster grootte uit instellingen
        width = self.settings.get("ui", "window_width", 1400)
        height = self.settings.get("ui", "window_height", 1000)
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
        
    def setup_menu(self):
        """Zet moderne menu systeem op"""
        # Maak moderne menu bar
        menubar = ctk.CTkFrame(self.root, height=50, corner_radius=15, fg_color=("#ffffff", "#34495e"))
        menubar.pack(fill="x", padx=30, pady=(0, 20))
        menubar.pack_propagate(False)
        
        # Bestand menu
        file_button = ctk.CTkButton(
            menubar,
            text="📁 Bestand",
            command=self.show_file_menu,
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d")
        )
        file_button.pack(side="left", padx=10, pady=7)
        self.file_button = file_button
        
        # Instellingen menu
        settings_button = ctk.CTkButton(
            menubar,
            text="⚙️ Instellingen",
            command=self.show_settings,
            width=120,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#9b59b6", "#8e44ad"),
            hover_color=("#8e44ad", "#7d3c98")
        )
        settings_button.pack(side="left", padx=5, pady=7)
        self.settings_button = settings_button
        
        # Help menu
        help_button = ctk.CTkButton(
            menubar,
            text="❓ Help",
            command=self.show_help_menu,
            width=80,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#f39c12", "#e67e22"),
            hover_color=("#e67e22", "#d35400")
        )
        help_button.pack(side="left", padx=5, pady=7)
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
            width=40,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=16),
            fg_color=("#34495e", "#2c3e50"),
            hover_color=("#2c3e50", "#1a252f")
        )
        self.theme_button.pack(side="right", padx=5, pady=7)
        
        # Taal wissel knop
        language_icon = "🇬🇧" if self.current_language == "nl" else "🇳🇱"
        self.language_button = ctk.CTkButton(
            menubar,
            text=language_icon,
            command=self.toggle_language,
            width=40,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=16),
            fg_color=("#34495e", "#2c3e50"),
            hover_color=("#2c3e50", "#1a252f")
        )
        self.language_button.pack(side="right", padx=5, pady=7)
    
    def on_window_resize(self, event):
        """Callback voor venster resize"""
        if event.widget == self.root:
            # Update venster grootte in settings
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.settings.set("ui", "window_width", width)
            self.settings.set("ui", "window_height", height)
    
    def setup_ui(self):
        """Zet de moderne gebruikersinterface op"""
        # Header sectie met moderne styling
        header_frame = ctk.CTkFrame(self.root, height=140, corner_radius=0, fg_color=("#ffffff", "#2c3e50"))
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Hoofdtitel met moderne typografie
        title_label = ctk.CTkLabel(
            header_frame,
            text="MakkelijkPdf",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("#2c3e50", "#ecf0f1")
        )
        title_label.pack(pady=(25, 5))
        self.title_label = title_label
        
        # Ondertitel met subtiele styling
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Professional PDF to Image Converter",
            font=ctk.CTkFont(size=16),
            text_color=("#7f8c8d", "#bdc3c7")
        )
        subtitle_label.pack(pady=(0, 25))
        self.subtitle_label = subtitle_label
        
        # Initialiseer conversie variabelen
        self.dpi_var = None
        self.format_var = None
        
        # Configureer venster resize callback
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Setup menu bar
        self.setup_menu()
        
        # Hoofdcontainer met moderne card layout (vast frame zodat grid goed kan schalen)
        main_container = ctk.CTkFrame(self.root, corner_radius=25, fg_color=("#ffffff", "#34495e"))
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Configureer grid voor responsive kolommen (gelijke breedte)
        main_container.grid_columnconfigure(0, weight=1, uniform="cols", minsize=400)
        main_container.grid_columnconfigure(1, weight=1, uniform="cols", minsize=400)
        
        # Linker kolom - Input en opties (moderne cards, scrollable, responsive)
        left_column = ctk.CTkScrollableFrame(main_container, corner_radius=20, fg_color=("#f8f9fa", "#2c3e50"))
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Rechter kolom - Preview en statistieken (moderne cards, scrollable, responsive)
        right_column = ctk.CTkScrollableFrame(main_container, corner_radius=20, fg_color=("#f8f9fa", "#2c3e50"))
        right_column.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        # Configureer row voor volledige hoogte
        main_container.grid_rowconfigure(0, weight=1)
        
        # Setup secties met moderne styling
        self.setup_input_section(left_column)
        self.setup_options_section(left_column)
        self.setup_actions_section(left_column)
        self.setup_preview(right_column)
        self.setup_stats(right_column)
        
        # Moderne status bar met gradient effect
        status_frame = ctk.CTkFrame(self.root, height=60, corner_radius=20, fg_color=("#e8f5e8", "#27ae60"))
        status_frame.pack(fill="x", padx=30, pady=(0, 30))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready for conversion",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#27ae60", "#ffffff")
        )
        self.status_label.pack(expand=True)
    
    def setup_input_section(self, parent):
        """Moderne input sectie"""
        # Input card
        input_card = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffffff", "#34495e"))
        input_card.pack(fill="x", padx=20, pady=(20, 15))
        
        # Card header
        header_frame = ctk.CTkFrame(input_card, height=50, corner_radius=10, fg_color=("#3498db", "#2980b9"))
        header_frame.pack(fill="x", padx=15, pady=15)
        header_frame.pack_propagate(False)
        
        pdf_label = ctk.CTkLabel(
            header_frame,
            text="📄 PDF File",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        pdf_label.pack(expand=True)
        self.pdf_label = pdf_label
        
        # File info
        self.input_label = ctk.CTkLabel(
            input_card,
            text="No file selected",
            font=ctk.CTkFont(size=14),
            text_color=("#7f8c8d", "#bdc3c7")
        )
        self.input_label.pack(pady=(0, 15), padx=15)
        
        # Modern button
        input_button = ctk.CTkButton(
            input_card,
            text="Select PDF File",
            command=self.select_input_file,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d")
        )
        input_button.pack(pady=(0, 15), padx=15, fill="x")
        self.input_button = input_button
        
        # Output card
        output_card = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffffff", "#34495e"))
        output_card.pack(fill="x", padx=20, pady=(0, 15))
        
        # Card header
        output_header = ctk.CTkFrame(output_card, height=50, corner_radius=10, fg_color=("#e74c3c", "#c0392b"))
        output_header.pack(fill="x", padx=15, pady=15)
        output_header.pack_propagate(False)
        
        output_label_title = ctk.CTkLabel(
            output_header,
            text="📁 Output Folder",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        output_label_title.pack(expand=True)
        self.output_label_title = output_label_title
        
        # Folder info
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_label = ctk.CTkLabel(
            output_card,
            text=f"📁 {downloads_path}",
            font=ctk.CTkFont(size=12),
            text_color=("#7f8c8d", "#bdc3c7")
        )
        self.output_label.pack(pady=(0, 15), padx=15)
        
        # Modern button
        output_button = ctk.CTkButton(
            output_card,
            text="Select Output Folder",
            command=self.select_output_folder,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
            fg_color=("#e74c3c", "#c0392b"),
            hover_color=("#c0392b", "#a93226")
        )
        output_button.pack(pady=(0, 15), padx=15, fill="x")
        self.output_button = output_button
    
    def setup_options_section(self, parent):
        """Moderne opties sectie"""
        options_card = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffffff", "#34495e"))
        options_card.pack(fill="x", padx=20, pady=(0, 15))
        
        # Card header
        options_header = ctk.CTkFrame(options_card, height=50, corner_radius=10, fg_color=("#9b59b6", "#8e44ad"))
        options_header.pack(fill="x", padx=15, pady=15)
        options_header.pack_propagate(False)
        
        options_label = ctk.CTkLabel(
            options_header,
            text="⚙️ Conversion Options",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        options_label.pack(expand=True)
        self.options_label = options_label
        
        # DPI section
        dpi_frame = ctk.CTkFrame(options_card, corner_radius=10, fg_color=("#ecf0f1", "#34495e"))
        dpi_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        dpi_label = ctk.CTkLabel(
            dpi_frame,
            text="DPI (Quality):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#2c3e50", "#ecf0f1")
        )
        dpi_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.dpi_label = dpi_label
        
        default_dpi = self.settings.get("conversion", "default_dpi", 300)
        self.dpi_var = ctk.StringVar(value=str(default_dpi))
        dpi_menu = ctk.CTkOptionMenu(
            dpi_frame,
            variable=self.dpi_var,
            values=["150", "200", "300", "400", "600"],
            width=200,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color=("#ffffff", "#2c3e50"),
            button_color=("#3498db", "#2980b9"),
            button_hover_color=("#2980b9", "#1f618d")
        )
        dpi_menu.pack(anchor="w", padx=15, pady=(0, 15), fill="x")
        self.dpi_menu = dpi_menu
        
        # Format section
        format_frame = ctk.CTkFrame(options_card, corner_radius=10, fg_color=("#ecf0f1", "#34495e"))
        format_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        format_label = ctk.CTkLabel(
            format_frame,
            text="Output Format:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#2c3e50", "#ecf0f1")
        )
        format_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.format_label = format_label
        
        default_format = self.settings.get("conversion", "default_format", "PNG")
        self.format_var = ctk.StringVar(value=default_format)
        format_menu = ctk.CTkOptionMenu(
            format_frame,
            variable=self.format_var,
            values=["PNG", "JPG", "JPEG", "TIFF", "BMP"],
            width=200,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color=("#ffffff", "#2c3e50"),
            button_color=("#e74c3c", "#c0392b"),
            button_hover_color=("#c0392b", "#a93226")
        )
        format_menu.pack(anchor="w", padx=15, pady=(0, 15), fill="x")
    
    def setup_actions_section(self, parent):
        """Moderne acties sectie"""
        actions_card = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffffff", "#34495e"))
        actions_card.pack(fill="x", padx=20, pady=(0, 20))
        
        # Main convert button
        self.convert_button = ctk.CTkButton(
            actions_card,
            text="🚀 Start Conversion",
            command=self.start_conversion,
            height=60,
            font=ctk.CTkFont(size=20, weight="bold"),
            corner_radius=15,
            fg_color=("#27ae60", "#229954"),
            hover_color=("#229954", "#1e8449")
        )
        self.convert_button.pack(pady=20, padx=20, fill="x")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            actions_card,
            height=20,
            corner_radius=10,
            fg_color=("#ecf0f1", "#34495e"),
            progress_color=("#27ae60", "#2ecc71")
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.progress_bar.set(0)
    
    def setup_preview(self, parent):
        """Moderne preview sectie"""
        preview_card = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffffff", "#34495e"))
        preview_card.pack(fill="both", expand=True, padx=20, pady=(20, 15))
        
        # Card header
        preview_header = ctk.CTkFrame(preview_card, height=50, corner_radius=10, fg_color=("#f39c12", "#e67e22"))
        preview_header.pack(fill="x", padx=15, pady=15)
        preview_header.pack_propagate(False)
        
        preview_label = ctk.CTkLabel(
            preview_header,
            text="👁️ Preview",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        preview_label.pack(expand=True)
        self.preview_label = preview_label
        
        # Preview content
        self.preview_container = ctk.CTkScrollableFrame(preview_card, corner_radius=10)
        self.preview_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Preview info
        self.preview_info = ctk.CTkLabel(
            self.preview_container,
            text="Select a PDF file to see preview information",
            font=ctk.CTkFont(size=14),
            text_color=("#7f8c8d", "#bdc3c7"),
            wraplength=300
        )
        self.preview_info.pack(pady=30)
    
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
        """Moderne statistieken sectie"""
        stats_card = ctk.CTkFrame(parent, corner_radius=15, fg_color=("#ffffff", "#34495e"))
        stats_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Card header
        stats_header = ctk.CTkFrame(stats_card, height=50, corner_radius=10, fg_color=("#16a085", "#138d75"))
        stats_header.pack(fill="x", padx=15, pady=15)
        stats_header.pack_propagate(False)
        
        stats_title = ctk.CTkLabel(
            stats_header,
            text="📊 Statistics",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        stats_title.pack(expand=True)
        self.stats_title = stats_title
        
        # Stats content
        stats_content = ctk.CTkFrame(stats_card, corner_radius=10, fg_color=("#ecf0f1", "#34495e"))
        stats_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Individual stat labels
        self.stats_labels = {}
        stats_info = [
            ("pages", "Pages:", "0"),
            ("time", "Time:", "0s"),
            ("size", "File Size:", "0 MB"),
            ("files", "Files:", "0")
        ]
        
        for key, label_text, default_value in stats_info:
            stat_frame = ctk.CTkFrame(stats_content, corner_radius=8, fg_color=("#ffffff", "#2c3e50"))
            stat_frame.pack(fill="x", padx=10, pady=8)
            
            label = ctk.CTkLabel(
                stat_frame,
                text=label_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#2c3e50", "#ecf0f1")
            )
            label.pack(anchor="w", padx=15, pady=(10, 5))
            
            value_label = ctk.CTkLabel(
                stat_frame,
                text=default_value,
                font=ctk.CTkFont(size=16),
                text_color=("#27ae60", "#2ecc71")
            )
            value_label.pack(anchor="w", padx=15, pady=(0, 10))
            
            self.stats_labels[key] = value_label
    
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
        if self.current_language == "nl":
            self.status_label.configure(text=f"Thema gewijzigd naar {new_theme}")
        else:
            self.status_label.configure(text=f"Theme changed to {new_theme}")
        
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
            new_icon = "🇬🇧"
        else:
            new_language = "nl"
            new_icon = "🇳🇱"
        
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
                if self.current_language == "nl":
                    self.pdf_label.configure(text="📄 PDF Bestand")
                else:
                    self.pdf_label.configure(text="📄 PDF File")
            if hasattr(self, 'output_label_title'):
                if self.current_language == "nl":
                    self.output_label_title.configure(text="📁 Output Map")
                else:
                    self.output_label_title.configure(text="📁 Output Folder")
            if hasattr(self, 'options_label'):
                if self.current_language == "nl":
                    self.options_label.configure(text="⚙️ Conversie Opties")
                else:
                    self.options_label.configure(text="⚙️ Conversion Options")
            if hasattr(self, 'dpi_label'):
                if self.current_language == "nl":
                    self.dpi_label.configure(text="DPI (Kwaliteit):")
                else:
                    self.dpi_label.configure(text="DPI (Quality):")
            if hasattr(self, 'format_label'):
                if self.current_language == "nl":
                    self.format_label.configure(text="Output Formaat:")
                else:
                    self.format_label.configure(text="Output Format:")
            
            # Update knoppen en labels
            if hasattr(self, 'input_button'):
                if self.current_language == "nl":
                    self.input_button.configure(text="Selecteer PDF Bestand")
                else:
                    self.input_button.configure(text="Select PDF File")
            if hasattr(self, 'output_button'):
                if self.current_language == "nl":
                    self.output_button.configure(text="Selecteer Output Map")
                else:
                    self.output_button.configure(text="Select Output Folder")
            if hasattr(self, 'convert_button'):
                if self.current_language == "nl":
                    self.convert_button.configure(text="🚀 Start Conversie")
                else:
                    self.convert_button.configure(text="🚀 Start Conversion")
            
            # Update andere knoppen
            if hasattr(self, 'new_conversion_button'):
                self.new_conversion_button.configure(text=get_text('new_conversion', self.current_language))
            
            # Update menu knoppen
            if hasattr(self, 'file_button'):
                if self.current_language == "nl":
                    self.file_button.configure(text="📁 Bestand")
                else:
                    self.file_button.configure(text="📁 File")
            if hasattr(self, 'settings_button'):
                if self.current_language == "nl":
                    self.settings_button.configure(text="⚙️ Instellingen")
                else:
                    self.settings_button.configure(text="⚙️ Settings")
            if hasattr(self, 'help_button'):
                self.help_button.configure(text="❓ Help")
            
            # Update preview en stats labels
            if hasattr(self, 'preview_label'):
                if self.current_language == "nl":
                    self.preview_label.configure(text="👁️ Preview")
                else:
                    self.preview_label.configure(text="👁️ Preview")
            if hasattr(self, 'stats_title'):
                if self.current_language == "nl":
                    self.stats_title.configure(text="📊 Statistieken")
                else:
                    self.stats_title.configure(text="📊 Statistics")
            
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
                    if self.current_language == "nl":
                        self.input_label.configure(text="Geen bestand geselecteerd")
                    else:
                        self.input_label.configure(text="No file selected")
            
            # Update output label
            if hasattr(self, 'output_label'):
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                self.output_label.configure(text=f"📁 {downloads_path}")
            
            # Update status
            if self.current_language == "nl":
                self.status_label.configure(text="Klaar voor conversie")
            else:
                self.status_label.configure(text="Ready for conversion")
            
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
            # Update pages
            if "pages" in self.stats_labels:
                self.stats_labels["pages"].configure(text=str(self.conversion_stats["pages_converted"]))
            
            # Update time
            if "time" in self.stats_labels:
                if self.conversion_stats["start_time"] and self.conversion_stats["end_time"]:
                    duration = self.conversion_stats["end_time"] - self.conversion_stats["start_time"]
                    self.stats_labels["time"].configure(text=f"{duration:.1f}s")
                else:
                    self.stats_labels["time"].configure(text="0s")
            
            # Update size
            if "size" in self.stats_labels:
                size_mb = self.conversion_stats["total_size"] / (1024 * 1024)
                self.stats_labels["size"].configure(text=f"{size_mb:.1f} MB")
            
            # Update files
            if "files" in self.stats_labels:
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
            if hasattr(self, 'input_label'):
                self.input_label.configure(text=f"📄 {filename}")
            
            # Update preview
            if hasattr(self, 'update_preview'):
                self.update_preview()
            
            # Update status
            if hasattr(self, 'status_label'):
                if self.current_language == "nl":
                    self.status_label.configure(text="PDF bestand geselecteerd")
                else:
                    self.status_label.configure(text="PDF file selected")
            
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
            if hasattr(self, 'output_label'):
                self.output_label.configure(text=f"📁 {folder_path}")
            
            # Update status
            if hasattr(self, 'status_label'):
                if self.current_language == "nl":
                    self.status_label.configure(text="Output map geselecteerd")
                else:
                    self.status_label.configure(text="Output folder selected")
            
    def start_conversion(self):
        """Start de conversie in een aparte thread"""
        if not self.input_file:
            if self.current_language == "nl":
                messagebox.showerror("Fout", "Selecteer eerst een PDF bestand!")
            else:
                messagebox.showerror("Error", "Please select a PDF file first!")
            return
            
        if not self.output_folder:
            if self.current_language == "nl":
                messagebox.showerror("Fout", "Selecteer eerst een output map!")
            else:
                messagebox.showerror("Error", "Please select an output folder first!")
            return
            
        # Start conversie in aparte thread
        thread = threading.Thread(target=self.convert_pdf, args=(self.dpi_var.get() if self.dpi_var else "300", self.format_var.get() if self.format_var else "PNG"))
        thread.daemon = True
        thread.start()
        
    def convert_pdf(self, dpi_value="300", format_value="PNG"):
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
            if self.current_language == "nl":
                self.status_label.configure(text="Conversie gestart...")
            else:
                self.status_label.configure(text="Conversion started...")
            self.progress_bar.set(0)
            
            # Lees PDF
            if self.current_language == "nl":
                self.status_label.configure(text="PDF wordt gelezen...")
            else:
                self.status_label.configure(text="Reading PDF...")
            pages = convert_from_path(
                self.input_file, 
                dpi=int(dpi_value),
                first_page=None,
                last_page=None,
                poppler_path=poppler_path
            )
            
            total_pages = len(pages)
            filename_base = Path(self.input_file).stem
            output_format = format_value.lower()
            quality = self.settings.get("conversion", "quality", 95)
            
            # Converteer elke pagina
            for i, page in enumerate(pages):
                if self.current_language == "nl":
                    self.status_label.configure(text=f"Pagina {i+1} van {total_pages} wordt geconverteerd...")
                else:
                    self.status_label.configure(text=f"Converting page {i+1} of {total_pages}...")
                
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
            
            if self.current_language == "nl":
                self.status_label.configure(text=f"Conversie voltooid! {total_pages} pagina('s) geconverteerd.")
            else:
                self.status_label.configure(text=f"Conversion complete! {total_pages} page(s) converted.")
            
            # Auto-open output folder als ingesteld
            if self.settings.get("conversion", "auto_open_output", False):
                self.open_output_folder()
            
            if self.current_language == "nl":
                messagebox.showinfo("Succes", f"Conversie voltooid!\n{total_pages} pagina('s) geconverteerd naar {self.output_folder}")
            else:
                messagebox.showinfo("Success", f"Conversion complete!\n{total_pages} page(s) converted to {self.output_folder}")
            
        except Exception as e:
            if self.current_language == "nl":
                self.status_label.configure(text="Fout opgetreden tijdens conversie")
                messagebox.showerror("Fout", f"Er is een fout opgetreden:\n{str(e)}")
            else:
                self.status_label.configure(text="Error occurred during conversion")
                messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            
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

© 2025 Laurens Lecocq"""
        
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
