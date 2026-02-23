"""
Core.Pages.Resumenes.contabilidad_tab - Tab de contabilidad MEJORADA
Usa tabla centralizada para cálculos correctos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from typing import Dict, List

from Core.Backends.contabilidad_backend import ContabilidadBackend
from Core.Backends.inventario_backend import InventarioBackend
from Core.Backends.gastos_backend import GastosBackend
from Core.Common.logger import setup_logger

logger = setup_logger()


class ContabilidadTab(ttk.Frame):
    """Tab de contabilidad usando tabla centralizada"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.contabilidad_backend = ContabilidadBackend()
        self.inv_backend = InventarioBackend()
        self.gastos_backend = GastosBackend()
        self.capital_adicional = Decimal(0)
        
        self.setup_ui()
        self.actualizar_datos()

    def setup_ui(self):
        """Configura la interfaz"""
        
        # Frame principal con dos columnas
        main_frame = tk.Frame(self, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ============================================
        # COLUMNA IZQUIERDA: KPIs y Controles
        # ============================================
        left_panel = tk.Frame(main_frame, bg="white", width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        left_panel.pack_propagate(False)
        
        title_left = tk.Label(
            left_panel,
            text="📊 MÉTRICAS PRINCIPALES",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#1a1a2e"
        )
        title_left.pack(anchor="w", pady=(0, 15))
        
        # KPIs
        self.kpi_widgets = {}
        kpi_data = [
            ("💰 INVERSIÓN EN INVENTARIO", "inversion", "#FF6B6B"),
            ("💵 TOTAL INGRESOS (VENTAS)", "ingresos", "#4ECDC4"),
            ("📊 COSTO TOTAL (PRODUCTOS VENDIDOS)", "costos", "#FFB347"),
            ("📈 GANANCIA NETA", "ganancia", "#45B7D1"),
            ("💎 MARGEN PROMEDIO", "margen", "#96CEB4")
        ]
        
        for label, key, color in kpi_data:
            self._create_kpi_mini(left_panel, label, key, color)
        
        # Capital
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        capital_title = tk.Label(
            left_panel,
            text="💎 CAPITAL DISPONIBLE",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#1a1a2e"
        )
        capital_title.pack(anchor="w", pady=(10, 10))
        
        capital_frame = tk.Frame(left_panel, bg="white")
        capital_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(capital_frame, text="Capital:", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT)
        self.lbl_capital = tk.Label(capital_frame, text="$0.00", font=("Segoe UI", 11, "bold"), bg="white", fg="#00a86b")
        self.lbl_capital.pack(side=tk.LEFT, padx=10)
        
        # ✅ SOLO VISUALIZACIÓN - sin entry
        # ============================================
        # NUEVA SECCIÓN: DINERO EN FÍSICO
        # ============================================
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        dinero_fis_title = tk.Label(
            left_panel,
            text="💵 DINERO EN FÍSICO",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#1a1a2e"
        )
        dinero_fis_title.pack(anchor="w", pady=(10, 10))

        dinero_fis_frame = tk.Frame(left_panel, bg="white")
        dinero_fis_frame.pack(fill=tk.X, pady=8)

        tk.Label(dinero_fis_frame, text="Disponible:", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT)
        self.lbl_dinero_fisico = tk.Label(
            dinero_fis_frame, 
            text="$0.00", 
            font=("Segoe UI", 11, "bold"), 
            bg="white", 
            fg="#00a86b"
        )
        self.lbl_dinero_fisico.pack(side=tk.LEFT, padx=10)

        # Detalles
        detalles_frame = tk.Frame(left_panel, bg="#f9f9f9", relief=tk.SUNKEN, bd=1)
        detalles_frame.pack(fill=tk.X, pady=(10, 0), padx=5)

        tk.Label(detalles_frame, text="Capital total:", font=("Segoe UI", 9), bg="#f9f9f9").pack(anchor="w", padx=8, pady=(8, 2))
        self.lbl_capital_detalle = tk.Label(detalles_frame, text="$0.00", font=("Segoe UI", 9), bg="#f9f9f9", fg="#0066cc")
        self.lbl_capital_detalle.pack(anchor="w", padx=20, pady=2)

        tk.Label(detalles_frame, text="Gastos totales:", font=("Segoe UI", 9), bg="#f9f9f9").pack(anchor="w", padx=8, pady=(8, 2))
        self.lbl_gastos_detalle = tk.Label(detalles_frame, text="$0.00", font=("Segoe UI", 9), bg="#f9f9f9", fg="#ff6b6b")
        self.lbl_gastos_detalle.pack(anchor="w", padx=20, pady=(2, 8))

        # Botones
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(left_panel, bg="white")
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="🔄 Actualizar", command=self.actualizar_datos, bg="#17a2b8", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(btn_frame, text="💾 Exportar", command=self.exportar, bg="#ffc107", fg="black", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # ============================================
        # COLUMNA DERECHA: Detalles
        # ============================================
        right_panel = tk.Frame(main_frame, bg="#f5f5f5")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Fondo total
        fondo_card = tk.Frame(right_panel, bg="#0066cc", relief=tk.RAISED, bd=2)
        fondo_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(fondo_card, text="🏦 FONDO TOTAL DEL NEGOCIO", font=("Segoe UI", 12, "bold"), bg="#0066cc", fg="white", pady=10).pack(fill=tk.X, padx=10)
        self.lbl_fondo_total = tk.Label(fondo_card, text="$0.00", font=("Segoe UI", 24, "bold"), bg="#0066cc", fg="white", pady=15)
        self.lbl_fondo_total.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Tabs de desglose
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Por tipo de producto
        self.tab_tipo = tk.Frame(notebook, bg="white")
        notebook.add(self.tab_tipo, text="📦 Por Tipo")
        
        cols_tipo = ("Tipo", "Ventas", "Unidades", "Ingresos", "Costos", "Ganancia", "Margen")
        self.tree_tipo = ttk.Treeview(self.tab_tipo, columns=cols_tipo, show="headings", height=12)
        for col in cols_tipo:
            self.tree_tipo.heading(col, text=col)
            self.tree_tipo.column(col, width=90)
        self.tree_tipo.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Por producto
        self.tab_producto = tk.Frame(notebook, bg="white")
        notebook.add(self.tab_producto, text="🍩 Por Producto")
        
        cols_prod = ("Producto", "Ventas", "Unidades", "Ingresos", "Costos", "Ganancia")
        self.tree_producto = ttk.Treeview(self.tab_producto, columns=cols_prod, show="headings", height=12)
        for col in cols_prod:
            self.tree_producto.heading(col, text=col)
            self.tree_producto.column(col, width=100)
        self.tree_producto.pack(fill=tk.BOTH, expand=True)
        
        # Tab 3: Historial
        self.tab_historial = tk.Frame(notebook, bg="white")
        notebook.add(self.tab_historial, text="📋 Historial")
        
        cols_hist = ("Fecha", "Producto", "Tipo", "Cant.", "Costo/U", "Venta/U", "Ganancia")
        self.tree_historial = ttk.Treeview(self.tab_historial, columns=cols_hist, show="headings", height=12)
        for col in cols_hist:
            self.tree_historial.heading(col, text=col)
            self.tree_historial.column(col, width=90)
        self.tree_historial.pack(fill=tk.BOTH, expand=True)
    
    def _create_kpi_mini(self, parent, label: str, key: str, color: str):
        """Crea tarjeta KPI"""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=8)
        
        tk.Label(card, text=label, font=("Segoe UI", 10), bg=color, fg="white", pady=5).pack(fill=tk.X, padx=10)
        
        value_label = tk.Label(card, text="$0.00", font=("Segoe UI", 14, "bold"), bg=color, fg="white", pady=8)
        value_label.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        self.kpi_widgets[key] = value_label
    
    def actualizar_datos(self):
        """Actualiza todos los datos con cálculos CORRECTOS"""
        try:
            # ============================================
            # OBTENER DATOS DE LA BD
            # ============================================
            
            # 1. Inversión en Inventario (stock actual)
            inversion = self._obtener_inversion()
            
            # 2. Resumen de ventas
            resumen = self.contabilidad_backend.obtener_resumen_general()

            # Obtener capital desde Gastos
            capital_total = Decimal(str(self.gastos_backend.obtener_capital_total()))

            gastos_totales = Decimal(str(self.gastos_backend.get_total_gastos()))
            
            # 3. Extraer valores
            ingresos = Decimal(str(resumen.get('total_ingresos', 0) or 0))
            costos_productos_vendidos = Decimal(str(resumen.get('total_costos', 0) or 0))
            ganancia_neta = Decimal(str(resumen.get('total_ganancia', 0) or 0))
            margen = Decimal(str(resumen.get('margen_promedio', 0) or 0))

            ganancia_calculada = ingresos - costos_productos_vendidos
            
            gastos_compras = Decimal(str(self.gastos_backend.obtener_gastos_compras()))

            
            
            # ===========================================
            # ==== NUEVA UI DINERO FISICO              
            # ===========================================
            dinero_fisico = capital_total + costos_productos_vendidos - gastos_compras

            color_dinero = "#00a86b" if dinero_fisico >= 0 else "#ff6b6b"
            self.lbl_dinero_fisico.config(
                text=f"${float(dinero_fisico):.2f}",
                fg=color_dinero
            )
            self.lbl_capital_detalle.config(text=f"${float(capital_total):.2f}")
            self.lbl_gastos_detalle.config(text=f"${float(gastos_totales):.2f}")
            
            fondo_total = inversion + dinero_fisico + ganancia_neta
            # Fondo total
            self.lbl_fondo_total.config(text=f"${float(fondo_total):.2f}")
            
            


            # ============================================
            # ACTUALIZAR UI
            # ============================================
            
            self.kpi_widgets["inversion"].config(text=f"${float(inversion):.2f}")
            self.kpi_widgets["ingresos"].config(text=f"${float(ingresos):.2f}")
            self.kpi_widgets["costos"].config(text=f"${float(costos_productos_vendidos):.2f}")
            self.kpi_widgets["ganancia"].config(text=f"${float(ganancia_neta):.2f}")
            self.kpi_widgets["margen"].config(text=f"{float(margen):.1f}%")
            
            self.lbl_capital.config(text=f"${float(self.capital_adicional):.2f}")
            self.lbl_fondo_total.config(text=f"${float(fondo_total):.2f}")
            
            # Actualizar tablas
            self._actualizar_tabla_tipo()
            self._actualizar_tabla_producto()
            self._actualizar_historial()
            
            logger.info(
                f"✅ Datos de contabilidad actualizados:\n"
                f"   Inversión: ${float(inversion):.2f}\n"
                f"   Ingresos: ${float(ingresos):.2f}\n"
                f"   Costos: ${float(costos_productos_vendidos):.2f}\n"
                f"   Ganancia Neta: ${float(ganancia_neta):.2f}\n"
                f"   Fondo Total: ${float(fondo_total):.2f}"
            )
        
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _obtener_inversion(self) -> Decimal:
        """
        Obtiene inversión en inventario.
        
        IMPORTANTE:
        - Suma el valor total de TODO el stock en almacén
        - cantidad_stock * costo_promedio_ponderado
        """
        try:
            inventario = self.inv_backend.get_inventario_para_resumen()
            total = Decimal(0)
            
            for item in inventario:
                valor_item = Decimal(str(item.get("total_valor", 0) or 0))
                total += valor_item
            
            logger.info(f"💰 Inversión en inventario: ${float(total):.2f}")
            return total
        except Exception as e:
            logger.error(f"Error obteniendo inversión: {e}")
            return Decimal(0)
    
    def _actualizar_tabla_tipo(self):
        """Actualiza tabla por tipo"""
        for item in self.tree_tipo.get_children():
            self.tree_tipo.delete(item)
        
        tipos = self.contabilidad_backend.obtener_resumen_por_tipo_producto()
        for t in tipos:
            self.tree_tipo.insert("", tk.END, values=(
                t['tipo_producto'],
                t['num_ventas'],
                t['total_unidades'],
                f"${t['total_ingresos']:.2f}",
                f"${t['total_costos']:.2f}",
                f"${t['total_ganancia']:.2f}",
                f"{t['margen_promedio']:.1f}%"
            ))
    
    def _actualizar_tabla_producto(self):
        """Actualiza tabla por producto"""
        for item in self.tree_producto.get_children():
            self.tree_producto.delete(item)
        
        productos = self.contabilidad_backend.obtener_resumen_por_producto()
        for p in productos:
            self.tree_producto.insert("", tk.END, values=(
                p['nombre_producto'],
                p['num_ventas'],
                p['total_unidades'],
                f"${p['total_ingresos']:.2f}",
                f"${p['total_costos']:.2f}",
                f"${p['total_ganancia']:.2f}"
            ))
    
# Capital viene de la BD (efectivo_movimientos)
# Solo mostrar, no usar entrada aquí

    def _obtener_capital_sistema(self) -> Decimal:
        """Obtiene capital del sistema desde BD"""
        try:
            conn = get_connection()
            if not conn:
                return Decimal(0)
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(monto), 0) as total
                    FROM efectivo_movimientos
                """)
                resultado = cursor.fetchone()
            
            close_connection(conn)
            return Decimal(str(resultado.get('total', 0) or 0))
        
        except Exception as e:
            logger.error(f"Error obteniendo capital: {e}")
            return Decimal(0)

    def _actualizar_historial(self):
        """Actualiza historial"""
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        
        historial = self.contabilidad_backend.obtener_historial_contabilidad(limit=50)
        for h in historial:
            self.tree_historial.insert("", tk.END, values=(
                str(h['fecha'])[:10],
                h['producto'],
                h['tipo_producto'],
                h['cantidad'],
                f"${h['costo_unitario']:.2f}",
                f"${h['venta_unitaria']:.2f}",
                f"${h['ganancia_neta']:.2f}"
            ))
    
    def exportar(self):
        """Exporta reporte"""
        try:
            from datetime import datetime
            filename = f"contabilidad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            resumen = self.contabilidad_backend.obtener_resumen_general()
            tipos = self.contabilidad_backend.obtener_resumen_por_tipo_producto()
            inversion = self._obtener_inversion()
            
            contenido = f"""REPORTE DE CONTABILIDAD - {datetime.now().strftime('%Y-%m-%d %H:%M')}

RESUMEN GENERAL:
  Inversión en Inventario: ${float(inversion):.2f}
  Total Ventas: {resumen.get('total_ventas', 0)}
  Total Unidades Vendidas: {resumen.get('total_unidades', 0)}
  Total Ingresos: ${resumen.get('total_ingresos', 0):.2f}
  Total Costos (Productos Vendidos): ${resumen.get('total_costos', 0):.2f}
  Ganancia Neta: ${resumen.get('total_ganancia', 0):.2f}
  Margen Promedio: {resumen.get('margen_promedio', 0):.1f}%

POR TIPO DE PRODUCTO:
"""
            
            for t in tipos:
                contenido += f"\n{t['tipo_producto']}:\n"
                contenido += f"  Ventas: {t['num_ventas']} | Unidades: {t['total_unidades']}\n"
                contenido += f"  Ingresos: ${t['total_ingresos']:.2f} | Costos: ${t['total_costos']:.2f}\n"
                contenido += f"  Ganancia: ${t['total_ganancia']:.2f} | Margen: {t['margen_promedio']:.1f}%\n"
            
            with open(filename, 'w') as f:
                f.write(contenido)
            
            messagebox.showinfo("✅", f"Exportado: {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))