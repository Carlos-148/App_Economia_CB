"""
Core.Common.import_fixes - Importaciones estandarizadas para evitar errores
"""

# ============================================
# IMPORTS: TKINTER CONSTANTS (Correctos)
# ============================================

from tkinter import (
    END,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
    CENTER,
    WEST,
    EAST,
    X,
    Y,
    BOTH,
    HORIZONTAL,
    VERTICAL,
)

from tkinter.constants import (
    LEFT as TK_LEFT,
    RIGHT as TK_RIGHT,
    X as TK_X,
    Y as TK_Y,
    BOTH as TK_BOTH,
)

# ============================================
# IMPORTS: TTKBOOTSTRAP CONSTANTS
# ============================================

from ttkbootstrap.constants import (
    LEFT as TTK_LEFT,
    RIGHT as TTK_RIGHT,
    TOP as TTK_TOP,
    BOTTOM as TTK_BOTTOM,
    X as TTK_X,
    Y as TTK_Y,
    BOTH as TTK_BOTH,
    CENTER as TTK_CENTER,
    HORIZONTAL as TTK_HORIZONTAL,
    VERTICAL as TTK_VERTICAL,
)

# ============================================
# EXPORTS ESTÁNDAR
# ============================================

# Usar estos en lugar de importar directamente
__all__ = [
    'END',
    'LEFT',
    'RIGHT',
    'TOP',
    'BOTTOM',
    'CENTER',
    'WEST',
    'EAST',
    'X',
    'Y',
    'BOTH',
    'HORIZONTAL',
    'VERTICAL',
]