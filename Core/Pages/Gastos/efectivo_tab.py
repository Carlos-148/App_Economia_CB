"""
Core.Pages.Gastos.efectivo_tab - Gestión centralizada de efectivo
Sistema de control de dinero físico vs dinero en el sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox, END
from decimal import Decimal
from datetime import datetime

from Core.Common.logger import setup_logger
from Core.Common.database import get_connection, close_connection
from Core.Styles.base_components import (
    BaseFrame, StyledLabel, StyledEntry, CardFrame
)
from Core.Styles.modern_styles import ModernStyleManager

logger = setup_logger()


class EfectivoTab(ttk.Frame):
    """Tab de gestión de efectivo y caja"""
    
    # Denominaciones disponibles (de mayor a menor)
    DENOMINACIONES = [
        ("Billete $1000", 1000),
        ("Billete $500", 500),
        ("Billete $200", 200),
        ("Billete $100", 100),
        ("Billete $50", 50),
        ("Billete $20", 20),
        ("Billete $10", 10),
        ("Billete $5", 5),
    ]
    
    def __init__(self, parent):
        super().__init__(parent)
        
        from Core.Common.config import load_config
        self.config_data = load_config()
        self.theme_name = self.config_data.get("theme", "solar")
        self.logger = setup_logger()
        
        # Estado de efectivo
        self.capital_fisico = Decimal(0)  # Dinero en caja
        self.capital_sistema = Decimal(0)  # Dinero registrado en sistema
        self.contador_billetes = {denom[1]: 0 for denom in self.DENOMINACIONES}
        
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main = BaseFrame(self, theme_name=self.theme_name)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title = StyledLabel(
            main,
            text="💰 GESTIÓN DE EFECTIVO Y CAJA",
            label_type="title",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 20))
        
        # ============================================
        # SECCIÓN 1: ENTRADA DE CAPITAL
        # ============================================
        entrada_card = CardFrame(main, title="➕ ENTRADA DE CAPITAL", theme_name=self.theme_name)
        entrada_card.pack(fill=tk.X, pady=(0, 15))
        
        entrada_frame = BaseFrame(entrada_card, theme_name=self.theme_name)
        entrada_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Capital inicial/extra
        capital_label = StyledLabel(
            entrada_frame,
            text="Capital Extra (Inyección de dinero):",
            label_type="normal",
            theme_name=self.theme_name
        )
        capital_label.pack(anchor="w", pady=(0, 5))
        
        capital_frame = BaseFrame(entrada_frame, theme_name=self.theme_name)
        capital_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.entry_capital_extra = StyledEntry(capital_frame, theme_name=self.theme_name, width=20)
        self.entry_capital_extra.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_capital_extra.bind("<Return>", lambda e: self.agregar_capital_extra())
        
        tk.Button(
            capital_frame,
            text="💵 Agregar",
            command=self.agregar_capital_extra,
            bg="#28a745", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), padx=15
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        

        # ============================================
        # SECCIÓN 2: CONTADOR DE BILLETES
        # ============================================
        contador_card = CardFrame(main, title="🧮 CONTADOR DE BILLETES", theme_name=self.theme_name)
        contador_card.pack(fill=tk.X, pady=(0, 15))
        
        contador_frame = BaseFrame(contador_card, theme_name=self.theme_name)
        contador_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Grid para billetes
        self.billetes_entries = {}
        self.billetes_subtotals = {}
        
        for idx, (label, valor) in enumerate(self.DENOMINACIONES):
            row = idx // 2
            col = idx % 2
            
            frame = BaseFrame(contador_frame, theme_name=self.theme_name)
            frame.grid(row=row, column=col, sticky="ew", padx=10, pady=8)
            
            # Label
            lbl = StyledLabel(
                frame,
                text=label,
                label_type="normal",
                theme_name=self.theme_name
            )
            lbl.pack(side=tk.LEFT, anchor="w", padx=(0, 10))
            
            # Spinbox para cantidad
            entry = tk.Spinbox(
                frame,
                from_=0,
                to=999,
                width=8,
                font=("Segoe UI", 10),
                command=self.actualizar_total_billetes
            )
            entry.pack(side=tk.LEFT, padx=(0, 10))
            self.billetes_entries[valor] = entry
            
            # Label para subtotal
            subtotal_lbl = StyledLabel(
                frame,
                text="= $0",
                label_type="small",
                theme_name=self.theme_name
            )
            subtotal_lbl.pack(side=tk.LEFT)
            self.billetes_subtotals[valor] = subtotal_lbl
        
        contador_frame.columnconfigure(0, weight=1)
        contador_frame.columnconfigure(1, weight=1)
        
        # Total de billetes
        total_billetes_frame = BaseFrame(contador_card, theme_name=self.theme_name)
        total_billetes_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        tk.Button(
            total_billetes_frame,
            text="🧮 Calcular Total",
            command=self.actualizar_total_billetes,
            bg="#ffc107", fg="black", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), padx=15
        ).pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.lbl_total_billetes = StyledLabel(
            total_billetes_frame,
            text="Total en billetes: $0.00",
            label_type="heading",
            theme_name=self.theme_name
        )
        self.lbl_total_billetes.set_accent()
        self.lbl_total_billetes.pack(side=tk.LEFT, padx=10)
        
        # ============================================
        # SECCIÓN 3: RESUMEN DE CAJA
        # ============================================
        resumen_card = CardFrame(main, title="📊 RESUMEN DE CAJA", theme_name=self.theme_name)
        resumen_card.pack(fill=tk.X, pady=(0, 15))
        
        resumen_frame = BaseFrame(resumen_card, theme_name=self.theme_name)
        resumen_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Capital físico
        capital_fis_label = StyledLabel(
            resumen_frame,
            text="💵 Capital Físico (en caja):",
            label_type="normal",
            theme_name=self.theme_name
        )
        capital_fis_label.pack(anchor="w", pady=(0, 5))
        
        self.lbl_capital_fisico = StyledLabel(
            resumen_frame,
            text="$0.00",
            label_type="heading",
            theme_name=self.theme_name
        )
        self.lbl_capital_fisico.set_accent()
        self.lbl_capital_fisico.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Capital en sistema
        capital_sis_label = StyledLabel(
            resumen_frame,
            text="💾 Capital en Sistema:",
            label_type="normal",
            theme_name=self.theme_name
        )
        capital_sis_label.pack(anchor="w", pady=(0, 5))
        
        self.lbl_capital_sistema = StyledLabel(
            resumen_frame,
            text="$0.00",
            label_type="heading",
            theme_name=self.theme_name
        )
        self.lbl_capital_sistema.set_accent()
        self.lbl_capital_sistema.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Diferencia
        diferencia_label = StyledLabel(
            resumen_frame,
            text="📈 Diferencia (Falta/Excedente):",
            label_type="normal",
            theme_name=self.theme_name
        )
        diferencia_label.pack(anchor="w", pady=(0, 5))
        
        self.lbl_diferencia = StyledLabel(
            resumen_frame,
            text="$0.00",
            label_type="heading",
            theme_name=self.theme_name
        )
        self.lbl_diferencia.set_accent()
        self.lbl_diferencia.pack(anchor="w", padx=20)
        
        # ============================================
        # SECCIÓN 4: MOVIMIENTOS
        # ============================================
        movimientos_card = CardFrame(main, title="📋 MOVIMIENTOS DE CAJA", theme_name=self.theme_name)
        movimientos_card.pack(fill=tk.BOTH, expand=True)
        
        cols = ("Fecha", "Tipo", "Monto", "Saldo")
        self.movimientos_tree = ttk.Treeview(movimientos_card, columns=cols, show="headings", height=8)
        
        for col in cols:
            self.movimientos_tree.heading(col, text=col)
        
        self.movimientos_tree.column("Fecha", width=150)
        self.movimientos_tree.column("Tipo", width=150)
        self.movimientos_tree.column("Monto", width=100, anchor=tk.E)
        self.movimientos_tree.column("Saldo", width=100, anchor=tk.E)
        
        self.movimientos_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def agregar_capital_extra(self):
        """Agrega capital extra (inyección de dinero)"""
        try:
            valor = self.entry_capital_extra.get().strip()
            if not valor:
                messagebox.showwarning("Aviso", "Ingresa un monto")
                return
            
            monto = Decimal(valor)
            if monto <= 0:
                raise ValueError("Monto debe ser mayor a 0")
            
            self.capital_fisico += monto
            self.capital_sistema += monto
            
            self.registrar_movimiento("Capital Extra", float(monto))
            self.entry_capital_extra.delete(0, END)
            self.actualizar_ui()
            
            messagebox.showinfo("✅", f"Capital extra agregado: ${float(monto):.2f}")
            logger.info(f"✅ Capital extra agregado: ${float(monto):.2f}")
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.error(f"Error agregando capital: {e}")
            messagebox.showerror("Error", str(e)[:100])
    
    def actualizar_total_billetes(self):
        """Actualiza el total de billetes contados"""
        total = Decimal(0)
        
        for valor, entry in self.billetes_entries.items():
            try:
                cantidad = int(entry.get() or 0)
                subtotal = Decimal(cantidad * valor)
                total += subtotal
                
                # Actualizar label de subtotal
                subtotal_lbl = self.billetes_subtotals.get(valor)
                if subtotal_lbl:
                    subtotal_lbl.config(text=f"= ${float(subtotal):.0f}")
            
            except ValueError:
                pass
        
        # Actualizar capital físico basado en billetes
        self.capital_fisico = total
        
        self.lbl_total_billetes.config(text=f"Total en billetes: ${float(total):.2f}")
        self.actualizar_ui()
    
    def registrar_movimiento(self, tipo: str, monto: float):
        """Registra un movimiento en el historial"""
        try:
            conn = get_connection()
            if not conn:
                logger.warning("No hay conexión para registrar movimiento")
                return
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO efectivo_movimientos (tipo, monto, saldo, fecha)
                    VALUES (%s, %s, %s, NOW())
                """, (tipo, round(monto, 2), round(float(self.capital_sistema), 2)))
            
            conn.commit()
            close_connection(conn)
            
            self.cargar_movimientos()
            logger.info(f"✅ Movimiento registrado: {tipo} - ${monto:.2f}")
        
        except Exception as e:
            logger.error(f"Error registrando movimiento: {e}")
            close_connection(conn)
    
    def actualizar_ui(self):
        """Actualiza los labels de resumen"""
        self.lbl_capital_fisico.config(text=f"${float(self.capital_fisico):.2f}")
        self.lbl_capital_sistema.config(text=f"${float(self.capital_sistema):.2f}")
        
        diferencia = self.capital_sistema - self.capital_fisico
        
        if diferencia > 0:
            color = "#d32f2f"  # Rojo (falta dinero)
            self.lbl_diferencia.config(
                text=f"Falta: ${float(abs(diferencia)):.2f}",
                foreground=color
            )
        elif diferencia < 0:
            color = "#388e3c"  # Verde (sobra dinero)
            self.lbl_diferencia.config(
                text=f"Excedente: ${float(abs(diferencia)):.2f}",
                foreground=color
            )
        else:
            self.lbl_diferencia.config(text="✅ Cuadre perfecto", foreground="#4caf50")
    
    def cargar_datos(self):
        """Carga datos desde BD"""
        try:
            conn = get_connection()
            if not conn:
                return
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(monto), 0) as total
                    FROM efectivo_movimientos
                    WHERE tipo IN ('Capital Extra')
                """)
                
                resultado = cursor.fetchone()
                self.capital_sistema = Decimal(str(resultado.get('total', 0) or 0))
            
            close_connection(conn)
            
            self.cargar_movimientos()
            self.actualizar_ui()
        
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
    
    def cargar_movimientos(self):
        """Carga el historial de movimientos"""
        try:
            # Limpiar tabla
            for item in self.movimientos_tree.get_children():
                self.movimientos_tree.delete(item)
            
            conn = get_connection()
            if not conn:
                return
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT fecha, tipo, monto, saldo
                    FROM efectivo_movimientos
                    ORDER BY fecha DESC
                    LIMIT 50
                """)
                
                movimientos = cursor.fetchall() or []
            
            close_connection(conn)
            
            for mov in movimientos:
                self.movimientos_tree.insert("", tk.END, values=(
                    str(mov.get('fecha'))[:16],
                    mov.get('tipo'),
                    f"${float(mov.get('monto', 0)):.2f}",
                    f"${float(mov.get('saldo', 0)):.2f}"
                ))
        
        except Exception as e:
            logger.error(f"Error cargando movimientos: {e}")