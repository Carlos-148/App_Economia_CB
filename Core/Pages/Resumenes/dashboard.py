"""
Core.Pages.Resumenes.dashboard - Dashboard con análisis
"""

import tkinter as tk
from tkinter import messagebox, END, ttk, messagebox
from datetime import datetime, timedelta

from Core.Backends.produccion_backend import ProduccionBackend
from Core.Common.logger import setup_logger

logger = setup_logger()


class DashboardTab(ttk.Frame):
    """Tab de dashboard con análisis"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = ProduccionBackend()
        self.logger = setup_logger()
        self.selected_subproducto_id = None
        self.setup_ui()
        self.load_subproductos()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main = ttk.Frame(self, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        control_frame = ttk.LabelFrame(main, text="⚙️ Controles")
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(control_frame, text="Subproducto:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.subproducto_combo = ttk.Combobox(control_frame, state="readonly", width=30)
        self.subproducto_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.subproducto_combo.bind("<<ComboboxSelected>>", lambda e: self.load_dashboard())
        
        ttk.Label(control_frame, text="Período:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.dias_combo = ttk.Combobox(control_frame, values=[7, 14, 30, 60, 90], state="readonly", width=10)
        self.dias_combo.set(30)
        self.dias_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.dias_combo.bind("<<ComboboxSelected>>", lambda e: self.load_dashboard())
        
        ttk.Button(control_frame, text="🔄 Actualizar", command=self.load_dashboard).pack(side=tk.LEFT)
        
        # Info
        info_frame = ttk.LabelFrame(main, text="📊 Información")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, height=15, width=80, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_subproductos(self):
        """Carga subproductos"""
        try:
            subs = self.backend.get_subproductos_disponibles()
            self.subproductos_info = {s['nombre']: s['id'] for s in subs}
            self.subproducto_combo['values'] = list(self.subproductos_info.keys())
            
            if self.subproductos_info:
                nombre_primero = list(self.subproductos_info.keys())[0]
                self.subproducto_combo.set(nombre_primero)
                self.selected_subproducto_id = self.subproductos_info[nombre_primero]
        except Exception as e:
            self.logger.error(f"Error cargando subproductos: {e}")
    
    def load_dashboard(self):
        """Carga dashboard"""
        nombre = self.subproducto_combo.get()
        
        if not nombre or nombre not in self.subproductos_info:
            return
        
        self.selected_subproducto_id = self.subproductos_info[nombre]
        dias = int(self.dias_combo.get())
        
        try:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            
            # Obtener producciones
            prods = self.backend.get_producciones_por_subproducto(self.selected_subproducto_id, dias)
            
            if not prods:
                self.info_text.insert(tk.END, "Sin datos en este período")
            else:
                texto = f"📊 Dashboard: {nombre}\n"
                texto += f"Período: últimos {dias} días\n"
                texto += f"Producciones: {len(prods)}\n\n"
                
                total_unidades = sum(p['unidades_producidas'] for p in prods)
                total_costo = sum(float(p['costo_total_masa']) for p in prods)
                
                texto += f"Total Unidades: {total_unidades}\n"
                texto += f"Costo Total: ${total_costo:.2f}\n"
                texto += f"Costo Promedio/Unidad: ${total_costo/total_unidades:.4f}\n\n"
                
                texto += "Producciones:\n"
                texto += "-" * 60 + "\n"
                
                for p in prods:
                    texto += f"Fecha: {p['created_at']} | Unidades: {p['unidades_producidas']} | Costo: ${p['costo_total_masa']:.2f}\n"
                
                self.info_text.insert(tk.END, texto)
            
            self.info_text.config(state=tk.DISABLED)
        
        except Exception as e:
            self.logger.error(f"Error cargando dashboard: {e}")
            messagebox.showerror("Error", f"Error: {e}")