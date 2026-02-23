"""
Core.Pages - Interfaces gráficas de la aplicación
"""

from Core.Pages.Compras.compras import ComprasFrame
from Core.Pages.Gastos.gastos import GastosFrame
from Core.Pages.Produccion.produccion import ProduccionFrame
from Core.Pages.Ventas.ventas import VentasFrame
from Core.Pages.Productos.productos import ProductosFrame
from Core.Pages.Resumenes.resumen import ResumenesFrame

__all__ = [
    'ComprasFrame',
    'GastosFrame',
    'ProduccionFrame',
    'VentasFrame',
    'ProductosFrame',
    'ResumenesFrame'
]