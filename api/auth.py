from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import Usuario
import bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'usuario' not in data or 'clave' not in data:
        return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400
    
    usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
    
    if not usuario:
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    clave = data['clave']
    stored = usuario.clave if isinstance(usuario.clave, str) else ''
    valida = False

    if stored.startswith('$2'):
        try:
            valida = bcrypt.checkpw(clave.encode('utf-8'), stored.encode('utf-8'))
        except (ValueError, TypeError):
            valida = False
    else:
        valida = (stored == clave)

    if not valida:
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    if not stored.startswith('$2'):
        from bd import db
        usuario.clave = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.session.commit()

    access_token = create_access_token(identity=str(usuario.id_usuario))
    refresh_token = create_refresh_token(identity=str(usuario.id_usuario))
    
    return jsonify({
        'success': True,
        'data': {
            'token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': usuario.id_usuario,
                'nombre': usuario.nombres,
                'rol': usuario.rol.id_rol if usuario.rol else None
            }
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT es stateless, simplemente retornamos exito
    return jsonify({'success': True, 'message': 'Sesión cerrada correctamente'})

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'success': True, 'data': {'token': access_token}})
