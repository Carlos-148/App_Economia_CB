import sys
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional, Type, Dict
import tkinter as tk
from contextlib import contextmanager

# Asegurar que el directorio actual está en el path
sys.path.insert(0, str(Path(__file__).parent))

from ttkbootstrap import Window
from ttkbootstrap.constants import *
from tkinter import messagebox

# ============================================
# IMPORTS: CORE MODULES
# ============================================
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
from Core.Common.database import DatabaseManager
from Core.Pages.Settings.setup_inicial import SetupInicial
from Core.Common.database import revisar_setup_completado

# ============================================
# GLOBAL LOGGER - Single instance
# ============================================
logger = setup_logger()


# ============================================
# LAZY PAGE LOADER
# ============================================
class PageLoader:
    """Lazy loader para páginas - mejora tiempo de inicio"""
    
    # Mapeo: nombre_página -> (módulo, clase)
    PAGES_MAP = {
        "compras": ("Core.Pages.Compras.compras", "ComprasFrame"),
        "resumenes": ("Core.Pages.Resumenes.resumen", "ResumenesFrame"),
        "produccion": ("Core.Pages.Produccion.produccion", "ProduccionFrame"),
        "ventas": ("Core.Pages.Ventas.ventas", "VentasFrame"),
        "gastos": ("Core.Pages.Gastos.gastos", "GastosFrame"),
        "productos": ("Core.Pages.Productos.productos", "ProductosFrame"),
        "settings": ("Core.Pages.Settings.settings", "SettingsFrame"),
    }
    
    _cache: Dict[str, Type] = {}
    
    @classmethod
    def get_page_class(cls, page_name: str) -> Optional[Type]:
        """
        Carga dinámicamente la clase de página.
        Cachea resultados para evitar re-importaciones.
        
        Args:
            page_name: Nombre de la página
            
        Returns:
            Clase de página o None
        """
        if page_name in cls._cache:
            return cls._cache[page_name]
        
        if page_name not in cls.PAGES_MAP:
            logger.warning(f"Página desconocida: {page_name}")
            return None
        
        try:
            module_path, class_name = cls.PAGES_MAP[page_name]
            module = __import__(module_path, fromlist=[class_name])
            page_class = getattr(module, class_name)
            
            # Cachear para uso futuro
            cls._cache[page_name] = page_class
            logger.debug(f"Página cargada: {page_name}")
            
            return page_class
        
        except (ImportError, AttributeError) as e:
            logger.error(f"Error cargando página {page_name}: {e}")
            return None


# ============================================
# BUTTON FACTORY - Centraliza creación de botones
# ============================================
class UIFactory:
    """Factory para crear componentes UI consistentes"""
    
    @staticmethod
    def create_menu_button(
        parent,
        text: str,
        command,
        bg_color: str,
        active_bg: str,
        **kwargs
    ) -> tk.Button:
        """
        Factory method para botones del menú.
        Asegura consistencia visual y reutilización de código.
        
        Args:
            parent: Frame padre
            text: Texto del botón
            command: Comando a ejecutar
            bg_color: Color de fondo
            active_bg: Color activo
            **kwargs: Argumentos adicionales
            
        Returns:
            Botón configurado
        """
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            width=26,
            relief="flat",
            cursor="hand2",
            bg=bg_color,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            activebackground=active_bg,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            **kwargs
        )
        return btn


# ============================================
# RESOURCE CONTEXT MANAGER
# ============================================
@contextmanager
def managed_page(current_page):
    """Context manager para manejo seguro de páginas"""
    try:
        yield
    finally:
        if current_page:
            try:
                current_page.destroy()
            except Exception as e:
                logger.warning(f"Error al destruir página: {e}")


# ============================================
# MAIN APPLICATION
# ============================================
class MainApplication:
 
    # Configuración UI
    BUTTON_CONFIG = {
        "compras": (COLOR_PRIMARY, "#0056b3"),
        "resumenes": (COLOR_PRIMARY, "#0056b3"),
        "produccion": (COLOR_PRIMARY, "#0056b3"),
        "ventas": (COLOR_PRIMARY, "#0056b3"),
        "gastos": (COLOR_PRIMARY, "#0056b3"),
        "productos": (COLOR_PRIMARY, "#0056b3"),
        "settings": (COLOR_PRIMARY, "#0056b3"),
        "reload": (COLOR_INFO, "#138496"),
        "exit": (COLOR_DANGER, "#c82333"),
    }
    
    def __init__(self, root):
        """
        Inicializa la aplicación principal.
        
        Args:
            root: Ventana raíz de ttkbootstrap
        """
        self.root = root
        self.logger = logger  # Usar instancia global
        
        # Estado de la aplicación
        self.current_page: Optional[tk.Widget] = None
        self.current_page_name: Optional[str] = None
        self.config = load_config()
        
        # Validar e inicializar tema
        self.current_theme = self._validate_and_setup_theme()
        
        # Configurar ventana
        self._setup_window()
        
        # Verificar setup inicial
        if not revisar_setup_completado():
            self._show_initial_setup()
        
        # Inicializar base de datos
        if not self._initialize_database():
            sys.exit(1)
        
        # Configurar UI
        self.setup_ui()
        
        # Mostrar página inicial
        self.show_page("compras")
        
        # Bindings
        self._setup_bindings()
        
        # Log de inicio
        self._log_startup()
    
    def _validate_and_setup_theme(self) -> str:
        """Valida y configura el tema"""
        theme = self.config.get("theme", DEFAULT_THEME)
        
        if theme not in AVAILABLE_THEMES:
            theme = DEFAULT_THEME
            self.config["theme"] = theme
            save_config(self.config)
        
        return theme
    
    def _setup_window(self):
        """Configura las propiedades de la ventana"""
        self.root.title(APP_TITLE)
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.root.minsize(1200, 700)
        
        # Aplicar estilos
        ModernStyleManager.configure_modern_styles(
            self.root.style, self.current_theme
        )
        
        # Aplicar temas personalizados si existen
        custom_themes = CustomThemeManager.load_custom_themes()
        if self.current_theme in custom_themes:
            CustomThemeManager.apply_custom_theme(
                self.root.style, custom_themes[self.current_theme]
            )
    
    def _show_initial_setup(self):
        """Muestra pantalla de setup inicial"""
        try:
            setup_window = SetupInicial(self.root)
            self.root.wait_window(setup_window)
        except Exception as e:
            self.logger.error(f"Error en setup inicial: {e}")
            messagebox.showerror("Error", f"Error en configuración inicial: {e}")
            sys.exit(1)
    
    def _initialize_database(self) -> bool:
        """
        Inicializa la base de datos de forma segura.
        
        Returns:
            bool: True si fue exitoso
        """
        try:
            if not DatabaseManager.initialize_database():
                self.logger.error("No se pudo inicializar la BD")
                messagebox.showerror(
                    "❌ Error de BD",
                    "No se pudo inicializar la base de datos.\n"
                    "Verifica la configuración."
                )
                return False
            
            self.logger.info("✅ Base de datos inicializada")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Error inicializando BD: {e}", exc_info=True)
            messagebox.showerror("❌ Error Crítico", f"Error de BD: {e}")
            return False
    
    def _setup_bindings(self):
        """Configura bindings de teclado y ventana"""
        def on_close_or_escape(event=None):
            """Unified handler para close y escape"""
            self.confirm_exit()
        
        self.root.bind("<Escape>", on_close_or_escape)
        self.root.protocol("WM_DELETE_WINDOW", on_close_or_escape)
    
    def _log_startup(self):
        """Registra información de startup"""
        self.logger.info("=" * 70)
        self.logger.info("🚀 APLICACIÓN INICIADA")
        self.logger.info(f"📱 Versión: {self.config.get('version', '3.2')}")
        self.logger.info(f"🎨 Tema: {self.current_theme}")
        self.logger.info(f"👤 Usuario: {self.config.get('user', {}).get('name', 'N/A')}")
        self.logger.info("=" * 70)
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Obtener colores del tema
        menu_bg = ModernStyleManager.get_bg_color(self.current_theme)
        
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
        self._create_menu_buttons()
        
        SeparatorFrame(self.menu_frame, height=20, theme_name=self.current_theme).pack()
        
        # Información
        self._create_info_section()
        
        # Espaciador
        SeparatorFrame(self.menu_frame, height=40, theme_name=self.current_theme).pack(expand=True)
        
        # Botones inferiores
        self._create_bottom_buttons()
        
        # === CONTENIDO PRINCIPAL ===
        self.content_frame = BaseFrame(self.root, theme_name=self.current_theme)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
    
    def _create_logo(self):
        """Crea la sección del logo"""
        logo_frame = MenuFrame(self.menu_frame, theme_name=self.current_theme)
        logo_frame.pack(fill=X, pady=(20, 10), padx=10)
        
        # Emoji
        logo_emoji = StyledLabel(
            logo_frame,
            text="📱",
            label_type="title",
            theme_name=self.current_theme
        )
        logo_emoji.set_accent()
        logo_emoji.pack()
        
        # Título
        logo_title = StyledLabel(
            logo_frame,
            text="ECONOMÍA",
            label_type="heading",
            theme_name=self.current_theme
        )
        logo_title.set_accent()
        logo_title.pack()
        
        # Versión
        logo_version = StyledLabel(
            logo_frame,
            text="v3.2 Premium",
            label_type="small",
            theme_name=self.current_theme
        )
        logo_version.pack()
    
    def _create_menu_buttons(self):
        """Crea botones del menú dinámicamente"""
        for label, page_name in MENU_ITEMS:
            bg, active_bg = self.BUTTON_CONFIG.get(
                page_name, 
                (COLOR_PRIMARY, "#0056b3")
            )
            
            btn = UIFactory.create_menu_button(
                self.menu_frame,
                label,
                lambda pn=page_name: self.show_page(pn),
                bg,
                active_bg
            )
            btn.pack(pady=5, padx=10, fill=X)
    
    def _create_info_section(self):
        """Crea sección de información"""
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
    
    def _create_bottom_buttons(self):
        """Crea botones inferiores (Reload, Exit)"""
        # Botón Recargar
        reload_bg, reload_active = self.BUTTON_CONFIG["reload"]
        reload_btn = UIFactory.create_menu_button(
            self.menu_frame,
            "🔄 Recargar",
            self.reload_app,
            reload_bg,
            reload_active
        )
        reload_btn.pack(pady=5, padx=10, fill=X, side=BOTTOM)
        
        # Botón Salir
        exit_bg, exit_active = self.BUTTON_CONFIG["exit"]
        exit_btn = UIFactory.create_menu_button(
            self.menu_frame,
            "🚪 Salir",
            self.confirm_exit,
            exit_bg,
            exit_active
        )
        exit_btn.pack(pady=5, padx=10, fill=X, side=BOTTOM)
    
    def show_page(self, page_name: str) -> bool:
        """
        Muestra una página específica con carga lazy.
        
        Args:
            page_name: Nombre de la página a mostrar
            
        Returns:
            bool: True si fue exitoso
        """
        # Validar página
        if page_name not in PageLoader.PAGES_MAP:
            self.logger.warning(f"⚠️ Página desconocida: {page_name}")
            messagebox.showwarning("Aviso", "Página no encontrada")
            return False
        
        # Si es la página actual, no recargar
        if self.current_page_name == page_name and self.current_page:
            return True
        
        # Destruir página anterior (con context manager)
        with managed_page(self.current_page):
            pass
        
        # Cargar nueva página
        try:
            # Usar lazy loader
            PageClass = PageLoader.get_page_class(page_name)
            
            if not PageClass:
                raise ImportError(f"No se pudo cargar {page_name}")
            
            self.current_page = PageClass(self.content_frame)
            self.current_page.pack(fill=BOTH, expand=True)
            self.current_page_name = page_name
            
            self.logger.info(f"✅ Página cargada: {page_name.upper()}")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Error cargando {page_name}: {e}", exc_info=True)
            messagebox.showerror(
                "❌ Error",
                f"Error cargando página:\n{str(e)[:100]}"
            )
            return False
    
    def reload_app(self):
        """Recarga la aplicación"""
        if messagebox.askyesno(
            "🔄 Recargar",
            "¿Deseas reiniciar la aplicación?"
        ):
            self.logger.info("🌀 Recargando aplicación...")
            self.root.after_idle(self._do_reload)
    
    def _do_reload(self):
        """Ejecuta la recarga de la aplicación"""
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            self.logger.error(f"Error recargando: {e}", exc_info=True)
            messagebox.showerror("❌ Error", f"Error en recarga: {e}")
    
    def confirm_exit(self, event=None):
        """Confirma y ejecuta salida de la aplicación"""
        if messagebox.askyesno(
            "Confirmar Salida",
            "¿Deseas cerrar la aplicación?"
        ):
            self.logger.info("=" * 70)
            self.logger.info("🚪 APLICACIÓN CERRADA")
            self.logger.info(f"⏰ Hora: {datetime.now()}")
            self.logger.info("=" * 70)
            
            self.root.quit()


# ============================================
# MAIN ENTRY POINT
# ============================================
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
        
        # Crear aplicación
        app = MainApplication(root)
        
        # Iniciar loop
        root.mainloop()
    
    except Exception as e:
        logger.critical(f"❌ Error crítico en main: {e}", exc_info=True)
        messagebox.showerror(
            "❌ Error Crítico",
            f"La aplicación no pudo iniciarse:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()