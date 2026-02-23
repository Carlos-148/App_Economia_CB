"""
Core.Common.database - Gestión de conexiones y pool de base de datos
"""

import pymysql
from datetime import datetime
from typing import Optional, List, Dict

from Core.Common.logger import setup_logger
from Core.Common.config import get_db_config

logger = setup_logger()


# ============================================
# CLASE: DATABASE MANAGER (Pool de conexiones)
# ============================================

class DatabaseManager:
    """Gestor centralizado de conexiones a base de datos"""
    
    _instance = None
    _connection = None
    _tables_created = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize_database(cls) -> bool:
        """
        Inicializa la BD con todas las tablas.
        
        Returns:
            bool: True si fue exitoso
        """
        try:
            conn = get_connection()
            
            if not conn:
                logger.error("❌ No hay conexión a BD")
                return False
            
            # Importar aquí para evitar circular import
            from Core.Database.manager import DatabaseMigrationManager
            
            migration_manager = DatabaseMigrationManager()
            success = migration_manager.migrate_to_latest(conn)
            
            if success:
                logger.info("✅ Base de datos inicializada correctamente")
                return True
            else:
                logger.error("❌ Error en migraciones")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error inicializando BD: {e}")
            return False
    
    @classmethod
    def get_connection(cls) -> Optional[pymysql.Connection]:
        """
        Obtiene conexión a la base de datos.
        
        Returns:
            Connection: Conexión a BD o None
        """
        try:
            cfg = get_db_config()
            connection = pymysql.connect(
                host=cfg.get("host", "localhost"),
                user=cfg.get("user", "pp"),
                database=cfg.get("database", "economia_oficial"),
                password=cfg.get("password", "1234"),
                charset=cfg.get("charset", "utf8mb4"),
                cursorclass=pymysql.cursors.DictCursor,
            )
            
            logger.debug("✓ Conexión a BD establecida")
            return connection
        
        except pymysql.Error as e:
            logger.error(f"❌ Error obteniendo conexión a BD: {e}")
            return None
    
    @staticmethod
    def get_stats() -> Dict:
        """
        Obtiene estadísticas del pool.
        
        Returns:
            Dict: Estadísticas
        """
        return {
            'active_connections': 1,
            'pool_size': 5,
            'max_overflow': 10
        }


# ============================================
# FUNCIONES GLOBALES
# ============================================

def get_connection() -> Optional[pymysql.Connection]:
    """
    Obtiene una conexión nueva a la base de datos.
    
    Returns:
        Connection: Conexión a BD o None
    """
    return DatabaseManager.get_connection()


def close_connection(connection: Optional[pymysql.Connection]):
    """
    Cierra una conexión.
    
    Args:
        connection: Conexión a cerrar
    """
    if connection:
        try:
            connection.close()
            logger.debug("✓ Conexión cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")


# ============================================
# FUNCIONES: USUARIOS
# ============================================

def create_user(username: str, password: str) -> Optional[Dict]:
    """
    Crea un nuevo usuario con contraseña hasheada.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        
    Returns:
        Dict: Usuario creado o None
    """
    from hashlib import sha256
    
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE nombre = %s", (username,))
            if cursor.fetchone():
                logger.warning(f"⚠️ Usuario {username} ya existe")
                return None
            
            password_hash = sha256(password.encode()).hexdigest()
            
            sql = "INSERT INTO users (nombre, password_hash, capital_inicial) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, password_hash, 1000.0))
            conn.commit()
            
            cursor.execute("SELECT id, nombre FROM users WHERE nombre = %s", (username,))
            user = cursor.fetchone()
            logger.info(f"✅ Usuario creado: {username}")
            return user
    
    except Exception as e:
        logger.error(f"❌ Error creando usuario: {e}")
        return None
    
    finally:
        close_connection(conn)


def verify_user(username: str, password: str) -> Optional[Dict]:
    """
    Verifica credenciales del usuario.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        
    Returns:
        Dict: Usuario si credenciales son válidas, None si no
    """
    from hashlib import sha256
    
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            password_hash = sha256(password.encode()).hexdigest()
            cursor.execute(
                "SELECT id, nombre FROM users WHERE nombre = %s AND password_hash = %s",
                (username, password_hash)
            )
            user = cursor.fetchone()
            
            if user:
                logger.info(f"✅ Usuario autenticado: {username}")
            else:
                logger.warning(f"⚠️ Intento fallido de login: {username}")
            
            return user
    
    except Exception as e:
        logger.error(f"❌ Error verificando usuario: {e}")
        return None
    
    finally:
        close_connection(conn)


def get_user_by_name(username: str) -> Optional[Dict]:
    """
    Obtiene usuario por nombre.
    
    Args:
        username: Nombre de usuario
        
    Returns:
        Dict: Datos del usuario o None
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre, capital_inicial FROM users WHERE nombre = %s",
                (username,)
            )
            return cursor.fetchone()
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuario: {e}")
        return None
    
    finally:
        close_connection(conn)


# ============================================
# FUNCIONES: COMPRAS
# ============================================

def insert_compra(producto: str, cantidad: str, unidad: str, precio_compra: float,
                 precio_total: float, proveedor: str, tipo: str) -> bool:
    """
    Inserta una compra en la base de datos.
    
    Args:
        producto: Nombre del producto
        cantidad: Cantidad
        unidad: Unidad de medida
        precio_compra: Precio por unidad
        precio_total: Precio total
        proveedor: Proveedor
        tipo: Tipo de compra
        
    Returns:
        bool: True si fue exitoso
    """
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO compras 
                     (producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo))
            conn.commit()
            logger.info(f"✅ Compra insertada: {producto}")
            return True
    
    except Exception as e:
        logger.error(f"❌ Error insertando compra: {e}")
        conn.rollback()
        return False
    
    finally:
        close_connection(conn)


def get_compras(limit: int = 100) -> List[Dict]:
    """
    Obtiene todas las compras.
    
    Args:
        limit: Límite de registros
        
    Returns:
        List: Compras
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
        logger.error(f"❌ Error obteniendo compras: {e}")
        return []
    
    finally:
        close_connection(conn)


# ============================================
# FUNCIONES: GASTOS
# ============================================

def insert_gasto_money(descripcion: str, monto: float, comentarios: str = None) -> bool:
    """Inserta un gasto monetario"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO gastos_money (descripcion, monto, comentarios) VALUES (%s, %s, %s)"
            cursor.execute(sql, (descripcion, round(float(monto), 2), comentarios))
            conn.commit()
            logger.info(f"✅ Gasto registrado: {descripcion} - ${monto:.2f}")
            return True
    
    except Exception as e:
        logger.error(f"❌ Error insertando gasto: {e}")
        conn.rollback()
        return False
    
    finally:
        close_connection(conn)


def insert_gasto_producto(producto: str, cantidad: float, unidad: str,
                         precio_total: float, comentarios: str = None) -> bool:
    """Inserta un gasto de producto"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO gastos_productos 
                     (producto, cantidad, unidad, precio_total, comentarios) 
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (producto, float(cantidad), unidad, round(float(precio_total), 2), comentarios))
            conn.commit()
            logger.info(f"✅ Gasto producto registrado: {producto}")
            return True
    
    except Exception as e:
        logger.error(f"❌ Error insertando gasto: {e}")
        conn.rollback()
        return False
    
    finally:
        close_connection(conn)


def get_gastos_money(limit: int = 100) -> List[Dict]:
    """Obtiene todos los gastos de dinero"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM gastos_money ORDER BY fecha DESC LIMIT %s""",
                (limit,)
            )
            return cursor.fetchall() or []
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo gastos: {e}")
        return []
    
    finally:
        close_connection(conn)


def get_gastos_productos(limit: int = 100) -> List[Dict]:
    """Obtiene todos los gastos de productos"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM gastos_productos ORDER BY fecha DESC LIMIT %s""",
                (limit,)
            )
            return cursor.fetchall() or []
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo gastos: {e}")
        return []
    
    finally:
        close_connection(conn)


# ============================================
# FUNCIONES: EXPORTACIÓN
# ============================================

def _ensure_folder(path: str) -> str:
    """Asegura que la carpeta existe"""
    import os
    os.makedirs(path, exist_ok=True)
    return path


def export_weekly_summary(export_base_folder: str = None) -> str:
    """
    Exporta resúmenes de ventas, compras y gastos a CSV.
    
    Args:
        export_base_folder: Carpeta base para exportar
        
    Returns:
        str: Ruta de la carpeta exportada
    """
    import csv
    from Core.Common.config import load_config
    
    cfg = load_config()
    base = export_base_folder or cfg.get("exports", {}).get("base_folder", "exports")
    ts = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    folder = os.path.join(base, f"summary_{ts}")
    _ensure_folder(folder)
    
    conn = get_connection()
    if not conn:
        raise Exception("No hay conexión a BD")
    
    try:
        with conn.cursor() as cursor:
            # Exportar Compras
            cursor.execute("SELECT * FROM compras ORDER BY fecha DESC")
            compras = cursor.fetchall() or []
            
            with open(os.path.join(folder, "compras.csv"), "w", newline="", encoding="utf-8") as f:
                if compras:
                    writer = csv.DictWriter(f, fieldnames=compras[0].keys())
                    writer.writeheader()
                    writer.writerows(compras)
            
            # Exportar Gastos
            cursor.execute("SELECT * FROM gastos_money ORDER BY fecha DESC")
            gastos = cursor.fetchall() or []
            
            with open(os.path.join(folder, "gastos.csv"), "w", newline="", encoding="utf-8") as f:
                if gastos:
                    writer = csv.DictWriter(f, fieldnames=gastos[0].keys())
                    writer.writeheader()
                    writer.writerows(gastos)
        
        logger.info(f"✅ Exportación completada: {folder}")
        return folder
    
    except Exception as e:
        logger.error(f"❌ Error exportando: {e}")
        raise
    
    finally:
        close_connection(conn)


def archive_and_reset_weekly(backup_base_folder: str = None) -> str:
    """
    Archiva datos y limpia tablas de transacciones.
    
    Args:
        backup_base_folder: Carpeta para backup
        
    Returns:
        str: Ruta de backup
    """
    from Core.Common.config import load_config
    
    base = backup_base_folder or load_config().get("exports", {}).get("base_folder", "exports")
    folder = export_weekly_summary(base)
    
    conn = get_connection()
    if not conn:
        raise Exception("No hay conexión a BD")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM ventas_items")
            cursor.execute("DELETE FROM ventas_cabecera")
            cursor.execute("DELETE FROM compras")
            cursor.execute("DELETE FROM gastos_money")
            cursor.execute("DELETE FROM gastos_productos")
        
        conn.commit()
        logger.info("✅ Base de datos reiniciada correctamente")
        return folder
    
    except Exception as e:
        logger.error(f"❌ Error reiniciando BD: {e}")
        conn.rollback()
        raise
    
    finally:
        close_connection(conn)

def revisar_setup_completado() -> bool:
    """
    Verifica si el setup inicial ya fue completado.
    
    Returns:
        bool: True si hay datos iniciales, False si es primer uso
    """
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            # Verificar si hay capital en la tabla
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM efectivo_movimientos
                LIMIT 1
            """)
            
            resultado = cursor.fetchone()
            tiene_datos = resultado.get('total', 0) > 0
            
            return tiene_datos
    
    except Exception as e:
        logger.error(f"Error verificando setup: {e}")
        return False
    
    finally:
        close_connection(conn)