"""
MakkelijkPdf - Instellingen Venster
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from settings import SettingsManager
import os

class SettingsWindow:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings = settings_manager
        self.window = None
        
    def show(self):
        """Toon instellingen venster"""
        if self.window is not None:
            self.window.focus()
            return
            
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Instellingen - MakkelijkPdf")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # Maak venster modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.setup_ui()
        
        # Center venster
        self.center_window()
        
    def setup_ui(self):
        """Zet UI op"""
        # Hoofdframe met scrollbar
        main_frame = ctk.CTkScrollableFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tab systeem simuleren met frames
        self.create_general_tab(main_frame)
        self.create_conversion_tab(main_frame)
        self.create_ui_tab(main_frame)
        self.create_advanced_tab(main_frame)
        
        # Knoppen onderaan
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Reset knop
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset naar Standaard",
            command=self.reset_settings,
            fg_color="red",
            hover_color="darkred"
        )
        reset_button.pack(side="left", padx=10, pady=10)
        
        # Export/Import knoppen
        export_button = ctk.CTkButton(
            button_frame,
            text="Exporteer Instellingen",
            command=self.export_settings
        )
        export_button.pack(side="left", padx=5, pady=10)
        
        import_button = ctk.CTkButton(
            button_frame,
            text="Importeer Instellingen",
            command=self.import_settings
        )
        import_button.pack(side="left", padx=5, pady=10)
        
        # OK/Cancel knoppen
        ok_button = ctk.CTkButton(
            button_frame,
            text="OK",
            command=self.save_and_close,
            width=100
        )
        ok_button.pack(side="right", padx=5, pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuleren",
            command=self.close_window,
            width=100
        )
        cancel_button.pack(side="right", padx=5, pady=10)
        
    def create_general_tab(self, parent):
        """Algemene instellingen"""
        general_frame = ctk.CTkFrame(parent)
        general_frame.pack(fill="x", pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            general_frame,
            text="Algemene Instellingen",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Thema selectie
        theme_frame = ctk.CTkFrame(general_frame)
        theme_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Thema:").pack(side="left", padx=10, pady=10)
        
        self.theme_var = ctk.StringVar(value=self.settings.get("general", "theme", "system"))
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["system", "light", "dark"],
            command=self.on_theme_change
        )
        theme_menu.pack(side="left", padx=10, pady=10)
        
        # Taal selectie
        language_frame = ctk.CTkFrame(general_frame)
        language_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(language_frame, text="Taal:").pack(side="left", padx=10, pady=10)
        
        self.language_var = ctk.StringVar(value=self.settings.get("general", "language", "nl"))
        language_menu = ctk.CTkOptionMenu(
            language_frame,
            variable=self.language_var,
            values=["nl", "en", "fr", "de"]
        )
        language_menu.pack(side="left", padx=10, pady=10)
        
        # Checkboxes
        checkbox_frame = ctk.CTkFrame(general_frame)
        checkbox_frame.pack(fill="x", padx=15, pady=5)
        
        self.auto_update_var = ctk.BooleanVar(value=self.settings.get("general", "auto_update_check", True))
        auto_update_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Controleer automatisch op updates",
            variable=self.auto_update_var
        )
        auto_update_checkbox.pack(anchor="w", padx=10, pady=5)
        
        self.remember_folder_var = ctk.BooleanVar(value=self.settings.get("general", "remember_last_folder", True))
        remember_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Onthoud laatste mappen",
            variable=self.remember_folder_var
        )
        remember_checkbox.pack(anchor="w", padx=10, pady=5)
        
    def create_conversion_tab(self, parent):
        """Conversie instellingen"""
        conversion_frame = ctk.CTkFrame(parent)
        conversion_frame.pack(fill="x", pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            conversion_frame,
            text="Conversie Instellingen",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Standaard DPI
        dpi_frame = ctk.CTkFrame(conversion_frame)
        dpi_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(dpi_frame, text="Standaard DPI:").pack(side="left", padx=10, pady=10)
        
        self.default_dpi_var = ctk.StringVar(value=str(self.settings.get("conversion", "default_dpi", 300)))
        dpi_entry = ctk.CTkEntry(dpi_frame, textvariable=self.default_dpi_var, width=100)
        dpi_entry.pack(side="left", padx=10, pady=10)
        
        # Standaard formaat
        format_frame = ctk.CTkFrame(conversion_frame)
        format_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(format_frame, text="Standaard Formaat:").pack(side="left", padx=10, pady=10)
        
        self.default_format_var = ctk.StringVar(value=self.settings.get("conversion", "default_format", "PNG"))
        format_menu = ctk.CTkOptionMenu(
            format_frame,
            variable=self.default_format_var,
            values=["PNG", "JPG", "JPEG", "TIFF", "BMP"]
        )
        format_menu.pack(side="left", padx=10, pady=10)
        
        # Kwaliteit voor JPEG
        quality_frame = ctk.CTkFrame(conversion_frame)
        quality_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(quality_frame, text="JPEG Kwaliteit:").pack(side="left", padx=10, pady=10)
        
        self.quality_var = ctk.IntVar(value=self.settings.get("conversion", "quality", 95))
        quality_slider = ctk.CTkSlider(
            quality_frame,
            from_=50,
            to=100,
            variable=self.quality_var,
            width=200
        )
        quality_slider.pack(side="left", padx=10, pady=10)
        
        quality_label = ctk.CTkLabel(quality_frame, textvariable=self.quality_var)
        quality_label.pack(side="left", padx=5, pady=10)
        
        # Checkboxes
        checkbox_frame = ctk.CTkFrame(conversion_frame)
        checkbox_frame.pack(fill="x", padx=15, pady=5)
        
        self.preserve_metadata_var = ctk.BooleanVar(value=self.settings.get("conversion", "preserve_metadata", True))
        metadata_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Behoud metadata",
            variable=self.preserve_metadata_var
        )
        metadata_checkbox.pack(anchor="w", padx=10, pady=5)
        
        self.auto_open_var = ctk.BooleanVar(value=self.settings.get("conversion", "auto_open_output", False))
        auto_open_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Open output map automatisch",
            variable=self.auto_open_var
        )
        auto_open_checkbox.pack(anchor="w", padx=10, pady=5)
        
    def create_ui_tab(self, parent):
        """UI instellingen"""
        ui_frame = ctk.CTkFrame(parent)
        ui_frame.pack(fill="x", pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            ui_frame,
            text="Interface Instellingen",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Venster grootte
        size_frame = ctk.CTkFrame(ui_frame)
        size_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(size_frame, text="Venster Grootte:").pack(side="left", padx=10, pady=10)
        
        self.width_var = ctk.StringVar(value=str(self.settings.get("ui", "window_width", 700)))
        width_entry = ctk.CTkEntry(size_frame, textvariable=self.width_var, width=80)
        width_entry.pack(side="left", padx=5, pady=10)
        
        ctk.CTkLabel(size_frame, text="x").pack(side="left", padx=5, pady=10)
        
        self.height_var = ctk.StringVar(value=str(self.settings.get("ui", "window_height", 600)))
        height_entry = ctk.CTkEntry(size_frame, textvariable=self.height_var, width=80)
        height_entry.pack(side="left", padx=5, pady=10)
        
        # Checkboxes
        checkbox_frame = ctk.CTkFrame(ui_frame)
        checkbox_frame.pack(fill="x", padx=15, pady=5)
        
        self.show_preview_var = ctk.BooleanVar(value=self.settings.get("ui", "show_preview", True))
        preview_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Toon preview",
            variable=self.show_preview_var
        )
        preview_checkbox.pack(anchor="w", padx=10, pady=5)
        
        self.show_stats_var = ctk.BooleanVar(value=self.settings.get("ui", "show_stats", True))
        stats_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Toon statistieken",
            variable=self.show_stats_var
        )
        stats_checkbox.pack(anchor="w", padx=10, pady=5)
        
        self.compact_mode_var = ctk.BooleanVar(value=self.settings.get("ui", "compact_mode", False))
        compact_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Compacte modus",
            variable=self.compact_mode_var
        )
        compact_checkbox.pack(anchor="w", padx=10, pady=5)
        
    def create_advanced_tab(self, parent):
        """Geavanceerde instellingen"""
        advanced_frame = ctk.CTkFrame(parent)
        advanced_frame.pack(fill="x", pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            advanced_frame,
            text="Geavanceerde Instellingen",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Thread count
        thread_frame = ctk.CTkFrame(advanced_frame)
        thread_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(thread_frame, text="Thread Count (0 = auto):").pack(side="left", padx=10, pady=10)
        
        self.thread_count_var = ctk.StringVar(value=str(self.settings.get("advanced", "thread_count", 0)))
        thread_entry = ctk.CTkEntry(thread_frame, textvariable=self.thread_count_var, width=100)
        thread_entry.pack(side="left", padx=10, pady=10)
        
        # Memory limit
        memory_frame = ctk.CTkFrame(advanced_frame)
        memory_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(memory_frame, text="Memory Limit (MB):").pack(side="left", padx=10, pady=10)
        
        self.memory_limit_var = ctk.StringVar(value=str(self.settings.get("advanced", "memory_limit", 512)))
        memory_entry = ctk.CTkEntry(memory_frame, textvariable=self.memory_limit_var, width=100)
        memory_entry.pack(side="left", padx=10, pady=10)
        
        # Temp folder
        temp_frame = ctk.CTkFrame(advanced_frame)
        temp_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(temp_frame, text="Temp Map:").pack(side="left", padx=10, pady=10)
        
        self.temp_folder_var = ctk.StringVar(value=self.settings.get("advanced", "temp_folder", ""))
        temp_entry = ctk.CTkEntry(temp_frame, textvariable=self.temp_folder_var)
        temp_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        
        temp_button = ctk.CTkButton(
            temp_frame,
            text="Bladeren",
            command=self.browse_temp_folder,
            width=100
        )
        temp_button.pack(side="right", padx=5, pady=10)
        
    def on_theme_change(self, theme):
        """Thema wijziging handler"""
        ctk.set_appearance_mode(theme)
        # Update parent venster ook
        if hasattr(self.parent, 'settings'):
            self.parent.settings.set("general", "theme", theme)
        
    def browse_temp_folder(self):
        """Blader naar temp map"""
        folder = filedialog.askdirectory(title="Selecteer temp map")
        if folder:
            self.temp_folder_var.set(folder)
            
    def reset_settings(self):
        """Reset instellingen"""
        if messagebox.askyesno("Reset Instellingen", "Weet je zeker dat je alle instellingen wilt resetten naar standaard?"):
            self.settings.reset_to_defaults()
            self.close_window()
            self.show()  # Herlaad venster
            
    def export_settings(self):
        """Exporteer instellingen"""
        file_path = filedialog.asksaveasfilename(
            title="Exporteer Instellingen",
            defaultextension=".json",
            filetypes=[("JSON bestanden", "*.json"), ("Alle bestanden", "*.*")]
        )
        if file_path:
            if self.settings.export_settings(file_path):
                messagebox.showinfo("Succes", "Instellingen geëxporteerd!")
            else:
                messagebox.showerror("Fout", "Kon instellingen niet exporteren!")
                
    def import_settings(self):
        """Importeer instellingen"""
        file_path = filedialog.askopenfilename(
            title="Importeer Instellingen",
            filetypes=[("JSON bestanden", "*.json"), ("Alle bestanden", "*.*")]
        )
        if file_path:
            if self.settings.import_settings(file_path):
                messagebox.showinfo("Succes", "Instellingen geïmporteerd!")
                self.close_window()
                self.show()  # Herlaad venster
            else:
                messagebox.showerror("Fout", "Kon instellingen niet importeren!")
                
    def save_and_close(self):
        """Bewaar instellingen en sluit venster"""
        self.save_settings()
        self.close_window()
        
    def save_settings(self):
        """Bewaar alle instellingen"""
        # Algemene instellingen
        self.settings.set("general", "theme", self.theme_var.get())
        self.settings.set("general", "language", self.language_var.get())
        self.settings.set("general", "auto_update_check", self.auto_update_var.get())
        self.settings.set("general", "remember_last_folder", self.remember_folder_var.get())
        
        # Conversie instellingen
        self.settings.set("conversion", "default_dpi", int(self.default_dpi_var.get()))
        self.settings.set("conversion", "default_format", self.default_format_var.get())
        self.settings.set("conversion", "quality", self.quality_var.get())
        self.settings.set("conversion", "preserve_metadata", self.preserve_metadata_var.get())
        self.settings.set("conversion", "auto_open_output", self.auto_open_var.get())
        
        # UI instellingen
        self.settings.set("ui", "window_width", int(self.width_var.get()))
        self.settings.set("ui", "window_height", int(self.height_var.get()))
        self.settings.set("ui", "show_preview", self.show_preview_var.get())
        self.settings.set("ui", "show_stats", self.show_stats_var.get())
        self.settings.set("ui", "compact_mode", self.compact_mode_var.get())
        
        # Geavanceerde instellingen
        self.settings.set("advanced", "thread_count", int(self.thread_count_var.get()))
        self.settings.set("advanced", "memory_limit", int(self.memory_limit_var.get()))
        self.settings.set("advanced", "temp_folder", self.temp_folder_var.get())
        
    def close_window(self):
        """Sluit instellingen venster"""
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.window = None
            
    def center_window(self):
        """Centreer venster op scherm"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
