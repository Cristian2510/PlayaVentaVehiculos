#!/usr/bin/env python3
"""
Script para inicializar la base de datos en Railway
"""
from app import app, db

def init_database():
    """Inicializa las tablas de la base de datos"""
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            
            # Verificar las tablas creadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tablas creadas: {tables}")
            
        except Exception as e:
            print(f"❌ Error inicializando la base de datos: {e}")

if __name__ == "__main__":
    init_database()
