"""
Core.Common.constants - Constantes centralizadas del sistema
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================
# APLICACIÓN
# ============================================
APP_NAME = "Sistema de Economía"
APP_VERSION = os.getenv("APP_VERSION", "3.2")
APP_TITLE = f"📱 {APP_NAME} v{APP_VERSION} - Moderno"

# ============================================
# DIMENSIONES
# ============================================
DEFAULT_WINDOW_WIDTH = 1500
DEFAULT_WINDOW_HEIGHT = 900
MENU_WIDTH = 280

# ============================================
# TEMAS
# ============================================
DEFAULT_THEME = os.getenv("APP_THEME", "solar")
AVAILABLE_THEMES = [
    "solar", "darkly", "vapor", "cosmo", "flatly", "litera", "lumen",
    "minty", "pulse", "sandstone", "simplex", "sketchy", "spacelab",
    "superhero", "united", "yeti", "morph", "zephyr"
]

# ============================================
# COLORES
# ============================================
COLOR_PRIMARY = "#007bff"
COLOR_SUCCESS = "#28a745"
COLOR_DANGER = "#dc3545"
COLOR_WARNING = "#ffc107"
COLOR_INFO = "#17a2b8"
COLOR_SECONDARY = "#6c757d"
COLOR_LIGHT = "#f8f9fa"
COLOR_DARK = "#212529"

# ============================================
# FUENTES
# ============================================
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 8)
FONT_MONO = ("Courier New", 9)

# ============================================
# PADDING/ESPACIADO
# ============================================
PADDING_XS = 4
PADDING_SM = 8
PADDING_MD = 12
PADDING_LG = 16
PADDING_XL = 20

# ============================================
# BASE DE DATOS
# ============================================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "pp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_NAME = os.getenv("DB_NAME", "economia_oficial")
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
DB_POOL_RECYCLE = 3600

# ============================================
# LOGGING
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10485760))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================
# CACHÉ
# ============================================
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
CACHE_TTL_DEFAULT = int(os.getenv("CACHE_TTL_DEFAULT", 600))  # 10 min
CACHE_TTL_INVENTORY = int(os.getenv("CACHE_TTL_INVENTORY", 300))  # 5 min
CACHE_TTL_PRODUCTS = int(os.getenv("CACHE_TTL_PRODUCTS", 600))  # 10 min

# ============================================
# EXPORTACIÓN
# ============================================
EXPORT_BASE_FOLDER = os.getenv("EXPORT_BASE_FOLDER", "exports")
EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "csv")
WEEKLY_EXPORT_WEEKDAY = int(os.getenv("WEEKLY_EXPORT_WEEKDAY", 6))
WEEKLY_EXPORT_TIME = os.getenv("WEEKLY_EXPORT_TIME", "02:00")

# ============================================
# MENSAJES
# ============================================
MSG_CAMPO_REQUERIDO = "❌ {field} es requerido"
MSG_GUARDADO_EXITO = "✅ {item} guardado correctamente"
MSG_ERROR_GENERICO = "❌ Error: {error}"
MSG_CONFIRMAR_ELIMINAR = "¿Está seguro que desea eliminar {item}?"
MSG_OPERACION_COMPLETADA = "✅ Operación completada"
MSG_VALIDACION_ERROR = "❌ Error de validación: {error}"

# ============================================
# MENÚ ITEMS
# ============================================
MENU_ITEMS = [
    ("🛒 Compras", "compras"),
    ("📈 Resúmenes", "resumenes"),
    ("🏭 Producción", "produccion"),
    ("📦 Productos", "productos"),
    ("💰 Ventas", "ventas"),
    ("💸 Gastos", "gastos"),
    ("⚙️ Ajustes", "settings"),
]

# ============================================
# CONFIGURACIÓN DE SESIÓN
# ============================================
SESSION_TIMEOUT = 3600  # 1 hora
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_TIME = 300  # 5 minutos

# ============================================
# UNIDADES
# ============================================
UNITS_WEIGHT = ["g", "kg", "lb", "oz"]
UNITS_VOLUME = ["ml", "l"]
UNITS_COUNT = ["unit", "docen", "decen"]