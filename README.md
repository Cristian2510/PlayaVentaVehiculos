# Sistema de Gestión de Vehículos

Sistema completo de gestión de venta de vehículos con funcionalidades de:

- Catastro de vehículos
- Gestión de clientes
- Ventas con múltiples formas de pago
- Financiamiento con cuotas
- Control de deudas y pagos
- Cuentas corrientes
- Dashboard con estadísticas

## Tecnologías

- **Backend**: Flask (Python)
- **Base de datos**: PostgreSQL
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Despliegue**: Railway

## Instalación Local

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno para la base de datos
4. Ejecutar: `python app.py`

## Despliegue en Railway

El proyecto está configurado para desplegarse automáticamente en Railway. Solo necesitas:

1. Conectar tu repositorio de GitHub a Railway
2. Railway detectará automáticamente que es una aplicación Python
3. Se desplegará automáticamente con la base de datos PostgreSQL

## Variables de Entorno

- `DATABASE_URL`: URL de conexión a PostgreSQL (proporcionada por Railway)
- `PORT`: Puerto de la aplicación (proporcionado por Railway)
