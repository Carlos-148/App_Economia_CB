"""
Core.Backends.ventas_backend - Backend de ventas
Corrección de Decimal/Float
"""

import pymysql
from Core.Common.database import get_connection, close_connection
from decimal import Decimal
from Core.Common.logger import setup_logger
from Core.Backends.produccion_backend import ProduccionBackend

logger = setup_logger()

class VentasBackend:
    def __init__(self):
        self.prod_backend = ProduccionBackend()
        logger.info("VentasBackend inicializado")

    def add_cliente(self, nombre_cliente):
        """Agrega un nuevo cliente"""
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO clientes (nombre) VALUES (%s)", (nombre_cliente,))
            conn.commit()
            logger.info(f"✅ Cliente '{nombre_cliente}' creado")
        
        except pymysql.IntegrityError:
            logger.warning(f"Cliente '{nombre_cliente}' ya existe")
            raise ValueError("Este cliente ya existe")
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)

    def get_clientes(self, only_active=False):
        """Obtiene clientes"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM clientes LIKE 'active'")
                has_active = bool(cursor.fetchone())
                
                if has_active:
                    if only_active:
                        cursor.execute("SELECT id, nombre, active FROM clientes WHERE active = 1 ORDER BY nombre")
                    else:
                        cursor.execute("SELECT id, nombre, active FROM clientes ORDER BY nombre")
                    return cursor.fetchall()
                else:
                    cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
                    rows = cursor.fetchall()
                    return [{"id": r["id"], "nombre": r["nombre"], "active": 1} for r in rows]
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
        
        finally:
            close_connection(conn)

    def toggle_cliente_active(self, cliente_id):
        """Cambia estado activo/inactivo"""
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM clientes LIKE 'active'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE clientes ADD COLUMN active TINYINT(1) NOT NULL DEFAULT 1")
                
                cursor.execute("SELECT active FROM clientes WHERE id = %s", (cliente_id,))
                row = cursor.fetchone()
                
                if not row:
                    raise ValueError("Cliente no encontrado")
                
                new_state = 0 if row.get("active", 1) == 1 else 1
                cursor.execute("UPDATE clientes SET active = %s WHERE id = %s", (new_state, cliente_id))
            
            conn.commit()
            return new_state
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)

    def get_clientes_activos(self):
        """Obtiene clientes activos"""
        return self.get_clientes(only_active=True)

    def get_productos_con_costo(self):
        """Obtiene productos finales con costo"""
        productos_info = self.prod_backend.get_productos_finales_info()
        result = []

        conn = get_connection()
        
        try:
            for p in productos_info:
                pid = p.get("id")
                precio_venta = p.get("precio_venta", None)
                
                # ✅ Convertir a float correctamente
                costo_unitario = float(p.get("costo_unitario_total", 0) or 0)
                
                precio_venta_final = float(precio_venta) if precio_venta is not None else 0.0
                
                ganancia = round(precio_venta_final - costo_unitario, 2)
                ganancia_pct = round((ganancia / costo_unitario * 100), 2) if costo_unitario > 0 else 0

                result.append({
                    "id": pid,
                    "nombre": p.get("nombre"),
                    "costo_unitario": costo_unitario,
                    "precio_venta": precio_venta_final,
                    "ganancia_unitaria": ganancia,
                    "ganancia_pct": ganancia_pct
                })
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
        
        finally:
            if conn:
                close_connection(conn)

    def set_precio_venta(self, producto_final_id, precio):
        """Asigna precio de venta"""
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM productos_finales LIKE 'precio_venta'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE productos_finales ADD COLUMN precio_venta DECIMAL(10,2) NULL DEFAULT NULL")
                
                # ✅ Convertir a float
                precio_float = float(precio)
                
                cursor.execute(
                    "UPDATE productos_finales SET precio_venta = %s WHERE id = %s",
                    (round(precio_float, 2), producto_final_id)
                )
            
            conn.commit()
            logger.info(f"✅ Precio actualizado: ${precio_float:.2f}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)

    def registrar_venta(self, cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta):
        """Registra una venta"""
        return self.crear_venta_multiple(cliente_id, [{
            "product_id": producto_final_id,
            "quantity": cantidad_vendida,
            "unit_price": precio_unitario_venta
        }])


    def crear_venta_multiple(self, cliente_id, items):
        """Crea venta con múltiples items - REGISTRA EN CONTABILIDAD"""
        if not items:
            raise ValueError("No hay items")
        
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión")
        
        from Core.Backends.contabilidad_backend import ContabilidadBackend  # ✅ AGREGAR
        contabilidad_backend = ContabilidadBackend()  # ✅ AGREGAR
        
        try:
            total_venta = 0.0
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, COALESCE(active,1) as active FROM clientes WHERE id = %s", (cliente_id,))
                klient = cursor.fetchone()
                
                if not klient:
                    raise ValueError("Cliente no encontrado")
                
                if klient.get("active", 1) != 1:
                    raise ValueError("Cliente inactivo")

                cursor.execute("INSERT INTO ventas_cabecera (cliente_id, total_venta) VALUES (%s, %s)", (cliente_id, 0.0))
                venta_id = cursor.lastrowid

                for it in items:
                    producto_id = it["product_id"]
                    cantidad = int(it.get("quantity", 1))
                    unit_price = float(it.get("unit_price", 0))
                    subtotal = round(cantidad * unit_price, 2)
                    total_venta += subtotal
                    
                    cursor.execute(
                        "INSERT INTO ventas_items (venta_id, producto_final_id, cantidad_vendida, precio_unitario_venta, subtotal) VALUES (%s, %s, %s, %s, %s)",
                        (venta_id, producto_id, cantidad, unit_price, subtotal)
                    )

                cursor.execute("UPDATE ventas_cabecera SET total_venta = %s WHERE id = %s", (round(total_venta, 2), venta_id))

            conn.commit()
            
            # ✅ REGISTRAR EN CONTABILIDAD
            for it in items:
                try:
                    producto_id = it["product_id"]
                    cantidad = int(it.get("quantity", 1))
                    
                    # Obtener tipo de producto
                    cursor = conn.cursor()
                    cursor.execute("SELECT nombre FROM productos_finales WHERE id = %s", (producto_id,))
                    resultado = cursor.fetchone()
                    tipo_producto = resultado.get('nombre', 'general') if resultado else 'general'
                    
                    contabilidad_backend.registrar_venta_contabilidad(
                        venta_id, producto_id, cantidad, tipo_producto
                    )
                except Exception as e:
                    logger.warning(f"Error registrando en contabilidad: {e}")
            
            logger.info(f"✅ Venta registrada: ${total_venta:.2f}")
            
            return {"venta_id": venta_id, "cliente_id": cliente_id, "total": total_venta}
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)
            
    def get_cliente_stats(self, cliente_id):
        """Estadísticas del cliente"""
        conn = get_connection()
        if not conn:
            return {"purchases_count": 0, "total_revenue": 0.0}
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS cnt FROM ventas_cabecera WHERE cliente_id = %s", (cliente_id,))
                row = cursor.fetchone() or {"cnt": 0}
                purchases_count = int(row.get("cnt", 0))

                cursor.execute("""
                    SELECT COALESCE(SUM(vi.subtotal),0) AS total
                    FROM ventas_cabecera vc
                    JOIN ventas_items vi ON vc.id = vi.venta_id
                    WHERE vc.cliente_id = %s
                """, (cliente_id,))
                row2 = cursor.fetchone() or {"total": 0}
                # ✅ Convertir a float
                total_revenue = float(row2.get("total", 0.0) or 0)

                return {"purchases_count": purchases_count, "total_revenue": total_revenue}
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return {"purchases_count": 0, "total_revenue": 0.0}
        
        finally:
            close_connection(conn)

    def get_ventas_por_dia(self, cliente_id):
        """Ventas por día"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT DATE(vc.fecha_venta) AS dia, COUNT(*) AS ventas_count, COALESCE(SUM(vi.subtotal),0) AS total_sum
                    FROM ventas_cabecera vc
                    JOIN ventas_items vi ON vc.id = vi.venta_id
                    WHERE vc.cliente_id = %s
                    GROUP BY dia
                    ORDER BY dia DESC
                """
                cursor.execute(sql, (cliente_id,))
                rows = cursor.fetchall()
                
                return [{
                    "day": str(r["dia"]),
                    "sales_count": int(r["ventas_count"]),
                    # ✅ Convertir a float
                    "total_sum": float(r["total_sum"] or 0)
                } for r in rows]
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
        
        finally:
            close_connection(conn)

    def get_historial_ventas(self):
        """Historial completo de ventas"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    vi.id AS item_id,
                    vc.fecha_venta,
                    c.nombre AS cliente,
                    pf.id AS producto_id,
                    pf.nombre AS producto,
                    vi.cantidad_vendida,
                    vi.precio_unitario_venta,
                    vi.subtotal
                FROM ventas_items vi
                JOIN ventas_cabecera vc ON vi.venta_id = vc.id
                LEFT JOIN clientes c ON vc.cliente_id = c.id
                LEFT JOIN productos_finales pf ON vi.producto_final_id = pf.id
                ORDER BY vc.fecha_venta DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
        
        finally:
            close_connection(conn)