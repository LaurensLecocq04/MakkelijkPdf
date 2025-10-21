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

# Voeg poppler pad toe aan PATH
poppler_path = r"C:\poppler\poppler-23.08.0\Library\bin"
if poppler_path not in os.environ["PATH"]:
    os.environ["PATH"] = poppler_path + os.pathsep + os.environ["PATH"]

class MakkelijkPdfApp:
    def __init__(self):
        # Configureer CustomTkinter
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Maak hoofdvenster
        self.root = ctk.CTk()
        self.root.title("MakkelijkPdf - PDF Converter")
        self.root.geometry("600x500")
        
        # Variabelen
        self.input_file = None
        self.output_folder = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Zet de gebruikersinterface op"""
        # Titel
        title_label = ctk.CTkLabel(
            self.root, 
            text="MakkelijkPdf", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self.root, 
            text="Converteer PDF bestanden naar afbeeldingen", 
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Input bestand sectie
        input_frame = ctk.CTkFrame(self.root)
        input_frame.pack(fill="x", padx=20, pady=10)
        
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
        output_frame = ctk.CTkFrame(self.root)
        output_frame.pack(fill="x", padx=20, pady=10)
        
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
        options_frame = ctk.CTkFrame(self.root)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(options_frame, text="Conversie Opties:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # DPI instelling
        dpi_frame = ctk.CTkFrame(options_frame)
        dpi_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(dpi_frame, text="DPI (kwaliteit):").pack(side="left", padx=10, pady=10)
        self.dpi_var = ctk.StringVar(value="300")
        dpi_entry = ctk.CTkEntry(dpi_frame, textvariable=self.dpi_var, width=100)
        dpi_entry.pack(side="left", padx=10, pady=10)
        
        # Formaat selectie
        format_frame = ctk.CTkFrame(options_frame)
        format_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(format_frame, text="Output Formaat:").pack(side="left", padx=10, pady=10)
        self.format_var = ctk.StringVar(value="PNG")
        format_menu = ctk.CTkOptionMenu(
            format_frame, 
            variable=self.format_var,
            values=["PNG", "JPG", "JPEG", "TIFF"]
        )
        format_menu.pack(side="left", padx=10, pady=10)
        
        # Conversie knop
        self.convert_button = ctk.CTkButton(
            self.root, 
            text="Start Conversie", 
            command=self.start_conversion,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.convert_button.pack(pady=30)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.root)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.root, text="Klaar voor conversie")
        self.status_label.pack(pady=(0, 20))
        
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
                    page.save(output_path, 'JPEG', quality=95)
                else:
                    page.save(output_path, output_format.upper())
                
                # Update progress
                progress = (i + 1) / total_pages
                self.progress_bar.set(progress)
                
            self.status_label.configure(text=f"Conversie voltooid! {total_pages} pagina('s) geconverteerd.")
            messagebox.showinfo("Succes", f"Conversie voltooid!\n{total_pages} pagina('s) geconverteerd naar {self.output_folder}")
            
        except Exception as e:
            self.status_label.configure(text="Fout opgetreden tijdens conversie")
            messagebox.showerror("Fout", f"Er is een fout opgetreden:\n{str(e)}")
            
        finally:
            self.convert_button.configure(state="normal")
            
    def run(self):
        """Start de applicatie"""
        self.root.mainloop()

def main():
    """Hoofdfunctie"""
    app = MakkelijkPdfApp()
    app.run()

if __name__ == "__main__":
    main()
