"""
Core.Database.schema - Definición del esquema de base de datos
CORRECCIÓN: Sintaxis SQL compatible con MariaDB
"""

from typing import List, Dict


class DatabaseSchema:
    """Define el esquema completo de la base de datos"""
    
    # ============================================
    # TABLA: USUARIOS
    # ============================================
    USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        capital_inicial DECIMAL(14,2) NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: COMPRAS
    # ============================================
    COMPRAS_TABLE = """
    CREATE TABLE IF NOT EXISTS compras (
        id INT AUTO_INCREMENT PRIMARY KEY,
        producto VARCHAR(255) NOT NULL,
        cantidad DECIMAL(15,4) NOT NULL,
        unidad VARCHAR(50) NOT NULL,
        precio_compra DECIMAL(10,2) NOT NULL,
        precio_total DECIMAL(12,2) NOT NULL,
        proveedor VARCHAR(255) NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        comentarios VARCHAR(1024),
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        INDEX idx_producto (producto),
        INDEX idx_proveedor (proveedor),
        INDEX idx_fecha (fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: INVENTARIO
    # ============================================
    INVENTARIO_TABLE = """
    CREATE TABLE IF NOT EXISTS inventario (
        id INT AUTO_INCREMENT PRIMARY KEY,
        producto VARCHAR(100) UNIQUE NOT NULL,
        cantidad_stock DECIMAL(15,4) NOT NULL DEFAULT 0,
        unidad_base VARCHAR(20) NOT NULL,
        costo_promedio_ponderado DECIMAL(10,4) NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_producto (producto),
        INDEX idx_cantidad (cantidad_stock)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: SUBPRODUCTOS
    # ============================================
    SUBPRODUCTOS_TABLE = """
    CREATE TABLE IF NOT EXISTS subproductos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE NOT NULL,
        costo_total_subproducto DECIMAL(10,2) NOT NULL,
        unidades_rendimiento INT NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: INGREDIENTES DE SUBPRODUCTOS
    # ============================================
    SUBPRODUCTO_INGREDIENTES_TABLE = """
    CREATE TABLE IF NOT EXISTS subproducto_ingredientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subproducto_id INT NOT NULL,
        producto_ingrediente VARCHAR(255) NOT NULL,
        cantidad_usada DECIMAL(10,4) NOT NULL,
        unidad_usada VARCHAR(20) NOT NULL,
        
        FOREIGN KEY (subproducto_id) REFERENCES subproductos(id) ON DELETE CASCADE,
        INDEX idx_subproducto (subproducto_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: PRODUCCIONES
    # ============================================
    SUBPRODUCTO_PRODUCCIONES_TABLE = """
    CREATE TABLE IF NOT EXISTS subproducto_producciones (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subproducto_id INT NOT NULL,
        unidades_producidas INT NOT NULL,
        tipo_unidad VARCHAR(20) NOT NULL,
        costo_total_masa DECIMAL(14,4) NOT NULL,
        costo_unitario DECIMAL(14,6) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (subproducto_id) REFERENCES subproductos(id) ON DELETE CASCADE,
        INDEX idx_subproducto (subproducto_id),
        INDEX idx_fecha (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: DETALLES DE PRODUCCIÓN
    # ============================================
    PRODUCCION_DETALLES_TABLE = """
    CREATE TABLE IF NOT EXISTS produccion_detalles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        produccion_id INT NOT NULL,
        producto_ingrediente VARCHAR(255) NOT NULL,
        cantidad_usada DECIMAL(15,4) NOT NULL,
        unidad_usada VARCHAR(20) NOT NULL,
        costo_usado DECIMAL(12,4) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (produccion_id) REFERENCES subproducto_producciones(id) ON DELETE CASCADE,
        INDEX idx_produccion (produccion_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: PRODUCTOS FINALES
    # ============================================
    PRODUCTOS_FINALES_TABLE = """
    CREATE TABLE IF NOT EXISTS productos_finales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE NOT NULL,
        unidades_producidas INT NOT NULL,
        precio_venta DECIMAL(10,2),
        costo_unitario_total DECIMAL (10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ============================================
    # TABLA: RELACIÓN PRODUCTOS-SUBPRODUCTOS
    # ============================================
    PRODUCTO_FINAL_SUBPRODUCTOS_TABLE = """
    CREATE TABLE IF NOT EXISTS producto_final_subproductos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        producto_final_id INT NOT NULL,
        subproducto_id INT NOT NULL,
        unidades_rinde INT NOT NULL,
        
        FOREIGN KEY (producto_final_id) REFERENCES productos_finales(id) ON DELETE CASCADE,
        FOREIGN KEY (subproducto_id) REFERENCES subproductos(id) ON DELETE CASCADE,
        UNIQUE KEY unique_producto_sub (producto_final_id, subproducto_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: CLIENTES
    # ============================================
    CLIENTES_TABLE = """
    CREATE TABLE IF NOT EXISTS clientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE NOT NULL,
        active TINYINT(1) NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_nombre (nombre),
        INDEX idx_active (active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: VENTAS (CABECERA)
    # ============================================
    VENTAS_CABECERA_TABLE = """
    CREATE TABLE IF NOT EXISTS ventas_cabecera (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id INT NOT NULL,
        total_venta DECIMAL(12,2) NOT NULL DEFAULT 0,
        fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        INDEX idx_cliente (cliente_id),
        INDEX idx_fecha (fecha_venta)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: VENTAS (ITEMS)
    # ============================================
    VENTAS_ITEMS_TABLE = """
    CREATE TABLE IF NOT EXISTS ventas_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        venta_id INT NOT NULL,
        producto_final_id INT NOT NULL,
        cantidad_vendida INT NOT NULL,
        precio_unitario_venta DECIMAL(10,2) NOT NULL,
        subtotal DECIMAL(12,2) NOT NULL,
        
        FOREIGN KEY (venta_id) REFERENCES ventas_cabecera(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_final_id) REFERENCES productos_finales(id),
        INDEX idx_venta (venta_id),
        INDEX idx_producto (producto_final_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: GASTOS (DINERO)
    # ============================================
    GASTOS_MONEY_TABLE = """
    CREATE TABLE IF NOT EXISTS gastos_money (
        id INT AUTO_INCREMENT PRIMARY KEY,
        descripcion VARCHAR(512) NOT NULL,
        monto DECIMAL(12,2) NOT NULL,
        comentarios VARCHAR(1024),
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        INDEX idx_descripcion (descripcion(100)),
        INDEX idx_fecha (fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    # ============================================
    # TABLA: GASTOS (PRODUCTOS)
    # ============================================
    GASTOS_PRODUCTOS_TABLE = """
    CREATE TABLE IF NOT EXISTS gastos_productos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        producto VARCHAR(255) NOT NULL,
        cantidad DECIMAL(15,4) NOT NULL,
        unidad VARCHAR(50) NOT NULL,
        precio_total DECIMAL(12,2) NOT NULL,
        comentarios VARCHAR(1024),
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        INDEX idx_producto (producto),
        INDEX idx_fecha (fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    
    # ============================================
    # TABLA: CONTABILIDAD (Nueva)
    # ============================================
    CONTABILIDAD_TABLE = """
    CREATE TABLE IF NOT EXISTS contabilidad (
        id INT AUTO_INCREMENT PRIMARY KEY,
        venta_id INT NOT NULL,
        producto_final_id INT NOT NULL,
        cantidad_vendida INT NOT NULL,
        precio_unitario_costo DECIMAL(10,4) NOT NULL,
        precio_unitario_venta DECIMAL(10,2) NOT NULL,
        costo_total DECIMAL(12,4) NOT NULL,
        ingreso_total DECIMAL(12,2) NOT NULL,
        ganancia_neta DECIMAL(12,4) NOT NULL,
        margen_ganancia DECIMAL(5,2) NOT NULL,
        tipo_producto VARCHAR(50) NOT NULL,
        fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (venta_id) REFERENCES ventas_cabecera(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_final_id) REFERENCES productos_finales(id),
        INDEX idx_venta (venta_id),
        INDEX idx_producto (producto_final_id),
        INDEX idx_fecha (fecha_venta),
        INDEX idx_tipo (tipo_producto)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    # ============================================
    # TABLA: MOVIMIENTOS DE EFECTIVO
    # ============================================
    EFECTIVO_MOVIMIENTOS_TABLE = """
    CREATE TABLE IF NOT EXISTS efectivo_movimientos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tipo VARCHAR(100) NOT NULL,
        monto DECIMAL(12,2) NOT NULL,
        saldo DECIMAL(12,2) NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        INDEX idx_tipo (tipo),
        INDEX idx_fecha (fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

# En DatabaseSchema agregar:

    EFECTIVO_CONTADOR_TABLE = """
    CREATE TABLE IF NOT EXISTS efectivo_contador (
        id INT AUTO_INCREMENT PRIMARY KEY,
        denominacion INT NOT NULL,
        cantidad INT NOT NULL DEFAULT 0,
        subtotal DECIMAL(12,2) NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        INDEX idx_fecha (fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    
    # Lista de todas las tablas
    TABLES = [
        ("users", USERS_TABLE),
        ("compras", COMPRAS_TABLE),
        ("inventario", INVENTARIO_TABLE),
        ("subproductos", SUBPRODUCTOS_TABLE),
        ("subproducto_ingredientes", SUBPRODUCTO_INGREDIENTES_TABLE),
        ("subproducto_producciones", SUBPRODUCTO_PRODUCCIONES_TABLE),
        ("produccion_detalles", PRODUCCION_DETALLES_TABLE),
        ("productos_finales", PRODUCTOS_FINALES_TABLE),
        ("producto_final_subproductos", PRODUCTO_FINAL_SUBPRODUCTOS_TABLE),
        ("clientes", CLIENTES_TABLE),
        ("ventas_cabecera", VENTAS_CABECERA_TABLE),
        ("ventas_items", VENTAS_ITEMS_TABLE),
        ("gastos_money", GASTOS_MONEY_TABLE),
        ("gastos_productos", GASTOS_PRODUCTOS_TABLE),
        ("contabilidad", CONTABILIDAD_TABLE),
        ("efectivo_movimientos", EFECTIVO_MOVIMIENTOS_TABLE),
        ("efectivo_contador", EFECTIVO_CONTADOR_TABLE),
    ]
    
    @classmethod
    def get_all_tables(cls) -> List[tuple]:
        """Retorna todas las tablas"""
        return cls.TABLES
    
    @classmethod
    def get_table_sql(cls, table_name: str) -> str:
        """Obtiene SQL de una tabla específica"""
        for name, sql in cls.TABLES:
            if name == table_name:
                return sql
        return None