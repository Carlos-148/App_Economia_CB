"""
Core.Pages.Settings.theme_section - Sección de Temas
Layout compacto
"""

import tkinter as tk
from tkinter import messagebox

from Core.Styles.base_components import BaseFrame, StyledLabel, StyledCombobox, CardFrame
from Core.Common.constants import COLOR_SUCCESS
from Core.Backends.settings_backend import SettingsBackend  # ✅ CORRECTO
from Core.Common.logger import setup_logger

logger = setup_logger()


class ThemeSection(BaseFrame):
    """Sección de gestión de temas"""
    
    def __init__(self, parent, theme_name="solar", backend: SettingsBackend = None):
        super().__init__(parent, theme_name=theme_name)
        self.backend = backend or SettingsBackend()  # ✅ CORRECTO
        self.logger = setup_logger()
        
        self.setup_ui()
        self.load_values()
    
    def setup_ui(self):
        """Configura la interfaz"""
        card = CardFrame(self, title="🎨 TEMAS", theme_name=self.theme_name)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # === Temas oficiales ===
        label1 = StyledLabel(
            card,
            text="Tema Oficial:",
            label_type="small",
            theme_name=self.theme_name
        )
        label1.pack(anchor="w", padx=10, pady=(10, 4))
        
        theme_frame = BaseFrame(card, theme_name=self.theme_name)
        theme_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        self.theme_combo = StyledCombobox(
            theme_frame,
            values=self.backend.get_valid_themes(),
            state="readonly",
            width=18,
            theme_name=self.theme_name
        )
        self.theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            theme_frame,
            text="✅",
            command=self.apply_theme,
            bg=COLOR_SUCCESS,
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            width=3,
            padx=5,
            pady=2
        ).pack(side=tk.LEFT)
        
        # === Presets ===
        label2 = StyledLabel(
            card,
            text="Preset:",
            label_type="small",
            theme_name=self.theme_name
        )
        label2.pack(anchor="w", padx=10, pady=(8, 4))
        
        preset_frame = BaseFrame(card, theme_name=self.theme_name)
        preset_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.preset_combo = StyledCombobox(
            preset_frame,
            values=self.backend.get_theme_presets(),
            state="readonly",
            width=18,
            theme_name=self.theme_name
        )
        self.preset_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            preset_frame,
            text="✅",
            command=self.apply_preset,
            bg=COLOR_SUCCESS,
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            width=3,
            padx=5,
            pady=2
        ).pack(side=tk.LEFT)
    
    def load_values(self):
        """Carga valores"""
        current = self.backend.get_current_theme()
        self.theme_combo.set(current)
    
    def apply_theme(self):
        """Aplica tema"""
        theme = self.theme_combo.get().strip()
        
        if not theme:
            messagebox.showwarning("Aviso", "Selecciona un tema")
            return
        
        success, msg = self.backend.save_theme(theme)
        
        if success:
            messagebox.showinfo("✅", "Recarga la app para aplicar")
        else:
            messagebox.showerror("❌", msg)
    
    def apply_preset(self):
        """Aplica preset"""
        preset = self.preset_combo.get().strip()
        
        if not preset:
            messagebox.showwarning("Aviso", "Selecciona un preset")
            return
        
        success, msg = self.backend.apply_preset(preset)
        
        if success:
            messagebox.showinfo("✅", msg)
        else:
            messagebox.showerror("❌", msg)