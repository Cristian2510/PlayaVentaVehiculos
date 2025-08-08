# PlayaVentaVehículos 🚗

Sistema completo de gestión de venta de vehículos con funcionalidades de:

- 🚗 **Catastro de vehículos** - Gestión completa del inventario
- 👥 **Gestión de clientes** - Base de datos de clientes
- 💰 **Ventas con múltiples formas de pago** - Efectivo, transferencia, cheque, cambio
- 📊 **Financiamiento con cuotas** - Control de pagos a plazos
- 💳 **Control de deudas y pagos** - Seguimiento de saldos pendientes
- 🏦 **Cuentas corrientes** - Gestión financiera
- 📈 **Dashboard con estadísticas** - Reportes y métricas

## 🌐 **Aplicación en Vivo**

**URL de la aplicación:** [https://playaventavehiculos-production.up.railway.app](https://playaventavehiculos-production.up.railway.app)

## 🛠️ Tecnologías

- **Backend**: Flask (Python 3.11)
- **Base de datos**: PostgreSQL
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Despliegue**: Railway
- **Servidor**: Gunicorn

## 📦 Instalación Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Cristian2510/PlayaVentaVehiculos.git
   cd PlayaVentaVehiculos
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar base de datos:**
   - Crear base de datos PostgreSQL
   - Configurar variable `DATABASE_URL`

4. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

## 🚀 Despliegue en Railway

El proyecto está **ya desplegado** en Railway y configurado para actualizaciones automáticas:

### ✅ **Estado Actual:**
- ✅ Aplicación desplegada exitosamente
- ✅ Base de datos PostgreSQL conectada
- ✅ Despliegue automático desde GitHub

### 🔄 **Actualizaciones:**
Cada vez que hagas `git push` a GitHub, Railway automáticamente:
1. Detecta los cambios
2. Reconstruye la aplicación
3. Despliega la nueva versión

## 🔧 Variables de Entorno

Railway configura automáticamente:
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `PORT`: Puerto de la aplicación
- `RAILWAY_ENVIRONMENT`: Entorno de despliegue

## 📁 Estructura del Proyecto

```
PlayaVentaVehiculos/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── Procfile             # Configuración para Railway
├── railway.json         # Configuración Railway
├── database_setup.py    # Script de configuración DB
├── init_db.py          # Inicialización de tablas
├── templates/           # Plantillas HTML
└── README.md           # Este archivo
```
