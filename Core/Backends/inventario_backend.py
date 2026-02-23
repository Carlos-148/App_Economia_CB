"""
Core.Backends.inventario_backend - Gestión de inventario
"""

from typing import List, Dict, Optional, Tuple
from Core.Common.database import get_connection, close_connection
from Core.Common.logger import setup_logger
from Core.Common.units import convert_to_base, CONVERSIONS
from Core.Common.data_cache import app_cache
from decimal import Decimal

logger = setup_logger()


class InventarioBackend:
    """Backend de inventario con caché y optimizaciones"""
    
    CACHE_KEY_INVENTORY = "inventario_completo"
    CACHE_KEY_PRODUCT = "producto_{name}"
    
    def __init__(self):
        self.logger = setup_logger()
        self.logger.info("✓ InventarioBackend inicializado")
    
    def _get_unidad_base(self, unidad: str) -> Optional[str]:
        """
        Determina la unidad base de una unidad dada.
        
        Args:
            unidad: Unidad a convertir
            
        Returns:
            str: Unidad base o None
        """
        if not unidad:
            return None
        
        unidad = unidad.lower()
        for category, units in CONVERSIONS.items():
            if unidad in units:
                if category == "weight":
                    return "g"
                if category == "volume":
                    return "ml"
                if category == "count":
                    return "unit"
        return None
    
    def actualizar_stock_desde_compra(
        self,
        producto: str,
        cantidad: float,
        unidad: str,
        precio_total: float
    ) -> bool:
        """
        Añade stock al inventario y recalcula costo promedio ponderado.
        
        Args:
            producto: Nombre del producto
            cantidad: Cantidad comprada
            unidad: Unidad de medida
            precio_total: Precio total pagado
            
        Returns:
            bool: True si fue exitoso
        """
        conn = get_connection()
        if not conn:
            logger.error("No hay conexión a BD")
            return False
        
        try:
            with conn.cursor() as cursor:
                unidad_base = self._get_unidad_base(unidad)
                if not unidad_base:
                    raise ValueError(f"Unidad '{unidad}' no reconocida")
                
                cantidad_base, _ = convert_to_base(float(cantidad), unidad)
                if cantidad_base is None:
                    raise ValueError("No se pudo convertir cantidad")
                
                # Buscar producto existente
                cursor.execute(
                    "SELECT cantidad_stock, costo_promedio_ponderado FROM inventario WHERE producto = %s",
                    (producto,)
                )
                result = cursor.fetchone()
                
                if result:
                    # Actualizar stock existente
                    stock_actual = float(result.get("cantidad_stock", 0) or 0)
                    costo_actual = float(result.get("costo_promedio_ponderado", 0) or 0)
                    nuevo_stock = stock_actual + cantidad_base
                    
                    if nuevo_stock > 0:
                        nuevo_costo_promedio = (
                            (stock_actual * costo_actual) + float(precio_total)
                        ) / nuevo_stock
                    else:
                        nuevo_costo_promedio = costo_actual
                    
                    cursor.execute(
                        """UPDATE inventario 
                           SET cantidad_stock = %s, costo_promedio_ponderado = %s, unidad_base = %s 
                           WHERE producto = %s""",
                        (nuevo_stock, nuevo_costo_promedio, unidad_base, producto)
                    )
                    
                    self.logger.info(
                        f"✓ Stock actualizado: {producto} +{cantidad_base}{unidad_base}, "
                        f"total: {nuevo_stock}{unidad_base}"
                    )
                else:
                    # Insertar nuevo producto
                    costo_unitario_base = (
                        float(precio_total) / cantidad_base if cantidad_base else 0.0
                    )
                    cursor.execute(
                        """INSERT INTO inventario 
                           (producto, cantidad_stock, unidad_base, costo_promedio_ponderado) 
                           VALUES (%s, %s, %s, %s)""",
                        (producto, cantidad_base, unidad_base, costo_unitario_base)
                    )
                    
                    self.logger.info(
                        f"✓ Producto nuevo en inventario: {producto} "
                        f"({cantidad_base}{unidad_base})"
                    )
            
            conn.commit()
            
            # Invalidar caché
            app_cache.invalidate(self.CACHE_KEY_INVENTORY)
            app_cache.invalidate(self.CACHE_KEY_PRODUCT.format(name=producto))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando stock: {e}")
            conn.rollback()
            raise
        finally:
            close_connection(conn)
    
    def consumir_stock(
        self,
        producto: str,
        cantidad_a_consumir: float,
        unidad_consumo: str
    ) -> bool:
        """
        Reduce el stock de un producto.
        
        Args:
            producto: Nombre del producto
            cantidad_a_consumir: Cantidad a consumir
            unidad_consumo: Unidad de consumo
            
        Returns:
            bool: True si fue exitoso
            
        Raises:
            ValueError: Si no hay stock suficiente
        """
        conn = get_connection()
        if not conn:
            logger.error("No hay conexión a BD")
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT cantidad_stock, unidad_base FROM inventario WHERE producto = %s",
                    (producto,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"Producto '{producto}' no existe")
                
                stock_actual_base = float(result['cantidad_stock'])
                unidad_base_db = result['unidad_base']
                
                cantidad_base_a_consumir, _ = convert_to_base(
                    float(cantidad_a_consumir),
                    unidad_consumo
                )
                
                if cantidad_base_a_consumir is None:
                    raise ValueError(
                        f"No se pudo convertir '{cantidad_a_consumir} {unidad_consumo}'"
                    )
                
                if stock_actual_base < cantidad_base_a_consumir:
                    raise ValueError(
                        f"Stock insuficiente para '{producto}'. "
                        f"Disponible: {stock_actual_base:.2f} {unidad_base_db}, "
                        f"Requerido: {cantidad_base_a_consumir:.2f} {unidad_base_db}"
                    )
                
                nuevo_stock = stock_actual_base - cantidad_base_a_consumir
                cursor.execute(
                    "UPDATE inventario SET cantidad_stock = %s WHERE producto = %s",
                    (nuevo_stock, producto)
                )
                
                self.logger.info(
                    f"✓ Stock consumido: {producto} -{cantidad_base_a_consumir}{unidad_base_db}, "
                    f"nuevo total: {nuevo_stock}{unidad_base_db}"
                )
            
            conn.commit()
            
            # Invalidar caché
            app_cache.invalidate(self.CACHE_KEY_INVENTORY)
            app_cache.invalidate(self.CACHE_KEY_PRODUCT.format(name=producto))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error consumiendo stock: {e}")
            conn.rollback()
            raise
        finally:
            close_connection(conn)
    
    def get_inventario_para_resumen(self) -> List[Dict]:
        """
        Obtiene inventario completo con caché.
        
        Returns:
            List[Dict]: Lista de productos con información de display
        """
        # Intentar obtener del caché
        cached = app_cache.get(self.CACHE_KEY_INVENTORY)
        if cached is not None:
            return cached
        
        conn = get_connection()
        if not conn:
            logger.error("No hay conexión a BD")
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT producto, cantidad_stock, unidad_base, costo_promedio_ponderado 
                       FROM inventario WHERE cantidad_stock > 0 ORDER BY producto"""
                )
                results = cursor.fetchall()
                
                processed_results = []
                
                for item in results:
                    producto = item["producto"]
                    cantidad_base = float(item["cantidad_stock"] or 0.0)
                    unidad_base = (item.get("unidad_base") or "").lower()
                    costo_por_base = float(item.get("costo_promedio_ponderado") or 0.0)
                    
                    # Convertir a unidades más legibles
                    display_cantidad = cantidad_base
                    display_unidad = unidad_base
                    
                    if unidad_base == "g":
                        if cantidad_base >= 1000:
                            display_cantidad = cantidad_base / 1000.0
                            display_unidad = "kg"
                        elif cantidad_base >= 453.592:
                            display_cantidad = cantidad_base / 453.592
                            display_unidad = "lb"
                    elif unidad_base == "ml":
                        if cantidad_base >= 1000:
                            display_cantidad = cantidad_base / 1000.0
                            display_unidad = "l"
                    
                    total_valor = cantidad_base * costo_por_base
                    
                    processed_results.append({
                        "producto": producto,
                        "cantidad_display": f"{display_cantidad:.2f}",
                        "unidad_display": display_unidad,
                        "costo_promedio_display": f"${costo_por_base:.4f}",
                        "total_valor": total_valor,
                        "cantidad_base": cantidad_base,
                        "unidad_base": unidad_base,
                        "costo_base": costo_por_base
                    })
                
                # Guardar en caché
                app_cache.set(self.CACHE_KEY_INVENTORY, processed_results)
                return processed_results
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo inventario: {e}")
            return []
        finally:
            close_connection(conn)
    
    def obtener_producto(self, producto_id: int) -> Optional[Dict]:
        """
        Obtiene información detallada de un producto.
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Dict con información del producto
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM inventario WHERE id = %s""",
                    (producto_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error obteniendo producto: {e}")
            return None
        finally:
            close_connection(conn)
    
    def obtener_total_invertido(self) -> float:
        """
        Obtiene inversión total en inventario.
        
        Returns:
            float: Total invertido
        """
        conn = get_connection()
        if not conn:
            return 0.0
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT SUM(cantidad_stock * costo_promedio_ponderado) as total 
                       FROM inventario"""
                )
                result = cursor.fetchone()
                return float(result['total'] or 0.0) if result else 0.0
        except Exception as e:
            logger.error(f"Error calculando total invertido: {e}")
            return 0.0
        finally:
            close_connection(conn)