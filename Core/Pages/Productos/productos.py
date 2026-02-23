"""
Core.Pages.Productos.productos - Tab de productos
"""

import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import BOTH, LEFT, RIGHT

from Core.Pages.Productos.precios_tab import PreciosTab
from Core.Common.logger import setup_logger
from Core.Styles.base_components import BaseFrame, StyledLabel

logger = setup_logger()


class ProductosFrame(BaseFrame):
    """Frame de gestión de productos"""
    
    def __init__(self, parent):
        from Core.Common.config import load_config
        config = load_config()
        theme = config.get("theme", "solar")
        
        super().__init__(parent, theme_name=theme)
        
        self.logger = setup_logger()
        
        # Header
        title = StyledLabel(
            self,
            text="📦 Gestión de Productos Finales",
            label_type="title",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 20), padx=20)
        
        # Notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Tab Precios
        self.precios_tab = PreciosTab(notebook)
        notebook.add(self.precios_tab, text="💰 Precios")