"""
Core.Backends.gastos_backend - Gestión de gastos
"""

from typing import List, Dict, Optional
from Core.Common.database import get_connection, close_connection
from Core.Common.logger import setup_logger
from Core.Backends.inventario_backend import InventarioBackend

logger = setup_logger()


class GastosBackend:
    """Backend para gestión de gastos"""
    
    def __init__(self):
        self.inventory = InventarioBackend()
        self.logger = setup_logger()
        self.logger.info("✓ GastosBackend inicializado")
    
    def add_gasto_dinero(
        self,
        descripcion: str,
        monto: float,
        comentario: str = ""
    ) -> bool:
        """
        Registra un gasto monetario.
        
        Args:
            descripcion: Descripción del gasto
            monto: Monto del gasto
            comentario: Comentario opcional
            
        Returns:
            bool: True si fue exitoso
        """
        conn = get_connection()
        if not conn:
            raise Exception("No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO gastos_money (descripcion, monto, comentarios) 
                       VALUES (%s, %s, %s)""",
                    (descripcion, round(float(monto), 2), comentario)
                )
            
            conn.commit()
            self.logger.info(
                f"✓ Gasto monetario registrado: {descripcion} - ${monto:.2f}"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ Error insertando gasto monetario: {e}")
            conn.rollback()
            raise
        finally:
            close_connection(conn)
    
    def add_gasto_producto(
        self,
        producto: str,
        cantidad: float,
        unidad: str,
        precio_total: float,
        comentario: str = ""
    ) -> bool:
        """
        Registra un gasto en producto (consume inventario).
        
        Args:
            producto: Nombre del producto
            cantidad: Cantidad consumida
            unidad: Unidad de medida
            precio_total: Precio total del gasto
            comentario: Comentario opcional
            
        Returns:
            bool: True si fue exitoso
        """
        # Consumir stock primero
        try:
            self.inventory.consumir_stock(producto, cantidad, unidad)
        except Exception as e:
            logger.error(f"No se pudo consumir stock: {e}")
            raise
        
        conn = get_connection()
        if not conn:
            raise Exception("No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO gastos_productos 
                       (producto, cantidad, unidad, precio_total, comentarios) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (producto, float(cantidad), unidad, round(float(precio_total), 2), comentario)
                )
            
            conn.commit()
            self.logger.info(
                f"✓ Gasto producto registrado: {producto} - "
                f"{cantidad}{unidad} - ${precio_total:.2f}"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ Error insertando gasto producto: {e}")
            conn.rollback()
            raise
        finally:
            close_connection(conn)
    
    def get_total_gastos(self) -> float:
        """
        Obtiene total de gastos (dinero + productos).
        
        Returns:
            float: Total de gastos
        """
        conn = get_connection()
        if not conn:
            return 0.0
        
        try:
            with conn.cursor() as cursor:
                # Gastos en dinero
                cursor.execute("SELECT COALESCE(SUM(monto), 0) AS total FROM gastos_money")
                r1 = cursor.fetchone() or {"total": 0}
                
                # Gastos en productos
                cursor.execute("SELECT COALESCE(SUM(precio_total), 0) AS total FROM gastos_productos")
                r2 = cursor.fetchone() or {"total": 0}
                
                total = float(r1.get("total", 0) or 0) + float(r2.get("total", 0) or 0)
                return total
                
        except Exception as e:
            logger.error(f"Error calculando total gastos: {e}")
            return 0.0
        finally:
            close_connection(conn)
    
    def get_gastos_recientes(self, limit: int = 50) -> List[Dict]:
        """
        Obtiene gastos recientes combinados.
        
        Args:
            limit: Cantidad máxima de registros
            
        Returns:
            List[Dict]: Gastos ordenados por fecha DESC
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                # Gastos en dinero
                cursor.execute(
                    """SELECT id, descripcion, monto, fecha, comentarios 
                       FROM gastos_money ORDER BY fecha DESC LIMIT %s""",
                    (limit,)
                )
                money = cursor.fetchall() or []
                
                # Gastos en productos
                cursor.execute(
                    """SELECT id, producto, cantidad, unidad, precio_total, fecha, comentarios 
                       FROM gastos_productos ORDER BY fecha DESC LIMIT %s""",
                    (limit,)
                )
                products = cursor.fetchall() or []
                
                combined = []
                
                for r in money:
                    combined.append({
                        "type": "money",
                        "id": r.get("id"),
                        "descripcion": r.get("descripcion"),
                        "monto": float(r.get("monto") or 0),
                        "fecha": str(r.get("fecha")),
                        "comentarios": r.get("comentarios", "") or ""
                    })
                
                for r in products:
                    combined.append({
                        "type": "product",
                        "id": r.get("id"),
                        "producto": r.get("producto"),
                        "cantidad": float(r.get("cantidad") or 0),
                        "unidad": r.get("unidad"),
                        "monto": float(r.get("precio_total") or 0),
                        "fecha": str(r.get("fecha")),
                        "comentarios": r.get("comentarios", "") or ""
                    })
                
                combined.sort(key=lambda x: x.get("fecha", ""), reverse=True)
                return combined[:limit]
                
        except Exception as e:
            logger.error(f"Error obteniendo gastos recientes: {e}")
            return []
        finally:
            close_connection(conn)
    
    def get_gastos_por_rango_fechas(
        self,
        fecha_inicio: str,
        fecha_fin: str
    ) -> Dict:
        """
        Obtiene gastos en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha inicio (YYYY-MM-DD)
            fecha_fin: Fecha fin (YYYY-MM-DD)
            
        Returns:
            Dict con gastos dinero y productos
        """
        conn = get_connection()
        if not conn:
            return {"money": [], "products": []}
        
        try:
            with conn.cursor() as cursor:
                # Gastos dinero
                cursor.execute(
                    """SELECT * FROM gastos_money 
                       WHERE DATE(fecha) BETWEEN %s AND %s 
                       ORDER BY fecha DESC""",
                    (fecha_inicio, fecha_fin)
                )
                money = cursor.fetchall() or []
                
                # Gastos productos
                cursor.execute(
                    """SELECT * FROM gastos_productos 
                       WHERE DATE(fecha) BETWEEN %s AND %s 
                       ORDER BY fecha DESC""",
                    (fecha_inicio, fecha_fin)
                )
                products = cursor.fetchall() or []
                
                return {
                    "money": money,
                    "products": products
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo gastos por fechas: {e}")
            return {"money": [], "products": []}
        finally:
            close_connection(conn)

    def obtener_capital_total(self) -> float:
        """
        Obtiene capital total SOLO Capital Extra.
        
        Este capital es lo que el usuario injected directamente.
        NO incluye ganancias de ventas.
        
        Returns:
            float: Total de capital extra en sistema
        """
        conn = get_connection()
        if not conn:
            return 0.0
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(monto), 0) as total
                    FROM efectivo_movimientos
                    WHERE tipo = 'Capital Extra'
                """)
                resultado = cursor.fetchone()
                capital = float(resultado.get('total', 0) or 0)
                
                self.logger.info(f"💰 Capital Total (Extra): ${capital:.2f}")
                return capital
        
        except Exception as e:
            self.logger.error(f"Error obteniendo capital total: {e}")
            return 0.0
        finally:
            close_connection(conn)