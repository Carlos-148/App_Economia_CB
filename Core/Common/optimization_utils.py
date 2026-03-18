"""
Core.Common.optimization_utils - Utilidades de optimización y monitoreo
"""

import time
import functools
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
import threading

from Core.Common.logger import setup_logger

logger = setup_logger()


# ============================================
# PERFORMANCE MONITORING
# ============================================

class PerformanceMonitor:
    """Monitor de rendimiento para funciones"""
    
    def __init__(self, threshold_seconds: float = 1.0):
        """
        Args:
            threshold_seconds: Umbral de alerta (segundos)
        """
        self.threshold = threshold_seconds
        self.metrics = {}
    
    def performance_monitor(self, func: Callable) -> Callable:
        """
        Decorator para monitorear rendimiento de funciones.
        
        Args:
            func: Función a monitorear
            
        Returns:
            Función envuelta
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                
                # Registrar métrica
                if func_name not in self.metrics:
                    self.metrics[func_name] = {
                        "calls": 0,
                        "total_time": 0,
                        "max_time": 0,
                        "min_time": float('inf'),
                    }
                
                metric = self.metrics[func_name]
                metric["calls"] += 1
                metric["total_time"] += elapsed
                metric["max_time"] = max(metric["max_time"], elapsed)
                metric["min_time"] = min(metric["min_time"], elapsed)
                
                # Alerta si excede umbral
                if elapsed > self.threshold:
                    logger.warning(
                        f"⏱️ {func_name} tomó {elapsed:.3f}s "
                        f"(umbral: {self.threshold}s)"
                    )
                else:
                    logger.debug(f"✓ {func_name}: {elapsed:.3f}s")
        
        return wrapper
    
    def get_metrics(self, func_name: Optional[str] = None) -> dict:
        """Obtiene métricas de rendimiento"""
        if func_name:
            return self.metrics.get(func_name, {})
        return self.metrics
    
    def print_report(self):
        """Imprime reporte de rendimiento"""
        logger.info("=" * 60)
        logger.info("📊 REPORTE DE RENDIMIENTO")
        logger.info("=" * 60)
        
        for func_name, metric in self.metrics.items():
            avg_time = metric["total_time"] / metric["calls"] if metric["calls"] > 0 else 0
            logger.info(
                f"\n{func_name}:"
                f"\n  Llamadas: {metric['calls']}"
                f"\n  Promedio: {avg_time:.3f}s"
                f"\n  Máximo: {metric['max_time']:.3f}s"
                f"\n  Mínimo: {metric['min_time']:.3f}s"
                f"\n  Total: {metric['total_time']:.3f}s"
            )


# Instancia global
_perf_monitor = PerformanceMonitor()


def monitor_performance(func: Callable) -> Callable:
    """
    Decorator global para monitorear rendimiento.
    
    Usage:
        @monitor_performance
        def mi_funcion():
            pass
    """
    return _perf_monitor.performance_monitor(func)


# ============================================
# SMART CACHING
# ============================================

class SmartCache:
    """Cache inteligente con TTL y estadísticas"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Args:
            max_size: Tamaño máximo del cache
            default_ttl: TTL por defecto (segundos)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.lock = threading.RLock()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache"""
        with self.lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            # Verificar expiración
            if datetime.now() > entry["expires"]:
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Almacena valor en cache"""
        with self.lock:
            # Evictar si necesario
            if len(self.cache) >= self.max_size:
                # LRU eviction
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]["accessed"]
                )
                del self.cache[oldest_key]
                self.stats["evictions"] += 1
            
            expires = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
            self.cache[key] = {
                "value": value,
                "expires": expires,
                "accessed": datetime.now()
            }
    
    def clear(self):
        """Limpia el cache"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas"""
        with self.lock:
            total = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                self.stats["hits"] / total * 100 if total > 0 else 0
            )
            return {
                **self.stats,
                "hit_rate": hit_rate,
                "size": len(self.cache)
            }


# ============================================
# RATE LIMITING
# ============================================

class RateLimiter:
    """Limitador de tasa para throttling"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        """
        Args:
            max_calls: Máximo de llamadas
            time_window: Ventana de tiempo (segundos)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def is_allowed(self) -> bool:
        """Verifica si llamada está permitida"""
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.time_window)
            
            # Limpiar llamadas antiguas
            self.calls = [c for c in self.calls if c > cutoff]
            
            # Verificar límite
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            return False
    
    def rate_limit(self, func: Callable) -> Callable:
        """Decorator para rate limiting"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.is_allowed():
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                return None
            
            return func(*args, **kwargs)
        
        return wrapper


# ============================================
# MEMORY PROFILING
# ============================================

import psutil
import os


class MemoryProfiler:
    """Perfilador de memoria"""
    
    @staticmethod
    def get_memory_usage() -> dict:
        """Obtiene uso actual de memoria"""
        process = psutil.Process(os.getpid())
        info = process.memory_info()
        
        return {
            "rss_mb": info.rss / 1024 / 1024,  # Resident set size
            "vms_mb": info.vms / 1024 / 1024,  # Virtual memory size
            "percent": process.memory_percent(),
        }
    
    @staticmethod
    def memory_profile(func: Callable) -> Callable:
        """Decorator para perfilar memoria"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            before = MemoryProfiler.get_memory_usage()
            
            result = func(*args, **kwargs)
            
            after = MemoryProfiler.get_memory_usage()
            
            delta_rss = after["rss_mb"] - before["rss_mb"]
            logger.debug(
                f"Memory {func.__name__}: "
                f"{delta_rss:+.2f}MB "
                f"(Total: {after['rss_mb']:.2f}MB)"
            )
            
            return result
        
        return wrapper


# ============================================
# BULK OPERATIONS
# ============================================

class BulkOperation:
    """Ejecutor de operaciones en lote"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.batch = []
        self.lock = threading.Lock()
    
    def add(self, item: Any) -> bool:
        """
        Añade item al lote.
        
        Returns:
            True si lote está listo
        """
        with self.lock:
            self.batch.append(item)
            return len(self.batch) >= self.batch_size
    
    def get_batch(self) -> list:
        """Obtiene y limpia el lote actual"""
        with self.lock:
            batch = self.batch.copy()
            self.batch.clear()
            return batch
    
    def size(self) -> int:
        """Retorna tamaño actual del lote"""
        with self.lock:
            return len(self.batch)


# ============================================
# EXPORTS
# ============================================

__all__ = [
    'PerformanceMonitor',
    'monitor_performance',
    'SmartCache',
    'RateLimiter',
    'MemoryProfiler',
    'BulkOperation',
]