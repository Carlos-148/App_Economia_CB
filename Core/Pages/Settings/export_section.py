"""
Core.Pages.Settings.export_section - Sección de Exportes
Layout compacto
"""

import tkinter as tk
from tkinter import messagebox

from Core.Styles.base_components import BaseFrame, CardFrame
from Core.Common.constants import COLOR_INFO, COLOR_PRIMARY
from Core.Backends.settings_backend import SettingsBackend  # ✅ CORRECTO
from Core.Common.logger import setup_logger

logger = setup_logger()


class ExportSection(BaseFrame):
    """Sección de exportes"""
    
    def __init__(self, parent, theme_name="solar", backend: SettingsBackend = None):
        super().__init__(parent, theme_name=theme_name)
        self.backend = backend or SettingsBackend()  # ✅ CORRECTO
        self.logger = setup_logger()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        card = CardFrame(self, title="📊 EXPORTES", theme_name=self.theme_name)
        card.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = BaseFrame(card, theme_name=self.theme_name)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        tk.Button(
            button_frame,
            text="📤 Exportar",
            command=self.export_summary,
            bg=COLOR_INFO,
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4
        ).pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(
            button_frame,
            text="📁 Abrir Carpeta",
            command=self.open_exports,
            bg=COLOR_PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4
        ).pack(fill=tk.X)
    
    def export_summary(self):
        """Exporta resumen"""
        success, msg = self.backend.export_summary()
        
        if success:
            messagebox.showinfo("✅", msg)
        else:
            messagebox.showerror("❌", msg)
    
    def open_exports(self):
        """Abre carpeta"""
        success, msg = self.backend.open_exports_folder()
        
        if success:
            self.logger.info(msg)
        else:
            messagebox.showerror("❌", msg)