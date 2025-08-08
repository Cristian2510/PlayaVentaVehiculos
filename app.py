from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Configuración de base de datos para Railway
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Railway proporciona DATABASE_URL, pero SQLAlchemy necesita postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Configuración local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kMNXapNmBpDFKCOLChvUoIoDkIMnAErr@switchyard.proxy.rlwy.net:19036/railway'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos de base de datos
class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30), nullable=False)
    chasis = db.Column(db.String(50), unique=True, nullable=False)
    motor = db.Column(db.String(50), nullable=False)
    placa = db.Column(db.String(20), unique=True)
    precio_compra = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float)
    estado = db.Column(db.String(20), default='Disponible')  # Disponible, Vendido, En reparación
    fecha_ingreso = db.Column(db.Date, default=date.today)
    observaciones = db.Column(db.Text)
    kilometraje = db.Column(db.Integer)
    combustible = db.Column(db.String(30))
    transmision = db.Column(db.String(30))
    tipo_vehiculo = db.Column(db.String(50))

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(15), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    fecha_registro = db.Column(db.Date, default=date.today)

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha_venta = db.Column(db.Date, default=date.today)
    precio_venta = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(3), default='G')  # G para Guaraníes, USD para Dólares
    forma_pago = db.Column(db.String(30))  # Contado, Crédito, Financiamiento
    estado_pago = db.Column(db.String(20), default='Pendiente')  # Pendiente, Pagado, Parcial
    # Campos para ventas financiadas
    entrega_inicial = db.Column(db.Float, default=0.0)
    saldo_financiado = db.Column(db.Float, default=0.0)
    numero_cuotas = db.Column(db.Integer, default=0)
    monto_cuota = db.Column(db.Float, default=0.0)
    fecha_primer_cuota = db.Column(db.Date)
    # Campos para método de pago detallado
    metodo_pago = db.Column(db.String(30))  # Efectivo, Transferencia, Cheque, Cambio, Mixto
    banco_transferencia = db.Column(db.String(100))
    numero_transferencia = db.Column(db.String(50))
    banco_cheque = db.Column(db.String(100))
    numero_cheque = db.Column(db.String(50))
    fecha_cobro_cheque = db.Column(db.Date)
    # Campos completos para vehículo de cambio (catastro completo)
    cambio_marca = db.Column(db.String(50))
    cambio_modelo = db.Column(db.String(50))
    cambio_anio = db.Column(db.Integer)
    cambio_color = db.Column(db.String(30))
    cambio_tipo_vehiculo = db.Column(db.String(30))
    cambio_chasis = db.Column(db.String(100))
    cambio_motor = db.Column(db.String(100))
    cambio_placa = db.Column(db.String(20))
    cambio_kilometraje = db.Column(db.Integer)
    cambio_combustible = db.Column(db.String(30))
    cambio_transmision = db.Column(db.String(30))
    cambio_estado = db.Column(db.String(30))
    valor_vehiculo_cambio = db.Column(db.Float)
    cambio_precio_venta = db.Column(db.Float)
    cambio_observaciones = db.Column(db.Text)
    auto_registrar_vehiculo = db.Column(db.Boolean, default=True)
    vehiculo_cambio_id = db.Column(db.Integer)  # ID del vehículo registrado automáticamente
    # Campos para pago mixto
    monto_efectivo = db.Column(db.Float)
    monto_diferencia = db.Column(db.Float)
    metodo_diferencia = db.Column(db.String(30))
    vehiculo = db.relationship('Vehiculo', backref='ventas')
    cliente = db.relationship('Cliente', backref='compras')

class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    fecha_emision = db.Column(db.Date, default=date.today)
    monto_total = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, default=0.10)  # 10% IVA Paraguay
    estado = db.Column(db.String(20), default='Emitida')
    venta = db.relationship('Venta', backref='facturas')

class Pagare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    numero_pagare = db.Column(db.String(20), unique=True, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_emision = db.Column(db.Date, default=date.today)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default='Pendiente')
    venta = db.relationship('Venta', backref='pagares')

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    numero_contrato = db.Column(db.String(20), unique=True, nullable=False)
    fecha_contrato = db.Column(db.Date, default=date.today)
    tipo_contrato = db.Column(db.String(30))  # Compraventa, Leasing, etc.
    estado = db.Column(db.String(20), default='Activo')
    venta = db.relationship('Venta', backref='contratos')

class Cuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    numero_cuota = db.Column(db.Integer, nullable=False)  # 1, 2, 3, etc.
    monto = db.Column(db.Float, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    fecha_pago = db.Column(db.Date)  # NULL si no se ha pagado
    estado = db.Column(db.String(20), default='Pendiente')  # Pendiente, Pagada, Vencida
    monto_pagado = db.Column(db.Float, default=0.0)
    venta = db.relationship('Venta', backref='cuotas')

class Recibir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    monto_deuda = db.Column(db.Float, nullable=False)  # Valor del vehículo (deuda total)
    monto_cancelado = db.Column(db.Float, default=0.0)  # Entrega inicial + pagos de cuotas
    saldo_pendiente = db.Column(db.Float, nullable=False)  # Deuda - cancelaciones
    fecha_creacion = db.Column(db.Date, default=date.today)
    fecha_ultimo_pago = db.Column(db.Date)
    estado = db.Column(db.String(20), default='Pendiente')  # Pendiente, Pagado, Parcial
    observaciones = db.Column(db.Text)
    venta = db.relationship('Venta', backref='recibir')
    cliente = db.relationship('Cliente', backref='deudas')
    vehiculo = db.relationship('Vehiculo', backref='deudas')

class RecibirPago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recibir_id = db.Column(db.Integer, db.ForeignKey('recibir.id'), nullable=False)
    monto_pago = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.Date, default=date.today)
    tipo_pago = db.Column(db.String(20), nullable=False)  # Entrega Inicial, Cuota, Pago Extra
    observaciones = db.Column(db.Text)
    recibir = db.relationship('Recibir', backref='pagos')

class CuentaCtaCte(db.Model):
    __tablename__ = 'cuenta_cta_cte'
    registro = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100))
    moneda = db.Column(db.Integer)  # 1=Guaraníes, 2=Dólares
    moneda_desc = db.Column(db.String(20))
    tipo_cuenta = db.Column(db.Integer)  # 1=Efectivo, 2=Banco, 3=Cheque, etc.
    tipo_descripcion = db.Column(db.String(80))
    usuario = db.Column(db.Integer)
    usuario_descripcion = db.Column(db.String(80))
    activo = db.Column(db.Integer, default=1)  # 1=Activo, 0=Inactivo
    estado = db.Column(db.Integer, default=1)

class CuentaCorriente(db.Model):
    __tablename__ = 'cuenta_corriente'
    registro = db.Column(db.Integer, primary_key=True)
    referencia = db.Column(db.String(20))
    codigo = db.Column(db.Integer, db.ForeignKey('cuenta_cta_cte.registro'))
    codigo_desc = db.Column(db.String(80))
    fecha = db.Column(db.Date, default=date.today)
    prove_cli = db.Column(db.Integer)  # ID del proveedor o cliente
    descripcion = db.Column(db.String(100))
    documento = db.Column(db.String(20))
    lanzamiento = db.Column(db.Integer)  # ID de la venta/compra que origina el movimiento
    moneda = db.Column(db.Integer)  # 1=Guaraníes, 2=Dólares
    moneda_desc = db.Column(db.String(20))
    cotizacion = db.Column(db.Float, default=7300.0)  # Tipo de cambio
    valor_guarani = db.Column(db.Float)
    valor_dolar = db.Column(db.Float)
    cod_contabilidad = db.Column(db.String(20))
    desc_contabilidad = db.Column(db.String(100))
    observacion = db.Column(db.Text)
    debito_guarani = db.Column(db.Float, default=0.0)
    debito_dolar = db.Column(db.Float, default=0.0)
    credito_guarani = db.Column(db.Float, default=0.0)
    credito_dolar = db.Column(db.Float, default=0.0)
    estado = db.Column(db.Integer, default=1)
    fecha_registro = db.Column(db.Date, default=date.today)
    cheque_no = db.Column(db.String(20))
    cheque_emisio = db.Column(db.Date)
    cheque_vencimiento = db.Column(db.Date)
    favorecido = db.Column(db.String(100))
    banco_desc = db.Column(db.String(100))
    nro_operacion = db.Column(db.String(50))
    tipo_pago = db.Column(db.Integer)  # 1=Efectivo, 2=Transferencia, 3=Cheque
    # Relaciones
    cuenta_cta_cte = db.relationship('CuentaCtaCte', backref='movimientos')

class Caja(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=date.today)
    tipo_movimiento = db.Column(db.String(20))  # Ingreso, Egreso
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    saldo_anterior = db.Column(db.Float)
    saldo_actual = db.Column(db.Float)
    referencia = db.Column(db.String(100))

class Banco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=date.today)
    tipo_movimiento = db.Column(db.String(20))  # Deposito, Retiro, Transferencia
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    saldo_anterior = db.Column(db.Float)
    saldo_actual = db.Column(db.Float)
    numero_cuenta = db.Column(db.String(50))

class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=date.today)
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))  # Combustible, Mantenimiento, Impuestos, etc.
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    forma_pago = db.Column(db.String(30))
    estado = db.Column(db.String(20), default='Pendiente')
    proveedor = db.relationship('Proveedor', backref='gastos')

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ruc = db.Column(db.String(15), unique=True)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    fecha_registro = db.Column(db.Date, default=date.today)

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catastros/vehiculos')
def catastros_vehiculos():
    vehiculos = Vehiculo.query.all()
    return render_template('catastros_vehiculos.html', vehiculos=vehiculos)

@app.route('/catastros/clientes')
def catastros_clientes():
    clientes = Cliente.query.all()
    return render_template('catastros_clientes.html', clientes=clientes)

@app.route('/catastros/cuentas')
def catastros_cuentas():
    cuentas = CuentaCtaCte.query.all()
    return render_template('catastros_cuentas.html', cuentas=cuentas)

@app.route('/facturacion/compras')
def compras():
    return render_template('compras.html')

@app.route('/facturacion/ventas')
def ventas():
    ventas_data = Venta.query.all()
    return render_template('ventas.html', ventas=ventas_data)

@app.route('/financiero')
def financiero():
    return render_template('financiero.html')

@app.route('/inventarios')
def inventarios():
    vehiculos = Vehiculo.query.all()
    return render_template('inventarios.html', vehiculos=vehiculos)

@app.route('/contabilidad')
def contabilidad():
    return render_template('contabilidad.html')



@app.route('/crm')
def crm():
    clientes = Cliente.query.all()
    return render_template('crm.html', clientes=clientes)

# API Routes para AJAX
@app.route('/api/vehiculos', methods=['GET', 'POST'])
def api_vehiculos():
    if request.method == 'POST':
        data = request.get_json()
        nuevo_vehiculo = Vehiculo(
            marca=data['marca'],
            modelo=data['modelo'],
            anio=int(data['año']),
            color=data['color'],
            chasis=data['chasis'],
            motor=data['motor'],
            placa=data.get('placa', ''),
            precio_compra=float(data['precio_compra']),
            kilometraje=int(data.get('kilometraje', 0)),
            combustible=data.get('combustible', ''),
            transmision=data.get('transmision', ''),
            tipo_vehiculo=data.get('tipo_vehiculo', ''),
            observaciones=data.get('observaciones', '')
        )
        db.session.add(nuevo_vehiculo)
        db.session.commit()
        return jsonify({'success': True, 'id': nuevo_vehiculo.id})
    
    vehiculos = Vehiculo.query.all()
    return jsonify([{
        'id': v.id,
        'marca': v.marca,
        'modelo': v.modelo,
        'año': v.anio,
        'color': v.color,
        'chasis': v.chasis,
        'motor': v.motor,
        'placa': v.placa,
        'precio_compra': v.precio_compra,
        'precio_venta': v.precio_venta,
        'estado': v.estado,
        'kilometraje': v.kilometraje,
        'combustible': v.combustible,
        'transmision': v.transmision,
        'tipo_vehiculo': v.tipo_vehiculo,
        'observaciones': v.observaciones,
        'fecha_ingreso': v.fecha_ingreso.isoformat() if v.fecha_ingreso else None
    } for v in vehiculos])

@app.route('/api/vehiculos/<int:vehiculo_id>', methods=['GET', 'PUT', 'DELETE'])
def api_vehiculo(vehiculo_id):
    vehiculo = db.session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        return jsonify({'success': False, 'error': 'Vehículo no encontrado'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'id': vehiculo.id,
            'marca': vehiculo.marca,
            'modelo': vehiculo.modelo,
            'año': vehiculo.anio,
            'color': vehiculo.color,
            'chasis': vehiculo.chasis,
            'motor': vehiculo.motor,
            'placa': vehiculo.placa,
            'precio_compra': vehiculo.precio_compra,
            'precio_venta': vehiculo.precio_venta,
            'estado': vehiculo.estado,
            'kilometraje': vehiculo.kilometraje,
            'combustible': vehiculo.combustible,
            'transmision': vehiculo.transmision,
            'tipo_vehiculo': vehiculo.tipo_vehiculo,
            'observaciones': vehiculo.observaciones,
            'fecha_ingreso': vehiculo.fecha_ingreso.isoformat() if vehiculo.fecha_ingreso else None
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        try:
            vehiculo.marca = data['marca']
            vehiculo.modelo = data['modelo']
            vehiculo.anio = int(data['año'])
            vehiculo.color = data['color']
            vehiculo.chasis = data['chasis']
            vehiculo.motor = data['motor']
            vehiculo.placa = data.get('placa', '')
            vehiculo.precio_compra = float(data['precio_compra'])
            vehiculo.precio_venta = float(data.get('precio_venta', 0)) if data.get('precio_venta') else None
            vehiculo.kilometraje = int(data.get('kilometraje', 0))
            vehiculo.combustible = data.get('combustible', '')
            vehiculo.transmision = data.get('transmision', '')
            vehiculo.tipo_vehiculo = data.get('tipo_vehiculo', '')
            vehiculo.observaciones = data.get('observaciones', '')
            vehiculo.estado = data.get('estado', 'Disponible')
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(vehiculo)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/vehiculos/imagenes', methods=['POST'])
def api_vehiculos_imagenes():
    """Endpoint para subir imágenes de vehículos"""
    try:
        vehiculo_id = request.form.get('vehiculo_id')
        if not vehiculo_id:
            return jsonify({'success': False, 'error': 'ID de vehículo requerido'}), 400
        
        # Verificar que el vehículo existe
        vehiculo = db.session.get(Vehiculo, vehiculo_id)
        if not vehiculo:
            return jsonify({'success': False, 'error': 'Vehículo no encontrado'}), 404
        
        # Procesar las imágenes (por ahora solo las aceptamos)
        # En una implementación real, aquí guardarías las imágenes en el servidor
        # y almacenarías las rutas en la base de datos
        
        imagenes_guardadas = []
        for i in range(1, 5):
            imagen_key = f'imagen{i}'
            if imagen_key in request.files:
                imagen = request.files[imagen_key]
                if imagen and imagen.filename:
                    # Aquí podrías guardar la imagen en el filesystem o cloud storage
                    # Por ahora solo simulamos que se guardó
                    imagenes_guardadas.append({
                        'numero': i,
                        'nombre': imagen.filename,
                        'tamaño': len(imagen.read())
                    })
                    imagen.seek(0)  # Reset file pointer
        
        return jsonify({
            'success': True, 
            'imagenes_guardadas': len(imagenes_guardadas),
            'detalles': imagenes_guardadas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clientes', methods=['GET', 'POST'])
def api_clientes():
    if request.method == 'POST':
        data = request.get_json()
        nuevo_cliente = Cliente(
            nombre=data['nombre'],
            apellido=data['apellido'],
            cedula=data['cedula'],
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            direccion=data.get('direccion', '')
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({'success': True, 'id': nuevo_cliente.id})
    
    clientes = Cliente.query.all()
    return jsonify([{
        'id': c.id,
        'nombre': c.nombre,
        'apellido': c.apellido,
        'cedula': c.cedula,
        'telefono': c.telefono,
        'email': c.email,
        'direccion': c.direccion
    } for c in clientes])

@app.route('/api/cuentas-corrientes', methods=['GET', 'POST'])
def api_cuentas_corrientes():
    if request.method == 'POST':
        data = request.get_json()
        try:
            nueva_cuenta = CuentaCtaCte(
                descripcion=data['descripcion'],
                moneda=int(data['moneda']),
                moneda_desc=data['moneda_desc'],
                tipo_cuenta=int(data['tipo_cuenta']),
                tipo_descripcion=data['tipo_descripcion'],
                usuario=1,
                usuario_descripcion='Sistema',
                activo=1,
                estado=1
            )
            db.session.add(nueva_cuenta)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request
    cuentas = CuentaCtaCte.query.all()
    return jsonify([{
        'registro': c.registro,
        'descripcion': c.descripcion,
        'moneda': c.moneda,
        'moneda_desc': c.moneda_desc,
        'tipo_cuenta': c.tipo_cuenta,
        'tipo_descripcion': c.tipo_descripcion,
        'activo': c.activo,
        'estado': c.estado
    } for c in cuentas])

@app.route('/api/cuentas-corrientes/<int:cuenta_id>', methods=['GET', 'PUT', 'DELETE'])
def api_cuenta_corriente(cuenta_id):
    cuenta = db.session.get(CuentaCtaCte, cuenta_id)
    if not cuenta:
        return jsonify({'success': False, 'error': 'Cuenta no encontrada'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'registro': cuenta.registro,
            'descripcion': cuenta.descripcion,
            'moneda': cuenta.moneda,
            'moneda_desc': cuenta.moneda_desc,
            'tipo_cuenta': cuenta.tipo_cuenta,
            'tipo_descripcion': cuenta.tipo_descripcion,
            'activo': cuenta.activo,
            'estado': cuenta.estado
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        try:
            cuenta.descripcion = data['descripcion']
            cuenta.moneda = int(data['moneda'])
            cuenta.moneda_desc = data['moneda_desc']
            cuenta.tipo_cuenta = int(data['tipo_cuenta'])
            cuenta.tipo_descripcion = data['tipo_descripcion']
            cuenta.activo = int(data.get('activo', 1))
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            # Verificar si la cuenta tiene movimientos
            movimientos = CuentaCorriente.query.filter_by(codigo=cuenta_id).first()
            if movimientos:
                return jsonify({'success': False, 'error': 'No se puede eliminar la cuenta porque tiene movimientos registrados'}), 400
            
            db.session.delete(cuenta)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

def generar_cuotas(venta_id, saldo_financiado, numero_cuotas, fecha_primer_cuota):
    """Genera las cuotas para una venta financiada"""
    
    if numero_cuotas <= 0 or saldo_financiado <= 0:
        return
    
    # Calcular monto por cuota (redondear a 2 decimales)
    monto_cuota = round(saldo_financiado / numero_cuotas, 2)
    
    # Ajustar la última cuota para que la suma sea exacta
    monto_ultima_cuota = saldo_financiado - (monto_cuota * (numero_cuotas - 1))
    
    fecha_actual = fecha_primer_cuota
    
    for i in range(1, numero_cuotas + 1):
        # Usar monto ajustado para la última cuota
        monto = monto_ultima_cuota if i == numero_cuotas else monto_cuota
        
        cuota = Cuota(
            venta_id=venta_id,
            numero_cuota=i,
            monto=monto,
            fecha_vencimiento=fecha_actual,
            estado='Pendiente',
            monto_pagado=0.0
        )
        db.session.add(cuota)
        
        # Avanzar al siguiente mes para la próxima cuota
        fecha_actual += relativedelta(months=1)
    
    db.session.commit()

@app.route('/api/ventas', methods=['GET', 'POST'])
@app.route('/api/ventas/<int:venta_id>', methods=['PUT'])
def api_ventas(venta_id=None):
    if request.method == 'PUT':
        # Lógica para actualizar venta
        venta = db.session.get(Venta, venta_id)
        if not venta:
            return jsonify({'success': False, 'error': 'Venta no encontrada'}), 404
            
        data = request.get_json()
        try:
            # Validar datos básicos
            try:
                precio_venta = float(data['precio_venta']) if data.get('precio_venta') and data.get('precio_venta') != '' else 0
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Precio de venta inválido'}), 400
                
            # Actualizar campos básicos
            venta.vehiculo_id = int(data.get('vehiculo_id')) if data.get('vehiculo_id') else venta.vehiculo_id
            venta.cliente_id = int(data.get('cliente_id')) if data.get('cliente_id') else venta.cliente_id
            venta.fecha_venta = datetime.strptime(data.get('fecha_venta', date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
            venta.precio_venta = precio_venta
            venta.forma_pago = data.get('forma_pago', 'Contado')
            venta.estado_pago = data.get('estado_pago', 'Pendiente')
            venta.moneda = data.get('moneda', 'G')
            
            # Actualizar campos de financiamiento
            if data.get('forma_pago') == 'Financiamiento':
                try:
                    entrega_inicial = float(data.get('entrega_inicial', 0)) if data.get('entrega_inicial') and data.get('entrega_inicial') != '' else 0
                    numero_cuotas = int(data.get('numero_cuotas', 0)) if data.get('numero_cuotas') and data.get('numero_cuotas') != '' else 0
                    fecha_primer_cuota = datetime.strptime(data.get('fecha_primer_cuota'), '%Y-%m-%d').date() if data.get('fecha_primer_cuota') else None
                    
                    venta.entrega_inicial = entrega_inicial
                    venta.numero_cuotas = numero_cuotas
                    venta.fecha_primer_cuota = fecha_primer_cuota
                    venta.saldo_financiado = precio_venta - entrega_inicial
                    venta.monto_cuota = round(venta.saldo_financiado / numero_cuotas, 2) if numero_cuotas > 0 else 0
                except (ValueError, TypeError) as e:
                    return jsonify({'success': False, 'error': f'Error en datos de financiamiento: {str(e)}'}), 400
            
            # Actualizar método de pago y campos relacionados
            venta.metodo_pago = data.get('metodo_pago')
            venta.banco_transferencia = data.get('banco_transferencia')
            venta.numero_transferencia = data.get('numero_transferencia')
            venta.banco_cheque = data.get('banco_cheque')
            venta.numero_cheque = data.get('numero_cheque')
            venta.fecha_cobro_cheque = datetime.strptime(data.get('fecha_cobro_cheque'), '%Y-%m-%d').date() if data.get('fecha_cobro_cheque') else None
            
            # Actualizar campos de cambio de vehículo
            if data.get('metodo_pago') == 'Cambio':
                venta.cambio_marca = data.get('cambio_marca')
                venta.cambio_modelo = data.get('cambio_modelo')
                venta.cambio_anio = int(data.get('cambio_anio')) if data.get('cambio_anio') else None
                venta.cambio_color = data.get('cambio_color')
                venta.cambio_tipo_vehiculo = data.get('cambio_tipo_vehiculo')
                venta.cambio_chasis = data.get('cambio_chasis')
                venta.cambio_motor = data.get('cambio_motor')
                venta.cambio_placa = data.get('cambio_placa')
                venta.cambio_kilometraje = int(data.get('cambio_kilometraje')) if data.get('cambio_kilometraje') else None
                venta.cambio_combustible = data.get('cambio_combustible')
                venta.cambio_transmision = data.get('cambio_transmision')
                venta.cambio_estado = data.get('cambio_estado')
                venta.valor_vehiculo_cambio = float(data.get('valor_vehiculo_cambio')) if data.get('valor_vehiculo_cambio') else None
                venta.cambio_precio_venta = float(data.get('cambio_precio_venta')) if data.get('cambio_precio_venta') else None
                venta.cambio_observaciones = data.get('cambio_observaciones')
                venta.auto_registrar_vehiculo = data.get('auto_registrar_vehiculo', False)
            
            # Actualizar campos de pago mixto
            if data.get('metodo_pago') == 'Mixto':
                venta.monto_efectivo = float(data.get('monto_efectivo')) if data.get('monto_efectivo') else None
                venta.monto_diferencia = float(data.get('monto_diferencia')) if data.get('monto_diferencia') else None
                venta.metodo_diferencia = data.get('metodo_diferencia')
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Venta actualizada exitosamente'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Error al actualizar la venta: {str(e)}'}), 500
    
    elif request.method == 'POST':
        data = request.get_json()
        
        try:
            # Calcular campos de financiamiento con validaciones
            try:
                precio_venta = float(data['precio_venta']) if data.get('precio_venta') and data.get('precio_venta') != '' else 0
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Precio de venta inválido'}), 400
                
            try:
                entrega_inicial = float(data.get('entrega_inicial', 0)) if data.get('entrega_inicial') and data.get('entrega_inicial') != '' else 0
            except (ValueError, TypeError):
                entrega_inicial = 0
                
            forma_pago = data.get('forma_pago', 'Contado')
            
            # Validar que la entrega inicial no sea mayor al precio
            if entrega_inicial > precio_venta:
                return jsonify({'success': False, 'error': 'La entrega inicial no puede ser mayor al precio de venta'}), 400
            
            saldo_financiado = precio_venta - entrega_inicial
            
            try:
                numero_cuotas = int(data.get('numero_cuotas', 0)) if data.get('numero_cuotas') and data.get('numero_cuotas') != '' else 0
            except (ValueError, TypeError):
                numero_cuotas = 0
            
            # Validar financiamiento
            if forma_pago == 'Financiamiento':
                if numero_cuotas <= 0:
                    return jsonify({'success': False, 'error': 'Debe especificar el número de cuotas para financiamiento'}), 400
                if not data.get('fecha_primer_cuota'):
                    return jsonify({'success': False, 'error': 'Debe especificar la fecha de la primera cuota'}), 400
                if entrega_inicial >= precio_venta:
                    return jsonify({'success': False, 'error': 'Para financiamiento debe haber un saldo a financiar'}), 400
            
            # Calcular monto por cuota solo si es financiamiento
            monto_cuota = 0
            if forma_pago == 'Financiamiento' and numero_cuotas > 0:
                monto_cuota = round(saldo_financiado / numero_cuotas, 2)
            
            # Verificar si ya existe una venta similar (protección contra duplicados)
            venta_existente = Venta.query.filter_by(
                vehiculo_id=int(data['vehiculo_id']),
                cliente_id=int(data['cliente_id']),
                fecha_venta=datetime.strptime(data.get('fecha_venta', date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
                precio_venta=precio_venta
            ).first()
            
            if venta_existente:
                return jsonify({'success': False, 'error': 'Ya existe una venta con estos datos. Verifique que no esté duplicando la operación.'}), 400
            
            # Validaciones básicas
            if not data.get('vehiculo_id') or not data.get('cliente_id') or not data.get('precio_venta'):
                return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
            
            # Crear la venta
            nueva_venta = Venta(
                vehiculo_id=int(data['vehiculo_id']),
                cliente_id=int(data['cliente_id']),
                fecha_venta=datetime.strptime(data.get('fecha_venta', date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
                precio_venta=precio_venta,
                forma_pago=forma_pago,
                estado_pago=data.get('estado_pago', 'Pendiente'),
                entrega_inicial=entrega_inicial,
                saldo_financiado=saldo_financiado,
                numero_cuotas=numero_cuotas,
                monto_cuota=monto_cuota,
                moneda=data.get('moneda', 'G'), # Asignar moneda
                fecha_primer_cuota=datetime.strptime(data.get('fecha_primer_cuota', date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date() if data.get('fecha_primer_cuota') else None,
                # Campos de método de pago
                metodo_pago=data.get('metodo_pago'),
                banco_transferencia=data.get('banco_transferencia'),
                numero_transferencia=data.get('numero_transferencia'),
                banco_cheque=data.get('banco_cheque'),
                numero_cheque=data.get('numero_cheque'),
                fecha_cobro_cheque=datetime.strptime(data.get('fecha_cobro_cheque'), '%Y-%m-%d').date() if data.get('fecha_cobro_cheque') else None,
                # Campos completos para vehículo de cambio
                cambio_marca=data.get('cambio_marca'),
                cambio_modelo=data.get('cambio_modelo'),
                cambio_anio=int(data.get('cambio_anio', 0)) if data.get('cambio_anio') and data.get('cambio_anio') != '' else None,
                cambio_color=data.get('cambio_color'),
                cambio_tipo_vehiculo=data.get('cambio_tipo_vehiculo'),
                cambio_chasis=data.get('cambio_chasis'),
                cambio_motor=data.get('cambio_motor'),
                cambio_placa=data.get('cambio_placa'),
                cambio_kilometraje=int(data.get('cambio_kilometraje', 0)) if data.get('cambio_kilometraje') and data.get('cambio_kilometraje') != '' else None,
                cambio_combustible=data.get('cambio_combustible'),
                cambio_transmision=data.get('cambio_transmision'),
                cambio_estado=data.get('cambio_estado'),
                valor_vehiculo_cambio=float(data.get('valor_vehiculo_cambio', 0)) if data.get('valor_vehiculo_cambio') and data.get('valor_vehiculo_cambio') != '' else None,
                cambio_precio_venta=float(data.get('cambio_precio_venta', 0)) if data.get('cambio_precio_venta') and data.get('cambio_precio_venta') != '' else None,
                cambio_observaciones=data.get('cambio_observaciones'),
                auto_registrar_vehiculo=data.get('auto_registrar_vehiculo', False),
                # Campos para pago mixto
                monto_efectivo=float(data.get('monto_efectivo', 0)) if data.get('monto_efectivo') and data.get('monto_efectivo') != '' else None,
                monto_diferencia=float(data.get('monto_diferencia', 0)) if data.get('monto_diferencia') and data.get('monto_diferencia') != '' else None,
                metodo_diferencia=data.get('metodo_diferencia')
            )
            db.session.add(nueva_venta)
            db.session.flush()  # Para obtener el ID de la venta
            
            # Generar cuotas si es una venta financiada
            if forma_pago == 'Financiamiento' and numero_cuotas > 0:
                generar_cuotas(
                    nueva_venta.id,
                    saldo_financiado,
                    numero_cuotas,
                    nueva_venta.fecha_primer_cuota
                )
            
            # Crear registro en RECIBIR (deuda del cliente)
            nuevo_recibir = Recibir(
                venta_id=nueva_venta.id,
                cliente_id=int(data['cliente_id']),
                vehiculo_id=int(data['vehiculo_id']),
                monto_deuda=precio_venta,  # Valor del vehículo = deuda total
                monto_cancelado=entrega_inicial,  # Entrega inicial como primer pago
                saldo_pendiente=precio_venta - entrega_inicial,  # Deuda - entrega inicial
                fecha_creacion=date.today(),
                estado='Pendiente' if entrega_inicial < precio_venta else 'Pagado',
                observaciones=f'Venta #{nueva_venta.id} - {forma_pago}'
            )
            db.session.add(nuevo_recibir)
            db.session.flush()  # Para obtener el ID del registro Recibir
            
            # Si hay entrega inicial, registrar el pago
            if entrega_inicial > 0:
                pago_entrega = RecibirPago(
                    recibir_id=nuevo_recibir.id,
                    monto_pago=entrega_inicial,
                    fecha_pago=date.today(),
                    tipo_pago='Entrega Inicial',
                    observaciones=f'Entrega inicial de venta #{nueva_venta.id}'
                )
                db.session.add(pago_entrega)
                nuevo_recibir.fecha_ultimo_pago = date.today()
            
            # Actualizar estado del vehículo
            vehiculo = db.session.get(Vehiculo, int(data['vehiculo_id']))
            vehiculo.estado = 'Vendido'
            vehiculo.precio_venta = precio_venta
            
            db.session.commit()
            return jsonify({'success': True, 'id': nueva_venta.id})
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Error en los datos numéricos: {str(e)}'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Error al guardar la venta: {str(e)}'}), 500
    
    # GET: Obtener todas las ventas
    ventas = Venta.query.all()
    return jsonify([{
        'id': v.id,
        'vehiculo_id': v.vehiculo_id,
        'cliente_id': v.cliente_id,
        'fecha_venta': v.fecha_venta.strftime('%Y-%m-%d'),
        'precio_venta': v.precio_venta,
        'moneda': v.moneda,
        'forma_pago': v.forma_pago,
        'estado_pago': v.estado_pago,
        'entrega_inicial': v.entrega_inicial,
        'saldo_financiado': v.saldo_financiado,
        'numero_cuotas': v.numero_cuotas,
        'monto_cuota': v.monto_cuota,
        'vehiculo_marca': v.vehiculo.marca,
        'vehiculo_modelo': v.vehiculo.modelo,
        'cliente_nombre': f"{v.cliente.nombre} {v.cliente.apellido}"
    } for v in ventas])

@app.route('/api/ventas/<int:venta_id>', methods=['DELETE'])
def eliminar_venta(venta_id):
    try:
        # Buscar la venta
        venta = Venta.query.get(venta_id)
        if not venta:
            return jsonify({'success': False, 'error': 'Venta no encontrada'}), 404
        
        # Eliminar registros relacionados primero (en orden de dependencia)
        # 1. Eliminar pagos de recibir
        recibir_pagos = RecibirPago.query.join(Recibir).filter(Recibir.venta_id == venta_id).all()
        for pago in recibir_pagos:
            db.session.delete(pago)
        
        # 2. Eliminar registros de recibir
        recibir_registros = Recibir.query.filter_by(venta_id=venta_id).all()
        for recibir in recibir_registros:
            db.session.delete(recibir)
        
        # 3. Eliminar cuotas
        cuotas = Cuota.query.filter_by(venta_id=venta_id).all()
        for cuota in cuotas:
            db.session.delete(cuota)
        
        # 4. Eliminar facturas relacionadas
        facturas = Factura.query.filter_by(venta_id=venta_id).all()
        for factura in facturas:
            db.session.delete(factura)
        
        # 5. Eliminar pagarés relacionados
        pagares = Pagare.query.filter_by(venta_id=venta_id).all()
        for pagare in pagares:
            db.session.delete(pagare)
        
        # 6. Eliminar contratos relacionados
        contratos = Contrato.query.filter_by(venta_id=venta_id).all()
        for contrato in contratos:
            db.session.delete(contrato)
        
        # 7. Finalmente eliminar la venta
        db.session.delete(venta)
        
        # Commit de todos los cambios
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Venta eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando venta: {e}")
        return jsonify({'success': False, 'error': 'Error al eliminar la venta'}), 500

@app.route('/api/caja', methods=['GET', 'POST'])
def api_caja():
    if request.method == 'POST':
        data = request.get_json()
        nuevo_movimiento = Caja(
            tipo_movimiento=data['tipo_movimiento'],
            concepto=data['concepto'],
            monto=float(data['monto']),
            referencia=data.get('referencia', '')
        )
        db.session.add(nuevo_movimiento)
        db.session.commit()
        return jsonify({'success': True, 'id': nuevo_movimiento.id})
    
    movimientos = Caja.query.order_by(Caja.fecha.desc()).all()
    return jsonify([{
        'id': m.id,
        'fecha': m.fecha.strftime('%Y-%m-%d'),
        'tipo_movimiento': m.tipo_movimiento,
        'concepto': m.concepto,
        'monto': m.monto,
        'referencia': m.referencia
    } for m in movimientos])

@app.route('/api/cuotas/<int:venta_id>', methods=['GET'])
def api_cuotas(venta_id):
    """Obtiene las cuotas de una venta específica"""
    cuotas = Cuota.query.filter_by(venta_id=venta_id).order_by(Cuota.numero_cuota).all()
    return jsonify([{
        'id': c.id,
        'numero_cuota': c.numero_cuota,
        'monto': c.monto,
        'fecha_vencimiento': c.fecha_vencimiento.strftime('%Y-%m-%d'),
        'fecha_pago': c.fecha_pago.strftime('%Y-%m-%d') if c.fecha_pago else None,
        'estado': c.estado,
        'monto_pagado': c.monto_pagado
    } for c in cuotas])

@app.route('/api/cuotas/<int:cuota_id>/pagar', methods=['POST'])
def pagar_cuota(cuota_id):
    """Marca una cuota como pagada"""
    data = request.get_json()
    cuota = Cuota.query.get_or_404(cuota_id)
    
    cuota.estado = 'Pagada'
    cuota.fecha_pago = date.today()
    cuota.monto_pagado = cuota.monto
    
    # Actualizar estado de la venta
    venta = cuota.venta
    cuotas_pagadas = len([c for c in venta.cuotas if c.estado == 'Pagada'])
    total_cuotas = len(venta.cuotas)
    
    if cuotas_pagadas == total_cuotas:
        venta.estado_pago = 'Pagado'
    else:
        venta.estado_pago = 'Parcial'
    
    # Actualizar tabla RECIBIR
    recibir = Recibir.query.filter_by(venta_id=venta.id).first()
    if recibir:
        # Registrar el pago de la cuota
        pago_cuota = RecibirPago(
            recibir_id=recibir.id,
            monto_pago=cuota.monto,
            fecha_pago=date.today(),
            tipo_pago='Cuota',
            observaciones=f'Pago de cuota #{cuota.numero_cuota} de venta #{venta.id}'
        )
        db.session.add(pago_cuota)
        
        # Actualizar montos en RECIBIR
        recibir.monto_cancelado += cuota.monto
        recibir.saldo_pendiente = recibir.monto_deuda - recibir.monto_cancelado
        recibir.fecha_ultimo_pago = date.today()
        
        # Actualizar estado de RECIBIR
        if recibir.saldo_pendiente <= 0:
            recibir.estado = 'Pagado'
        else:
            recibir.estado = 'Parcial'
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/cuotas/<int:cuota_id>/deshacer-pago', methods=['POST'])
def deshacer_pago_cuota(cuota_id):
    """Deshace el pago de una cuota (elimina el pago)"""
    cuota = Cuota.query.get_or_404(cuota_id)
    
    if cuota.estado != 'Pagada':
        return jsonify({'success': False, 'error': 'La cuota no está pagada'})
    
    # Buscar el pago correspondiente en RecibirPago
    recibir = Recibir.query.filter_by(venta_id=cuota.venta_id).first()
    if recibir:
        # Buscar el pago específico de esta cuota
        pago = RecibirPago.query.filter_by(
            recibir_id=recibir.id,
            monto_pago=cuota.monto,
            tipo_pago='Cuota'
        ).filter(
            RecibirPago.observaciones.like(f'%cuota #{cuota.numero_cuota}%')
        ).first()
        
        if pago:
            # Eliminar el pago
            db.session.delete(pago)
            
            # Actualizar montos en RECIBIR
            recibir.monto_cancelado -= cuota.monto
            recibir.saldo_pendiente = recibir.monto_deuda - recibir.monto_cancelado
            
            # Actualizar estado de RECIBIR
            if recibir.saldo_pendiente > 0:
                recibir.estado = 'Parcial'
            else:
                recibir.estado = 'Pendiente'
    
    # Actualizar la cuota
    cuota.estado = 'Pendiente'
    cuota.fecha_pago = None
    cuota.monto_pagado = 0.0
    
    # Actualizar estado de la venta
    venta = cuota.venta
    cuotas_pagadas = len([c for c in venta.cuotas if c.estado == 'Pagada'])
    total_cuotas = len(venta.cuotas)
    
    if cuotas_pagadas == 0:
        venta.estado_pago = 'Pendiente'
    else:
        venta.estado_pago = 'Parcial'
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/recibir/<int:cliente_id>', methods=['GET'])
def api_recibir_cliente(cliente_id):
    """Obtiene las deudas de un cliente específico"""
    deudas = Recibir.query.filter_by(cliente_id=cliente_id).order_by(Recibir.fecha_creacion.desc()).all()
    return jsonify([{
        'id': r.id,
        'venta_id': r.venta_id,
        'vehiculo_id': r.vehiculo_id,
        'monto_deuda': r.monto_deuda,
        'monto_cancelado': r.monto_cancelado,
        'saldo_pendiente': r.saldo_pendiente,
        'fecha_creacion': r.fecha_creacion.strftime('%Y-%m-%d'),
        'fecha_ultimo_pago': r.fecha_ultimo_pago.strftime('%Y-%m-%d') if r.fecha_ultimo_pago else None,
        'estado': r.estado,
        'vehiculo_marca': r.vehiculo.marca,
        'vehiculo_modelo': r.vehiculo.modelo,
        'observaciones': r.observaciones
    } for r in deudas])

@app.route('/api/recibir/pagos/<int:recibir_id>', methods=['GET'])
def api_recibir_pagos(recibir_id):
    """Obtiene los pagos de una deuda específica"""
    pagos = RecibirPago.query.filter_by(recibir_id=recibir_id).order_by(RecibirPago.fecha_pago).all()
    return jsonify([{
        'id': p.id,
        'monto_pago': p.monto_pago,
        'fecha_pago': p.fecha_pago.strftime('%Y-%m-%d'),
        'tipo_pago': p.tipo_pago,
        'observaciones': p.observaciones
    } for p in pagos])

@app.route('/api/summary', methods=['GET'])
def api_summary():
    """Obtiene datos de resumen para el dashboard"""
    try:
        # Calcular total de compras (precio_compra de vehículos)
        compra_total = db.session.query(db.func.sum(Vehiculo.precio_compra)).scalar() or 0
        
        # Calcular total de ventas
        venta_total = db.session.query(db.func.sum(Venta.precio_venta)).scalar() or 0
        
        # Calcular utilidad
        utilidad = venta_total - compra_total
        
        # Calcular ventas del mes actual
        from datetime import datetime
        now = datetime.now()
        ventas_mes = db.session.query(db.func.sum(Venta.precio_venta)).filter(
            db.extract('month', Venta.fecha_venta) == now.month,
            db.extract('year', Venta.fecha_venta) == now.year
        ).scalar() or 0
        
        # Calcular gastos del mes
        gastos_mes = db.session.query(db.func.sum(Gasto.monto)).filter(
            db.extract('month', Gasto.fecha) == now.month,
            db.extract('year', Gasto.fecha) == now.year
        ).scalar() or 0
        
        return jsonify({
            'compra_total': float(compra_total),
            'venta_total': float(venta_total),
            'utilidad': float(utilidad),
            'ventas_mes': float(ventas_mes),
            'gastos_mes': float(gastos_mes)
        })
    except Exception as e:
        return jsonify({
            'compra_total': 0,
            'venta_total': 0,
            'utilidad': 0,
            'ventas_mes': 0,
            'gastos_mes': 0
        })

@app.route('/api/gastos', methods=['GET', 'POST'])
def api_gastos():
    if request.method == 'POST':
        data = request.get_json()
        nuevo_gasto = Gasto(
            concepto=data['concepto'],
            monto=float(data['monto']),
            categoria=data.get('categoria', ''),
            proveedor_id=int(data.get('proveedor_id', 0)) if data.get('proveedor_id') else None,
            forma_pago=data.get('forma_pago', ''),
            estado=data.get('estado', 'Pendiente')
        )
        db.session.add(nuevo_gasto)
        db.session.commit()
        return jsonify({'success': True, 'id': nuevo_gasto.id})
    
    gastos = Gasto.query.order_by(Gasto.fecha.desc()).all()
    return jsonify([{
        'id': g.id,
        'fecha': g.fecha.strftime('%Y-%m-%d'),
        'concepto': g.concepto,
        'monto': g.monto,
        'categoria': g.categoria,
        'estado': g.estado,
        'proveedor_nombre': g.proveedor.nombre if g.proveedor else ''
    } for g in gastos])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Configuración para Railway
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 