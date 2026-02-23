"""
Core.Styles.theme_manager - Gestión de temas personalizados y presets
"""

import json
import os
from typing import Dict, List
from ttkbootstrap import Style

from Core.Common.logger import setup_logger

logger = setup_logger()


class CustomThemeManager:
    """
    Gestor de temas personalizados.
    
    Características:
    - Guardar/cargar temas personalizados
    - Aplicar temas dinámicamente
    - Exportar/importar temas
    """
    
    # Componentes editables por defecto
    DEFAULT_COMPONENTS = {
        "Button": {
            "font": ("Segoe UI", 10),
            "background": "#0078d4",
            "foreground": "#ffffff",
            "padding": 10,
        },
        "Label": {
            "font": ("Segoe UI", 10),
            "foreground": "#212529",
            "background": "#ffffff",
        },
        "Entry": {
            "font": ("Segoe UI", 10),
            "foreground": "#212529",
            "background": "#ffffff",
            "border": 1,
        },
        "Frame": {
            "background": "#f8f9fa",
            "padding": 10,
        },
        "Treeview": {
            "font": ("Segoe UI", 9),
            "rowheight": 28,
            "background": "#ffffff",
            "foreground": "#212529",
        },
    }
    
    # Temas válidos de ttkbootstrap
    VALID_BOOTSTRAP_THEMES = [
        "solar", "darkly", "vapor", "cosmo", "flatly", "litera", "lumen",
        "minty", "pulse", "sandstone", "simplex", "sketchy", "spacelab",
        "superhero", "united", "yeti", "morph", "zephyr"
    ]
    
    CUSTOM_THEMES_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "custom_themes.json"
    )
    
    @staticmethod
    def load_custom_themes() -> Dict:
        """
        Carga temas personalizados desde archivo.
        
        Returns:
            Dict: Temas personalizados
        """
        if os.path.exists(CustomThemeManager.CUSTOM_THEMES_PATH):
            try:
                with open(CustomThemeManager.CUSTOM_THEMES_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando temas personalizados: {e}")
                return {}
        return {}
    
    @staticmethod
    def save_custom_theme(theme_name: str, theme_data: Dict) -> bool:
        """
        Guarda un tema personalizado.
        
        Args:
            theme_name: Nombre del tema
            theme_data: Datos del tema
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            themes = CustomThemeManager.load_custom_themes()
            themes[theme_name] = theme_data
            
            os.makedirs(os.path.dirname(CustomThemeManager.CUSTOM_THEMES_PATH), exist_ok=True)
            
            with open(CustomThemeManager.CUSTOM_THEMES_PATH, 'w', encoding='utf-8') as f:
                json.dump(themes, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Tema guardado: {theme_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error guardando tema: {e}")
            return False
    
    @staticmethod
    def delete_custom_theme(theme_name: str) -> bool:
        """
        Elimina un tema personalizado.
        
        Args:
            theme_name: Nombre del tema
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            themes = CustomThemeManager.load_custom_themes()
            
            if theme_name in themes:
                del themes[theme_name]
                
                with open(CustomThemeManager.CUSTOM_THEMES_PATH, 'w', encoding='utf-8') as f:
                    json.dump(themes, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Tema eliminado: {theme_name}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error eliminando tema: {e}")
            return False
    
    @staticmethod
    def get_theme_list() -> List[str]:
        """Retorna lista de temas personalizados"""
        return list(CustomThemeManager.load_custom_themes().keys())
    
    @staticmethod
    def apply_custom_theme(style: Style, theme_data: Dict) -> bool:
        """
        Aplica un tema personalizado.
        
        Args:
            style: Objeto Style de ttkbootstrap
            theme_data: Datos del tema
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            for component, settings in theme_data.items():
                try:
                    style.configure(component, **settings)
                except Exception as e:
                    logger.warning(f"Error configurando {component}: {e}")
            
            logger.info("✅ Tema aplicado")
            return True
        
        except Exception as e:
            logger.error(f"Error aplicando tema: {e}")
            return False
    
    @staticmethod
    def is_valid_bootstrap_theme(theme_name: str) -> bool:
        """
        Verifica si es un tema válido de ttkbootstrap.
        
        Args:
            theme_name: Nombre del tema
            
        Returns:
            bool: True si es válido
        """
        return theme_name in CustomThemeManager.VALID_BOOTSTRAP_THEMES


class ThemePreset:
    """
    Presets de temas predefinidos.
    
    Proporciona temas listos para usar.
    """
    
    PRESETS = {
        "Profesional Azul": {
            "Button": {
                "font": ("Segoe UI", 10, "bold"),
                "background": "#0078d4",
                "foreground": "#ffffff",
                "padding": 12,
            },
            "Label": {
                "font": ("Segoe UI", 10),
                "foreground": "#212529",
                "background": "#ffffff",
            },
            "Entry": {
                "font": ("Segoe UI", 10),
                "foreground": "#212529",
                "background": "#f8f9fa",
            },
            "Frame": {
                "background": "#ffffff",
                "padding": 12,
            },
        },
        "Verde Naturaleza": {
            "Button": {
                "font": ("Segoe UI", 10, "bold"),
                "background": "#198754",
                "foreground": "#ffffff",
                "padding": 12,
            },
            "Label": {
                "font": ("Segoe UI", 10),
                "foreground": "#0d3b2e",
                "background": "#f0fdf4",
            },
            "Entry": {
                "font": ("Segoe UI", 10),
                "foreground": "#0d3b2e",
                "background": "#f0fdf4",
            },
            "Frame": {
                "background": "#f0fdf4",
                "padding": 12,
            },
        },
        "Oscuro Moderno": {
            "Button": {
                "font": ("Segoe UI", 10, "bold"),
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "padding": 12,
            },
            "Label": {
                "font": ("Segoe UI", 10),
                "foreground": "#e0e0e0",
                "background": "#2d2d2d",
            },
            "Entry": {
                "font": ("Segoe UI", 10),
                "foreground": "#e0e0e0",
                "background": "#3d3d3d",
            },
            "Frame": {
                "background": "#2d2d2d",
                "padding": 12,
            },
        },
        "Naranja Energético": {
            "Button": {
                "font": ("Segoe UI", 10, "bold"),
                "background": "#ff8c00",
                "foreground": "#ffffff",
                "padding": 12,
            },
            "Label": {
                "font": ("Segoe UI", 10),
                "foreground": "#5a3a1a",
                "background": "#fff8f0",
            },
            "Entry": {
                "font": ("Segoe UI", 10),
                "foreground": "#5a3a1a",
                "background": "#fff8f0",
            },
            "Frame": {
                "background": "#fff8f0",
                "padding": 12,
            },
        },
        "Rosa Moderno": {
            "Button": {
                "font": ("Segoe UI", 10, "bold"),
                "background": "#e91e63",
                "foreground": "#ffffff",
                "padding": 12,
            },
            "Label": {
                "font": ("Segoe UI", 10),
                "foreground": "#c2185b",
                "background": "#fce4ec",
            },
            "Entry": {
                "font": ("Segoe UI", 10),
                "foreground": "#c2185b",
                "background": "#fce4ec",
            },
            "Frame": {
                "background": "#fce4ec",
                "padding": 12,
            },
        },
    }
    
    @staticmethod
    def get_preset(name: str) -> Dict:
        """
        Obtiene un preset predefinido.
        
        Args:
            name: Nombre del preset
            
        Returns:
            Dict: Datos del preset
        """
        return ThemePreset.PRESETS.get(name, {})
    
    @staticmethod
    def list_presets() -> List[str]:
        """Lista todos los presets disponibles"""
        return list(ThemePreset.PRESETS.keys())