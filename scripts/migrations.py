#!/usr/bin/env python3
# scripts/migrations.py - Herramienta CLI para migraciones

import argparse
from Core.Common.database import get_connection
from Core.Database.manager import DatabaseMigrationManager
from Core.Common.logger import setup_logger

logger = setup_logger()


def main():
    parser = argparse.ArgumentParser(description="Gestor de migraciones de BD")
    subparsers = parser.add_subparsers(dest="command", help="Comando")
    
    # Comando: status
    subparsers.add_parser("status", help="Ver estado de migraciones")
    
    # Comando: migrate
    subparsers.add_parser("migrate", help="Aplicar todas las migraciones pendientes")
    
    # Comando: list
    subparsers.add_parser("list", help="Listar todas las migraciones disponibles")
    
    # Comando: rollback
    rollback = subparsers.add_parser("rollback", help="Revertir una migración")
    rollback.add_argument("version", type=int, help="Versión a revertir")
    
    # Comando: init
    subparsers.add_parser("init", help="Inicializar base de datos")
    
    args = parser.parse_args()
    
    if args.command == "status":
        status_command()
    elif args.command == "migrate":
        migrate_command()
    elif args.command == "list":
        list_command()
    elif args.command == "rollback":
        rollback_command(args.version)
    elif args.command == "init":
        init_command()
    else:
        parser.print_help()


def status_command():
    """Muestra estado de migraciones"""
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a BD")
        return
    
    manager = DatabaseMigrationManager()
    status = manager.get_migration_status(conn)
    
    print("\n📊 Estado de Migraciones:")
    print(f"   Versión actual: v{status['current_version']}")
    print(f"   Versión objetivo: v{status['target_version']}")
    print(f"   Migraciones pendientes: {status['pending']}")
    print(f"   Estado: {'✅ Al día' if status['is_updated'] else '⚠️ Actualizaciones pendientes'}")
    
    conn.close()


def migrate_command():
    """Aplica todas las migraciones"""
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a BD")
        return
    
    manager = DatabaseMigrationManager()
    if manager.migrate_to_latest(conn):
        print("✅ Migraciones completadas exitosamente")
    else:
        print("❌ Error durante migraciones")
    
    conn.close()


def list_command():
    """Lista migraciones disponibles"""
    manager = DatabaseMigrationManager()
    migrations = manager.list_migrations()
    
    print("\n📋 Migraciones Disponibles:")
    for migration in migrations:
        print(f"   v{migration.version}: {migration.description}")


def rollback_command(version: int):
    """Revierte una migración"""
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a BD")
        return
    
    manager = DatabaseMigrationManager()
    if manager.rollback_migration(conn, version):
        print(f"✅ Migración v{version} revertida")
    else:
        print(f"❌ Error revirtiendo migración v{version}")
    
    conn.close()


def init_command():
    """Inicializa la BD"""
    from Core.Common.database import DatabaseManager
    
    if DatabaseManager.initialize_database():
        print("✅ Base de datos inicializada")
    else:
        print("❌ Error inicializando BD")


if __name__ == "__main__":
    main()