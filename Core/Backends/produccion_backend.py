"""
Core.Backends.produccion_backend - Backend de gestión de producción
CORRECCIÓN: Cálculo correcto de costos
"""

import pymysql
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from Core.Common.database import get_connection, close_connection
from Core.Common.logger import setup_logger
from Core.Backends.inventario_backend import InventarioBackend
from Core.Common.units import convert_to_base

logger = setup_logger()


class ProduccionBackend:
    """
    Backend de producción con cálculos CORRECTOS
    """
    
    def __init__(self):
        """Inicializa el backend"""
        self.inventory_manager = InventarioBackend()
        self.logger = setup_logger()
        self.logger.info("ProduccionBackend inicializado")
    
    # ============================================
    # SUBPRODUCTOS (Recetas base)
    # ============================================
    
    def crear_subproducto(self, nombre_subproducto: str, ingredientes: List[Dict]) -> Decimal:
        """Crea un subproducto calculando el costo TOTAL"""
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        total_costo = Decimal(0)
        detalles_ingredientes = []
        
        try:
            with conn.cursor() as cursor:
                for ing in ingredientes:
                    producto = ing['producto']
                    cantidad = float(ing['cantidad'])
                    unidad = ing['unidad']
                    
                    cursor.execute(
                        "SELECT costo_promedio_ponderado FROM inventario WHERE producto = %s",
                        (producto,)
                    )
                    result = cursor.fetchone()
                    
                    if not result:
                        raise ValueError(f"❌ Ingrediente '{producto}' no está en inventario")
                    
                    costo_por_base = Decimal(str(result['costo_promedio_ponderado']))
                    cantidad_base, base_unit = convert_to_base(cantidad, unidad)
                    
                    if cantidad_base is None:
                        raise ValueError(f"❌ No se pudo convertir {cantidad}{unidad}")
                    
                    costo_ingrediente = Decimal(str(cantidad_base)) * costo_por_base
                    total_costo += costo_ingrediente
                    
                    detalles_ingredientes.append({
                        'producto': producto,
                        'cantidad': cantidad,
                        'unidad': unidad,
                        'cantidad_base': float(cantidad_base),
                        'base_unit': base_unit,
                        'costo_por_base': float(costo_por_base),
                        'costo_total': float(costo_ingrediente)
                    })
                    
                    self.logger.debug(
                        f"  {producto}: {cantidad}{unidad} → {cantidad_base}{base_unit} × "
                        f"${float(costo_por_base):.4f} = ${float(costo_ingrediente):.2f}"
                    )
            
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO subproductos (nombre, costo_total_subproducto) VALUES (%s, %s)",
                    (nombre_subproducto, float(total_costo))
                )
                subproducto_id = cursor.lastrowid
                
                for ing in ingredientes:
                    cursor.execute(
                        """INSERT INTO subproducto_ingredientes 
                           (subproducto_id, producto_ingrediente, cantidad_usada, unidad_usada) 
                           VALUES (%s, %s, %s, %s)""",
                        (subproducto_id, ing['producto'], float(ing['cantidad']), ing['unidad'])
                    )
            
            conn.commit()
            
            self.logger.info(
                f"✅ Subproducto '{nombre_subproducto}' creado\n"
                f"   Costo Total (receta completa): ${float(total_costo):.2f}"
            )
            
            return total_costo
        
        except Exception as e:
            logger.error(f"❌ Error creando subproducto: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)
    
    def get_subproductos_disponibles(self) -> List[Dict]:
        """Obtiene todos los subproductos"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, costo_total_subproducto FROM subproductos ORDER BY nombre"
                )
                return cursor.fetchall() or []
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo subproductos: {e}")
            return []
        
        finally:
            close_connection(conn)
    
    def get_subproducto_ingredientes(self, subproducto_id: int) -> List[Dict]:
        """Obtiene ingredientes de un subproducto"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT id, producto_ingrediente, cantidad_usada, unidad_usada 
                       FROM subproducto_ingredientes WHERE subproducto_id = %s""",
                    (subproducto_id,)
                )
                return cursor.fetchall() or []
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo ingredientes: {e}")
            return []
        
        finally:
            close_connection(conn)
    
    def eliminar_subproducto(self, subproducto_id: int) -> bool:
        """Elimina un subproducto"""
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM subproducto_ingredientes WHERE subproducto_id = %s", (subproducto_id,))
                cursor.execute("DELETE FROM subproductos WHERE id = %s", (subproducto_id,))
            
            conn.commit()
            logger.info(f"✅ Subproducto {subproducto_id} eliminado")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error eliminando subproducto: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)
    
    # ============================================
    # ESTIMACIÓN Y PRODUCCIÓN
    # ============================================
    
    def estimar_costo_produccion(self, subproducto_id: int, unidades_producidas: int) -> Dict:
        """Estima el costo de producción"""
        if unidades_producidas <= 0:
            raise ValueError("❌ Unidades debe ser > 0")
        
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT costo_total_subproducto FROM subproductos WHERE id = %s",
                    (subproducto_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"❌ Subproducto {subproducto_id} no encontrado")
                
                costo_total_receta = Decimal(str(result['costo_total_subproducto']))
            
            close_connection(conn)
            
            costo_unitario = costo_total_receta / Decimal(unidades_producidas)
            costo_total_masa = costo_total_receta
            
            self.logger.info(
                f"📊 Estimación de Producción:\n"
                f"   Costo Receta Total: ${float(costo_total_receta):.2f}\n"
                f"   Unidades a Producir: {unidades_producidas}\n"
                f"   Costo por Unidad: ${float(costo_total_receta):.2f} ÷ {unidades_producidas} = ${float(costo_unitario):.2f}\n"
                f"   Costo Total Masa: ${float(costo_total_masa):.2f}"
            )
            
            return {
                "costo_total_masa": float(costo_total_masa),
                "costo_unitario": float(costo_unitario)
            }
        
        except Exception as e:
            logger.error(f"❌ Error estimando costo: {e}")
            raise
    
    def crear_produccion_run(
        self,
        subproducto_id: int,
        unidades_producidas: int,
        tipo_unidad: str = "reales"
    ) -> Dict:
        """Crea una ejecución de producción (consume stock)"""
        if unidades_producidas <= 0:
            raise ValueError("❌ Unidades debe ser > 0")
        
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        try:
            ingredientes = self.get_subproducto_ingredientes(subproducto_id)
            if not ingredientes:
                raise ValueError("❌ Subproducto sin ingredientes")
            
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT costo_total_subproducto FROM subproductos WHERE id = %s",
                    (subproducto_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"❌ Subproducto no encontrado")
                
                costo_total_receta = Decimal(str(result['costo_total_subproducto']))
            
            for ing in ingredientes:
                producto = ing['producto_ingrediente']
                cantidad = float(ing['cantidad_usada'])
                unidad = ing['unidad_usada']
                
                self.inventory_manager.consumir_stock(producto, cantidad, unidad)
            
            costo_unitario = costo_total_receta / Decimal(unidades_producidas)
            
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO subproducto_producciones 
                       (subproducto_id, unidades_producidas, tipo_unidad, 
                        costo_total_masa, costo_unitario) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (
                        subproducto_id,
                        int(unidades_producidas),
                        tipo_unidad,
                        round(float(costo_total_receta), 2),
                        round(float(costo_unitario), 4)
                    )
                )
                prod_id = cursor.lastrowid
            
            conn.commit()
            
            self.logger.info(
                f"✅ Producción creada:\n"
                f"   Subproducto ID: {subproducto_id}\n"
                f"   Unidades Producidas: {unidades_producidas}\n"
                f"   Costo Total: ${float(costo_total_receta):.2f}\n"
                f"   Costo/Unidad: ${float(costo_unitario):.2f}"
            )
            
            return {
                'produccion_id': prod_id,
                'subproducto_id': subproducto_id,
                'unidades_producidas': unidades_producidas,
                'tipo_unidad': tipo_unidad,
                'costo_total_masa': float(costo_total_receta),
                'costo_unitario': float(costo_unitario)
            }
        
        except Exception as e:
            logger.error(f"❌ Error creando producción: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)
    
    def get_producciones_por_subproducto(self, subproducto_id: int, limit: int = 50) -> List[Dict]:
        """Obtiene historial de producciones"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM subproducto_producciones 
                       WHERE subproducto_id = %s 
                       ORDER BY created_at DESC 
                       LIMIT %s""",
                    (subproducto_id, limit)
                )
                return cursor.fetchall() or []
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo producciones: {e}")
            return []
        
        finally:
            close_connection(conn)
    
    # ============================================
    # PRODUCTOS FINALES
    # ============================================

    def crear_producto_final(
        self,
        nombre_producto: str,
        subproductos_config: List[Dict],
        precio_venta: float = 0
    ) -> Dict:
        """Crea un producto final a partir de múltiples subproductos
        
        IMPORTANTE: 
        - subproductos_config contiene unidades_rinde
        - Cada subproducto tiene un costo_total_subproducto
        - Dividimos por unidades_rinde para obtener costo UNITARIO
        """
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        try:
            costo_producto_final = Decimal(0)
            detalles_subproductos = []
            
            with conn.cursor() as cursor:
                # Iterar sobre CADA subproducto en la configuración
                for config in subproductos_config:
                    subproducto_id = config['subproducto_id']
                    unidades_rinde = config['unidades_rinde']
                    
                    # Obtener datos del subproducto
                    cursor.execute(
                        "SELECT id, nombre, costo_total_subproducto FROM subproductos WHERE id = %s",
                        (subproducto_id,)
                    )
                    subproducto = cursor.fetchone()
                    
                    if not subproducto:
                        raise ValueError(f"❌ Subproducto {subproducto_id} no encontrado")
                    
                    # ✅ CÁLCULO CORRECTO:
                    # costo_total_subproducto es el costo de TODA la receta
                    # unidades_rinde es cuántas UNIDADES FINALES produce
                    # El costo unitario = costo_total / unidades_rinde
                    
                    costo_total_sub = Decimal(str(subproducto['costo_total_subproducto']))
                    costo_por_unidad_final = costo_total_sub / Decimal(unidades_rinde)
                    
                    # Sumar al costo total del producto final
                    costo_producto_final += costo_por_unidad_final
                    
                    detalles_subproductos.append({
                        'subproducto_id': subproducto_id,
                        'nombre': subproducto['nombre'],
                        'costo_total_subproducto': float(costo_total_sub),
                        'unidades_rinde': unidades_rinde,
                        'costo_por_unidad_final': float(costo_por_unidad_final)
                    })
                    
                    self.logger.debug(
                        f"  {subproducto['nombre']}:\n"
                        f"    Costo Total Receta: ${float(costo_total_sub):.2f}\n"
                        f"    Unidades Rinde: {unidades_rinde}\n"
                        f"    Cálculo: ${float(costo_total_sub):.2f} ÷ {unidades_rinde} = ${float(costo_por_unidad_final):.2f} por unidad\n"
                        f"    Aporte al Costo Final: ${float(costo_por_unidad_final):.2f}"
                    )
                
                # ✅ GUARDAR: costo_producto_final YA ES EL COSTO UNITARIO
                cursor.execute(
                    """INSERT INTO productos_finales 
                    (nombre, unidades_producidas, precio_venta, costo_unitario_total) 
                    VALUES (%s, %s, %s, %s)""",
                    (
                        nombre_producto, 
                        1, 
                        round(float(precio_venta), 2) if precio_venta else None, 
                        round(float(costo_producto_final), 4)  # ✅ YA ES UNITARIO
                    )
                )
                producto_id = cursor.lastrowid
                
                # Crear relaciones producto-subproductos
                for config in subproductos_config:
                    cursor.execute(
                        """INSERT INTO producto_final_subproductos 
                        (producto_final_id, subproducto_id, unidades_rinde) 
                        VALUES (%s, %s, %s)""",
                        (producto_id, config['subproducto_id'], config['unidades_rinde'])
                    )
            
            conn.commit()
            
            # Calcular ganancia
            ganancia_margen = 0
            if costo_producto_final > 0 and precio_venta:
                ganancia_margen = ((Decimal(precio_venta) - costo_producto_final) / costo_producto_final * 100)
            
            resultado = {
                'producto_id': producto_id,
                'nombre': nombre_producto,
                'costo_total': float(costo_producto_final),  # ✅ UNITARIO
                'precio_venta': float(precio_venta) if precio_venta else 0,
                'margen': float(ganancia_margen),
                'subproductos': detalles_subproductos
            }
            
            self.logger.info(
                f"✅ Producto Final '{nombre_producto}' creado\n"
                f"   Costo por Unidad Final: ${float(costo_producto_final):.2f}\n"
                f"   (Suma de costos unitarios de subproductos)"
            )
            
            return resultado
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)

            
    def get_productos_finales_info(self) -> List[Dict]:
        """Obtiene información de productos finales con cálculos CORRECTOS"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT 
                        pf.id,
                        pf.nombre,
                        pf.unidades_producidas,
                        pf.precio_venta,
                        GROUP_CONCAT(sp.nombre SEPARATOR ' + ') AS subproductos_str
                    FROM productos_finales pf
                    LEFT JOIN producto_final_subproductos pfs ON pf.id = pfs.producto_final_id
                    LEFT JOIN subproductos sp ON sp.id = pfs.subproducto_id
                    GROUP BY pf.id
                    ORDER BY pf.nombre"""
                )
                productos = cursor.fetchall() or []
                
                # ✅ CORRECCIÓN: Obtener costo_unitario de PRODUCCIÓN, NO de configuración
                for producto in productos:
                    pid = producto['id']
                    
                    cursor.execute(
                        """SELECT pfs.subproducto_id, sp.nombre, sp.costo_total_subproducto
                        FROM producto_final_subproductos pfs
                        JOIN subproductos sp ON sp.id = pfs.subproducto_id
                        WHERE pfs.producto_final_id = %s""",
                        (pid,)
                    )
                    
                    costo_total = Decimal(0)
                    detalles = []
                    relaciones = cursor.fetchall() or []
                    
                    self.logger.debug(
                        f"\n📊 Calculando costo para producto: {producto['nombre']}"
                    )
                    
                    for rel in relaciones:
                        subproducto_id = rel['subproducto_id']
                        nombre_sub = rel['nombre']
                        costo_total_sub = Decimal(str(rel['costo_total_subproducto']))
                        
                        # ✅ OBTENER COSTO UNITARIO DE LA ÚLTIMA PRODUCCIÓN
                        cursor.execute(
                            """SELECT costo_unitario FROM subproducto_producciones 
                            WHERE subproducto_id = %s 
                            ORDER BY created_at DESC 
                            LIMIT 1""",
                            (subproducto_id,)
                        )
                        
                        prod_result = cursor.fetchone()
                        
                        if prod_result:
                            # ✅ USAR costo_unitario de producción
                            costo_unitario_real = Decimal(str(prod_result['costo_unitario']))
                            costo_total += costo_unitario_real
                            
                            detalles.append({
                                'nombre': nombre_sub,
                                'costo_total_sub': float(costo_total_sub),
                                'costo_unitario_real': float(costo_unitario_real)
                            })
                            
                            self.logger.debug(
                                f"  {nombre_sub}:\n"
                                f"    Costo Total Subproducto: ${float(costo_total_sub):.2f}\n"
                                f"    Costo/Unidad (de producción): ${float(costo_unitario_real):.2f}"
                            )
                        else:
                            # Si no hay producción, no sumar nada
                            self.logger.warning(
                                f"  ⚠️ {nombre_sub}: No tiene producciones registradas"
                            )
                    
                    self.logger.debug(
                        f"  ✅ COSTO FINAL PRODUCTO: ${float(costo_total):.2f}\n"
                    )
                    
                    producto['costo_unitario_total'] = float(costo_total)
                    
                    precio_venta = float(producto.get('precio_venta') or 0)
                    if costo_total > 0:
                        margen = ((precio_venta - float(costo_total)) / float(costo_total) * 100)
                        producto['margen_ganancia'] = round(margen, 2)
                    else:
                        producto['margen_ganancia'] = 0
                
                return productos
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
        
        finally:
            close_connection(conn)
    
    def set_precio_venta(self, producto_id: int, precio: float) -> bool:
        """Actualiza precio de venta"""
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE productos_finales SET precio_venta = %s WHERE id = %s",
                    (round(float(precio), 2), producto_id)
                )
            
            conn.commit()
            logger.info(f"✅ Precio actualizado: ${precio:.2f}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error actualizando precio: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)
    
    def eliminar_producto_final(self, producto_id: int) -> bool:
        """Elimina un producto final"""
        conn = get_connection()
        if not conn:
            raise Exception("❌ No hay conexión a BD")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM producto_final_subproductos WHERE producto_final_id = %s",
                    (producto_id,)
                )
                cursor.execute(
                    "DELETE FROM productos_finales WHERE id = %s",
                    (producto_id,)
                )
            
            conn.commit()
            logger.info(f"✅ Producto {producto_id} eliminado")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error eliminando producto: {e}")
            conn.rollback()
            raise
        
        finally:
            close_connection(conn)