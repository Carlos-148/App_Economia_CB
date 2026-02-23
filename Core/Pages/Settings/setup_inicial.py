"""
Ventana de setup inicial para configurar los datos base de la aplicación
"""

import tkinter as tk
from tkinter import messagebox, ttk
from decimal import Decimal
from datetime import datetime

from Core.Common.logger import setup_logger
from Core.Backends.inventario_backend import InventarioBackend
from Core.Common.database import get_connection, close_connection
from Core.Styles.base_components import BaseFrame, StyledLabel, StyledEntry
from Core.Common.config import load_config
from Core.Common.units import get_unit_choices

logger = setup_logger()


class SetupInicial(tk.Toplevel):
    """Ventana de setup inicial de la aplicación"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🚀 SETUP INICIAL - Configuración de Base de Datos")
        self.geometry("900x700")
        self.resizable(False, False)
        
        # Cargar config
        config = load_config()
        self.theme_name = config.get("theme", "solar")
        
        self.inventory_backend = InventarioBackend()
        self.logger = setup_logger()
        
        # Variables de productos
        self.productos = []
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        
        # Frame principal
        main_frame = tk.Frame(self, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(
            main_frame,
            text="🚀 CONFIGURACIÓN INICIAL DE LA APLICACIÓN",
            font=("Segoe UI", 16, "bold"),
            bg="#f5f5f5",
            fg="#1a1a2e"
        )
        titulo.pack(anchor="w", pady=(0, 20))
        
        # Instrucción
        instruccion = tk.Label(
            main_frame,
            text="Ingresa los datos iniciales con los que comenzará tu negocio",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#666"
        )
        instruccion.pack(anchor="w", pady=(0, 20))
        
        # ============================================
        # SECCIÓN 1: CAPITAL INICIAL
        # ============================================
        capital_frame = tk.LabelFrame(
            main_frame,
            text="💰 CAPITAL INICIAL",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        capital_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            capital_frame,
            text="Ingresa el dinero con el que comenzarás:",
            font=("Segoe UI", 9),
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        capital_input_frame = tk.Frame(capital_frame, bg="white")
        capital_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(capital_input_frame, text="$", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT)
        
        self.entry_capital = tk.Entry(
            capital_input_frame,
            font=("Segoe UI", 10),
            width=20,
            relief=tk.FLAT,
            bd=2
        )
        self.entry_capital.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        self.entry_capital.insert(0, "0.00")
        
        # ============================================
        # SECCIÓN 2: PRODUCTOS INICIALES
        # ============================================
        productos_frame = tk.LabelFrame(
            main_frame,
            text="📦 PRODUCTOS INICIALES",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        productos_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(
            productos_frame,
            text="Agrega los productos con los que iniciarás (opcional)",
            font=("Segoe UI", 9),
            bg="white"
        ).pack(anchor="w", pady=(0, 15))
        
        # Formulario para agregar productos
        formulario_frame = tk.Frame(productos_frame, bg="white")
        formulario_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Nombre
        tk.Label(formulario_frame, text="Producto:", font=("Segoe UI", 9), bg="white").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.entry_producto = tk.Entry(formulario_frame, font=("Segoe UI", 9), width=20, relief=tk.FLAT, bd=2)
        self.entry_producto.grid(row=0, column=1, sticky="ew", padx=(0, 15))
        
        # Cantidad
        tk.Label(formulario_frame, text="Cantidad:", font=("Segoe UI", 9), bg="white").grid(
            row=0, column=2, sticky="w", padx=(0, 10)
        )
        self.entry_cantidad = tk.Entry(formulario_frame, font=("Segoe UI", 9), width=12, relief=tk.FLAT, bd=2)
        self.entry_cantidad.grid(row=0, column=3, sticky="ew", padx=(0, 5))
        
        # Unidad
        tk.Label(formulario_frame, text="Unidad:", font=("Segoe UI", 9), bg="white").grid(
            row=0, column=4, sticky="w", padx=(0, 10)
        )
        self.combo_unidad = ttk.Combobox(
            formulario_frame,
            values=get_unit_choices(),
            state="readonly",
            width=12,
            font=("Segoe UI", 9)
        )
        self.combo_unidad.grid(row=0, column=5, sticky="ew", padx=(0, 15))
        
        # Costo unitario
        tk.Label(formulario_frame, text="Costo/Unidad:", font=("Segoe UI", 9), bg="white").grid(
            row=0, column=6, sticky="w", padx=(0, 10)
        )
        self.entry_costo = tk.Entry(formulario_frame, font=("Segoe UI", 9), width=12, relief=tk.FLAT, bd=2)
        self.entry_costo.grid(row=0, column=7, sticky="ew")
        
        formulario_frame.columnconfigure(1, weight=1)
        formulario_frame.columnconfigure(3, weight=0)
        formulario_frame.columnconfigure(5, weight=0)
        formulario_frame.columnconfigure(7, weight=0)
        
        # Botón agregar producto
        btn_agregar_producto = tk.Button(
            productos_frame,
            text="➕ Agregar Producto",
            command=self.agregar_producto,
            bg="#28a745",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=15,
            pady=8
        )
        btn_agregar_producto.pack(anchor="w", pady=(0, 15))
        
        # Lista de productos agregados
        tk.Label(
            productos_frame,
            text="Productos agregados:",
            font=("Segoe UI", 9, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(15, 5))
        
        # Treeview para mostrar productos
        cols = ("Producto", "Cantidad", "Unidad", "Costo/U", "Total")
        self.tree_productos = ttk.Treeview(productos_frame, columns=cols, show="headings", height=5)
        
        for col in cols:
            self.tree_productos.heading(col, text=col)
            width = 150 if col == "Producto" else 80
            self.tree_productos.column(col, width=width)
        
        self.tree_productos.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Botón eliminar producto
        btn_eliminar = tk.Button(
            productos_frame,
            text="🗑️ Eliminar Producto",
            command=self.eliminar_producto,
            bg="#dc3545",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=15,
            pady=5
        )
        btn_eliminar.pack(anchor="w")
        
        # ============================================
        # BOTONES DE ACCIÓN
        # ============================================
        btn_frame = tk.Frame(main_frame, bg="#f5f5f5")
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(
            btn_frame,
            text="✅ INICIAR APLICACIÓN",
            command=self.guardar_setup,
            bg="#007bff",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        tk.Button(
            btn_frame,
            text="❌ CANCELAR",
            command=self.destroy,
            bg="#6c757d",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def agregar_producto(self):
        """Agrega un producto a la lista"""
        try:
            nombre = self.entry_producto.get().strip()
            cantidad_str = self.entry_cantidad.get().strip()
            unidad = self.combo_unidad.get()
            costo_str = self.entry_costo.get().strip()
            
            # Validaciones
            if not nombre:
                messagebox.showwarning("Validación", "Ingresa el nombre del producto")
                return
            
            if not cantidad_str:
                messagebox.showwarning("Validación", "Ingresa la cantidad")
                return
            
            if not unidad:
                messagebox.showwarning("Validación", "Selecciona una unidad")
                return
            
            if not costo_str:
                messagebox.showwarning("Validación", "Ingresa el costo unitario")
                return
            
            # Convertir a números
            cantidad = float(cantidad_str)
            costo = float(costo_str)
            
            if cantidad <= 0 or costo < 0:
                raise ValueError("Cantidad y costo deben ser positivos")
            
            # Agregar a lista interna
            total = cantidad * costo
            producto = {
                'nombre': nombre,
                'cantidad': cantidad,
                'unidad': unidad,
                'costo': costo,
                'total': total
            }
            self.productos.append(producto)
            
            # Actualizar treeview
            self.tree_productos.insert("", tk.END, values=(
                nombre,
                f"{cantidad:.2f}",
                unidad,
                f"${costo:.2f}",
                f"${total:.2f}"
            ))
            
            # Limpiar formulario
            self.entry_producto.delete(0, tk.END)
            self.entry_cantidad.delete(0, tk.END)
            self.combo_unidad.set("")
            self.entry_costo.delete(0, tk.END)
            self.entry_producto.focus()
            
            logger.info(f"✅ Producto agregado: {nombre}")
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error agregando producto: {e}")
    
    def eliminar_producto(self):
        """Elimina un producto seleccionado"""
        try:
            seleccionado = self.tree_productos.selection()
            if not seleccionado:
                messagebox.showwarning("Aviso", "Selecciona un producto para eliminar")
                return
            
            # Obtener índice
            indice = self.tree_productos.index(seleccionado[0])
            
            # Eliminar de lista interna
            self.productos.pop(indice)
            
            # Eliminar de treeview
            self.tree_productos.delete(seleccionado[0])
            
            logger.info(f"✅ Producto eliminado")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error eliminando producto: {e}")
    
    def guardar_setup(self):
        """Guarda la configuración inicial"""
        try:
            # Obtener capital
            capital_str = self.entry_capital.get().strip()
            if not capital_str:
                messagebox.showwarning("Validación", "Ingresa el capital inicial")
                return
            
            capital = float(capital_str)
            if capital < 0:
                raise ValueError("Capital debe ser positivo")
            
            logger.info("📊 Guardando configuración inicial...")
            
            # ============================================
            # 1. GUARDAR CAPITAL EN BD
            # ============================================
            self._guardar_capital_inicial(capital)
            
            # ============================================
            # 2. GUARDAR PRODUCTOS EN INVENTARIO
            # ============================================
            for producto in self.productos:
                self._guardar_producto_inicial(producto)
            
            logger.info("✅ Setup inicial completado")
            messagebox.showinfo(
                "✅ Éxito",
                f"Configuración guardada:\n"
                f"• Capital: ${capital:.2f}\n"
                f"• Productos: {len(self.productos)}"
            )
            
            self.destroy()
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.error(f"Error en setup: {e}")
            messagebox.showerror("Error", f"Error guardando setup: {e}")
    
    def _guardar_capital_inicial(self, monto: float):
        """Guarda el capital inicial en efectivo_movimientos"""
        conn = get_connection()
        if not conn:
            raise Exception("No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO efectivo_movimientos 
                    (tipo, monto, saldo, fecha)
                    VALUES (%s, %s, %s, NOW())
                """, ("Capital Extra", round(monto, 2), round(monto, 2)))
            
            conn.commit()
            logger.info(f"✅ Capital inicial guardado: ${monto:.2f}")
        
        except Exception as e:
            logger.error(f"Error guardando capital: {e}")
            raise
        
        finally:
            close_connection(conn)
    
    def _guardar_producto_inicial(self, producto: dict):
        """Guarda un producto inicial en inventario"""
        try:
            # Agregar a inventario
            self.inventory_backend.agregar_producto(
                nombre=producto['nombre'],
                cantidad_stock=producto['cantidad'],
                unidad=producto['unidad'],
                costo_promedio_ponderado=producto['costo'],
                tipo_producto="Inicial"
            )
            
            logger.info(f"✅ Producto inicial guardado: {producto['nombre']}")
        
        except Exception as e:
            logger.error(f"Error guardando producto: {e}")
            raise