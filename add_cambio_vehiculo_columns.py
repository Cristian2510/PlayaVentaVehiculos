import psycopg2

# Parámetros de conexión
DB_PARAMS = {
    'host': 'switchyard.proxy.rlwy.net',
    'database': 'railway', 
    'user': 'postgres',
    'password': 'kMNXapNmBpDFKCOLChvUoIoDkIMnAErr',
    'port': '19036'
}

def add_cambio_vehiculo_columns():
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        print("🔗 Conectado a la base de datos")
        
        # Primero eliminar la columna antigua si existe
        cursor.execute("ALTER TABLE venta DROP COLUMN IF EXISTS vehiculo_cambio;")
        
        # Agregar las nuevas columnas para datos completos del vehículo de cambio
        alter_commands = [
            # Datos básicos del vehículo de cambio
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_marca VARCHAR(50);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_modelo VARCHAR(50);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_anio INTEGER;',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_color VARCHAR(30);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_tipo_vehiculo VARCHAR(30);',
            
            # Identificación del vehículo
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_chasis VARCHAR(100);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_motor VARCHAR(100);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_placa VARCHAR(20);',
            
            # Características técnicas
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_kilometraje INTEGER;',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_combustible VARCHAR(30);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_transmision VARCHAR(30);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_estado VARCHAR(30);',
            
            # Precios y observaciones
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_precio_venta DECIMAL(10,2);',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS cambio_observaciones TEXT;',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS auto_registrar_vehiculo BOOLEAN DEFAULT TRUE;',
            'ALTER TABLE venta ADD COLUMN IF NOT EXISTS vehiculo_cambio_id INTEGER;'
        ]
        
        for command in alter_commands:
            print(f'Ejecutando: {command}')
            cursor.execute(command)
        
        # Confirmar cambios
        conn.commit()
        print('✅ Todas las columnas del vehículo de cambio agregadas exitosamente')
        
        # Verificar las columnas agregadas
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'venta' 
            AND column_name LIKE 'cambio_%' OR column_name = 'auto_registrar_vehiculo' OR column_name = 'vehiculo_cambio_id'
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        print('\n📋 Columnas del vehículo de cambio:')
        for col in columns:
            print(f'  - {col[0]}: {col[1]}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Agregando columnas del vehículo de cambio...")
    add_cambio_vehiculo_columns()
    print("🏁 Script completado")
