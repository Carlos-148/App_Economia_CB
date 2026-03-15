"""
Main.py - Punto de entrada de la aplicación
Aplicación de Gestión de Economía v3.2 - Moderna
"""

import sys
import os
from pathlib import Path

# Asegurar que el directorio actual está en el path
sys.path.insert(0, str(Path(__file__).parent))

from ttkbootstrap import Window
from ttkbootstrap.constants import *
from tkinter import messagebox

from Core.Common.logger import setup_logger
from Core.Common.config import load_config, save_config, get_db_config
from Core.Common.constants import (
    APP_TITLE, DEFAULT_THEME, AVAILABLE_THEMES, DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT, MENU_WIDTH, MENU_ITEMS, COLOR_PRIMARY, COLOR_DANGER,
    COLOR_INFO
)

from Core.Styles.modern_styles import ModernStyleManager
from Core.Styles.base_components import (
    MenuFrame, StyledLabel, InfoFrame, SeparatorFrame, BaseFrame
)
from Core.Styles.theme_manager import CustomThemeManager

# Pages
from Core.Pages.Resumenes.resumen import ResumenesFrame
from Core.Pages.Compras.compras import ComprasFrame
from Core.Pages.Produccion.produccion import ProduccionFrame
from Core.Pages.Ventas.ventas import VentasFrame
from Core.Pages.Productos.productos import ProductosFrame
from Core.Pages.Gastos.gastos import GastosFrame
from Core.Pages.Settings.settings import SettingsFrame

from Core.Common.database import DatabaseManager
from Core.Pages.Settings.setup_inicial import SetupInicial
from Core.Common.database import revisar_setup_completado

logger = setup_logger()


class MainApplication:
    """
    Aplicación principal de gestión de economía.
    
    Características:
    - Dashboard moderno con ttkbootstrap
    - Sistema de temas personalizable
    - Gestión de múltiples módulos
    - Caché inteligente
    - Logging completo
    """
    
    PAGES = {
        "compras": ComprasFrame,
        "resumenes": ResumenesFrame,
        "produccion": ProduccionFrame,
        "ventas": VentasFrame,
        "gastos": GastosFrame,
        "productos": ProductosFrame,
        "settings": SettingsFrame, # Se carga dinámicamente
    }
    
    def __init__(self, root):
        """
        Inicializa la aplicación.
        
        Args:
            root: Ventana raíz de ttkbootstrap
        """
        
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.root.minsize(1200, 700)
        
        if not revisar_setup_completado():
            setup_window = SetupInicial(root)
            root.wait_window(setup_window)
        # Estado de la aplicación
        self.logger = setup_logger()
        self.config = load_config()
        self.current_page = None
        self.current_page_name = None
        self.current_theme = self.config.get("theme", DEFAULT_THEME)
        
        # Validar tema
        if self.current_theme not in AVAILABLE_THEMES:
            self.current_theme = DEFAULT_THEME
            self.config["theme"] = self.current_theme
            save_config(self.config)
        
        # Aplicar estilos
        ModernStyleManager.configure_modern_styles(self.root.style, self.current_theme)
        
        # Colores del tema
        self.menu_bg = ModernStyleManager.get_bg_color(self.current_theme)
        self.menu_fg = ModernStyleManager.get_fg_color(self.current_theme)
        self.accent = ModernStyleManager.get_accent_color(self.current_theme)
        
        # Log de inicio
        self.logger.info("=" * 70)
        self.logger.info("🚀 APLICACIÓN INICIADA")
        self.logger.info(f"📱 Versión: {self.config.get('version', '3.2')}")
        self.logger.info(f"🎨 Tema: {self.current_theme}")
        self.logger.info(f"👤 Usuario: {self.config.get('user', {}).get('name', 'N/A')}")
        self.logger.info("=" * 70)
        
        # Inicializar BD
        self._initialize_database()
        
        # Configurar UI
        self.setup_ui()
        
        # Mostrar página inicial
        self.show_page("compras")
        
        # Bindings
        self.root.bind("<Escape>", self.confirm_exit)
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
    
    def _initialize_database(self):
        """Inicializa la base de datos"""
        try:
            if not DatabaseManager.initialize_database():
                messagebox.showerror(
                    "❌ Error de BD",
                    "No se pudo inicializar la base de datos.\n"
                    "Verifica la configuración."
                )
                sys.exit(1)
        except Exception as e:
            self.logger.error(f"❌ Error inicializando BD: {e}")
            messagebox.showerror("❌ Error", f"Error de BD: {e}")
            sys.exit(1)
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # === MENÚ LATERAL ===
        self.menu_frame = MenuFrame(
            self.root,
            theme_name=self.current_theme,
            width=MENU_WIDTH
        )
        self.menu_frame.pack(side=LEFT, fill=Y, padx=(10, 5), pady=10)
        
        # Logo
        self._create_logo()
        
        SeparatorFrame(self.menu_frame, height=10, theme_name=self.current_theme).pack()
        
        # Botones del menú
        for label, page_name in MENU_ITEMS:
            self._create_menu_button(label, page_name)
        
        SeparatorFrame(self.menu_frame, height=20, theme_name=self.current_theme).pack()
        
        # Información
        info_items = [
            "✅ Temas Personalizables",
            "✅ Análisis Avanzados",
            "✅ Base de Datos Robusta",
            "✅ Logging Completo"
        ]
        info = InfoFrame(
            self.menu_frame,
            title="ℹ️ CARACTERÍSTICAS",
            items=info_items,
            theme_name=self.current_theme
        )
        info.pack(fill=X, padx=10)
        
        # Espaciador
        SeparatorFrame(self.menu_frame, height=40, theme_name=self.current_theme).pack(expand=True)
        
        # === BOTONES INFERIORES ===
        self._create_bottom_buttons()
        
        # === CONTENIDO PRINCIPAL ===
        self.content_frame = BaseFrame(self.root, theme_name=self.current_theme)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
    
    def _create_logo(self):
        """Crea la sección del logo"""
        logo_frame = MenuFrame(self.menu_frame, theme_name=self.current_theme)
        logo_frame.pack(fill=X, pady=(20, 10), padx=10)
        
        logo_emoji = StyledLabel(
            logo_frame,
            text="📱",
            label_type="title",
            theme_name=self.current_theme
        )
        logo_emoji.set_accent()
        logo_emoji.pack()
        
        logo_title = StyledLabel(
            logo_frame,
            text="ECONOMÍA",
            label_type="heading",
            theme_name=self.current_theme
        )
        logo_title.set_accent()
        logo_title.pack()
        
        logo_version = StyledLabel(
            logo_frame,
            text="v3.2 Premium",
            label_type="small",
            theme_name=self.current_theme
        )
        logo_version.pack()
    
    def _create_menu_button(self, label: str, page_name: str):
        """Crea un botón del menú"""
        import tkinter as tk
        
        btn = tk.Button(
            self.menu_frame,
            text=label,
            command=lambda: self.show_page(page_name),
            width=26,
            relief="flat",
            cursor="hand2",
            bg=COLOR_PRIMARY,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            activebackground="#0056b3",
            activeforeground="white",
            bd=0,
            highlightthickness=0
        )
        btn.pack(pady=5, padx=10, fill=X)
    
    def _create_bottom_buttons(self):
        """Crea botones inferiores"""
        import tkinter as tk
        
        reload_btn = tk.Button(
            self.menu_frame,
            text="🔄 Recargar",
            command=self.reload_app,
            width=26,
            relief="flat",
            cursor="hand2",
            bg=COLOR_INFO,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            activebackground="#138496",
            activeforeground="white",
            bd=0,
            highlightthickness=0
        )
        reload_btn.pack(pady=5, padx=10, fill=X, side=BOTTOM)
        
        exit_btn = tk.Button(
            self.menu_frame,
            text="🚪 Salir",
            command=self.confirm_exit,
            width=26,
            relief="flat",
            cursor="hand2",
            bg=COLOR_DANGER,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            activebackground="#c82333",
            activeforeground="white",
            bd=0,
            highlightthickness=0
        )
        exit_btn.pack(pady=5, padx=10, fill=X, side=BOTTOM)
    
    def show_page(self, page_name: str) -> bool:
        """
        Muestra una página específica.
        
        Args:
            page_name: Nombre de la página
            
        Returns:
            bool: True si fue exitoso
        """
        # Validar página
        if page_name not in self.PAGES:
            self.logger.warning(f"⚠️ Página desconocida: {page_name}")
            messagebox.showwarning("Aviso", "Página no encontrada")
            return False
        
        # Si es la página actual, no recargar
        if self.current_page_name == page_name and self.current_page:
            return True
        
        # Destruir página anterior
        if self.current_page:
            try:
                self.current_page.destroy()
            except Exception as e:
                self.logger.error(f"Error destruyendo página: {e}")
        
        # Cargar nueva página
        try:
            if page_name == "settings":
                from Core.Common.config import load_config as settings_loader
                from Core.Pages.Settings.settings import SettingsFrame
                PageClass = SettingsFrame
            else:
                PageClass = self.PAGES[page_name]
            
            self.current_page = PageClass(self.content_frame)
            self.current_page.pack(fill=BOTH, expand=True)
            self.current_page_name = page_name
            
            self.logger.info(f"✅ Página cargada: {page_name.upper()}")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Error cargando {page_name}: {e}")
            messagebox.showerror(
                "❌ Error",
                f"Error cargando página:\n{str(e)[:100]}"
            )
            return False
    
    def reload_app(self):
        """Recarga la aplicación"""
        self.logger.info("🌀 Recargando aplicación...")
        messagebox.showinfo(
            "🔄 Recarga",
            "La aplicación se reiniciará en 1 segundos..."
        )
        self.root.after(1000, self._do_reload)
    
    def _do_reload(self):
        """Ejecuta la recarga"""
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            self.logger.error(f"Error recargando: {e}")
            messagebox.showerror("❌ Error", f"Error en recarga: {e}")
    
    def confirm_exit(self, event=None):
        """Confirma salida de la aplicación"""
        if messagebox.askyesno(
            "Confirmar Salida",
            "¿Deseas cerrar la aplicación?"
        ):
            self.logger.info("=" * 70)
            self.logger.info("🚪 APLICACIÓN CERRADA")
            self.logger.info(f"⏰ Hora: {__import__('datetime').datetime.now()}")
            self.logger.info("=" * 70)
            
            self.root.quit()


def main():
    """
    Punto de entrada principal.
    Inicializa la aplicación con todas las configuraciones.
    """
    try:
        # Cargar configuración
        config = load_config()
        theme = config.get("theme", DEFAULT_THEME)
        
        # Validar tema
        if theme not in AVAILABLE_THEMES:
            theme = DEFAULT_THEME
        
        # Crear ventana
        root = Window(themename=theme)
        
        # Aplicar temas personalizados si existen
        custom_themes = CustomThemeManager.load_custom_themes()
        if theme in custom_themes:
            CustomThemeManager.apply_custom_theme(root.style, custom_themes[theme])
        
        # Crear aplicación
        app = MainApplication(root)
        
        # Iniciar loop
        root.mainloop()
    
    except Exception as e:
        logger.critical(f"❌ Error crítico en main: {e}")
        messagebox.showerror(
            "❌ Error Crítico",
            f"La aplicación no pudo iniciarse:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()