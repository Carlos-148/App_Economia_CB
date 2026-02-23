"""
Core.Pages.Gastos.gastos_tab - Gestión de gastos operacionales
"""

import tkinter as tk
from tkinter import messagebox, END, ttk

from Core.Common.logger import setup_logger
from Core.Backends.gastos_backend import GastosBackend
from Core.Common.units import get_unit_choices, convert_to_base
from Core.Backends.inventario_backend import InventarioBackend

logger = setup_logger()


class GastosTab(ttk.Frame):
    """Tab de gastos operacionales (productos y dinero)"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = setup_logger()
        self.backend = GastosBackend()
        self.inv_backend = InventarioBackend()
        self.product_info = {}
        
        self.setup_ui()
        self.reload_product_choices()
        self.load_recent_gastos()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # ============================================
        # TAB: GASTOS POR PRODUCTO
        # ============================================
        self.tab_product = ttk.Frame(notebook)
        notebook.add(self.tab_product, text="💸 Gastos por Producto")
        
        frm = ttk.Frame(self.tab_product, padding=10)
        frm.pack(fill=tk.X)
        
        ttk.Label(frm, text="Producto:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.prod_combo = ttk.Combobox(frm, values=[], state="readonly", width=30)
        self.prod_combo.grid(row=0, column=1, sticky=tk.W, pady=4)
        self.prod_combo.bind("<<ComboboxSelected>>", lambda e: self._recalculate_prod_total())
        
        ttk.Label(frm, text="Cantidad:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.prod_cant = ttk.Entry(frm, width=20)
        self.prod_cant.grid(row=1, column=1, sticky=tk.W, pady=4)
        self.prod_cant.bind("<KeyRelease>", lambda e: self._recalculate_prod_total())
        
        ttk.Label(frm, text="Unidad:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.prod_unidad = ttk.Combobox(frm, values=get_unit_choices(), state="readonly", width=20)
        self.prod_unidad.grid(row=2, column=1, sticky=tk.W, pady=4)
        self.prod_unidad.bind("<<ComboboxSelected>>", lambda e: self._recalculate_prod_total())
        
        ttk.Label(frm, text="Precio Total:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.prod_precio_var = tk.StringVar(value="$0.00")
        ttk.Entry(frm, textvariable=self.prod_precio_var, width=20, state="readonly").grid(row=3, column=1, sticky=tk.W, pady=4)
        
        ttk.Label(frm, text="Comentarios:").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.prod_comment = ttk.Entry(frm, width=50)
        self.prod_comment.grid(row=4, column=1, sticky=tk.W, pady=4)
        
        ttk.Button(frm, text="Registrar Gasto", command=self.on_add_gasto_producto).grid(row=5, column=0, columnspan=2, pady=10)
        
        # ============================================
        # TAB: GASTOS MONETARIOS OPERACIONALES
        # ============================================
        self.tab_money = ttk.Frame(notebook)
        notebook.add(self.tab_money, text="💰 Gastos Operacionales")
        
        frm2 = ttk.Frame(self.tab_money, padding=10)
        frm2.pack(fill=tk.X)
        
        ttk.Label(frm2, text="Descripción:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.money_desc = ttk.Entry(frm2, width=40)
        self.money_desc.grid(row=0, column=1, sticky=tk.W, pady=4)
        
        ttk.Label(frm2, text="Monto:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.money_amount = ttk.Entry(frm2, width=20)
        self.money_amount.grid(row=1, column=1, sticky=tk.W, pady=4)
        
        ttk.Label(frm2, text="Comentarios:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.money_comment = ttk.Entry(frm2, width=50)
        self.money_comment.grid(row=2, column=1, sticky=tk.W, pady=4)
        
        ttk.Button(frm2, text="Registrar Gasto", command=self.on_add_gasto_dinero).grid(row=3, column=0, columnspan=2, pady=10)
        
        # ============================================
        # HISTORIAL DE GASTOS
        # ============================================
        bottom = ttk.LabelFrame(main, text="📊 Gastos Recientes", padding=8)
        bottom.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        
        cols = ("Fecha", "Tipo", "Detalle", "Monto", "Comentarios")
        self.gastos_tree = ttk.Treeview(bottom, columns=cols, show="headings", height=8)
        
        for c in cols:
            self.gastos_tree.heading(c, text=c)
        
        self.gastos_tree.column("Fecha", width=160)
        self.gastos_tree.column("Tipo", width=120)
        self.gastos_tree.column("Detalle", width=280)
        self.gastos_tree.column("Monto", width=100, anchor=tk.E)
        self.gastos_tree.column("Comentarios", width=240)
        
        self.gastos_tree.pack(fill=tk.BOTH, expand=True)
    
    def reload_product_choices(self):
        """Recarga opciones de productos"""
        try:
            from Core.Common.database import get_connection, close_connection
            
            conn = get_connection()
            if not conn:
                return
            
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT producto, cantidad_stock, unidad_base, costo_promedio_ponderado FROM inventario WHERE cantidad_stock > 0"
                )
                rows = cursor.fetchall() or []
            
            close_connection(conn)
            
            prods = []
            self.product_info.clear()
            
            for r in rows:
                producto = r.get("producto")
                prods.append(producto)
                self.product_info[producto] = {
                    "cantidad_stock": float(r.get("cantidad_stock") or 0),
                    "unidad_base": (r.get("unidad_base") or "").lower(),
                    "costo_por_base": float(r.get("costo_promedio_ponderado") or 0),
                }
            
            self.prod_combo['values'] = prods
            if prods:
                self.prod_combo.set(prods[0])
            
            self._recalculate_prod_total()
            
        except Exception as e:
            self.logger.error(f"Error cargando productos: {e}")
    
    def _recalculate_prod_total(self):
        """Recalcula precio total del producto"""
        producto = self.prod_combo.get().strip()
        if not producto:
            self.prod_precio_var.set("$0.00")
            return
        
        info = self.product_info.get(producto)
        if not info:
            self.prod_precio_var.set("$0.00")
            return
        
        cantidad_str = self.prod_cant.get().strip()
        unidad_sel = self.prod_unidad.get().strip()
        
        if not cantidad_str or not unidad_sel:
            self.prod_precio_var.set("$0.00")
            return
        
        try:
            cantidad = float(cantidad_str)
            converted, _ = convert_to_base(cantidad, unidad_sel)
            
            if converted is None:
                self.prod_precio_var.set("$0.00")
                return
            
            costo_por_base = info.get("costo_por_base", 0.0)
            total = round(converted * costo_por_base, 2)
            self.prod_precio_var.set(f"${total:.2f}")
            
        except ValueError:
            self.prod_precio_var.set("$0.00")
    
    def on_add_gasto_producto(self):
        """Agrega gasto de producto"""
        producto = self.prod_combo.get().strip()
        cantidad = self.prod_cant.get().strip()
        unidad = self.prod_unidad.get().strip()
        comentario = self.prod_comment.get().strip()
        
        if not producto or not cantidad or not unidad:
            messagebox.showwarning("Aviso", "Completa todos los campos")
            return
        
        try:
            cantidad_f = float(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
            return
        
        info = self.product_info.get(producto)
        if not info:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        
        converted, _ = convert_to_base(cantidad_f, unidad)
        if converted is None:
            messagebox.showerror("Error", "No se pudo convertir la unidad")
            return
        
        precio_total = round(converted * info.get("costo_por_base", 0.0), 2)
        
        try:
            self.backend.add_gasto_producto(producto, cantidad_f, unidad, precio_total, comentario)
            messagebox.showinfo("✅ OK", "Gasto registrado y stock actualizado")
            
            self.prod_cant.delete(0, tk.END)
            self.prod_precio_var.set("$0.00")
            self.prod_comment.delete(0, tk.END)
            
            self.reload_product_choices()
            self.load_recent_gastos()
            
            logger.info(f"✅ Gasto de producto registrado: {producto} - ${precio_total:.2f}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            logger.error(f"Error registrando gasto de producto: {e}")
    
    def on_add_gasto_dinero(self):
        """Agrega gasto monetario"""
        desc = self.money_desc.get().strip()
        monto = self.money_amount.get().strip()
        comentario = self.money_comment.get().strip()
        
        if not desc or not monto:
            messagebox.showwarning("Aviso", "Completa todos los campos")
            return
        
        try:
            monto_f = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
            return
        
        try:
            self.backend.add_gasto_dinero(desc, monto_f, comentario)
            messagebox.showinfo("✅ OK", "Gasto monetario registrado")
            
            self.money_desc.delete(0, tk.END)
            self.money_amount.delete(0, tk.END)
            self.money_comment.delete(0, tk.END)
            
            self.load_recent_gastos()
            
            logger.info(f"✅ Gasto monetario registrado: {desc} - ${monto_f:.2f}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            logger.error(f"Error registrando gasto monetario: {e}")
    
    def load_recent_gastos(self):
        """Carga gastos recientes"""
        try:
            rows = self.backend.get_gastos_recientes(100)
            
            for i in self.gastos_tree.get_children():
                self.gastos_tree.delete(i)
            
            for r in rows:
                if r["type"] == "money":
                    detalle = r.get("descripcion", "")
                    monto = r.get("monto", 0)
                    tipo = "💵 Dinero"
                else:
                    detalle = f"{r.get('producto')} — {r.get('cantidad')}{r.get('unidad')}"
                    monto = r.get("monto", 0)
                    tipo = "📦 Producto"
                
                comentarios = r.get("comentarios", "") or ""
                
                self.gastos_tree.insert(
                    "",
                    tk.END,
                    values=(r.get("fecha"), tipo, detalle, f"${monto:.2f}", comentarios)
                )
        
        except Exception as e:
            self.logger.error(f"Error cargando gastos: {e}")