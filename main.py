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

# Voeg poppler pad toe aan PATH
poppler_path = r"C:\poppler\poppler-23.08.0\Library\bin"
if poppler_path not in os.environ["PATH"]:
    os.environ["PATH"] = poppler_path + os.pathsep + os.environ["PATH"]

class MakkelijkPdfApp:
    def __init__(self):
        # Laad instellingen
        self.settings = SettingsManager()
        
        # Configureer CustomTkinter
        theme = self.settings.get("general", "theme", "system")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # Maak hoofdvenster
        self.root = ctk.CTk()
        version_string = get_version_string()
        self.root.title(f"MakkelijkPdf - PDF Converter v{version_string}")
        
        # Venster grootte uit instellingen
        width = self.settings.get("ui", "window_width", 700)
        height = self.settings.get("ui", "window_height", 600)
        self.root.geometry(f"{width}x{height}")
        
        # Variabelen
        self.input_file = None
        self.output_folder = None
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
        
        # Instellingen menu
        settings_button = ctk.CTkButton(
            menubar,
            text="Instellingen",
            command=self.show_settings,
            width=80,
            height=25
        )
        settings_button.pack(side="left", padx=5, pady=2)
        
        # Help menu
        help_button = ctk.CTkButton(
            menubar,
            text="Help",
            command=self.show_help_menu,
            width=80,
            height=25
        )
        help_button.pack(side="left", padx=5, pady=2)
        
        # Spacer
        spacer = ctk.CTkLabel(menubar, text="")
        spacer.pack(side="left", fill="x", expand=True)
        
        # Thema switcher
        theme_button = ctk.CTkButton(
            menubar,
            text="🌙" if ctk.get_appearance_mode() == "light" else "☀️",
            command=self.toggle_theme,
            width=30,
            height=25
        )
        theme_button.pack(side="right", padx=5, pady=2)
        
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
        
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="Converteer PDF bestanden naar afbeeldingen", 
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 10))
        
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
        
        ctk.CTkLabel(input_frame, text="PDF Bestand:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.input_label = ctk.CTkLabel(input_frame, text="Geen bestand geselecteerd", text_color="gray")
        self.input_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        input_button = ctk.CTkButton(
            input_frame, 
            text="Selecteer PDF", 
            command=self.select_input_file
        )
        input_button.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Output folder sectie
        output_frame = ctk.CTkFrame(left_frame)
        output_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(output_frame, text="Output Map:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.output_label = ctk.CTkLabel(output_frame, text="Geen map geselecteerd", text_color="gray")
        self.output_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        output_button = ctk.CTkButton(
            output_frame, 
            text="Selecteer Output Map", 
            command=self.select_output_folder
        )
        output_button.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Conversie opties
        options_frame = ctk.CTkFrame(left_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(options_frame, text="Conversie Opties:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # DPI instelling
        dpi_frame = ctk.CTkFrame(options_frame)
        dpi_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(dpi_frame, text="DPI (kwaliteit):").pack(side="left", padx=10, pady=10)
        default_dpi = self.settings.get("conversion", "default_dpi", 300)
        self.dpi_var = ctk.StringVar(value=str(default_dpi))
        dpi_entry = ctk.CTkEntry(dpi_frame, textvariable=self.dpi_var, width=100)
        dpi_entry.pack(side="left", padx=10, pady=10)
        
        # Formaat selectie
        format_frame = ctk.CTkFrame(options_frame)
        format_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(format_frame, text="Output Formaat:").pack(side="left", padx=10, pady=10)
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
        
        # Preview canvas
        self.preview_canvas = ctk.CTkCanvas(preview_frame, width=200, height=300, bg="gray20")
        self.preview_canvas.pack(pady=10)
        
        self.preview_label = ctk.CTkLabel(preview_frame, text="Selecteer een PDF voor preview")
        self.preview_label.pack(pady=10)
    
    def setup_stats(self, parent):
        """Zet statistieken sectie op"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Statistieken", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
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
            
            ctk.CTkLabel(frame, text=label_text).pack(side="left", padx=5)
            self.stats_labels[key] = ctk.CTkLabel(frame, text="0")
            self.stats_labels[key].pack(side="right", padx=5)
    
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
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.root, self.settings)
        self.settings_window.show()
    
    def toggle_theme(self):
        """Wissel tussen licht en donker thema"""
        current = ctk.get_appearance_mode()
        new_theme = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_theme)
        self.settings.set("general", "theme", new_theme)
    
    def new_conversion(self):
        """Start nieuwe conversie"""
        self.input_file = None
        self.output_folder = None
        self.input_label.configure(text="Geen bestand geselecteerd", text_color="gray")
        self.output_label.configure(text="Geen map geselecteerd", text_color="gray")
        self.progress_bar.set(0)
        self.status_label.configure(text="Klaar voor conversie")
        self.update_stats()
    
    def open_output_folder(self):
        """Open output map"""
        if self.output_folder and os.path.exists(self.output_folder):
            os.startfile(self.output_folder)
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
            
    def select_output_folder(self):
        """Selecteer output map"""
        folder_path = filedialog.askdirectory(title="Selecteer output map")
        
        if folder_path:
            self.output_folder = folder_path
            self.output_label.configure(text=folder_path, text_color="white")
            
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
