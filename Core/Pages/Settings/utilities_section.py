"""
Core.Pages.Settings.utilities_section - Sección de Utilidades
Layout compacto
"""

import tkinter as tk
from tkinter import messagebox

from Core.Styles.base_components import BaseFrame, CardFrame
from Core.Common.constants import COLOR_WARNING
from Core.Backends.settings_backend import SettingsBackend  # ✅ CORRECTO
from Core.Common.logger import setup_logger

logger = setup_logger()


class UtilitiesSection(BaseFrame):
    """Sección de utilidades"""
    
    def __init__(self, parent, theme_name="solar", backend: SettingsBackend = None):
        super().__init__(parent, theme_name=theme_name)
        self.backend = backend or SettingsBackend()  # ✅ CORRECTO
        self.logger = setup_logger()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        card = CardFrame(self, title="🛠️ UTILIDADES", theme_name=self.theme_name)
        card.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            card,
            text="🔄 Recargar App",
            command=self.reload_app,
            bg=COLOR_WARNING,
            fg="black",
            relief="flat",
            cursor="hand2",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4
        ).pack(fill=tk.X, padx=10, pady=(10, 10))
    
    def reload_app(self):
        """Recarga app"""
        if messagebox.askyesno(
            "🔄 Recargar",
            "¿Reiniciar la aplicación?"
        ):
            self.logger.info("🔄 Recargando...")
            self.backend.reload_application()