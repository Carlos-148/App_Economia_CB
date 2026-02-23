"""
Core.Pages.Productos.precios_tab - Tab de precios
Corrección: Tomar datos de PRODUCTOS FINALES, no subproductos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from Core.Backends.produccion_backend import ProduccionBackend
from Core.Common.logger import setup_logger

logger = setup_logger()


class PreciosTab(ttk.Frame):
    tab_name = "Precios"

    def __init__(self, parent):
        super().__init__(parent)
        self.backend = ProduccionBackend()  # ✅ Usar ProduccionBackend
        self.editing_entry = None
        self.column_ids = ("Producto", "Costo/U", "Precio Venta", "Ganancia", "% Ganancia")
        self.product_ids = {}  # Mapeo de producto a ID
        self.setup_ui()
        self.load_precios()

    def setup_ui(self):
        """Configura la interfaz"""
        precios_frame = ttk.Frame(self)
        precios_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(
            precios_frame,
            text="💰 Precios de Productos Finales",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=5)

        columns = self.column_ids
        self.precios_tree = ttk.Treeview(
            precios_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        for c in columns:
            self.precios_tree.heading(c, text=c)
        
        self.precios_tree.column("Producto", width=250)
        self.precios_tree.column("Costo/U", width=120, anchor=tk.E)
        self.precios_tree.column("Precio Venta", width=140, anchor=tk.E)
        self.precios_tree.column("Ganancia", width=120, anchor=tk.E)
        self.precios_tree.column("% Ganancia", width=120, anchor=tk.E)
        
        self.precios_tree.pack(fill=tk.BOTH, expand=True)

        # Bind doble click
        self.precios_tree.bind("<Double-1>", self.on_double_click)

        # Frame de botones
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10, fill=tk.X)

        tk.Button(
            btn_frame,
            text="🔄 Actualizar",
            command=self.load_precios,
            bg="#17a2b8",
            fg="white",
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="💡 Instrucciones",
            command=self.show_instructions,
            bg="#28a745",
            fg="white",
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

    def show_instructions(self):
        """Muestra instrucciones"""
        msg = """
📋 INSTRUCCIONES - PRECIOS DE PRODUCTOS FINALES

1. VISUALIZAR:
   • Ve los productos finales creados en la pestaña de Producción
   • Cada fila muestra:
     - Costo/U: Costo calculado automáticamente
     - Precio Venta: Precio que define el vendedor
     - Ganancia: Diferencia (Precio - Costo)
     - % Ganancia: Porcentaje de ganancia

2. EDITAR PRECIO:
   • Haz doble click en la columna "Precio Venta"
   • Ingresa el nuevo precio
   • Presiona ENTER para guardar

3. EJEMPLO:
   • Producto: Dona Glaseada
   • Costo/U: $13.82 (calculado)
   • Precio Venta: (vacío = ingresa precio)
   • Al ingresar $20, Ganancia = $6.18, % = 44.8%

✅ Solo edita precios de productos finales que hayas creado.
        """
        messagebox.showinfo("ℹ️ Instrucciones", msg)

    def load_precios(self):
        """Carga PRODUCTOS FINALES con sus precios"""
        try:
            # ✅ Obtener información de PRODUCTOS FINALES
            productos_finales = self.backend.get_productos_finales_info()
            
            # Limpiar tabla
            for i in self.precios_tree.get_children():
                self.precios_tree.delete(i)
            
            self.product_ids.clear()
            
            logger.info(f"📊 Cargando {len(productos_finales)} productos finales")
            
            for p in productos_finales:
                pid = p.get("id")
                nombre = p.get("nombre", "N/A")
                
                # ✅ IMPORTANTE: Usar costo_unitario_total (costo del producto final)
                costo_unitario = float(p.get("costo_unitario_total", 0) or 0)
                
                # Precio de venta puede estar vacío
                precio_venta = p.get("precio_venta")
                precio_venta_float = float(precio_venta) if precio_venta is not None and precio_venta != 0 else 0.0
                
                # Calcular ganancia
                if precio_venta_float > 0:
                    ganancia = round(precio_venta_float - costo_unitario, 2)
                    pct_ganancia = round((ganancia / costo_unitario * 100), 2) if costo_unitario > 0 else 0
                    ganancia_display = f"${ganancia:.2f}"
                    pct_display = f"{pct_ganancia:.2f}%"
                else:
                    ganancia_display = "-"
                    pct_display = "-"
                
                # Guardar mapping
                self.product_ids[str(pid)] = pid
                
                # Insertar fila
                self.precios_tree.insert(
                    "",
                    tk.END,
                    iid=str(pid),
                    values=(
                        nombre,
                        f"${costo_unitario:.2f}",
                        f"${precio_venta_float:.2f}" if precio_venta_float > 0 else "(sin precio)",
                        ganancia_display,
                        pct_display
                    ),
                    tags=("sin_precio",) if precio_venta_float == 0 else ()
                )
            
            # Estilo para productos sin precio
            self.precios_tree.tag_configure("sin_precio", foreground="#FFC107")
            
            logger.info(f"✅ {len(productos_finales)} productos cargados")
        
        except Exception as e:
            logger.error(f"❌ Error cargando precios: {e}")
            messagebox.showerror("Error", f"Error cargando precios: {str(e)[:100]}")

    def _start_edit_cell(self, item_id, col_name, bbox):
        """Inicia edición de celda"""
        if self.editing_entry:
            try:
                self.editing_entry.destroy()
            except Exception:
                pass
            self.editing_entry = None

        # Obtener valor actual
        cur_values = self.precios_tree.item(item_id, "values")
        col_index = self.column_ids.index(col_name)
        cur_text = cur_values[col_index] if col_index < len(cur_values) else ""
        
        # Remover $ si existe
        if isinstance(cur_text, str):
            cur_text = cur_text.replace("$", "").replace("(sin precio)", "").strip()

        x, y, width, height = bbox
        entry = tk.Entry(self.precios_tree, font=("Segoe UI", 10))
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, cur_text)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def finish_edit(event=None):
            new_text = entry.get().strip()
            
            try:
                # ✅ Convertir a float
                new_price = float(new_text) if new_text else 0.0
            except ValueError:
                messagebox.showwarning("Valor inválido", "Por favor ingresa un número válido")
                entry.focus_set()
                return
            
            # Guardar en BD
            try:
                product_id = self.product_ids.get(item_id)
                if not product_id:
                    messagebox.showerror("Error", "ID de producto no encontrado")
                    entry.destroy()
                    self.editing_entry = None
                    return
                
                self.backend.set_precio_venta(product_id, new_price)
                logger.info(f"✅ Precio actualizado: ${new_price:.2f}")
            
            except Exception as e:
                logger.error(f"❌ Error guardando: {e}")
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)[:100]}")
                entry.destroy()
                self.editing_entry = None
                return
            
            # Actualizar fila
            try:
                vals = list(self.precios_tree.item(item_id, "values"))
                
                # Obtener costo
                costo_str = vals[1].replace("$", "").strip()
                costo = float(costo_str)
                
                # Calcular ganancia
                ganancia = round(new_price - costo, 2)
                pct = round((ganancia / costo * 100), 2) if costo > 0 else 0
                
                # Actualizar valores
                vals[2] = f"${new_price:.2f}"
                vals[3] = f"${ganancia:.2f}"
                vals[4] = f"{pct:.2f}%"
                
                self.precios_tree.item(item_id, values=vals, tags=())
                
                messagebox.showinfo("✅ Éxito", f"Precio actualizado a ${new_price:.2f}")
            
            except Exception as e:
                logger.error(f"Error actualizando fila: {e}")
            
            entry.destroy()
            self.editing_entry = None

        entry.bind("<Return>", finish_edit)
        entry.bind("<Escape>", lambda e: entry.destroy())
        entry.bind("<FocusOut>", finish_edit)
        
        self.editing_entry = entry

    def on_double_click(self, event):
        """Maneja doble click para editar"""
        region = self.precios_tree.identify("region", event.x, event.y)
        
        if region != "cell":
            return
        
        col = self.precios_tree.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1
        
        if col_index < 0 or col_index >= len(self.column_ids):
            return
        
        col_name = self.column_ids[col_index]
        
        # Solo permitir editar "Precio Venta"
        if col_name != "Precio Venta":
            messagebox.showinfo("ℹ️", "Solo puedes editar la columna 'Precio Venta'")
            return
        
        rowid = self.precios_tree.identify_row(event.y)
        
        if not rowid:
            return
        
        bbox = self.precios_tree.bbox(rowid, column=col)
        
        if not bbox:
            return
        
        self._start_edit_cell(rowid, col_name, bbox)