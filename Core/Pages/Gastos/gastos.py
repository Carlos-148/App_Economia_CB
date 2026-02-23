"""
Core.Pages.Gastos.gastos - Interfaz de gestión de gastos y efectivo
Estructura modular con tabs separadas
"""

import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import BOTH

from Core.Pages.Gastos.efectivo_tab import EfectivoTab
from Core.Pages.Gastos.gastos_tab import GastosTab
from Core.Common.logger import setup_logger
from Core.Styles.base_components import BaseFrame, StyledLabel

logger = setup_logger()


class GastosFrame(BaseFrame):
    """Frame principal de gestión de gastos y efectivo"""
    
    def __init__(self, parent):
        from Core.Common.config import load_config
        config = load_config()
        theme = config.get("theme", "solar")
        
        super().__init__(parent, theme_name=theme)
        self.logger = setup_logger()
        
        # Título principal
        title = StyledLabel(
            self,
            text="💸 GESTIÓN DE GASTOS Y EFECTIVO",
            label_type="title",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 20), padx=20)
        
        # Notebook con tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # ============================================
        # TAB 1: CAJA / EFECTIVO (Principal)
        # ============================================
        self.efectivo_tab = EfectivoTab(notebook)
        notebook.add(self.efectivo_tab, text="💰 Caja / Efectivo")
        
        # ============================================
        # TAB 2: GASTOS OPERACIONALES
        # ============================================
        self.gastos_tab = GastosTab(notebook)
        notebook.add(self.gastos_tab, text="💸 Gastos Operacionales")
        
        logger.info("✅ GastosFrame inicializado con tabs separadas")