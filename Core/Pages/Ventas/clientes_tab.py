"""
Core.Pages.Ventas.clientes_tab - Gestión de clientes
"""

import tkinter as tk
import tkinter as tk
from tkinter import messagebox, END, ttk, messagebox
from Core.Common.logger import setup_logger

logger = setup_logger()


class ClientesTab(ttk.Frame):
    """Tab de gestión de clientes"""
    
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        self.setup_ui()
        self.load_clients()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear cliente
        create_frame = ttk.Frame(main)
        create_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(create_frame, text="Nuevo cliente:").pack(side=tk.LEFT)
        self.new_client_entry = ttk.Entry(create_frame)
        self.new_client_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(create_frame, text="Crear", command=self.create_client).pack(side=tk.LEFT, padx=5)
        
        # Clientes list
        mid = ttk.Frame(main)
        mid.pack(fill=tk.BOTH, expand=True)
        
        cols = ("Nombre", "Estado")
        self.clients_tree = ttk.Treeview(mid, columns=cols, show="headings", height=15)
        
        self.clients_tree.heading("Nombre", text="Nombre")
        self.clients_tree.heading("Estado", text="Estado")
        self.clients_tree.column("Nombre", width=220)
        self.clients_tree.column("Estado", width=80, anchor=tk.CENTER)
        
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clients_tree.bind("<<TreeviewSelect>>", self.on_client_select)
        
        scrollbar = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Stats
        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        ttk.Label(right, text="Estadísticas", font=("Segoe UI", 12, "bold")).pack(pady=(0, 5))
        self.stats_label = ttk.Label(right, text="Selecciona un cliente")
        self.stats_label.pack(pady=5)
        
        self.toggle_btn = ttk.Button(right, text="Activar/Inactivar", command=self.toggle_active, state=tk.DISABLED)
        self.toggle_btn.pack(pady=5)
        
        ttk.Label(right, text="Ventas por día", font=("Segoe UI", 11, "bold")).pack(pady=(10, 5))
        
        self.ventas_tree = ttk.Treeview(right, columns=("Fecha", "Ventas", "Total"), show="headings", height=8)
        self.ventas_tree.heading("Fecha", text="Fecha")
        self.ventas_tree.heading("Ventas", text="Ventas")
        self.ventas_tree.heading("Total", text="Total")
        self.ventas_tree.column("Fecha", width=120)
        self.ventas_tree.column("Ventas", width=60, anchor=tk.E)
        self.ventas_tree.column("Total", width=80, anchor=tk.E)
        self.ventas_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_clients(self):
        """Carga clientes"""
        try:
            rows = self.backend.get_clientes()
            
            for i in self.clients_tree.get_children():
                self.clients_tree.delete(i)
            
            for r in rows:
                active = r.get("active", 1)
                self.clients_tree.insert(
                    "",
                    tk.END,
                    iid=str(r["id"]),
                    values=(r["nombre"], "✅ Activo" if active else "❌ Inactivo")
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def create_client(self):
        """Crea un cliente"""
        name = self.new_client_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Aviso", "Ingresa nombre")
            return
        
        try:
            self.backend.add_cliente(name)
            self.new_client_entry.delete(0, tk.END)
            self.load_clients()
            messagebox.showinfo("OK", "Cliente creado")
        except ValueError as ve:
            messagebox.showwarning("Aviso", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def on_client_select(self, _evt):
        """Selecciona un cliente"""
        selected = self.clients_tree.selection()
        
        if not selected:
            self.toggle_btn.config(state=tk.DISABLED)
            return
        
        cliente_id = int(selected[0])
        self.toggle_btn.config(state=tk.NORMAL)
        
        stats = self.backend.get_cliente_stats(cliente_id)
        self.stats_label.config(
            text=f"Compras: {stats['purchases_count']} | Total: ${stats['total_revenue']:.2f}"
        )
        
        ventas = self.backend.get_ventas_por_dia(cliente_id)
        
        for i in self.ventas_tree.get_children():
            self.ventas_tree.delete(i)
        
        for v in ventas:
            self.ventas_tree.insert(
                "",
                tk.END,
                values=(v["day"], v["sales_count"], f"${v['total_sum']:.2f}")
            )
    
    def toggle_active(self):
        """Alterna estado de cliente"""
        selected = self.clients_tree.selection()
        
        if not selected:
            return
        
        cliente_id = int(selected[0])
        
        try:
            new_state = self.backend.toggle_cliente_active(cliente_id)
            self.load_clients()
            
            state_text = "Activo" if new_state == 1 else "Inactivo"
            messagebox.showinfo("OK", f"Cliente ahora: {state_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")