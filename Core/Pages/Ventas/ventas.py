"""
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
Core.Pages.Ventas.ventas - Interfaz de gestión de ventas
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
"""
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH

from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
import tkinter as tk
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
import tkinter as tk
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
from tkinter import messagebox, END, ttk
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
from ttkbootstrap import Notebook
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH

from Core.Pages.Ventas.clientes_tab import ClientesTab
from Core.Pages.Ventas.registro_tab import RegistrarVentaTab
from Core.Pages.Ventas.history_tab import HistorialTab
from Core.Backends.ventas_backend import VentasBackend
from Core.Common.logger import setup_logger

logger = setup_logger()


class VentasFrame(ttk.Frame):
    """Frame de gestión de ventas"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = VentasBackend()
        self.logger = setup_logger()
        self.setup_ui()
        
        self.clientes_tab = ClientesTab(self.notebook, self.backend)
        self.notebook.add(self.clientes_tab, text="👥 Clientes")
        
        self.registrar_tab = RegistrarVentaTab(self.notebook, self.backend)
        self.notebook.add(self.registrar_tab, text="💳 Registrar Venta")
        
        self.historial_tab = HistorialTab(self.notebook, self.backend)
        self.notebook.add(self.historial_tab, text="📋 Historial")
    
    def setup_ui(self):
        """Configura la interfaz"""
        self.notebook = Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)