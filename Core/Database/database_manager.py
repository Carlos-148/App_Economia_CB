"""
Core.Common.database_manager - Gestor de base de datos local
Manejo de BD local con MariaDB/MySQL
"""

import os
import subprocess
import pymysql
from typing import Dict, Optional, Tuple
from Core.Common.logger import setup_logger
from Core.Common.config import load_config, save_config

logger = setup_logger()


class LocalDatabaseManager:
    """
    Gestor de base de datos local con MariaDB.
    
    Características:
    - Crear BD locales en carpeta /database
    - Resetear datos sin eliminar estructura
    - Backup automático antes de operaciones
    - Validar integridad
    """
    
    # Carpeta donde se guarda la BD
    DB_FOLDER = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "database"
    )
    
    # Puerto por defecto de MariaDB local
    DEFAULT_PORT = 3306
    
    # Usuario local por defecto
    DEFAULT_USER = "pp"
    DEFAULT_PASSWORD = "1234"
    
    def __init__(self):
        """Inicializa el gestor"""
        self.logger = setup_logger()
        self.config = load_config()
        self._ensure_db_folder()
    
    def _ensure_db_folder(self):
        """Asegura que existe la carpeta de BD"""
        try:
            os.makedirs(self.DB_FOLDER, exist_ok=True)
            self.logger.info(f"📁 Carpeta BD: {self.DB_FOLDER}")
        except Exception as e:
            self.logger.error(f"Error creando carpeta BD: {e}")
    
    def get_db_config(self) -> Dict:
        """
        Obtiene configuración actual de BD.
        Si no existe, retorna la local por defecto.
        """
        db_config = self.config.get("db", {})
        
        # Si no está configurada o está vacía, usar defaults locales
        if not db_config or db_config.get("host") == "localhost":
            return {
                "host": "localhost",
                "port": self.DEFAULT_PORT,
                "user": self.DEFAULT_USER,
                "password": self.DEFAULT_PASSWORD,
                "database": "economia_oficial",
                "charset": "utf8mb4"
            }
        
        return db_config
    
    def set_local_database(self, db_name: str = "economia_oficial") -> bool:
        """
        Configura para usar BD local en localhost.
        
        Args:
            db_name: Nombre de la BD
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            config = load_config()
            config["db"] = {
                "host": "localhost",
                "port": self.DEFAULT_PORT,
                "user": self.DEFAULT_USER,
                "password": self.DEFAULT_PASSWORD,
                "database": db_name,
                "charset": "utf8mb4"
            }
            
            save_config(config)
            self.config = config
            
            self.logger.info(f"✅ BD local configurada: {db_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error configurando BD local: {e}")
            return False
    
    def create_new_database(self, db_name: str = "economia_oficial") -> bool:
        """
        Crea una nueva BD completamente limpia.
        
        Args:
            db_name: Nombre de la BD a crear
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            self.logger.info(f"🔄 Creando nueva BD: {db_name}")
            
            # Conectar sin especificar BD (para crear BD)
            conn = pymysql.connect(
                host="localhost",
                user=self.DEFAULT_USER,
                password=self.DEFAULT_PASSWORD,
                charset="utf8mb4"
            )
            
            with conn.cursor() as cursor:
                # Eliminar BD si existe
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                self.logger.info(f"✓ BD anterior eliminada (si existía)")
                
                # Crear BD nueva
                cursor.execute(
                    f"CREATE DATABASE {db_name} "
                    f"CHARACTER SET utf8mb4 "
                    f"COLLATE utf8mb4_unicode_ci"
                )
                self.logger.info(f"✓ BD nueva creada: {db_name}")
            
            conn.commit()
            conn.close()
            
            # Configurar para usar esta BD
            self.set_local_database(db_name)
            
            self.logger.info(f"✅ Nueva BD lista para inicializar")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Error creando BD: {e}")
            return False
    
    def reset_database_data(self, db_name: Optional[str] = None) -> bool:
        """
        Resetea todos los datos de la BD (mantiene estructura).
        
        Args:
            db_name: Nombre de la BD (si es None, usa la actual)
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            if db_name is None:
                db_name = self.config.get("db", {}).get("database", "economia_oficial")
            
            self.logger.info(f"🔄 Reseteando datos de: {db_name}")
            
            # Crear backup antes
            self._create_backup(db_name)
            
            conn = pymysql.connect(
                host="localhost",
                user=self.DEFAULT_USER,
                password=self.DEFAULT_PASSWORD,
                database=db_name,
                charset="utf8mb4"
            )
            
            with conn.cursor() as cursor:
                # Obtener todas las tablas
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                # Desactivar foreign key checks temporalmente
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                
                # Truncate (eliminar datos pero mantener estructura)
                for table in tables:
                    table_name = table[0] if isinstance(table, tuple) else table.get('Tables_in_' + db_name)
                    cursor.execute(f"TRUNCATE TABLE {table_name}")
                    self.logger.info(f"  ✓ {table_name} reseteada")
                
                # Reactivar foreign key checks
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"✅ BD reseteada correctamente")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Error reseteando BD: {e}")
            return False
    
    def _create_backup(self, db_name: str) -> Optional[str]:
        """
        Crea backup de la BD antes de operaciones destructivas.
        
        Args:
            db_name: Nombre de la BD
            
        Returns:
            str: Ruta del backup o None si falló
        """
        try:
            from datetime import datetime
            
            # Crear carpeta de backups
            backup_folder = os.path.join(self.DB_FOLDER, "backups")
            os.makedirs(backup_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_folder, f"{db_name}_backup_{timestamp}.sql")
            
            # Usar mysqldump si está disponible
            try:
                cmd = [
                    "mysqldump",
                    f"-u{self.DEFAULT_USER}",
                    f"-p{self.DEFAULT_PASSWORD}",
                    "-h", "localhost",
                    "--single-transaction",
                    "--quick",
                    "--lock-tables=false",
                    db_name
                ]
                
                with open(backup_file, "w", encoding="utf-8") as f:
                    subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
                
                self.logger.info(f"✓ Backup creado: {backup_file}")
                return backup_file
            
            except (FileNotFoundError, subprocess.CalledProcessError):
                self.logger.warning("mysqldump no disponible, usando backup Python")
                return self._create_backup_python(db_name, backup_file)
        
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return None
    
    def _create_backup_python(self, db_name: str, backup_file: str) -> Optional[str]:
        """
        Crea backup usando Python (sin mysqldump).
        
        Args:
            db_name: Nombre de la BD
            backup_file: Ruta del archivo backup
            
        Returns:
            str: Ruta del backup
        """
        try:
            conn = pymysql.connect(
                host="localhost",
                user=self.DEFAULT_USER,
                password=self.DEFAULT_PASSWORD,
                database=db_name,
                charset="utf8mb4"
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(f"-- Backup de {db_name}\n")
                    f.write(f"-- {datetime.now().isoformat()}\n\n")
                    
                    for table in tables:
                        table_name = table[0] if isinstance(table, tuple) else table.get('Tables_in_' + db_name)
                        
                        # Get CREATE TABLE
                        cursor.execute(f"SHOW CREATE TABLE {table_name}")
                        create_result = cursor.fetchone()
                        create_table = create_result[1] if isinstance(create_result, tuple) else create_result.get('Create Table')
                        f.write(f"{create_table};\n\n")
            
            conn.close()
            
            self.logger.info(f"✓ Backup Python creado: {backup_file}")
            return backup_file
        
        except Exception as e:
            self.logger.error(f"Error en backup Python: {e}")
            return None
    
    def verify_connection(self) -> Tuple[bool, str]:
        """
        Verifica que la conexión a BD sea válida.
        
        Returns:
            Tuple[bool, str]: (exitoso, mensaje)
        """
        try:
            db_config = self.get_db_config()
            
            conn = pymysql.connect(
                host=db_config.get("host"),
                port=db_config.get("port", 3306),
                user=db_config.get("user"),
                password=db_config.get("password"),
                database=db_config.get("database"),
                charset=db_config.get("charset", "utf8mb4")
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            conn.close()
            
            return True, "✅ Conexión exitosa"
        
        except pymysql.Error as e:
            msg = f"❌ Error de BD: {str(e)[:100]}"
            self.logger.error(msg)
            return False, msg
        
        except Exception as e:
            msg = f"❌ Error: {str(e)[:100]}"
            self.logger.error(msg)
            return False, msg
    
    def get_database_stats(self, db_name: Optional[str] = None) -> Dict:
        """
        Obtiene estadísticas de la BD.
        
        Args:
            db_name: Nombre de la BD
            
        Returns:
            Dict: Estadísticas
        """
        try:
            if db_name is None:
                db_name = self.config.get("db", {}).get("database", "economia_oficial")
            
            conn = pymysql.connect(
                host="localhost",
                user=self.DEFAULT_USER,
                password=self.DEFAULT_PASSWORD,
                database=db_name,
                charset="utf8mb4"
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                table_count = len(cursor.fetchall())
                
                cursor.execute("""
                    SELECT 
                        SUM(TABLE_ROWS) as row_count
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = %s
                """, (db_name,))
                
                result = cursor.fetchone()
                row_count = result.get('row_count', 0) if result else 0
                
                cursor.execute(f"SELECT VERSION()")
                version = cursor.fetchone()[0] if cursor.fetchone() else "N/A"
            
            conn.close()
            
            return {
                "database": db_name,
                "tables": table_count,
                "rows": row_count or 0,
                "status": "✅ Activa"
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {
                "database": db_name,
                "tables": 0,
                "rows": 0,
                "status": "❌ Error"
            }
    
    def list_backups(self, db_name: Optional[str] = None) -> list:
        """
        Lista los backups disponibles.
        
        Args:
            db_name: Nombre de la BD (None = todos)
            
        Returns:
            list: Lista de archivos de backup
        """
        try:
            backup_folder = os.path.join(self.DB_FOLDER, "backups")
            
            if not os.path.exists(backup_folder):
                return []
            
            backups = []
            for filename in sorted(os.listdir(backup_folder), reverse=True):
                if filename.endswith(".sql"):
                    if db_name is None or db_name in filename:
                        filepath = os.path.join(backup_folder, filename)
                        size = os.path.getsize(filepath)
                        backups.append({
                            "filename": filename,
                            "path": filepath,
                            "size": size,
                            "size_mb": round(size / (1024 * 1024), 2)
                        })
            
            return backups
        
        except Exception as e:
            logger.error(f"Error listando backups: {e}")
            return []