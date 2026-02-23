# Core/Styles/base_components.py - Componentes reutilizables y compatibles

import tkinter as tk
from ttkbootstrap import Label, Entry, Combobox
from Core.Styles.modern_styles import ModernStyleManager

class BaseFrame(tk.Frame):
    """Frame base con background coherente según el tema"""
    
    def __init__(self, parent, theme_name=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_name = theme_name or "solar"
        self.bg_color = ModernStyleManager.get_bg_color(self.theme_name)
        self.fg_color = ModernStyleManager.get_fg_color(self.theme_name)
        self.accent_color = ModernStyleManager.get_accent_color(self.theme_name)
        self.configure(bg=self.bg_color)


class MenuFrame(tk.Frame):
    """Frame especial para menús laterales"""
    
    def __init__(self, parent, theme_name=None, width=280, **kwargs):
        super().__init__(parent, width=width, **kwargs)
        self.theme_name = theme_name or "solar"
        self.bg_color = ModernStyleManager.get_bg_color(self.theme_name)
        self.fg_color = ModernStyleManager.get_fg_color(self.theme_name)
        self.accent_color = ModernStyleManager.get_accent_color(self.theme_name)
        self.configure(bg=self.bg_color)
        self.pack_propagate(False)


class StyledLabel(Label):
    """Label con estilos consistentes según el tema - COMPATIBLE CON TKINTER Y TTKBOOTSTRAP"""
    
    LABEL_TYPES = {
        "title": ("Segoe UI", 20, "bold"),
        "heading": ("Segoe UI", 14, "bold"),
        "normal": ("Segoe UI", 10),
        "small": ("Segoe UI", 8),
        "info": ("Segoe UI", 7),
    }
    
    def __init__(self, parent, text="", label_type="normal", theme_name=None, **kwargs):
        # Remover opciones que pueden causar conflicto
        kwargs.pop('width', None)
        kwargs.pop('height', None)
        kwargs.pop('wraplength', None)
        
        super().__init__(parent, text=text, **kwargs)
        
        self.theme_name = theme_name or "solar"
        self.bg_color = ModernStyleManager.get_bg_color(self.theme_name)
        self.fg_color = ModernStyleManager.get_fg_color(self.theme_name)
        self.accent_color = ModernStyleManager.get_accent_color(self.theme_name)
        
        # Aplicar font según tipo
        font = self.LABEL_TYPES.get(label_type, self.LABEL_TYPES["normal"])
        self.configure(
            font=font,
            background=self.bg_color,
            foreground=self.fg_color
        )
    
    def set_accent(self):
        """Cambia el color al color de acentuación"""
        self.configure(foreground=self.accent_color)
    
    def set_foreground(self, color):
        """Cambia el color de texto"""
        self.configure(foreground=color)
    
    def set_background(self, color):
        """Cambia el background"""
        self.configure(background=color)


class StyledEntry(Entry):
    """Entry con estilos consistentes"""
    
    def __init__(self, parent, theme_name=None, width=30, **kwargs):
        super().__init__(parent, width=width, **kwargs)
        self.theme_name = theme_name or "solar"


class StyledCombobox(Combobox):
    """Combobox con estilos consistentes"""
    
    def __init__(self, parent, theme_name=None, width=25, **kwargs):
        super().__init__(parent, width=width, **kwargs)
        self.theme_name = theme_name or "solar"


class FormRow(tk.Frame):
    """Fila de formulario con label y entrada"""
    
    def __init__(self, parent, label_text="", theme_name=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.theme_name = theme_name or "solar"
        self.bg_color = ModernStyleManager.get_bg_color(self.theme_name)
        self.configure(bg=self.bg_color)
        
        # Label sin parámetros conflictivos
        label = StyledLabel(
            self, 
            text=label_text, 
            label_type="normal",
            theme_name=self.theme_name
        )
        label.pack(side="left", anchor="w", padx=(0, 10))
        
        self.entry = StyledEntry(self, theme_name=self.theme_name)
        self.entry.pack(side="left", fill="both", expand=True, padx=5)
    
    def get(self):
        """Obtiene el valor de la entrada"""
        return self.entry.get()
    
    def set(self, value):
        """Establece el valor de la entrada"""
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))


class InfoFrame(tk.Frame):
    """Frame para mostrar información con múltiples labels"""
    
    def __init__(self, parent, title="", items=None, theme_name=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.theme_name = theme_name or "solar"
        self.bg_color = ModernStyleManager.get_bg_color(self.theme_name)
        self.configure(bg=self.bg_color)
        
        if title:
            title_label = StyledLabel(
                self,
                text=title,
                label_type="small",
                theme_name=self.theme_name
            )
            title_label.set_accent()
            title_label.pack(anchor="w", pady=(0, 5))
        
        if items:
            for item in items:
                item_label = StyledLabel(
                    self,
                    text=item,
                    label_type="info",
                    theme_name=self.theme_name
                )
                item_label.pack(anchor="w")


class CardFrame(tk.LabelFrame):
    """Frame tipo tarjeta para secciones"""
    
    def __init__(self, parent, title="", theme_name=None, **kwargs):
        # Filtrar kwargs para evitar pasar 'padding' a tk.LabelFrame
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'padding'}
        
        super().__init__(parent, text=title, **filtered_kwargs)
        
        self.theme_name = theme_name or "solar"
        self.bg_color = ModernStyleManager.get_bg_color(self.theme_name)
        self.fg_color = ModernStyleManager.get_fg_color(self.theme_name)
        self.accent_color = ModernStyleManager.get_accent_color(self.theme_name)
        
        self.configure(
            bg=self.bg_color,
            fg=self.fg_color,
            relief="flat",
            borderwidth=1,
            padx=12,
            pady=10
        )


class SeparatorFrame(tk.Frame):
    """Frame separador con altura personalizable"""
    
    def __init__(self, parent, height=20, theme_name=None, **kwargs):
        super().__init__(parent, height=height, **kwargs)
        
        self.theme_name = theme_name or "solar"
        bg_color = ModernStyleManager.get_bg_color(self.theme_name)
        self.configure(bg=bg_color)
        self.pack_propagate(False)


# Funciones helper para crear layouts comunes

def create_form_row(parent, label_text, theme_name=None):
    """Crea una fila de formulario y retorna la entrada"""
    row = FormRow(parent, label_text=label_text, theme_name=theme_name)
    row.pack(fill="x", padx=6, pady=5)
    return row.entry


def create_labeled_frame(parent, title, theme_name=None):
    """Crea un frame etiquetado (Card)"""
    card = CardFrame(parent, title=title, theme_name=theme_name)
    card.pack(fill="x", pady=(0, 10), padx=5)
    return card


def create_info_section(parent, title, items, theme_name=None):
    """Crea una sección de información"""
    info = InfoFrame(parent, title=title, items=items, theme_name=theme_name)
    info.pack(fill="x", padx=10, pady=5)
    return info