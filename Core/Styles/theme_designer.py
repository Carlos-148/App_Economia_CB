"""
Core.Styles.theme_designer - Diseñador visual de temas
"""

import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
from ttkbootstrap import Toplevel, Label, Entry, Button, Combobox, Scrollbar
from ttkbootstrap.constants import *
import json

from Core.Styles.theme_manager import CustomThemeManager, ThemePreset
from Core.Common.logger import setup_logger
from Core.Styles.base_components import BaseFrame, StyledLabel

logger = setup_logger()


class ThemeDesignerWindow(Toplevel):
    """
    Ventana del diseñador visual de temas.
    
    Permite:
    - Editar componentes
    - Seleccionar colores
    - Previsualizar cambios
    - Guardar temas
    """
    
    def __init__(self, parent, root_style, on_theme_save=None):
        """
        Inicializa la ventana del diseñador.
        
        Args:
            parent: Ventana padre
            root_style: Objeto Style
            on_theme_save: Callback cuando se guarda
        """
        super().__init__(parent)
        self.title("🎨 Diseñador de Temas")
        self.geometry("900x700")
        
        self.root_style = root_style
        self.on_theme_save = on_theme_save
        self.current_theme = CustomThemeManager.DEFAULT_COMPONENTS.copy()
        self.color_pickers = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        
        # Header
        header = BaseFrame(self, theme_name="solar")
        header.pack(fill=BOTH, padx=15, pady=15)
        
        title = StyledLabel(
            header,
            text="🎨 Editor de Temas Personalizado",
            label_type="heading",
            theme_name="solar"
        )
        title.set_accent()
        title.pack(anchor=WEST)
        
        # Selector de presets
        preset_frame = BaseFrame(self, theme_name="solar")
        preset_frame.pack(fill=X, padx=10, pady=10)
        
        preset_label = StyledLabel(
            preset_frame,
            text="📋 Presets:",
            label_type="normal",
            theme_name="solar"
        )
        preset_label.pack(anchor=WEST)
        
        preset_combo_frame = BaseFrame(preset_frame, theme_name="solar")
        preset_combo_frame.pack(fill=X, pady=5)
        
        self.preset_combo = Combobox(
            preset_combo_frame,
            values=ThemePreset.list_presets(),
            state="readonly",
            width=30
        )
        self.preset_combo.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        
        Button(
            preset_combo_frame,
            text="Cargar Preset",
            command=self.load_preset,
            bootstyle="info"
        ).pack(side=LEFT, padx=2)
        
        # Canvas scrollable
        main_frame = BaseFrame(self, theme_name="solar")
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame, highlightthickness=0, bg="#f8f9fa")
        scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
        
        self.scrollable_frame = BaseFrame(canvas, theme_name="solar")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg="#f8f9fa")
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Controles de componentes
        for component, settings in CustomThemeManager.DEFAULT_COMPONENTS.items():
            self._create_component_editor(self.scrollable_frame, component, settings)
        
        # Botones de acción
        button_frame = BaseFrame(self, theme_name="solar")
        button_frame.pack(fill=X, side=BOTTOM, padx=10, pady=10)
        
        tk.Button(
            button_frame,
            text="👁️ Vista Previa",
            command=self.preview_theme,
            bg="#17a2b8",
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0
        ).pack(side=LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="💾 Guardar Tema",
            command=self.save_theme_dialog,
            bg="#28a745",
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0
        ).pack(side=LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📤 Exportar",
            command=self.export_theme,
            bg="#ffc107",
            fg="black",
            relief="flat",
            cursor="hand2",
            bd=0
        ).pack(side=LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cerrar",
            command=self.destroy,
            bg="#dc3545",
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0
        ).pack(side=RIGHT, padx=5)
    
    def _create_component_editor(self, parent, component_name: str, settings: dict):
        """Crea editor para un componente"""
        comp_frame = BaseFrame(parent, theme_name="solar")
        comp_frame.configure(relief="solid", borderwidth=1)
        comp_frame.pack(fill=X, pady=5, padx=5)
        
        comp_label = StyledLabel(
            comp_frame,
            text=f"📌 {component_name}",
            label_type="normal",
            theme_name="solar"
        )
        comp_label.set_accent()
        comp_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        for prop, value in settings.items():
            self._create_property_editor(comp_frame, component_name, prop, value)
    
    def _create_property_editor(self, parent, component: str, prop_name: str, default_value):
        """Crea editor para una propiedad"""
        prop_frame = BaseFrame(parent, theme_name="solar")
        prop_frame.pack(fill=X, pady=5, padx=10)
        
        prop_label = StyledLabel(
            prop_frame,
            text=f"{prop_name}:",
            label_type="small",
            theme_name="solar"
        )
        prop_label.pack(side=LEFT, anchor=WEST, width=100)
        
        if prop_name in ["background", "foreground", "color"]:
            color_button = tk.Button(
                prop_frame,
                text="🎨 Color",
                command=lambda: self.pick_color(component, prop_name),
                bg="#007bff",
                fg="white",
                relief="flat",
                cursor="hand2",
                bd=0,
                width=20
            )
            color_button.pack(side=LEFT, padx=5)
            self.color_pickers[f"{component}_{prop_name}"] = color_button
        
        else:
            text_entry = Entry(prop_frame, width=30)
            text_entry.insert(0, str(default_value))
            text_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
    
    def pick_color(self, component: str, prop_name: str):
        """Abre selector de color"""
        color = colorchooser.askcolor(title=f"Color - {component}")[1]
        
        if color:
            if component not in self.current_theme:
                self.current_theme[component] = {}
            
            self.current_theme[component][prop_name] = color
            
            button = self.color_pickers.get(f"{component}_{prop_name}")
            if button:
                button.configure(
                    bg=color,
                    fg="#ffffff" if self._is_dark(color) else "#000000"
                )
    
    @staticmethod
    def _is_dark(color_hex: str) -> bool:
        """Determina si un color es oscuro"""
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        return (r*299 + g*587 + b*114) / 1000 < 128
    
    def load_preset(self):
        """Carga un preset"""
        preset_name = self.preset_combo.get()
        
        if preset_name:
            self.current_theme = ThemePreset.get_preset(preset_name).copy()
            messagebox.showinfo("✓", f"Preset '{preset_name}' cargado")
    
    def preview_theme(self):
        """Previsualiza el tema"""
        try:
            CustomThemeManager.apply_custom_theme(self.root_style, self.current_theme)
            messagebox.showinfo("✓ Vista Previa", "Tema aplicado a la vista previa")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)[:100]}")
    
    def save_theme_dialog(self):
        """Abre diálogo para guardar tema"""
        dialog = Toplevel(self)
        dialog.title("Guardar Tema")
        dialog.geometry("400x150")
        dialog.transient(self)
        
        dialog_frame = BaseFrame(dialog, theme_name="solar")
        dialog_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        label = StyledLabel(
            dialog_frame,
            text="Nombre del tema:",
            label_type="normal",
            theme_name="solar"
        )
        label.pack(pady=10)
        
        name_entry = Entry(dialog_frame, width=40)
        name_entry.pack(pady=5, padx=10, fill=X)
        
        def save():
            theme_name = name_entry.get().strip()
            
            if not theme_name:
                messagebox.showwarning("Validación", "Ingresa un nombre")
                return
            
            try:
                CustomThemeManager.save_custom_theme(theme_name, self.current_theme)
                messagebox.showinfo("✓ Éxito", f"Tema '{theme_name}' guardado")
                
                if self.on_theme_save:
                    self.on_theme_save(theme_name)
                
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)[:100]}")
        
        tk.Button(
            dialog_frame,
            text="Guardar",
            command=save,
            bg="#28a745",
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            width=20
        ).pack(pady=10)
    
    def export_theme(self):
        """Exporta tema a archivo"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_theme, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("✓ Exportado", f"Tema exportado a {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)[:100]}")