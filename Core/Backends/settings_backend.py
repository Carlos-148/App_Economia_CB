"""
Core.Backends.settings_backend - Backend de Configuración
Maneja todas las operaciones de settings
"""

import os
import sys
from typing import Tuple, Dict, List
from datetime import datetime

from Core.Common.database import get_connection, close_connection, DatabaseManager
from Core.Common.config import load_config, save_config
from Core.Common.logger import setup_logger

logger = setup_logger()


class SettingsBackend:
    """Backend centralizado de configuración"""
    
    def __init__(self):
        self.logger = setup_logger()
    
    # ============================================
    # BASE DE DATOS
    # ============================================
    
    def test_db_connection(self) -> Tuple[bool, str]:
        """Prueba conexión a BD"""
        try:
            conn = get_connection()
            if conn:
                close_connection(conn)
                return True, "✅ Conexión exitosa"
            else:
                return False, "❌ No se pudo conectar"
        except Exception as e:
            return False, f"❌ Error: {str(e)[:100]}"
    
    def get_db_stats(self) -> Dict:
        """Obtiene estadísticas de BD"""
        try:
            config = load_config()
            db_name = config.get('db', {}).get('database', 'economia_oficial')
            
            conn = get_connection()
            if not conn:
                return {
                    'database': db_name,
                    'tables': 0,
                    'rows': 0
                }
            
            with conn.cursor() as cursor:
                # Contar tablas
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                """)
                result1 = cursor.fetchone()
                tables = result1.get('count', 0) if result1 else 0
                
                # Contar filas (aproximado)
                cursor.execute("""
                    SELECT SUM(table_rows) as total 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                """)
                result2 = cursor.fetchone()
                rows = result2.get('total', 0) if result2 else 0
            
            close_connection(conn)
            
            return {
                'database': db_name,
                'tables': int(tables) if tables else 0,
                'rows': int(rows) if rows else 0
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo stats: {e}")
            config = load_config()
            db_name = config.get('db', {}).get('database', 'economia_oficial')
            return {
                'database': db_name,
                'tables': 0,
                'rows': 0
            }
    
    def reset_database(self) -> Tuple[bool, str]:
        """Resetea la BD (elimina datos, mantiene estructura)"""
        try:
            # Hacer backup primero
            backup_file = self._create_backup()
            
            conn = get_connection()
            if not conn:
                return False, "❌ No hay conexión"
            
            with conn.cursor() as cursor:
                # Desactivar foreign keys
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                
                # Tablas que se limpian
                tables_to_clear = [
                    'contabilidad', 'ventas_items', 'ventas_cabecera',
                    'gastos_money', 'gastos_productos', 'compras',
                    'subproducto_producciones', 'produccion_detalles',
                    'producto_final_subproductos', 'productos_finales',
                    'subproducto_ingredientes', 'subproductos',
                    'inventario', 'clientes', 'efectivo_movimientos'
                ]
                
                for table in tables_to_clear:
                    try:
                        cursor.execute(f"TRUNCATE TABLE {table}")
                    except Exception as e:
                        self.logger.warning(f"No se pudo limpiar {table}: {e}")
                
                # Reactivar foreign keys
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            
            conn.commit()
            close_connection(conn)
            
            return True, f"✅ BD reseteada (backup: {backup_file})"
        
        except Exception as e:
            self.logger.error(f"Error en reset: {e}")
            return False, f"❌ Error: {str(e)[:100]}"
    
    def create_new_database(self) -> Tuple[bool, str]:
        """Crea BD completamente nueva"""
        try:
            backup_file = self._create_backup()
            
            # Recrear
            if DatabaseManager.initialize_database():
                return True, f"✅ BD nueva creada (backup: {backup_file})"
            else:
                return False, "❌ Error creando BD"
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False, f"❌ Error: {str(e)[:100]}"
    
    def list_backups(self) -> List[Dict]:
        """Lista backups"""
        try:
            folder = self.get_db_folder()
            backups = []
            
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.startswith('backup_'):
                        path = os.path.join(folder, file)
                        size_mb = os.path.getsize(path) / (1024 * 1024)
                        backups.append({
                            'filename': file,
                            'size_mb': round(size_mb, 2)
                        })
            
            return sorted(backups, reverse=True)
        
        except Exception as e:
            self.logger.error(f"Error listando backups: {e}")
            return []
    
    def get_db_folder(self) -> str:
        """Obtiene carpeta de BD"""
        config = load_config()
        return config.get('exports', {}).get('base_folder', 'database')
    
    def _create_backup(self) -> str:
        """Crea backup de BD"""
        try:
            folder = self.get_db_folder()
            os.makedirs(folder, exist_ok=True)
            
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            filepath = os.path.join(folder, filename)
            
            self.logger.info(f"Backup creado: {filename}")
            return filename
        
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return "backup_error"
    
    # ============================================
    # USUARIO
    # ============================================
    
    def get_user_config(self) -> Dict:
        """Obtiene configuración de usuario"""
        config = load_config()
        return config.get('user', {
            'name': 'usuario',
            'capital': 0.0
        })
    
    def save_user_config(self, name: str, capital: float = 0.0) -> Tuple[bool, str]:
        """Guarda configuración de usuario"""
        try:
            config = load_config()
            config['user'] = {
                'name': name,
                'capital': float(capital),
                'current_user_id': config.get('user', {}).get('current_user_id')
            }
            
            save_config(config)
            self.logger.info(f"✅ Usuario guardado: {name}")
            return True, f"✅ Usuario '{name}' guardado"
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False, f"❌ Error: {str(e)[:100]}"
    
    # ============================================
    # TEMAS
    # ============================================
    
    def get_valid_themes(self) -> List[str]:
        """Obtiene temas válidos"""
        return [
            "solar", "darkly", "vapor", "cosmo", "flatly", "litera", "lumen",
            "minty", "pulse", "sandstone", "simplex", "sketchy", "spacelab",
            "superhero", "united", "yeti", "morph", "zephyr"
        ]
    
    def get_current_theme(self) -> str:
        """Obtiene tema actual"""
        config = load_config()
        return config.get('theme', 'solar')
    
    def save_theme(self, theme: str) -> Tuple[bool, str]:
        """Guarda tema"""
        try:
            if theme not in self.get_valid_themes():
                return False, f"❌ Tema '{theme}' no válido"
            
            config = load_config()
            config['theme'] = theme
            save_config(config)
            
            self.logger.info(f"✅ Tema guardado: {theme}")
            return True, f"✅ Tema '{theme}' guardado"
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False, f"❌ Error: {str(e)[:100]}"
    
    def get_theme_presets(self) -> List[str]:
        """Obtiene presets de temas"""
        return [
            "Profesional Azul",
            "Verde Naturaleza",
            "Oscuro Moderno",
            "Naranja Energético",
            "Rosa Moderno"
        ]
    
    def apply_preset(self, preset: str) -> Tuple[bool, str]:
        """Aplica preset"""
        try:
            if preset not in self.get_theme_presets():
                return False, f"❌ Preset no válido"
            
            self.logger.info(f"✅ Preset aplicado: {preset}")
            return True, f"✅ Preset '{preset}' aplicado"
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False, f"❌ Error: {str(e)[:100]}"
    
    # ============================================
    # EXPORTES
    # ============================================
    
    def export_summary(self) -> Tuple[bool, str]:
        """Exporta resumen"""
        try:
            from datetime import datetime
            
            folder = self.get_db_folder()
            os.makedirs(folder, exist_ok=True)
            
            filename = f"resumen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(folder, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"RESUMEN - {datetime.now()}\n")
            
            self.logger.info(f"✅ Resumen exportado: {filename}")
            return True, f"✅ Exportado: {filename}"
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False, f"❌ Error: {str(e)[:100]}"
    
    def open_exports_folder(self) -> Tuple[bool, str]:
        """Abre carpeta de exportes"""
        try:
            folder = self.get_db_folder()
            os.makedirs(folder, exist_ok=True)
            
            if os.name == "nt":
                os.startfile(folder)
            elif os.name == "posix":
                import subprocess
                subprocess.Popen(["open", folder])
            
            self.logger.info(f"Carpeta abierta: {folder}")
            return True, f"Carpeta abierta: {folder}"
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False, f"❌ Error: {str(e)[:100]}"
    
    # ============================================
    # SISTEMA
    # ============================================
    
    def get_system_stats(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        try:
            config = load_config()
            db_stats = self.get_db_stats()
            
            return {
                'app_version': config.get('version', '3.2'),
                'current_user': config.get('user', {}).get('name', 'usuario'),
                'current_theme': config.get('theme', 'solar'),
                'database': db_stats
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo stats: {e}")
            return {
                'app_version': '3.2',
                'current_user': 'usuario',
                'current_theme': 'solar',
                'database': {'database': 'N/A', 'tables': 0, 'rows': 0}
            }
    
    def reload_application(self):
        """Recarga la aplicación"""
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            self.logger.error(f"Error recargando: {e}")