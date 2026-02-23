"""
Core.Common.config - Gestión de configuración de la aplicación
"""

import json
import os
from typing import Dict, Any

DEFAULT_CONFIG = {
    "db": {
        "host": "localhost",
        "port": 3306,
        "user": "pp",
        "password": "1234",
        "database": "economia_oficial",
        "charset": "utf8mb4"
    },
    "user": {
        "current_user_id": None,
        "name": "usuario",
        "capital": 1000.0
    },
    "theme": "solar",
    "exports": {
        "base_folder": "exports",
        "weekly_export_weekday": 6,
        "weekly_export_time": "02:00"
    },
    "scheduler": {
        "enabled": False
    }
}

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "app_config.json"
)


def load_config() -> Dict[str, Any]:
    """
    Carga configuración desde archivo o retorna default.
    
    Returns:
        Dict con configuración
    """
    try:
        if os.path.exists(_CONFIG_PATH):
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
    except Exception as e:
        print(f"⚠️ Error cargando config: {e}")
    
    return DEFAULT_CONFIG.copy()


def save_config(cfg: Dict[str, Any]) -> bool:
    """
    Guarda configuración en archivo.
    
    Args:
        cfg: Diccionario de configuración
        
    Returns:
        bool: True si fue exitoso
    """
    try:
        os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando config: {e}")
        return False


def get_db_config() -> Dict[str, Any]:
    """
    Obtiene configuración de base de datos.
    
    Returns:
        Dict con config de BD
    """
    return load_config().get("db", DEFAULT_CONFIG["db"])


def update_config(key: str, value: Any) -> bool:
    """
    Actualiza un valor específico de configuración.
    
    Args:
        key: Clave a actualizar (usa puntos para anidación)
        value: Nuevo valor
        
    Returns:
        bool: True si fue exitoso
    """
    cfg = load_config()
    keys = key.split(".")
    obj = cfg
    
    for k in keys[:-1]:
        if k not in obj:
            obj[k] = {}
        obj = obj[k]
    
    obj[keys[-1]] = value
    return save_config(cfg)