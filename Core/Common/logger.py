"""
Core.Common.logger - Sistema centralizado de logging
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from Core.Common.constants import (
    LOG_LEVEL, LOG_FILE, LOG_MAX_BYTES, 
    LOG_BACKUP_COUNT, LOG_FORMAT, LOG_DATE_FORMAT
)


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name="economia_app"):
    """
    Configura un logger centralizado con:
    - Console handler (coloreado)
    - File handler (rotativo)
    - Evita duplicación de handlers
    
    Args:
        name: Nombre del logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Nivel de logging
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False
    
    # Crear directorio de logs si no existe
    os.makedirs(os.path.dirname(LOG_FILE) or "logs", exist_ok=True)
    
    # Handler para consola (coloreado)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (rotativo)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


# Logger por defecto
logger = setup_logger()