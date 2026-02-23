"""
Core.Pages.Produccion.produccion - Interfaz completa de producción
Con tab de productos finales mejorada
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, END, ttk
from ttkbootstrap import Radiobutton, StringVar, Notebook, Treeview
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
from decimal import Decimal

from Core.Backends.produccion_backend import ProduccionBackend
from Core.Backends.inventario_backend import InventarioBackend
from Core.Common.database import get_connection, close_connection
from Core.Common.logger import setup_logger
from Core.Common.units import get_unit_choices
from Core.Common.constants import COLOR_SUCCESS, COLOR_PRIMARY, COLOR_INFO, COLOR_DANGER
from Core.Styles.modern_styles import ModernStyleManager
from Core.Styles.base_components import (
    BaseFrame, StyledLabel, StyledEntry, StyledCombobox,
    CardFrame, FormRow
)

logger = setup_logger()


class ProduccionFrame(BaseFrame):
    """Frame de gestión de producción con interfaz mejorada"""
    
    def __init__(self, parent):
        from Core.Common.config import load_config
        config = load_config()
        theme = config.get("theme", "solar")
        
        super().__init__(parent, theme_name=theme)
        
        self.backend = ProduccionBackend()
        self.inv_backend = InventarioBackend()
        self.logger = setup_logger()
        
        ModernStyleManager.configure_modern_styles(self.winfo_toplevel().style, theme)
        
        self.subproductos_map = {}
        self.selected_subproducto_id = None
        self.producciones_cache = {}
        
        self.setup_ui()
        self.reload_inventario()
        self.load_subproductos()
        self.load_productos_finales()
    
    def setup_ui(self):
        """Configura la interfaz completa"""
        
        title = StyledLabel(
            self,
            text="🏭 Gestión de Producción",
            label_type="title",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 20), padx=20)
        
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # TAB 1: PRODUCTOS FINALES
        self.tab_productos_finales = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(self.tab_productos_finales, text="📦 Productos Finales")
        self._setup_productos_finales_tab()
        
        # TAB 2: CREAR SUBPRODUCTOS
        self.tab_crear_sub = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(self.tab_crear_sub, text="⚙️ Crear / Producir Subproductos")
        self._setup_subproductos_tab()
    
    # ============================================
    # TAB 1: PRODUCTOS FINALES
    # ============================================
    
    def _setup_productos_finales_tab(self):
        """Configura tab de productos finales"""
        
        header = BaseFrame(self.tab_productos_finales, theme_name=self.theme_name)
        header.pack(fill=X, padx=10, pady=(10, 15))
        
        title = StyledLabel(
            header,
            text="📦 Gestión de Productos Finales",
            label_type="heading",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 10))
        
        btn_frame = BaseFrame(header, theme_name=self.theme_name)
        btn_frame.pack(fill=X)
        
        tk.Button(
            btn_frame,
            text="➕ Crear Nuevo Producto Final",
            command=self.open_create_product_dialog,
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=8
        ).pack(side=LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Actualizar",
            command=self.load_productos_finales,
            bg=COLOR_INFO, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=8
        ).pack(side=LEFT, padx=5)
        
        # Tabla
        cols_pf = ("ID", "Producto", "Subproductos", "Costo/U", "Precio Venta", "Margen")
        self.pf_tree = Treeview(
            self.tab_productos_finales,
            columns=cols_pf,
            show="headings",
            height=15
        )
        
        for c in cols_pf:
            self.pf_tree.heading(c, text=c)
            if c == "Producto":
                self.pf_tree.column(c, width=200)
            elif c == "Subproductos":
                self.pf_tree.column(c, width=250)
            else:
                self.pf_tree.column(c, width=120)
        
        self.pf_tree.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.pf_tree.bind("<Button-1>", lambda e: self._on_product_click(e))
        
        # Panel de detalles
        self._create_product_details_panel()
    
    def _create_product_details_panel(self):
        """Panel de detalles"""
        
        details_frame = CardFrame(
            self.tab_productos_finales,
            title="📋 Detalles",
            theme_name=self.theme_name
        )
        details_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.details_text = tk.Text(
            details_frame,
            height=6,
            width=80,
            wrap=tk.WORD,
            bg="white",
            relief="solid",
            bd=1,
            font=("Segoe UI", 10),
            state=tk.DISABLED
        )
        self.details_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
    
    def _on_product_click(self, event):
        """Muestra detalles del producto"""
        item = self.pf_tree.selection()
        
        if not item:
            return
        
        values = self.pf_tree.item(item[0], 'values')
        
        if len(values) >= 3:
            detalles = f"""
╔══════════════════════════════════════════════════════════════╗
║  DETALLES DEL PRODUCTO FINAL
╚══════════════════════════════════════════════════════════════╝

📌 Nombre: {values[1]}

🧪 Subproductos:
   {values[2]}

💰 Información de Costos:
   • Costo por Unidad: {values[3]}
   • Precio de Venta: {values[4]}
   • Margen de Ganancia: {values[5]}

✅ Este producto está listo para ser vendido.
   Ve a la pestaña de "Precios" para ajustar el precio de venta.
            """
            
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, detalles)
            self.details_text.config(state=tk.DISABLED)
    
    def open_create_product_dialog(self):
        """Abre diálogo para crear producto final"""
        
        win = tk.Toplevel(self)
        win.title("➕ Crear Producto Final")
        win.geometry("900x700")
        win.transient(self.winfo_toplevel())
        win.grab_set()
        
        win.configure(bg=self.bg_color)
        
        main_frame = BaseFrame(win, theme_name=self.theme_name)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        title = StyledLabel(
            main_frame,
            text="Crear Nuevo Producto Final",
            label_type="heading",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 20))
        
        # Nombre
        name_card = CardFrame(main_frame, title="📝 Información", theme_name=self.theme_name)
        name_card.pack(fill=X, pady=(0, 15))
        
        name_label = StyledLabel(
            name_card,
            text="Nombre del Producto Final:",
            label_type="normal",
            theme_name=self.theme_name
        )
        name_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        name_entry = StyledEntry(name_card, theme_name=self.theme_name, width=40)
        name_entry.pack(fill=X, padx=10, pady=(0, 10))
        
        # Subproductos
        sub_card = CardFrame(main_frame, title="🧪 Seleccionar Subproductos", theme_name=self.theme_name)
        sub_card.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Obtener producciones
        producciones_disponibles = self._get_producciones_disponibles()
        
        if not producciones_disponibles:
            info_label = StyledLabel(
                sub_card,
                text="⚠️ No hay producciones disponibles. Produce subproductos primero.",
                label_type="normal",
                theme_name=self.theme_name
            )
            info_label.pack(padx=10, pady=20)
            
            tk.Button(
                main_frame,
                text="❌ Cerrar",
                command=win.destroy,
                bg="#6c757d", fg="white", relief="flat", cursor="hand2", bd=0
            ).pack(pady=10)
            
            return
        
        # Grid
        grid_frame = BaseFrame(sub_card, theme_name=self.theme_name)
        grid_frame.pack(fill=X, padx=10, pady=(10, 10))
        
        StyledLabel(grid_frame, text="Subproducto", label_type="small", theme_name=self.theme_name).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        StyledLabel(grid_frame, text="Unidades Producidas", label_type="small", theme_name=self.theme_name).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )
        StyledLabel(grid_frame, text="Costo/U", label_type="small", theme_name=self.theme_name).grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        StyledLabel(grid_frame, text="Incluir", label_type="small", theme_name=self.theme_name).grid(
            row=0, column=3, sticky="w", padx=5, pady=5
        )
        
        grid_frame.columnconfigure(0, weight=1)
        
        selected_subproductos = {}
        
        for idx, prod in enumerate(producciones_disponibles, start=1):
            sub_name = prod['nombre']
            unidades_producidas = prod['unidades_producidas']  # ✅ IMPORTANTE
            costo_unitario = prod['costo_unitario']
            
            tk.Label(
                grid_frame,
                text=sub_name,
                font=("Segoe UI", 10),
                bg=self.bg_color
            ).grid(row=idx, column=0, sticky="w", padx=5, pady=8)
            
            # ✅ MOSTRAR las unidades que se produjeron
            tk.Label(
                grid_frame,
                text=f"{unidades_producidas} unidades",
                font=("Segoe UI", 10),
                bg=self.bg_color
            ).grid(row=idx, column=1, sticky="w", padx=5, pady=8)
            
            tk.Label(
                grid_frame,
                text=f"${costo_unitario:.2f}",
                font=("Segoe UI", 10, "bold"),
                fg=COLOR_SUCCESS,
                bg=self.bg_color
            ).grid(row=idx, column=2, sticky="w", padx=5, pady=8)
            
            var = tk.BooleanVar()
            tk.Checkbutton(
                grid_frame,
                variable=var,
                bg=self.bg_color
            ).grid(row=idx, column=3, sticky="w", padx=5, pady=8)
            
            selected_subproductos[sub_name] = {
                'var': var,
                'costo_unitario': costo_unitario,
                'subproducto_id': prod['subproducto_id'],
                'unidades_producidas': unidades_producidas  # ✅ GUARDAR ESTO
            }
        
        # Resumen
        summary_card = CardFrame(main_frame, title="📊 Resumen", theme_name=self.theme_name)
        summary_card.pack(fill=X, pady=(0, 15))
        
        summary_frame = BaseFrame(summary_card, theme_name=self.theme_name)
        summary_frame.pack(fill=X, padx=10, pady=10)
        
        StyledLabel(
            summary_frame,
            text="Costo Total por Unidad:",
            label_type="normal",
            theme_name=self.theme_name
        ).pack(anchor="w", pady=(0, 5))
        
        costo_total_label = StyledLabel(
            summary_frame,
            text="$0.00",
            label_type="heading",
            theme_name=self.theme_name
        )
        costo_total_label.set_accent()
        costo_total_label.pack(anchor="w", pady=(0, 10))
        
        StyledLabel(
            summary_frame,
            text="Desglose:",
            label_type="small",
            theme_name=self.theme_name
        ).set_accent()
        
        desglose_text = tk.Text(
            summary_frame,
            height=3,
            width=60,
            wrap=tk.WORD,
            bg="white",
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
            state=tk.DISABLED
        )
        desglose_text.pack(fill=BOTH, expand=True, pady=5)
        
        def actualizar_resumen(*args):
            costo_total = Decimal(0)
            desglose = []
            
            for sub_name, data in selected_subproductos.items():
                if data['var'].get():
                    # ✅ COSTO UNITARIO ya viene de la producción
                    costo_unitario = Decimal(str(data['costo_unitario']))
                    costo_total += costo_unitario
                    desglose.append(f"  • {sub_name}: ${data['costo_unitario']:.2f}")
            
            costo_total_label.config(text=f"${float(costo_total):.2f}")
            
            desglose_text.config(state=tk.NORMAL)
            desglose_text.delete(1.0, tk.END)
            desglose_text.insert(1.0, "\n".join(desglose) if desglose else "  (Selecciona subproductos)")
            desglose_text.config(state=tk.DISABLED)
        
        for sub_name, data in selected_subproductos.items():
            data['var'].trace('w', actualizar_resumen)
        
        # Botones
        btn_frame = BaseFrame(main_frame, theme_name=self.theme_name)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        def guardar_producto():
            nombre = name_entry.get().strip()
            
            if not nombre:
                messagebox.showwarning("Validación", "Ingresa un nombre")
                return
            
            subproductos_seleccionados = [
                (sub_name, data)
                for sub_name, data in selected_subproductos.items()
                if data['var'].get()
            ]
            
            if not subproductos_seleccionados:
                messagebox.showwarning("Validación", "Selecciona subproductos")
                return
            
            costo_total = sum(
                Decimal(str(data['costo_unitario']))
                for _, data in subproductos_seleccionados
            )
            
            desglose_msg = "\n".join([
                f"  • {sub}: ${data['costo_unitario']:.2f}"
                for sub, data in subproductos_seleccionados
            ])
            
            confirm_msg = (
                f"¿Crear producto '{nombre}'?\n\n"
                f"Componentes:\n{desglose_msg}\n\n"
                f"Costo Total por Unidad: ${float(costo_total):.2f}"
            )
            
            if messagebox.askyesno("Confirmar", confirm_msg):
                try:
                    # ✅ USAR unidades_producidas REAL
                    subproductos_config = [
                        {
                            'subproducto_id': data['subproducto_id'],
                            'unidades_rinde': data['unidades_producidas']  # ✅ LAS REALES
                        }
                        for _, data in subproductos_seleccionados
                    ]
                    
                    resultado = self.backend.crear_producto_final(
                        nombre,
                        subproductos_config,
                        precio_venta=0
                    )
                    
                    messagebox.showinfo(
                        "✅ Éxito",
                        f"Producto '{nombre}' creado\n"
                        f"Costo por Unidad: ${float(costo_total):.2f}\n\n"
                        f"Ve a 'Precios' para asignar precio de venta."
                    )
                    
                    win.destroy()
                    self.load_productos_finales()
                
                except Exception as e:
                    messagebox.showerror("Error", str(e)[:150])
        
        tk.Button(
            btn_frame,
            text="✅ Crear",
            command=guardar_producto,
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=8
        ).pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=win.destroy,
            bg="#6c757d", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=8
        ).pack(side=LEFT, fill=X, expand=True)
        
        def actualizar_resumen(*args):
            costo_total = Decimal(0)
            desglose = []
            
            for sub_name, data in selected_subproductos.items():
                if data['var'].get():
                    costo_total += Decimal(str(data['costo_unitario']))
                    desglose.append(f"  • {sub_name}: ${data['costo_unitario']:.2f}")
            
            costo_total_label.config(text=f"${float(costo_total):.2f}")
            
            desglose_text.config(state=tk.NORMAL)
            desglose_text.delete(1.0, tk.END)
            desglose_text.insert(1.0, "\n".join(desglose) if desglose else "  (Selecciona subproductos)")
            desglose_text.config(state=tk.DISABLED)
        
        for sub_name, data in selected_subproductos.items():
            data['var'].trace('w', actualizar_resumen)
        
        # Botones
        btn_frame = BaseFrame(main_frame, theme_name=self.theme_name)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        def guardar_producto():
            nombre = name_entry.get().strip()
            
            if not nombre:
                messagebox.showwarning("Validación", "Ingresa un nombre")
                return
            
            subproductos_seleccionados = [
                (sub_name, data)
                for sub_name, data in selected_subproductos.items()
                if data['var'].get()
            ]
            
            if not subproductos_seleccionados:
                messagebox.showwarning("Validación", "Selecciona subproductos")
                return
            
            costo_total = sum(
                Decimal(str(data['costo_unitario']))
                for _, data in subproductos_seleccionados
            )
            
            desglose_msg = "\n".join([
                f"  • {sub}: ${data['costo_unitario']:.2f}"
                for sub, data in subproductos_seleccionados
            ])
            
            confirm_msg = (
                f"¿Crear producto '{nombre}'?\n\n"
                f"Componentes:\n{desglose_msg}\n\n"
                f"Costo Total: ${float(costo_total):.2f}"
            )
            
            if messagebox.askyesno("Confirmar", confirm_msg):
                try:
                    subproductos_config = [
                        {
                            'subproducto_id': data['subproducto_id'],
                            'unidades_rinde': 1
                        }
                        for _, data in subproductos_seleccionados
                    ]
                    
                    resultado = self.backend.crear_producto_final(
                        nombre,
                        subproductos_config,
                        precio_venta=0
                    )
                    
                    messagebox.showinfo(
                        "✅ Éxito",
                        f"Producto '{nombre}' creado\n"
                        f"Costo: ${float(costo_total):.2f}\n\n"
                        f"Ve a 'Precios' para asignar precio de venta."
                    )
                    
                    win.destroy()
                    self.load_productos_finales()
                
                except Exception as e:
                    messagebox.showerror("Error", str(e)[:150])
        
        tk.Button(
            btn_frame,
            text="✅ Crear",
            command=guardar_producto,
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=8
        ).pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=win.destroy,
            bg="#6c757d", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=8
        ).pack(side=LEFT, fill=X, expand=True)
    
    def _get_producciones_disponibles(self) -> list:
        """Obtiene producciones recientes con ID correcto del subproducto"""
        conn_db = get_connection()
        
        if not conn_db:
            return []
        
        try:
            with conn_db.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        sp.id as produccion_id,
                        sp.subproducto_id,
                        s.id as subproducto_id_check,
                        s.nombre,
                        sp.costo_unitario,
                        sp.unidades_producidas,
                        sp.created_at
                    FROM subproducto_producciones sp
                    JOIN subproductos s ON sp.subproducto_id = s.id
                    ORDER BY sp.created_at DESC
                """)
                
                resultados = cursor.fetchall() or []
                
                # Agrupar por subproducto y tomar el más reciente
                vistos = set()
                producciones = []
                
                for row in resultados:
                    sub_id = row['subproducto_id']
                    if sub_id not in vistos:
                        vistos.add(sub_id)
                        producciones.append({
                            'produccion_id': row['produccion_id'],
                            'subproducto_id': row['subproducto_id'],
                            'nombre': row['nombre'],
                            'costo_unitario': float(row['costo_unitario']),
                            'unidades_producidas': row['unidades_producidas'],
                            'created_at': row['created_at']
                        })
                
                self.logger.info(f"✅ Producciones disponibles: {len(producciones)}")
                for prod in producciones:
                    self.logger.debug(
                        f"  - {prod['nombre']}: "
                        f"ID={prod['subproducto_id']}, "
                        f"Costo/U=${prod['costo_unitario']:.2f}"
                    )
                
                return producciones
        
        except Exception as e:
            self.logger.error(f"Error obteniendo producciones: {e}")
            return []
        
        finally:
            close_connection(conn_db)
    
    def load_productos_finales(self):
        """Carga productos finales"""
        try:
            for i in self.pf_tree.get_children():
                self.pf_tree.delete(i)
            
            pf_list = self.backend.get_productos_finales_info()
            
            for p in pf_list:
                pid = p.get("id")
                name = p.get("nombre")
                sp = p.get("subproductos_str", "N/A")
                costo = p.get("costo_unitario_total", 0.0)
                precio = p.get("precio_venta", 0.0) or 0.0
                margen = p.get("margen_ganancia", 0)
                
                self.pf_tree.insert(
                    "",
                    END,
                    values=(
                        pid,
                        name,
                        sp,
                        f"${float(costo):.2f}",
                        f"${float(precio):.2f}",
                        f"{margen:.1f}%"
                    )
                )
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
    # ============================================
    # TAB 2: CREAR SUBPRODUCTOS
    # ============================================
    
    def _setup_subproductos_tab(self):
        """Configura tab de subproductos"""
        
        container = BaseFrame(self.tab_crear_sub, theme_name=self.theme_name)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Izquierda
        left_card = CardFrame(container, title="📦 Inventario", theme_name=self.theme_name)
        left_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        cols_inv = ("Producto", "Stock", "Unidad")
        self.inv_tree = Treeview(left_card, columns=cols_inv, show="headings", height=18)
        
        for c in cols_inv:
            self.inv_tree.heading(c, text=c)
            self.inv_tree.column(c, width=100)
        
        self.inv_tree.pack(fill=BOTH, expand=True, padx=0, pady=(0, 10))
        
        tk.Button(
            left_card,
            text="🔄 Refrescar",
            command=self.reload_inventario,
            bg=COLOR_INFO, fg="white", relief="flat", cursor="hand2", bd=0
        ).pack(fill=X)
        
        # Centro
        center_card = CardFrame(container, title="⚡ Subproductos", theme_name=self.theme_name)
        center_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        cols_sub = ("ID", "Nombre", "Costo")
        self.subproductos_tree = Treeview(center_card, columns=cols_sub, show="headings", height=10)
        
        for c in cols_sub:
            self.subproductos_tree.heading(c, text=c)
            self.subproductos_tree.column(c, width=100)
        
        self.subproductos_tree.pack(fill=BOTH, expand=True, padx=0, pady=(0, 10))
        self.subproductos_tree.bind("<<TreeviewSelect>>", self.on_subproducto_select)
        
        btn_frame = BaseFrame(center_card, theme_name=self.theme_name)
        btn_frame.pack(fill=X)
        
        tk.Button(
            btn_frame,
            text="➕ Nuevo",
            command=self.open_new_subproducto_window,
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 8, "bold")
        ).pack(side=LEFT, padx=(0, 5), fill=X, expand=True)
        
        tk.Button(
            btn_frame,
            text="🗑️ Eliminar",
            command=self.delete_selected_subproducto,
            bg=COLOR_DANGER, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 8, "bold")
        ).pack(side=LEFT, fill=X, expand=True)
        
        # Derecha
        right_card = CardFrame(container, title="📊 Producción", theme_name=self.theme_name)
        right_card.pack(side=LEFT, fill=BOTH, expand=True)
        
        sub_name_label = StyledLabel(
            right_card,
            text="Subproducto:",
            label_type="small",
            theme_name=self.theme_name
        )
        sub_name_label.pack(anchor="w", padx=6, pady=(6, 2))
        
        self.lbl_sub_nombre = StyledLabel(
            right_card,
            text="(Ninguno)",
            label_type="heading",
            theme_name=self.theme_name
        )
        self.lbl_sub_nombre.set_accent()
        self.lbl_sub_nombre.pack(anchor="w", padx=6, pady=(0, 10))
        
        ing_label = StyledLabel(
            right_card,
            text="Ingredientes:",
            label_type="normal",
            theme_name=self.theme_name
        )
        ing_label.set_accent()
        ing_label.pack(anchor="w", padx=6, pady=(0, 5))
        
        cols_i = ("Producto", "Cantidad", "Unidad")
        self.sub_ing_tree = Treeview(right_card, columns=cols_i, show="headings", height=6)
        
        for c in cols_i:
            self.sub_ing_tree.heading(c, text=c)
            self.sub_ing_tree.column(c, width=80)
        
        self.sub_ing_tree.pack(fill=BOTH, expand=True, padx=6, pady=(0, 10))
        
        prod_label = StyledLabel(
            right_card,
            text="Unidades a producir:",
            label_type="normal",
            theme_name=self.theme_name
        )
        prod_label.pack(anchor="w", padx=6, pady=(10, 2))
        
        self.unidades_entry = StyledEntry(right_card, theme_name=self.theme_name, width=12)
        self.unidades_entry.pack(anchor="w", padx=6, pady=(0, 10))
        
        modo_label = StyledLabel(
            right_card,
            text="Modo:",
            label_type="normal",
            theme_name=self.theme_name
        )
        modo_label.pack(anchor="w", padx=6, pady=(0, 2))
        
        self.tipo_combobox = StyledCombobox(
            right_card,
            values=["reales", "aproximadas"],
            state="readonly",
            width=14,
            theme_name=self.theme_name
        )
        self.tipo_combobox.set("reales")
        self.tipo_combobox.pack(anchor="w", padx=6, pady=(0, 10))
        
        calc_btn_frame = BaseFrame(right_card, theme_name=self.theme_name)
        calc_btn_frame.pack(fill=X, padx=6, pady=(0, 10))
        
        tk.Button(
            calc_btn_frame,
            text="📊 Calcular",
            command=self.on_calculate_cost,
            bg="#ffc107", fg="black", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 8, "bold")
        ).pack(side=LEFT, padx=(0, 5), fill=X, expand=True)
        
        tk.Button(
            calc_btn_frame,
            text="✅ Producir",
            command=self.on_produce,
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 8, "bold")
        ).pack(side=LEFT, fill=X, expand=True)
        
        costo_total_label = StyledLabel(
            right_card,
            text="Costo total:",
            label_type="normal",
            theme_name=self.theme_name
        )
        costo_total_label.pack(anchor="w", padx=6, pady=(10, 0))
        
        self.lbl_costo_total = StyledLabel(
            right_card,
            text="$0.00",
            label_type="heading",
            theme_name=self.theme_name
        )
        self.lbl_costo_total.set_accent()
        self.lbl_costo_total.pack(anchor="w", padx=6, pady=(0, 10))
        
        costo_unit_label = StyledLabel(
            right_card,
            text="Costo/unidad:",
            label_type="normal",
            theme_name=self.theme_name
        )
        costo_unit_label.pack(anchor="w", padx=6, pady=(0, 0))
        
        self.lbl_costo_unit = StyledLabel(
            right_card,
            text="$0.00",
            label_type="heading",
            theme_name=self.theme_name
        )
        self.lbl_costo_unit.set_accent()
        self.lbl_costo_unit.pack(anchor="w", padx=6)
        
        # Producciones
        prod_card = CardFrame(
            self.tab_crear_sub,
            title="📈 Producciones",
            theme_name=self.theme_name
        )
        prod_card.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        cols_prod = ("Fecha", "Unidades", "Tipo", "Costo Total", "Costo/u")
        self.producciones_tree = Treeview(prod_card, columns=cols_prod, show="headings", height=8)
        
        for c in cols_prod:
            self.producciones_tree.heading(c, text=c)
            self.producciones_tree.column(c, width=100)
        
        self.producciones_tree.pack(fill=BOTH, expand=True)
    
    # ============================================
    # MÉTODOS
    # ============================================
    
    def reload_inventario(self):
        """Recarga inventario"""
        try:
            for i in self.inv_tree.get_children():
                self.inv_tree.delete(i)
            
            inv = self.inv_backend.get_inventario_para_resumen()
            
            for item in inv:
                self.inv_tree.insert(
                    "",
                    END,
                    values=(item["producto"], item["cantidad_display"], item["unidad_display"])
                )
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
    def load_subproductos(self):
        """Carga subproductos"""
        try:
            for i in self.subproductos_tree.get_children():
                self.subproductos_tree.delete(i)
            
            subs = self.backend.get_subproductos_disponibles()
            self.subproductos_map.clear()
            
            for s in subs:
                sid = s['id']
                self.subproductos_map[sid] = s
                self.subproductos_tree.insert(
                    "",
                    END,
                    iid=str(sid),
                    values=(sid, s.get('nombre'), f"${float(s['costo_total_subproducto']):.2f}")
                )
        
        except Exception as e:
            messagebox.showerror("Error", str(e)[:100])
    
    def on_subproducto_select(self, event):
        """Selecciona subproducto"""
        sel = self.subproductos_tree.selection()
        
        if not sel:
            return
        
        sid = int(sel[0])
        self.selected_subproducto_id = sid
        sub = self.subproductos_map.get(sid, {})
        self.lbl_sub_nombre.config(text=sub.get('nombre', "(Sin nombre)"))
        
        try:
            self.sub_ing_tree.delete(*self.sub_ing_tree.get_children())
            ings = self.backend.get_subproducto_ingredientes(sid)
            
            for ing in ings:
                self.sub_ing_tree.insert(
                    "",
                    END,
                    values=(
                        ing['producto_ingrediente'],
                        ing['cantidad_usada'],
                        ing['unidad_usada']
                    )
                )
            
            self.load_producciones_for_selected()
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
    def delete_selected_subproducto(self):
        """Elimina subproducto"""
        sel = self.subproductos_tree.selection()
        
        if not sel:
            return
        
        if not messagebox.askyesno("Confirmar", "¿Eliminar?"):
            return
        
        try:
            sid = int(sel[0])
            self.backend.eliminar_subproducto(sid)
            self.load_subproductos()
            messagebox.showinfo("✅", "Eliminado")
        
        except Exception as e:
            messagebox.showerror("Error", str(e)[:100])
    
    def load_producciones_for_selected(self):
        """Carga producciones"""
        self.producciones_tree.delete(*self.producciones_tree.get_children())
        
        if not self.selected_subproducto_id:
            return
        
        try:
            rows = self.backend.get_producciones_por_subproducto(self.selected_subproducto_id, limit=200)
            
            for r in rows:
                self.producciones_tree.insert(
                    "",
                    END,
                    values=(
                        str(r.get("created_at")),
                        r.get("unidades_producidas"),
                        r.get("tipo_unidad"),
                        f"${float(r.get('costo_total_masa')):.2f}",
                        f"${float(r.get('costo_unitario')):.2f}"
                    )
                )
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
    def on_calculate_cost(self):
        """Calcula costo"""
        if not self.selected_subproducto_id:
            messagebox.showwarning("⚠️", "Selecciona subproducto")
            return
        
        try:
            units_text = self.unidades_entry.get().strip()
            unidades = int(float(units_text)) if units_text else 0
        
        except Exception:
            messagebox.showerror("❌", "Unidades inválidas")
            return
        
        if unidades <= 0:
            messagebox.showwarning("⚠️", "Unidades > 0")
            return
        
        try:
            est = self.backend.estimar_costo_produccion(self.selected_subproducto_id, unidades)
            self.lbl_costo_total.config(text=f"${est['costo_total_masa']:.2f}")
            self.lbl_costo_unit.config(text=f"${est['costo_unitario']:.2f}")
        
        except Exception as e:
            messagebox.showerror("❌", str(e)[:100])
    
    def on_produce(self):
        """Produce"""
        if not self.selected_subproducto_id:
            messagebox.showwarning("⚠️", "Selecciona subproducto")
            return
        
        try:
            units_text = self.unidades_entry.get().strip()
            unidades = int(float(units_text)) if units_text else 0
        
        except Exception:
            messagebox.showerror("❌", "Unidades inválidas")
            return
        
        if unidades <= 0:
            messagebox.showwarning("⚠️", "Unidades > 0")
            return
        
        modo = self.tipo_combobox.get().strip() or "reales"
        
        try:
            est = self.backend.estimar_costo_produccion(self.selected_subproducto_id, unidades)
            
            if not messagebox.askyesno(
                "Confirmar",
                f"¿Producir {unidades} unidades?\n"
                f"Costo: ${est['costo_total_masa']:.2f}\n"
                f"Costo/U: ${est['costo_unitario']:.2f}"
            ):
                return
            
            res = self.backend.crear_produccion_run(self.selected_subproducto_id, unidades, tipo_unidad=modo)
            
            messagebox.showinfo("✅", f"OK\n${res['costo_unitario']:.2f}/u")
            
            self.unidades_entry.delete(0, END)
            self.lbl_costo_total.config(text="$0.00")
            self.lbl_costo_unit.config(text="$0.00")
            self.reload_inventario()
            self.load_producciones_for_selected()
            self.load_subproductos()
        
        except Exception as e:
            messagebox.showerror("❌", str(e)[:100])
    
    def open_new_subproducto_window(self):
        """Abre diálogo para crear subproducto"""
        win = tk.Toplevel(self)
        win.title("➕ Nuevo Subproducto")
        win.geometry("700x600")
        win.transient(self.winfo_toplevel())
        win.grab_set()
        
        win.configure(bg=self.bg_color)
        main_frame = BaseFrame(win, theme_name=self.theme_name)
        main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        title = StyledLabel(
            main_frame,
            text="Nuevo Subproducto",
            label_type="heading",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 15))
        
        name_label = StyledLabel(
            main_frame,
            text="Nombre:",
            label_type="normal",
            theme_name=self.theme_name
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        name_entry = StyledEntry(main_frame, theme_name=self.theme_name)
        name_entry.pack(fill=X, pady=(0, 15))
        
        ing_title = StyledLabel(
            main_frame,
            text="Ingredientes",
            label_type="normal",
            theme_name=self.theme_name
        )
        ing_title.set_accent()
        ing_title.pack(anchor="w", pady=(0, 10))
        
        ing_input_frame = BaseFrame(main_frame, theme_name=self.theme_name)
        ing_input_frame.pack(fill=X, pady=(0, 10))
        
        prod_label = StyledLabel(ing_input_frame, text="Producto:", label_type="small", theme_name=self.theme_name)
        prod_label.grid(row=0, column=0, sticky="w", padx=5)
        
        prod_combo = StyledCombobox(
            ing_input_frame,
            values=[i['producto'] for i in self.inv_backend.get_inventario_para_resumen()],
            state="readonly",
            width=25,
            theme_name=self.theme_name
        )
        prod_combo.grid(row=0, column=1, sticky="ew", padx=5)
        
        cant_label = StyledLabel(ing_input_frame, text="Cantidad:", label_type="small", theme_name=self.theme_name)
        cant_label.grid(row=1, column=0, sticky="w", padx=5, pady=(5, 0))
        
        cant_entry = StyledEntry(ing_input_frame, theme_name=self.theme_name, width=12)
        cant_entry.grid(row=1, column=1, sticky="w", padx=5, pady=(5, 0))
        
        unidad_label = StyledLabel(ing_input_frame, text="Unidad:", label_type="small", theme_name=self.theme_name)
        unidad_label.grid(row=0, column=2, sticky="w", padx=5)
        
        unidad_combo = StyledCombobox(
            ing_input_frame,
            values=get_unit_choices(),
            state="readonly",
            width=12,
            theme_name=self.theme_name
        )
        unidad_combo.grid(row=0, column=3, sticky="ew", padx=5)
        
        add_btn = tk.Button(
            ing_input_frame,
            text="➕ Agregar",
            command=lambda: add_ing(),
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold")
        )
        add_btn.grid(row=1, column=3, sticky="ew", padx=5, pady=(5, 0))
        
        ing_input_frame.columnconfigure(1, weight=1)
        
        preview_label = StyledLabel(
            main_frame,
            text="Ingredientes:",
            label_type="normal",
            theme_name=self.theme_name
        )
        preview_label.pack(anchor="w", pady=(10, 5))
        
        cols_preview = ("Producto", "Cantidad", "Unidad")
        preview = Treeview(main_frame, columns=cols_preview, show="headings", height=6)
        
        for c in cols_preview:
            preview.heading(c, text=c)
            preview.column(c, width=150)
        
        preview.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        ingredients_list = []
        
        def add_ing():
            p = prod_combo.get().strip()
            c = cant_entry.get().strip()
            u = unidad_combo.get().strip()
            
            if not p or not c or not u:
                messagebox.showwarning("⚠️", "Completa campos")
                return
            
            try:
                cf = float(c)
            except ValueError:
                messagebox.showerror("❌", "Cantidad inválida")
                return
            
            preview.insert("", END, values=(p, f"{cf}", u))
            ingredients_list.append({'producto': p, 'cantidad': cf, 'unidad': u})
            
            prod_combo.set("")
            cant_entry.delete(0, END)
            unidad_combo.set("")
        
        def save():
            name = name_entry.get().strip()
            
            if not name:
                messagebox.showwarning("⚠️", "Ingresa nombre")
                return
            
            if not ingredients_list:
                messagebox.showwarning("⚠️", "Agrega ingredientes")
                return
            
            try:
                costo = self.backend.crear_subproducto(name, ingredients_list)
                messagebox.showinfo("✅", f"Creado\nCosto: ${float(costo):.2f}")
                win.destroy()
                self.load_subproductos()
                self.reload_inventario()
            
            except Exception as e:
                messagebox.showerror("❌", str(e)[:100])
        
        btn_frame = BaseFrame(main_frame, theme_name=self.theme_name)
        btn_frame.pack(fill=X)
        
        tk.Button(
            btn_frame,
            text="💾 Guardar",
            command=save,
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold")
        ).pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=win.destroy,
            bg="#6c757d", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold")
        ).pack(side=LEFT, fill=X, expand=True)