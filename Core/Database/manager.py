"""
Core.Database.manager - Gestor de migraciones de base de datos
"""

from typing import Optional
import pymysql

from Core.Common.logger import setup_logger
from Core.Database.schema import DatabaseSchema

logger = setup_logger()


class DatabaseMigrationManager:
    """
    Gestor de migraciones de base de datos.
    
    Maneja la creación de tablas, versionado y actualizaciones.
    """
    
    # Versión actual del esquema
    SCHEMA_VERSION = 1
    
    # Historial de migraciones
    MIGRATIONS = {
        1: "Initial schema creation"
    }
    
    def __init__(self):
        """Inicializa el gestor de migraciones"""
        self.logger = setup_logger()
    
    def migrate_to_latest(self, conn: Optional[pymysql.Connection] = None) -> bool:
        """
        Ejecuta todas las migraciones pendientes.
        
        Args:
            conn: Conexión a BD (opcional)
            
        Returns:
            bool: True si fue exitoso
        """
        # Importar aquí para evitar circular import
        from Core.Common.database import close_connection
        
        should_close = False
        
        if conn is None:
            # Importar aquí para evitar circular import
            from Core.Common.database import get_connection
            conn = get_connection()
            should_close = True
        
        if not conn:
            logger.error("No hay conexión a BD")
            return False
        
        try:
            # Crear todas las tablas
            self._create_all_tables(conn)
            
            logger.info("✅ Base de datos migrada exitosamente")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error en migraciones: {e}")
            return False
        
        finally:
            if should_close:
                close_connection(conn)
    
    def _create_all_tables(self, conn: pymysql.Connection) -> bool:
        """
        Crea todas las tablas del esquema.
        
        Args:
            conn: Conexión a BD
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            with conn.cursor() as cursor:
                for table_name, table_sql in DatabaseSchema.get_all_tables():
                    try:
                        cursor.execute(table_sql)
                        logger.info(f"✓ Tabla '{table_name}' verificada/creada")
                    
                    except pymysql.Error as e:
                        if "already exists" in str(e):
                            logger.debug(f"Tabla '{table_name}' ya existe")
                        else:
                            logger.error(f"Error creando tabla '{table_name}': {e}")
                            raise
            
            conn.commit()
            logger.info("✅ Todas las tablas creadas correctamente")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            conn.rollback()
            return False
    
    def get_schema_version(self, conn: pymysql.Connection) -> int:
        """
        Obtiene la versión actual del esquema.
        
        Args:
            conn: Conexión a BD
            
        Returns:
            int: Número de versión
        """
        return self.SCHEMA_VERSION
    
    def list_migrations(self) -> dict:
        """
        Lista todas las migraciones disponibles.
        
        Returns:
            dict: Migraciones por versión
        """
        return self.MIGRATIONS.copy()