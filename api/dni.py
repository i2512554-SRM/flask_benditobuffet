from functools import wraps
from datetime import timedelta
import os
import re
import requests
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from api.admin import admin_required
from api.fechas import ahora
from models import db, ActividadUsuario


@admin_required
def consultar_dni(dni):
    if not re.fullmatch(r'[0-9]{8}', dni):
        return jsonify(error='DNI inválido'), 400
    token = os.getenv('DNI_API_TOKEN', '').strip()
    if not token:
        return jsonify(error='La consulta de DNI no está disponible.'), 503
    uid = int(get_jwt_identity())
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(db.text('SELECT pg_advisory_xact_lock(:clave)'), {'clave': 72600000 + uid})
    consultas = ActividadUsuario.query.filter(ActividadUsuario.id_usuario == uid,
        ActividadUsuario.accion == 'Consulta DNI', ActividadUsuario.fecha >= ahora() - timedelta(minutes=1)).count()
    if consultas >= 10:
        return jsonify(error='Alcanzaste el límite de consultas. Intenta en un minuto.'), 429
    db.session.add(ActividadUsuario(id_usuario=uid, accion='Consulta DNI', fecha=ahora()))
    db.session.commit()
    try:
        respuesta = requests.get(f'https://dniruc.apisperu.com/api/v1/dni/{dni}', params={'token': token}, timeout=10)
        cuerpo = respuesta.json()
        if respuesta.status_code != 200 or cuerpo.get('success') is False:
            return jsonify(error='No se pudo obtener el DNI del proveedor.'), 502
        return jsonify(cuerpo)
    except (requests.RequestException, ValueError):
        return jsonify(error='El servicio de consulta no respondió correctamente.'), 502
