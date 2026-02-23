"""
Core.Common.data_cache - Sistema de caché con expiración automática
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable
import threading
from Core.Common.logger import setup_logger

logger = setup_logger()


class DataCache:
    """
    Cache thread-safe con TTL automático.
    
    Características:
    - Thread-safe (usa locks)
    - Expiración automática de entradas
    - Invalidación por patrón
    - Estadísticas de uso
    """
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Inicializa cache.
        
        Args:
            ttl_seconds: Tiempo de vida por defecto (segundos)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Almacena valor en cache.
        
        Args:
            key: Clave
            value: Valor
            ttl: TTL override (opcional)
        """
        with self.lock:
            expires = datetime.now() + timedelta(seconds=ttl or self.ttl)
            self.cache[key] = {"value": value, "expires": expires}
            self.stats["sets"] += 1
            logger.debug(f"Cache SET: {key} (TTL: {ttl or self.ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor del cache si existe y no expiró.
        
        Args:
            key: Clave
            
        Returns:
            Valor o None
        """
        with self.lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            # Verificar expiración
            if datetime.now() > entry["expires"]:
                del self.cache[key]
                self.stats["misses"] += 1
                logger.debug(f"Cache EXPIRED: {key}")
                return None
            
            self.stats["hits"] += 1
            logger.debug(f"Cache HIT: {key}")
            return entry["value"]
    
    def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Obtiene del cache o ejecuta función de fetch.
        
        Args:
            key: Clave
            fetch_func: Función para obtener valor
            ttl: TTL override (opcional)
            *args, **kwargs: Argumentos para fetch_func
            
        Returns:
            Valor desde cache o fetch_func
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        
        logger.debug(f"Cache FETCH: {key}")
        value = fetch_func(*args, **kwargs)
        self.set(key, value, ttl)
        return value
    
    def invalidate(self, key: str):
        """
        Invalida entrada específica.
        
        Args:
            key: Clave a invalidar
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats["deletes"] += 1
                logger.debug(f"Cache INVALIDATE: {key}")
    
    def invalidate_pattern(self, pattern: str):
        """
        Invalida múltiples entradas que coincidan con patrón.
        
        Args:
            pattern: Patrón de búsqueda
        """
        with self.lock:
            keys = [k for k in self.cache.keys() if pattern in k]
            for k in keys:
                del self.cache[k]
                self.stats["deletes"] += 1
            
            if keys:
                logger.debug(f"Cache INVALIDATE PATTERN: {pattern} ({len(keys)} entries)")
    
    def clear(self):
        """Limpia todo el cache"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.stats["deletes"] += count
            logger.info(f"Cache CLEAR: {count} entries removidas")
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estadísticas de uso"""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                "total_entries": len(self.cache),
                "total_requests": total_requests,
                "hit_rate": f"{hit_rate:.1f}%"
            }
    
    def size(self) -> int:
        """Retorna cantidad de entradas"""
        with self.lock:
            return len(self.cache)


# Instancia global de caché
app_cache = DataCache(ttl_seconds=600)