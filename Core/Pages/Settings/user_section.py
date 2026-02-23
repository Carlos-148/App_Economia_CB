"""
Core.Pages.Settings.user_section - Sección de Usuario
Usa configuración centralizada
"""

import tkinter as tk
from tkinter import messagebox

from Core.Styles.base_components import BaseFrame, StyledLabel, CardFrame
from Core.Backends.settings_backend import SettingsBackend
from Core.Common.logger import setup_logger
from Core.Pages.Settings.settings_config import USER_SECTION, LAYOUT

logger = setup_logger()


class UserSection(BaseFrame):
    """Sección de usuario y capital"""
    
    def __init__(self, parent, theme_name="solar", backend: SettingsBackend = None):
        super().__init__(parent, theme_name=theme_name)
        self.backend = backend or SettingsBackend()
        self.logger = setup_logger()
        self.config = USER_SECTION
        
        self.setup_ui()
        self.load_values()
    
    def setup_ui(self):
        """Configura la interfaz"""
        card = CardFrame(self, title=self.config['title'], theme_name=self.theme_name)
        card.pack(fill=tk.X, pady=LAYOUT['card_pady'])
        
        # Nombre
        name_frame = BaseFrame(card, theme_name=self.theme_name)
        name_frame.pack(fill=tk.X, padx=10, pady=(10, 6))
        
        tk.Label(
            name_frame, 
            text=self.config['name_label'], 
            font=("Segoe UI", 9), 
            bg=self.bg_color
        ).pack(side=tk.LEFT, anchor="w")
        
        self.entry_name = tk.Entry(name_frame, font=("Segoe UI", 9))
        self.entry_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Capital
        capital_frame = BaseFrame(card, theme_name=self.theme_name)
        capital_frame.pack(fill=tk.X, padx=10, pady=(0, 6))
        
        tk.Label(
            capital_frame, 
            text=self.config['capital_label'], 
            font=("Segoe UI", 9), 
            bg=self.bg_color
        ).pack(side=tk.LEFT, anchor="w")
        
        self.entry_capital = tk.Entry(
            capital_frame, 
            font=("Segoe UI", 9),
            state=tk.DISABLED
        )
        self.entry_capital.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Info
        info_label = StyledLabel(
            card,
            text=self.config['info_text'],
            label_type="small",
            theme_name=self.theme_name
        )
        info_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Botón
        tk.Button(
            card,
            text=self.config['button_save'],
            command=self.save_user,
            bg="#198754",
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4
        ).pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def load_values(self):
        try:
            user_config = self.backend.get_user_config()
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, user_config.get("name", ""))
            
            self.entry_capital.config(state=tk.NORMAL)
            self.entry_capital.delete(0, tk.END)
            self.entry_capital.insert(0, str(user_config.get("capital", 0.0)))
            self.entry_capital.config(state=tk.DISABLED)
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
    def save_user(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Validación", "Ingresa un nombre")
            return
        
        success, msg = self.backend.save_user_config(name, 0.0)
        if success:
            messagebox.showinfo("✅", msg)
        else:
            messagebox.showerror("❌", msg)