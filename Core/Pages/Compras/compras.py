"""
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
Core.Pages.Compras.compras - Interfaz de gestión de compras
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
"""
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH
from ttkbootstrap import Frame, StringVar, Radiobutton, Treeview
from tkinter import messagebox, END, ttk
import tkinter as tk

from Core.Backends.compras_backend import ComprasBackend
from Core.Common.units import get_unit_choices
from Core.Common.logger import setup_logger
from Core.Common.validators import FormValidator
from Core.Common.constants import COLOR_SUCCESS, COLOR_PRIMARY
from Core.Styles.modern_styles import ModernStyleManager
from Core.Styles.base_components import (
    BaseFrame, StyledLabel, StyledEntry, StyledCombobox,
    CardFrame, FormRow
)

logger = setup_logger()


class ComprasFrame(BaseFrame):
    """Frame de gestión de compras"""
    
    def __init__(self, parent):
        from Core.Common.config import load_config
        config = load_config()
        theme = config.get("theme", "solar")
        
        super().__init__(parent, theme_name=theme)
        
        self.backend = ComprasBackend()
        self.logger = setup_logger()
        self.tipo_var = StringVar(value="granel")
        
        ModernStyleManager.configure_modern_styles(self.winfo_toplevel().style, theme)
        
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        """Configura la interfaz"""
        
        # Header
        title = StyledLabel(
            self,
            text="🛒 Gestión de Compras",
            label_type="title",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 20), padx=20)
        
        # Selector de tipo
        type_frame = BaseFrame(self, theme_name=self.theme_name)
        type_frame.pack(fill=X, padx=20, pady=(0, 15))
        
        type_label = StyledLabel(
            type_frame,
            text="Tipo de compra:",
            label_type="normal",
            theme_name=self.theme_name
        )
        type_label.pack(side=LEFT, padx=(0, 15))
        
        Radiobutton(
            type_frame,
            text="📦 Granel",
            variable=self.tipo_var,
            value="granel",
            command=self.update_fields,
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 15))
        
        Radiobutton(
            type_frame,
            text="📫 Paquetes",
            variable=self.tipo_var,
            value="paquetes",
            command=self.update_fields,
            bootstyle="success"
        ).pack(side=LEFT)
        
        # Formulario
        form_frame = CardFrame(self, title="📝 Datos de Compra", theme_name=self.theme_name)
        form_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Campos comunes
        nombre_row = FormRow(form_frame, "Producto:", theme_name=self.theme_name)
        nombre_row.pack(fill=X, padx=6, pady=5)
        self.nombre_entry = nombre_row.entry
        
        proveedor_row = FormRow(form_frame, "Proveedor:", theme_name=self.theme_name)
        proveedor_row.pack(fill=X, padx=6, pady=5)
        self.proveedor_entry = proveedor_row.entry
        
        # Frames dinámicos
        self.granel_frame = BaseFrame(form_frame, theme_name=self.theme_name)
        self.paquetes_frame = BaseFrame(form_frame, theme_name=self.theme_name)
        
        # === GRANEL ===
        granel_label1 = StyledLabel(
            self.granel_frame,
            text="Cantidad:",
            label_type="small",
            theme_name=self.theme_name
        )
        granel_label1.grid(row=0, column=0, sticky="w", pady=8, padx=6)
        
        self.cantidad_entry = StyledEntry(self.granel_frame, theme_name=self.theme_name, width=15)
        self.cantidad_entry.grid(row=0, column=1, padx=6, sticky="ew")
        
        granel_label2 = StyledLabel(
            self.granel_frame,
            text="Unidad:",
            label_type="small",
            theme_name=self.theme_name
        )
        granel_label2.grid(row=0, column=2, sticky="w", padx=6)
        
        self.unidad_combo = StyledCombobox(
            self.granel_frame,
            values=get_unit_choices(),
            theme_name=self.theme_name,
            width=12,
            state="readonly"
        )
        self.unidad_combo.grid(row=0, column=3, padx=6, sticky="ew")
        
        granel_label3 = StyledLabel(
            self.granel_frame,
            text="Precio/Unidad:",
            label_type="small",
            theme_name=self.theme_name
        )
        granel_label3.grid(row=1, column=0, sticky="w", pady=8, padx=6)
        
        self.precio_entry = StyledEntry(self.granel_frame, theme_name=self.theme_name, width=15)
        self.precio_entry.grid(row=1, column=1, padx=6, sticky="ew")
        
        self.granel_frame.columnconfigure(1, weight=1)
        self.granel_frame.columnconfigure(3, weight=1)
        
        # === PAQUETES ===
        paq_label1 = StyledLabel(
            self.paquetes_frame,
            text="# Paquetes:",
            label_type="small",
            theme_name=self.theme_name
        )
        paq_label1.grid(row=0, column=0, sticky="w", pady=8, padx=6)
        
        self.cantidad_paq_entry = StyledEntry(self.paquetes_frame, theme_name=self.theme_name, width=15)
        self.cantidad_paq_entry.grid(row=0, column=1, padx=6, sticky="ew")
        
        paq_label2 = StyledLabel(
            self.paquetes_frame,
            text="Precio/Paq:",
            label_type="small",
            theme_name=self.theme_name
        )
        paq_label2.grid(row=0, column=2, sticky="w", padx=6)
        
        self.precio_paq_entry = StyledEntry(self.paquetes_frame, theme_name=self.theme_name, width=15)
        self.precio_paq_entry.grid(row=0, column=3, padx=6, sticky="ew")
        
        paq_label3 = StyledLabel(
            self.paquetes_frame,
            text="Peso/Paq:",
            label_type="small",
            theme_name=self.theme_name
        )
        paq_label3.grid(row=1, column=0, sticky="w", pady=8, padx=6)
        
        self.peso_paq_entry = StyledEntry(self.paquetes_frame, theme_name=self.theme_name, width=15)
        self.peso_paq_entry.grid(row=1, column=1, padx=6, sticky="ew")
        
        paq_label4 = StyledLabel(
            self.paquetes_frame,
            text="Unidad:",
            label_type="small",
            theme_name=self.theme_name
        )
        paq_label4.grid(row=1, column=2, sticky="w", padx=6)
        
        self.unidad_peso_combo = StyledCombobox(
            self.paquetes_frame,
            values=get_unit_choices(),
            theme_name=self.theme_name,
            width=12,
            state="readonly"
        )
        self.unidad_peso_combo.grid(row=1, column=3, padx=6, sticky="ew")
        
        self.paquetes_frame.columnconfigure(1, weight=1)
        self.paquetes_frame.columnconfigure(3, weight=1)
        
        self.update_fields()
        
        # Botones
        btn_frame = BaseFrame(self, theme_name=self.theme_name)
        btn_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        tk.Button(
            btn_frame,
            text="💾 Guardar",
            command=self.save_purchase,
            bg=COLOR_SUCCESS, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold")
        ).pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        tk.Button(
            btn_frame,
            text="🔄 Recargar",
            command=self.load_history,
            bg=COLOR_PRIMARY, fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold")
        ).pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        tk.Button(
            btn_frame,
            text="🗑️ Limpiar",
            command=self.clear_form,
            bg="#ffc107", fg="black", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold")
        ).pack(side=LEFT, fill=X, expand=True)
        
        # Historial
        hist_label = StyledLabel(
            self,
            text="📊 Historial de Compras",
            label_type="heading",
            theme_name=self.theme_name
        )
        hist_label.set_accent()
        hist_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        cols = ("Producto", "Cantidad", "Unidad", "Precio", "Total", "Proveedor", "Tipo", "Fecha")
        
        self.history_tree = Treeview(
            self,
            columns=cols,
            show="headings",
            height=12
        )
        
        for col in cols:
            self.history_tree.heading(col, text=col)
            width = 150 if col == "Producto" else (80 if col in ("Cantidad", "Precio", "Total") else 70)
            self.history_tree.column(col, width=width)
        
        self.history_tree.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
    
    def update_fields(self):
        """Actualiza campos según tipo de compra"""
        if self.tipo_var.get() == "granel":
            self.granel_frame.pack(fill=X, padx=6, pady=10)
            self.paquetes_frame.pack_forget()
        else:
            self.paquetes_frame.pack(fill=X, padx=6, pady=10)
            self.granel_frame.pack_forget()
    
    def save_purchase(self):
        """Guarda una compra"""
        nombre = self.nombre_entry.get().strip()
        proveedor = self.proveedor_entry.get().strip()
        tipo = self.tipo_var.get()
        
        # Validaciones
        is_valid, msg = FormValidator.validate_required(nombre, "Producto")
        if not is_valid:
            messagebox.showwarning("Validación", msg)
            return
        
        is_valid, msg = FormValidator.validate_required(proveedor, "Proveedor")
        if not is_valid:
            messagebox.showwarning("Validación", msg)
            return
        
        try:
            if tipo == "granel":
                cantidad = self.cantidad_entry.get().strip()
                unidad = self.unidad_combo.get()
                precio = self.precio_entry.get().strip()
                
                is_valid, msg = FormValidator.validate_number(cantidad, "Cantidad")
                if not is_valid:
                    messagebox.showwarning("Validación", msg)
                    return
                
                is_valid, msg = FormValidator.validate_number(precio, "Precio")
                if not is_valid:
                    messagebox.showwarning("Validación", msg)
                    return
                
                if not unidad:
                    messagebox.showwarning("Validación", "Selecciona una unidad")
                    return
                
                self.backend.save_purchase(
                    tipo="granel",
                    nombre=nombre,
                    proveedor=proveedor,
                    cantidad=float(cantidad),
                    unidad=unidad,
                    precio_compra=float(precio)
                )
            
            else:  # paquetes
                cantidad_paq = self.cantidad_paq_entry.get().strip()
                precio_paq = self.precio_paq_entry.get().strip()
                peso_paq = self.peso_paq_entry.get().strip()
                unidad_peso = self.unidad_peso_combo.get()
                
                for val, name in [(cantidad_paq, "Cantidad paquetes"), (precio_paq, "Precio/paquete"), (peso_paq, "Peso/paquete")]:
                    is_valid, msg = FormValidator.validate_number(val, name)
                    if not is_valid:
                        messagebox.showwarning("Validación", msg)
                        return
                
                if not unidad_peso:
                    messagebox.showwarning("Validación", "Selecciona una unidad")
                    return
                
                self.backend.save_purchase(
                    tipo="paquetes",
                    nombre=nombre,
                    proveedor=proveedor,
                    cantidad_paq=int(float(cantidad_paq)),
                    precio_paq=float(precio_paq),
                    peso_paq=float(peso_paq),
                    unidad_peso=unidad_peso
                )
            
            messagebox.showinfo("✅ Éxito", "Compra guardada correctamente")
            self.clear_form()
            self.load_history()
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error: {e}")
            self.logger.error(f"Error guardando compra: {e}")
    
    def load_history(self):
        """Carga historial de compras"""
        try:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            history = self.backend.get_purchase_history()
            for p in history:
                self.history_tree.insert(
                    "",
                    END,
                    values=(
                        p.get("producto"),
                        f"{p.get('cantidad')}",
                        p.get("unidad"),
                        f"${float(p.get('precio_compra', 0)):.2f}",
                        f"${float(p.get('precio_total', 0)):.2f}",
                        p.get("proveedor"),
                        p.get("tipo"),
                        str(p.get("fecha", ""))[:10]
                    )
                )
        except Exception as e:
            self.logger.error(f"Error cargando historial: {e}")
    
    def clear_form(self):
        """Limpia el formulario"""
        for widget in [
            self.nombre_entry,
            self.proveedor_entry,
            self.cantidad_entry,
            self.precio_entry,
            self.cantidad_paq_entry,
            self.precio_paq_entry,
            self.peso_paq_entry
        ]:
            widget.delete(0, END)
        
        for combo in [self.unidad_combo, self.unidad_peso_combo]:
            combo.set("")