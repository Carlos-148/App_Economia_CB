"""
Core.Pages.Settings.stats_section - Sección de Estadísticas
CORREGIDO: Manejo de errores mejorado
"""

import tkinter as tk

from Core.Styles.base_components import BaseFrame, StyledLabel, CardFrame
from Core.Common.constants import COLOR_INFO
from Core.Backends.settings_backend import SettingsBackend
from Core.Common.logger import setup_logger

logger = setup_logger()


class StatsSection(BaseFrame):
    """Sección de estadísticas"""
    
    def __init__(self, parent, theme_name="solar", backend: SettingsBackend = None):
        super().__init__(parent, theme_name=theme_name)
        self.backend = backend or SettingsBackend()
        self.logger = setup_logger()
        
        self.setup_ui()
        self.load_stats()
    
    def setup_ui(self):
        """Configura la interfaz"""
        card = CardFrame(self, title="📈 ESTADÍSTICAS", theme_name=self.theme_name)
        card.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(
            card,
            height=4,
            wrap=tk.WORD,
            bg="white",
            relief="solid",
            bd=1,
            font=("Segoe UI", 8),
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.X, padx=10, pady=(10, 8))
        
        tk.Button(
            card,
            text="🔄 Actualizar",
            command=self.load_stats,
            bg=COLOR_INFO,
            fg="white",
            relief="flat",
            cursor="hand2",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4
        ).pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def load_stats(self):
        """Carga estadísticas"""
        try:
            stats = self.backend.get_system_stats()
            
            # Manejo seguro de diccionarios
            app_version = stats.get('app_version', 'N/A') if isinstance(stats, dict) else 'N/A'
            current_user = stats.get('current_user', 'N/A') if isinstance(stats, dict) else 'N/A'
            current_theme = stats.get('current_theme', 'N/A') if isinstance(stats, dict) else 'N/A'
            
            db_info = stats.get('database', {}) if isinstance(stats, dict) else {}
            if isinstance(db_info, dict):
                database = db_info.get('database', 'N/A')
                rows = db_info.get('rows', 0)
            else:
                database = 'N/A'
                rows = 0
            
            msg = f"""📱 v{app_version}
👤 {current_user}
🎨 {current_theme}

🗄️ {database}
📦 Registros: {rows:,}"""
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, msg.strip())
            self.stats_text.config(state=tk.DISABLED)
        
        except Exception as e:
            self.logger.error(f"Error cargando estadísticas: {e}")
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"Error: {str(e)[:50]}")
            self.stats_text.config(state=tk.DISABLED)