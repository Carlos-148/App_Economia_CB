"""
Core.Pages.Settings.settings_config - Configuración y definiciones de Settings
Centraliza toda la configuración de la UI
"""

# ============================================
# COLORES Y ESTILOS
# ============================================
COLORS = {
    'primary': '#0d6efd',
    'success': '#198754',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#0dcaf0',
    'secondary': '#6c757d',
    'database': '#17a2b8',
    'text_dark': '#212529',
    'text_light': '#f8f9fa',
}

FONTS = {
    'title': ('Segoe UI', 16, 'bold'),
    'heading': ('Segoe UI', 12, 'bold'),
    'normal': ('Segoe UI', 10),
    'small': ('Segoe UI', 9),
    'tiny': ('Segoe UI', 8),
}

# ============================================
# CONFIGURACIÓN DE SECCIONES
# ============================================
SECTIONS_LEFT = [
    {
        'title': '🗄️ BASE DE DATOS',
        'key': 'database',
        'module': 'database_section',
        'class': 'DatabaseSection'
    },
    {
        'title': '👤 USUARIO',
        'key': 'user',
        'module': 'user_section',
        'class': 'UserSection'
    },
    {
        'title': '📊 EXPORTES',
        'key': 'export',
        'module': 'export_section',
        'class': 'ExportSection'
    }
]

SECTIONS_RIGHT = [
    {
        'title': '🎨 TEMAS',
        'key': 'theme',
        'module': 'theme_section',
        'class': 'ThemeSection'
    },
    {
        'title': '📈 ESTADÍSTICAS',
        'key': 'stats',
        'module': 'stats_section',
        'class': 'StatsSection'
    },
    {
        'title': '🛠️ UTILIDADES',
        'key': 'utilities',
        'module': 'utilities_section',
        'class': 'UtilitiesSection'
    }
]

# ============================================
# TEXTOS Y MENSAJES
# ============================================
HEADERS = {
    'main_title': '⚙️ CONFIGURACIÓN AVANZADA',
    'main_subtitle': 'Gestiona la configuración de tu aplicación',
    'left_column': '📋 GESTIÓN DE DATOS',
    'right_column': '🎨 APARIENCIA Y SISTEMA',
}

# ============================================
# VARIABLES DE SECCIONES
# ============================================

# Database Section
DATABASE_SECTION = {
    'title': '🗄️ BASE DE DATOS',
    'state_label': 'Estado:',
    'info_label': 'Información:',
    'buttons': [
        {'text': '🔌 Probar', 'command': 'test_connection', 'color': COLORS['info']},
        {'text': '📊 Stats', 'command': 'show_stats', 'color': COLORS['database']},
        {'text': '📥 Backups', 'command': 'show_backups', 'color': COLORS['secondary']},
        {'text': '🔄 Reset', 'command': 'reset_data', 'color': COLORS['warning']},
        {'text': '🔨 Nueva BD', 'command': 'create_new_db', 'color': COLORS['danger']},
        {'text': '📂 Abrir', 'command': 'open_folder', 'color': '#007bff'},
    ]
}

# User Section
USER_SECTION = {
    'title': '👤 USUARIO',
    'name_label': 'Nombre:',
    'capital_label': 'Capital:',
    'info_text': '💡 Se gestiona en: Caja → Efectivo',
    'button_save': '💾 Guardar'
}

# Export Section
EXPORT_SECTION = {
    'title': '📊 EXPORTES',
    'buttons': [
        {'text': '📤 Exportar', 'command': 'export_summary', 'color': COLORS['info']},
        {'text': '📁 Abrir Carpeta', 'command': 'open_exports', 'color': COLORS['primary']},
    ]
}

# Theme Section
THEME_SECTION = {
    'title': '🎨 TEMAS',
    'theme_label': 'Tema Oficial:',
    'preset_label': 'Preset:',
    'button_apply': '✅',
}

# Stats Section
STATS_SECTION = {
    'title': '📈 ESTADÍSTICAS',
    'button_refresh': '🔄 Actualizar',
}

# Utilities Section
UTILITIES_SECTION = {
    'title': '🛠️ UTILIDADES',
    'button_reload': '🔄 Recargar App',
}

# ============================================
# DIÁLOGOS Y CONFIRMACIONES
# ============================================
DIALOGS = {
    'connection_test': 'Conexión BD',
    'export': 'Exportar',
    'theme_apply': 'Tema',
    'reload': 'Recargar',
    'reload_message': '¿Reiniciar la aplicación?',
    'reset_confirm': '⚠️ RESET',
    'reset_message': '¿Eliminar todos los datos?',
    'new_db_confirm': '⚠️ BD NUEVA',
    'new_db_message': '¿Crear BD nueva? (Irreversible)',
    'select_theme': 'Aviso',
    'select_theme_message': 'Selecciona un tema',
    'select_preset': 'Aviso',
    'select_preset_message': 'Selecciona un preset',
}

# ============================================
# LAYOUT DIMENSIONS
# ============================================
LAYOUT = {
    'header_padx': 20,
    'header_pady': (20, 15),
    'content_padx': 20,
    'content_pady': (0, 20),
    'column_padx': (0, 10),
    'column_pady': (0, 15),
    'card_pady': (0, 10),
    'button_grid_padx': 2,
    'button_grid_pady': 2,
    'button_width': 3,
}