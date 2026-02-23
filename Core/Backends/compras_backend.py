"""
Core.Backends.compras_backend - Gestión de compras
"""

from typing import List, Dict, Optional
from Core.Common.database import get_connection, close_connection
from Core.Common.logger import setup_logger
from Core.Backends.inventario_backend import InventarioBackend
from Core.Backends.gastos_backend import GastosBackend

logger = setup_logger()


class ComprasBackend:
    """Backend para gestión de compras"""
    
    def __init__(self):
        self.inventory_manager = InventarioBackend()
        self.gastos_backend = GastosBackend()
        self.logger = setup_logger()
        self.logger.info("✓ ComprasBackend inicializado")
    
    def save_purchase(
        self,
        tipo: str,
        nombre: str,
        proveedor: str,
        cantidad: Optional[float] = None,
        unidad: Optional[str] = None,
        precio_compra: Optional[float] = None,
        cantidad_paq: Optional[int] = None,
        precio_paq: Optional[float] = None,
        peso_paq: Optional[float] = None,
        unidad_peso: Optional[str] = None
    ) -> bool:
        """
        Guarda una compra en la base de datos.
        
        Args:
            tipo: 'granel' o 'paquetes'
            nombre: Nombre del producto
            proveedor: Nombre del proveedor
            ... (otros parámetros según tipo)
            
        Returns:
            bool: True si fue exitoso
        """
        self.logger.info(f"Guardando compra {tipo}: {nombre}")
        
        if not nombre or not proveedor:
            raise ValueError("Nombre y proveedor son obligatorios")
        
        conn = get_connection()
        if not conn:
            raise Exception("No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                if tipo == "granel":
                    cantidad = float(cantidad)
                    precio_compra = float(precio_compra)
                    precio_total = precio_compra * cantidad
                    
                    if not unidad:
                        raise ValueError("Unidad es obligatoria")
                    
                    cursor.execute(
                        """INSERT INTO compras 
                           (producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (nombre, str(cantidad), unidad, precio_compra, precio_total, proveedor, "granel")
                    )
                    
                    # Actualizar inventario
                    self.inventory_manager.actualizar_stock_desde_compra(
                        nombre, cantidad, unidad, precio_total
                    )
                    
                    self.logger.info(
                        f"✓ Compra granel guardada: {nombre}, "
                        f"{cantidad} {unidad}, ${precio_total:.2f}"
                    )
                
                # ✅ NUEVO: Registrar gasto monetario vinculado
                try:
                    from Core.Backends.gastos_backend import GastosBackend
                    gastos_b = GastosBackend()
                    gastos_b.add_gasto_dinero(
                        descripcion=f"Compra: {nombre}",
                        monto=precio_total,
                        comentario=f"Compra de {cantidad}{unidad} a {proveedor}"
                    )
                    self.logger.info(f"✓ Compra registrada como gasto: ${precio_total:.2f}")
                except Exception as e:
                    self.logger.warning(f"⚠️ No se pudo registrar gasto de compra: {e}")

                elif tipo == "paquetes":
                    cantidad_paq = int(cantidad_paq)
                    precio_paq = float(precio_paq)
                    peso_paq = float(peso_paq)
                    
                    if not unidad_peso:
                        raise ValueError("Unidad de peso es obligatoria")
                    
                    cantidad_total_peso = cantidad_paq * peso_paq
                    precio_total = cantidad_paq * precio_paq
                    
                    cursor.execute(
                        """INSERT INTO compras 
                           (producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (nombre, cantidad_total_peso, unidad_peso, precio_paq, precio_total, proveedor, "paquetes")
                    )
                    
                    # Actualizar inventario
                    self.inventory_manager.actualizar_stock_desde_compra(
                        nombre, cantidad_total_peso, unidad_peso, precio_total
                    )
                    
                    self.logger.info(
                        f"✓ Compra paquetes guardada: {nombre}, "
                        f"{cantidad_paq} paquetes, ${precio_paq:.2f} c/u"
                    )

                    # ✅ NUEVO: Registrar gasto monetario vinculado
                    try:
                        from Core.Backends.gastos_backend import GastosBackend
                        gastos_b = GastosBackend()
                        gastos_b.add_gasto_dinero(
                            descripcion=f"Compra: {nombre}",
                            monto=precio_total,
                            comentario=f"Compra de {cantidad}{unidad} a {proveedor}"
                        )
                        self.logger.info(f"✓ Compra registrada como gasto: ${precio_total:.2f}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ No se pudo registrar gasto de compra: {e}")

                
                else:
                    raise ValueError("Tipo de compra inválido")
            
            conn.commit()
            return True
            
        except ValueError as e:
            logger.error(f"❌ Validación fallida: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error guardando compra: {e}")
            conn.rollback()
            raise
        finally:
            close_connection(conn)
    
    def get_purchase_history(self, limit: int = 100) -> List[Dict]:
        """
        Obtiene historial de compras.
        
        Args:
            limit: Cantidad máxima de registros
            
        Returns:
            List[Dict]: Historial de compras
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM compras ORDER BY fecha DESC LIMIT %s""",
                    (limit,)
                )
                return cursor.fetchall() or []
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
        finally:
            close_connection(conn)
    
    def obtener_compras_por_producto(self, producto: str) -> List[Dict]:
        """
        Obtiene todas las compras de un producto.
        
        Args:
            producto: Nombre del producto
            
        Returns:
            List[Dict]: Compras del producto
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM compras WHERE producto = %s ORDER BY fecha DESC""",
                    (producto,)
                )
                return cursor.fetchall() or []
        except Exception as e:
            logger.error(f"Error obteniendo compras: {e}")
            return []
        finally:
            close_connection(conn)
    
    def obtener_compras_por_proveedor(self, proveedor: str) -> List[Dict]:
        """
        Obtiene todas las compras de un proveedor.
        
        Args:
            proveedor: Nombre del proveedor
            
        Returns:
            List[Dict]: Compras del proveedor
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM compras WHERE proveedor = %s ORDER BY fecha DESC""",
                    (proveedor,)
                )
                return cursor.fetchall() or []
        except Exception as e:
            logger.error(f"Error obteniendo compras: {e}")
            return []
        finally:
            close_connection(conn)