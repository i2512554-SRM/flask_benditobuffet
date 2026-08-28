from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Usuario, PagoPersonal, Adelanto, DocumentoIdentidad
from schemas.usuario import usuario_schema, usuarios_schema, pago_schema, pagos_schema

personal_bp = Blueprint('personal', __name__)

@personal_bp.route('/', methods=['GET'])
@jwt_required()
def get_empleados():
    empleados = Usuario.query.filter_by(estado=True).all()
    return jsonify({'success': True, 'data': usuarios_schema.dump(empleados)})

@personal_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/', methods=['POST'])
@jwt_required()
def crear_empleado():
    data = request.get_json()
    
    documento = DocumentoIdentidad(
        tipo='DNI',
        numero=data['dni']
    )
    db.session.add(documento)
    db.session.flush()
    
    empleado = Usuario(
        nombres=data['nombres'],
        apellido=data['apellido'],
        correo=data['correo'],
        telefono=data.get('telefono', ''),
        usuario=data['usuario'],
        clave=data.get('clave', ''),
        id_documento=documento.id_documento,
        id_rol=2,
        estado=True,
        turno=data.get('turno', 'Manana')
    )
    db.session.add(empleado)
    db.session.commit()
    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    data = request.get_json()
    
    empleado.nombres = data.get('nombres', empleado.nombres)
    empleado.apellido = data.get('apellido', empleado.apellido)
    empleado.correo = data.get('correo', empleado.correo)
    empleado.telefono = data.get('telefono', empleado.telefono)
    empleado.turno = data.get('turno', empleado.turno)
    
    if 'dni' in data and empleado.documento:
        empleado.documento.numero = data['dni']
    
    db.session.commit()
    return jsonify({'success': True, 'data': usuario_schema.dump(empleado)})

@personal_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    empleado.estado = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Empleado desactivado'})

@personal_bp.route('/pagos', methods=['GET'])
@jwt_required()
def get_pagos():
    pagos = PagoPersonal.query.order_by(PagoPersonal.fecha.desc()).all()
    return jsonify({'success': True, 'data': pagos_schema.dump(pagos)})

@personal_bp.route('/pagos', methods=['POST'])
@jwt_required()
def crear_pago():
    data = request.get_json()
    pago = PagoPersonal(
        id_usuario=data['id_usuario'],
        monto=data['monto'],
        fecha=data['fecha'],
        tipo=data['tipo'],
        descripcion=data.get('descripcion', '')
    )
    db.session.add(pago)
    db.session.commit()
    return jsonify({'success': True, 'data': pago_schema.dump(pago)})

@personal_bp.route('/adelantos', methods=['GET'])
@jwt_required()
def get_adelantos():
    adelantos = Adelanto.query.order_by(Adelanto.fecha.desc()).all()
    return jsonify({'success': True, 'data': [{'id_adelanto': a.id_adelanto, 'id_usuario': a.id_usuario, 'monto': a.monto, 'fecha': a.fecha, 'estado': a.estado, 'motivo': a.motivo} for a in adelantos]})

@personal_bp.route('/adelantos', methods=['POST'])
@jwt_required()
def crear_adelanto():
    data = request.get_json()
    from datetime import datetime
    adelanto = Adelanto(
        id_usuario=data['id_usuario'],
        monto=data['monto'],
        fecha=datetime.utcnow().date(),
        estado='Pendiente',
        descripcion=data.get('descripcion', '')
    )
    db.session.add(adelanto)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id_adelanto': adelanto.id_adelanto, 'id_usuario': adelanto.id_usuario, 'monto': adelanto.monto, 'fecha': adelanto.fecha, 'estado': adelanto.estado}})

@personal_bp.route('/salarios', methods=['GET'])
@jwt_required()
def get_salarios():
    from datetime import datetime
    from flask import request as req
    from dateutil.relativedelta import relativedelta

    now = datetime.now()
    mes = req.args.get('mes', type=int) or now.month
    anio = req.args.get('anio', type=int) or now.year

    inicio = datetime(anio, mes, 1)
    fin = inicio + relativedelta(months=1)

    empleados = Usuario.query.filter_by(estado=True).all()
    salarios = []

    for emp in empleados:
        pagos = PagoPersonal.query.filter(
            PagoPersonal.id_usuario == emp.id_usuario,
            PagoPersonal.fecha >= inicio,
            PagoPersonal.fecha < fin
        ).all()

        adelantos = Adelanto.query.filter(
            Adelanto.id_usuario == emp.id_usuario,
            Adelanto.fecha >= inicio,
            Adelanto.fecha < fin
        ).all()

        total_pagos = sum(p.monto for p in pagos)
        total_adelantos = sum(a.monto for a in adelantos)

        salarios.append({
            'id_usuario': emp.id_usuario,
            'nombres': emp.nombres,
            'apellido': emp.apellido,
            'sueldo_base': 0,
            'total_pagos': total_pagos,
            'total_adelantos': total_adelantos,
            'neto': total_pagos - total_adelantos
        })

    return jsonify({'success': True, 'data': salarios})
