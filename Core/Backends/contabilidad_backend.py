"""
VERSIÓN CORREGIDA: Obtiene datos DIRECTAMENTE de las tablas existentes
Sin cálculos complejos, solo lectura de lo que YA ESTÁ GUARDADO
"""

from decimal import Decimal
from typing import List, Dict
from datetime import datetime

from Core.Common.database import get_connection, close_connection
from Core.Common.logger import setup_logger

logger = setup_logger()


class ContabilidadBackend:
    """Backend para gestión centralizada de contabilidad"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.logger.info("✅ ContabilidadBackend inicializado")
    
    def registrar_venta_contabilidad(self, venta_id: int, producto_final_id: int,
                                    cantidad: int, tipo_producto: str) -> Dict:
        """
        Registra una venta en contabilidad.
        
        ESTRATEGIA ROBUSTA:
        1. Obtener precio_venta de productos_finales (ya está definido por el usuario)
        2. Obtener costo_unitario_total de productos_finales (ya está calculado)
        3. Cantidad viene de parámetro
        4. Calcular: costo_total = costo_unitario * cantidad
        5. Calcular: ingreso_total = precio_venta * cantidad
        6. Calcular: ganancia = ingreso_total - costo_total
        """
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                # ============================================
                # PASO 1: Obtener datos del PRODUCTO FINAL
                # ============================================
                # Estos datos YA fueron definidos/calculados
                # cuando se creó el producto final
                cursor.execute("""
                    SELECT 
                        costo_unitario_total,
                        precio_venta
                    FROM productos_finales
                    WHERE id = %s
                """, (producto_final_id,))
                
                resultado = cursor.fetchone()
                
                if not resultado:
                    raise ValueError(f"❌ Producto final {producto_final_id} no encontrado")
                
                # ✅ Estos valores YA existen en productos_finales
                precio_costo_unitario = Decimal(str(resultado.get('costo_unitario_total', 0) or 0))
                precio_venta_unitario = Decimal(str(resultado.get('precio_venta', 0) or 0))
                
                # ============================================
                # PASO 2: Calculos simples
                # ============================================
                cantidad_dec = Decimal(cantidad)
                
                # Basados en costo y venta unitarios YA existentes
                costo_total = cantidad_dec * precio_costo_unitario
                ingreso_total = cantidad_dec * precio_venta_unitario
                ganancia_neta = ingreso_total - costo_total
                
                # Margen
                if ingreso_total > 0:
                    margen = (ganancia_neta / ingreso_total * 100)
                else:
                    margen = Decimal(0)
                
                self.logger.info(
                    f"✅ Venta registrada en contabilidad:\n"
                    f"   Producto ID: {producto_final_id}\n"
                    f"   Cantidad: {cantidad} unidades\n"
                    f"   Costo/U: ${float(precio_costo_unitario):.2f}\n"
                    f"   Venta/U: ${float(precio_venta_unitario):.2f}\n"
                    f"   ---\n"
                    f"   Costo Total: ${float(costo_total):.2f}\n"
                    f"   Ingreso Total: ${float(ingreso_total):.2f}\n"
                    f"   Ganancia Neta: ${float(ganancia_neta):.2f}\n"
                    f"   Margen: {float(margen):.2f}%"
                )
                
                # ============================================
                # PASO 3: Insertar en contabilidad
                # ============================================
                cursor.execute("""
                    INSERT INTO contabilidad (
                        venta_id, producto_final_id, cantidad_vendida,
                        precio_unitario_costo, precio_unitario_venta,
                        costo_total, ingreso_total, ganancia_neta,
                        margen_ganancia, tipo_producto
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    venta_id, producto_final_id, int(cantidad),
                    float(precio_costo_unitario), float(precio_venta_unitario),
                    float(costo_total), float(ingreso_total),
                    float(ganancia_neta), float(margen),
                    tipo_producto
                ))
                
                conn.commit()
                
                return {
                    'venta_id': venta_id,
                    'cantidad': int(cantidad),
                    'costo_unitario': float(precio_costo_unitario),
                    'precio_venta': float(precio_venta_unitario),
                    'costo_total': float(costo_total),
                    'ingreso_total': float(ingreso_total),
                    'ganancia_neta': float(ganancia_neta),
                    'margen': float(margen)
                }
        
        except Exception as e:
            logger.error(f"❌ Error registrando venta: {e}")
            import traceback
            logger.error(traceback.format_exc())
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)
    
    def obtener_resumen_general(self) -> Dict:
        """Obtiene resumen general - SIN CAMBIOS"""
        conn = get_connection()
        if not conn:
            return {}
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_ventas,
                        SUM(cantidad_vendida) as total_unidades,
                        SUM(ingreso_total) as total_ingresos,
                        SUM(costo_total) as total_costos,
                        SUM(ganancia_neta) as total_ganancia,
                        AVG(margen_ganancia) as margen_promedio
                    FROM contabilidad
                """)
                
                resultado = cursor.fetchone()
                
                return {
                    'total_ventas': int(resultado.get('total_ventas', 0) or 0),
                    'total_unidades': int(resultado.get('total_unidades', 0) or 0),
                    'total_ingresos': float(resultado.get('total_ingresos', 0) or 0),
                    'total_costos': float(resultado.get('total_costos', 0) or 0),
                    'total_ganancia': float(resultado.get('total_ganancia', 0) or 0),
                    'margen_promedio': float(resultado.get('margen_promedio', 0) or 0)
                }
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return {}
        
        finally:
            close_connection(conn)
    
    def obtener_resumen_por_tipo_producto(self) -> List[Dict]:
        """Resumen por tipo - SIN CAMBIOS"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        tipo_producto,
                        COUNT(*) as num_ventas,
                        SUM(cantidad_vendida) as total_unidades,
                        SUM(ingreso_total) as total_ingresos,
                        SUM(costo_total) as total_costos,
                        SUM(ganancia_neta) as total_ganancia,
                        AVG(precio_unitario_costo) as costo_promedio,
                        AVG(precio_unitario_venta) as venta_promedio,
                        AVG(margen_ganancia) as margen_promedio
                    FROM contabilidad
                    GROUP BY tipo_producto
                    ORDER BY total_ganancia DESC
                """)
                
                resultados = cursor.fetchall() or []
                
                return [
                    {
                        'tipo_producto': r['tipo_producto'],
                        'num_ventas': int(r['num_ventas']),
                        'total_unidades': int(r['total_unidades'] or 0),
                        'total_ingresos': float(r['total_ingresos'] or 0),
                        'total_costos': float(r['total_costos'] or 0),
                        'total_ganancia': float(r['total_ganancia'] or 0),
                        'costo_promedio': float(r['costo_promedio'] or 0),
                        'venta_promedio': float(r['venta_promedio'] or 0),
                        'margen_promedio': float(r['margen_promedio'] or 0)
                    }
                    for r in resultados
                ]
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
        
        finally:
            close_connection(conn)
    
    def obtener_resumen_por_producto(self) -> List[Dict]:
        """Resumen por producto - SIN CAMBIOS"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        c.producto_final_id,
                        pf.nombre as nombre_producto,
                        c.tipo_producto,
                        COUNT(*) as num_ventas,
                        SUM(c.cantidad_vendida) as total_unidades,
                        SUM(c.ingreso_total) as total_ingresos,
                        SUM(c.costo_total) as total_costos,
                        SUM(c.ganancia_neta) as total_ganancia,
                        AVG(c.precio_unitario_costo) as costo_promedio,
                        AVG(c.precio_unitario_venta) as venta_promedio,
                        AVG(c.margen_ganancia) as margen_promedio
                    FROM contabilidad c
                    JOIN productos_finales pf ON c.producto_final_id = pf.id
                    GROUP BY c.producto_final_id, pf.nombre, c.tipo_producto
                    ORDER BY total_ganancia DESC
                """)
                
                resultados = cursor.fetchall() or []
                
                return [
                    {
                        'producto_id': r['producto_final_id'],
                        'nombre_producto': r['nombre_producto'],
                        'tipo_producto': r['tipo_producto'],
                        'num_ventas': int(r['num_ventas']),
                        'total_unidades': int(r['total_unidades'] or 0),
                        'total_ingresos': float(r['total_ingresos'] or 0),
                        'total_costos': float(r['total_costos'] or 0),
                        'total_ganancia': float(r['total_ganancia'] or 0),
                        'costo_promedio': float(r['costo_promedio'] or 0),
                        'venta_promedio': float(r['venta_promedio'] or 0),
                        'margen_promedio': float(r['margen_promedio'] or 0)
                    }
                    for r in resultados
                ]
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
        
        finally:
            close_connection(conn)
    
    def obtener_historial_contabilidad(self, limit: int = 100) -> List[Dict]:
        """Historial de transacciones - SIN CAMBIOS"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        c.id,
                        c.fecha_venta,
                        pf.nombre as producto,
                        c.tipo_producto,
                        c.cantidad_vendida,
                        c.precio_unitario_costo,
                        c.precio_unitario_venta,
                        c.costo_total,
                        c.ingreso_total,
                        c.ganancia_neta,
                        c.margen_ganancia
                    FROM contabilidad c
                    JOIN productos_finales pf ON c.producto_final_id = pf.id
                    ORDER BY c.fecha_venta DESC
                    LIMIT %s
                """, (limit,))
                
                resultados = cursor.fetchall() or []
                
                return [
                    {
                        'id': r['id'],
                        'fecha': str(r['fecha_venta']),
                        'producto': r['producto'],
                        'tipo_producto': r['tipo_producto'],
                        'cantidad': int(r['cantidad_vendida']),
                        'costo_unitario': float(r['precio_unitario_costo']),
                        'venta_unitaria': float(r['precio_unitario_venta']),
                        'costo_total': float(r['costo_total']),
                        'ingreso_total': float(r['ingreso_total']),
                        'ganancia_neta': float(r['ganancia_neta']),
                        'margen': float(r['margen_ganancia'])
                    }
                    for r in resultados
                ]
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
        
        finally:
            close_connection(conn)