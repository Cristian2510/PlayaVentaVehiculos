#!/usr/bin/env python3
"""
Script para configurar la base de datos PostgreSQL en Railway
"""
import os
import psycopg2
from urllib.parse import urlparse

def setup_database():
    """Configura la base de datos PostgreSQL en Railway"""
    try:
        # Obtener la URL de la base de datos desde Railway
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("❌ No se encontró DATABASE_URL en las variables de entorno")
            return False
        
        # Parsear la URL de la base de datos
        parsed_url = urlparse(database_url)
        
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=parsed_url.hostname,
            port=parsed_url.port,
            database=parsed_url.path[1:],  # Remover el slash inicial
            user=parsed_url.username,
            password=parsed_url.password
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Conexión a PostgreSQL establecida exitosamente")
        
        # Verificar si las tablas existen
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tablas existentes: {existing_tables}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando la base de datos: {e}")
        return False

if __name__ == "__main__":
    setup_database()
