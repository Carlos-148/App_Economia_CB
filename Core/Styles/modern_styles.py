# Core/Styles/modern_styles.py - Estilos modernos y consistentes para temas

from ttkbootstrap import Style

class ModernStyleManager:
    """Gestor de estilos modernos sin backgrounds inconsistentes"""
    
    @staticmethod
    def get_bg_color(theme_name):
        """Retorna el color de fondo apropiado según el tema"""
        bg_colors = {
            # Temas Claros
            "solar": "#f8f9fa",
            "flatly": "#ecf0f1",
            "cosmo": "#ecf0f1",
            "lumen": "#fafafa",
            "minty": "#f1f5f5",
            "sandstone": "#faf9f7",
            "simplex": "#f1f1f1",
            "sketchy": "#f8f9fa",
            "yeti": "#ecf0f1",
            
            # Temas Oscuros
            "darkly": "#222222",
            "vapor": "#2b2d42",
            "pulse": "#1a1a1a",
            "superhero": "#2b3035",
            "united": "#1a1a1a",
            "spacelab": "#303d47",
            "litera": "#f7f7f7",
            
            # Nuevos
            "morph": "#f0f0f0",
            "zephyr": "#1e1e1e",
        }
        return bg_colors.get(theme_name, "#f8f9fa")
    
    @staticmethod
    def get_fg_color(theme_name):
        """Retorna el color de texto apropiado según el tema"""
        fg_colors = {
            # Temas Claros
            "solar": "#212529",
            "flatly": "#212529",
            "cosmo": "#212529",
            "lumen": "#212529",
            "minty": "#0d3b2e",
            "sandstone": "#3e3e3e",
            "simplex": "#212529",
            "sketchy": "#212529",
            "yeti": "#212529",
            
            # Temas Oscuros
            "darkly": "#e8e8e8",
            "vapor": "#d8e1f7",
            "pulse": "#ffffff",
            "superhero": "#e8e8e8",
            "united": "#ffffff",
            "spacelab": "#ecf0f1",
            "litera": "#212529",
            
            # Nuevos
            "morph": "#212529",
            "zephyr": "#ffffff",
        }
        return fg_colors.get(theme_name, "#212529")
    
    @staticmethod
    def get_accent_color(theme_name):
        """Retorna color de acentos según tema"""
        accent_colors = {
            "solar": "#ffc107",
            "flatly": "#3498db",
            "cosmo": "#2c3e50",
            "lumen": "#e74c3c",
            "minty": "#1abc9c",
            "sandstone": "#c0504d",
            "simplex": "#c0504d",
            "sketchy": "#0e5cb8",
            "yeti": "#3498db",
            "darkly": "#375a7f",
            "vapor": "#a29bfe",
            "pulse": "#ff006e",
            "superhero": "#df4601",
            "united": "#e74c3c",
            "spacelab": "#3498db",
            "litera": "#e74c3c",
            "morph": "#0d7377",
            "zephyr": "#00d9ff",
        }
        return accent_colors.get(theme_name, "#0078d4")
    
    @staticmethod
    def configure_modern_styles(style, theme_name):
        """Configura estilos modernos sin crear estilos personalizados"""
        
        # === BUTTONS ===
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=10,
            relief="flat"
        )
        
        # === ENTRY ===
        style.configure(
            "TEntry",
            font=("Segoe UI", 10),
            padding=8,
            relief="solid",
            borderwidth=1
        )
        
        # === COMBOBOX ===
        style.configure(
            "TCombobox",
            font=("Segoe UI", 10),
            padding=8,
            relief="solid",
            borderwidth=1
        )
        
        # === TREEVIEW ===
        tree_bg = "#ffffff" if "dark" not in theme_name.lower() else "#2b2d42"
        
        style.configure(
            "Treeview",
            font=("Segoe UI", 9),
            rowheight=28,
            relief="solid",
            borderwidth=1
        )
        
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            relief="solid",
            borderwidth=1
        )
        
        return style