"""
Core.Backends - Lógica de negocio de la aplicación
"""

from Core.Backends.compras_backend import ComprasBackend
from Core.Backends.gastos_backend import GastosBackend
from Core.Backends.inventario_backend import InventarioBackend
from Core.Backends.produccion_backend import ProduccionBackend
from Core.Backends.ventas_backend import VentasBackend
from Core.Backends.contabilidad_backend import ContabilidadBackend
from Core.Backends.settings_backend import SettingsBackend

__all__ = [
    'ComprasBackend',
    'GastosBackend',
    'InventarioBackend',
    'ProduccionBackend',
    'VentasBackend',
    'ContabilidadBackend',
    'SettingsBackend'
]