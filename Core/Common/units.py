"""
Core.Common.units - Sistema de conversión de unidades
"""

from Core.Common.logger import setup_logger

logger = setup_logger()

# Factores de conversión a unidades base
CONVERSIONS = {
    "weight": {
        "g": 1,
        "kg": 1000,
        "lb": 453.592,
        "oz": 28.3495,
    },
    "volume": {
        "ml": 1,
        "l": 1000,
    },
    "count": {
        "unit": 1,
        "decen": 10,
        "docen": 12,
    },
}

# Unidades disponibles por categoría
UNIT_CHOICES_BY_CATEGORY = {
    "weight": ["g", "kg", "lb", "oz"],
    "volume": ["ml", "l"],
    "count": ["unit", "docen", "decen"],
}

# Lista plana de unidades
UNIT_CHOICES = (
    UNIT_CHOICES_BY_CATEGORY["weight"]
    + UNIT_CHOICES_BY_CATEGORY["volume"]
    + UNIT_CHOICES_BY_CATEGORY["count"]
)

# Mapeo de aliases
ALIASES = {
    "gr": "g",
    "gram": "g",
    "grams": "g",
    "gramo": "g",
    "kgs": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "lbs": "lb",
    "libra": "lb",
    "libras": "lb",
    "oz": "oz",
    "ounce": "oz",
    "ml": "ml",
    "milliliter": "ml",
    "millilitre": "ml",
    "l": "l",
    "litro": "l",
    "litros": "l",
    "unit": "unit",
    "unidad": "unit",
    "docen": "docen",
    "dozen": "docen",
    "decen": "decen",
    "diez": "decen",
}


def normalize_unit(unit: str) -> str:
    """
    Normaliza unidad a clave canónica.
    
    Args:
        unit: Unidad a normalizar
        
    Returns:
        str: Unidad normalizada
    """
    if not unit:
        return ""
    
    u = unit.strip().lower()
    return ALIASES.get(u, u)


def get_unit_choices() -> list:
    """Retorna lista de unidades disponibles"""
    return UNIT_CHOICES.copy()


def get_unit_choices_by_category() -> dict:
    """Retorna unidades agrupadas por categoría"""
    return {k: v.copy() for k, v in UNIT_CHOICES_BY_CATEGORY.items()}


def get_base_unit(category: str) -> str:
    """
    Obtiene unidad base de una categoría.
    
    Args:
        category: Categoría (weight, volume, count)
        
    Returns:
        str: Unidad base
    """
    base_units = {
        "weight": "g",
        "volume": "ml",
        "count": "unit"
    }
    return base_units.get(category)


def convert_to_base(quantity: float, unit: str) -> tuple:
    """
    Convierte cantidad a unidad base.
    
    Args:
        quantity: Cantidad a convertir
        unit: Unidad actual
        
    Returns:
        tuple: (cantidad_convertida, unidad_base) o (None, None)
    """
    try:
        quantity = float(quantity)
        unit_norm = normalize_unit(unit)
        
        for category, factors in CONVERSIONS.items():
            if unit_norm in factors:
                base_unit = get_base_unit(category)
                converted = quantity * factors[unit_norm]
                logger.debug(
                    f"Convertido {quantity} {unit_norm} a {converted} {base_unit}"
                )
                return converted, base_unit
        
        logger.error(f"Unidad {unit} no reconocida (normalizada: {unit_norm})")
        return None, None
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error convirtiendo cantidad: {e}")
        return None, None


def convert_from_base(quantity: float, from_unit: str, to_unit: str) -> float:
    """
    Convierte desde unidad base a otra unidad.
    
    Args:
        quantity: Cantidad en unidad base
        from_unit: Unidad origen
        to_unit: Unidad destino
        
    Returns:
        float: Cantidad convertida o None
    """
    try:
        quantity = float(quantity)
        from_unit_norm = normalize_unit(from_unit)
        to_unit_norm = normalize_unit(to_unit)
        
        # Encontrar categoría
        category = None
        for cat, factors in CONVERSIONS.items():
            if from_unit_norm in factors:
                category = cat
                break
        
        if not category or to_unit_norm not in CONVERSIONS[category]:
            logger.error(f"No se puede convertir de {from_unit_norm} a {to_unit_norm}")
            return None
        
        # Convertir a base primero si es necesario
        if from_unit_norm != get_base_unit(category):
            quantity, _ = convert_to_base(quantity, from_unit_norm)
        
        # Convertir a unidad destino
        factor = CONVERSIONS[category][to_unit_norm]
        converted = quantity / factor
        
        logger.debug(
            f"Convertido {quantity} {get_base_unit(category)} a {converted} {to_unit_norm}"
        )
        return converted
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error en conversión: {e}")
        return None


def calculate_cost_per_base_unit(item_data: dict) -> dict:
    """
    Calcula costo por unidad base desde datos de compra.
    
    Args:
        item_data: Diccionario con datos de compra
        
    Returns:
        dict: item_data con costo_promedio añadido
    """
    total_quantity_bulk = item_data.get("cantidad_granel", 0)
    total_quantity_packages = item_data.get("cantidad_paquetes", 0)
    unidad = item_data.get("unidad")
    total_precio = float(item_data.get("total_precio", 0))
    
    total_physical_quantity = total_quantity_bulk + total_quantity_packages
    
    if not total_physical_quantity or total_precio <= 0 or not unidad:
        logger.warning(
            f"Saltando cálculo de costo para {item_data.get('producto', 'Desconocido')}"
        )
        item_data["costo_promedio"] = 0
        return item_data
    
    converted_quantity, base_unit = convert_to_base(total_physical_quantity, unidad)
    
    if converted_quantity and converted_quantity > 0:
        cost_per_unit = total_precio / converted_quantity
        logger.info(
            f"Costo calculado para {item_data.get('producto')}: "
            f"${cost_per_unit:.4f} por {base_unit}"
        )
        item_data["costo_promedio"] = cost_per_unit
    else:
        logger.warning(
            f"No se pudo convertir cantidad para {item_data.get('producto')}"
        )
        item_data["costo_promedio"] = 0
    
    return item_data