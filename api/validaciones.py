import math
import re
from decimal import Decimal, InvalidOperation


def validar_personal(data, crear=False):
    if not isinstance(data, dict):
        return 'Los datos del empleado no son válidos.'
    if (crear or 'dni' in data) and not re.fullmatch(r'[0-9]{8}', str(data.get('dni') or '')):
        return 'El DNI debe contener exactamente 8 números.'
    for campo in ('nombres', 'apellido'):
        if crear or campo in data:
            recibido = data.get(campo) or ''
            if not isinstance(recibido, str):
                return 'Nombres y apellidos deben contener letras, sin números.'
            valor = recibido.strip()
            if not valor or len(valor) > 100 or not all(c.isalpha() or c in " '-" for c in valor) or not any(c.isalpha() for c in valor):
                return 'Nombres y apellidos deben contener letras, sin números.'
    correo = data.get('correo')
    if 'correo' in data:
        if correo in (None, ''):
            if not crear:
                return 'El correo no es válido.'
        elif not isinstance(correo, str) or len(correo.strip()) > 150 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', correo.strip()):
            return 'El correo no es válido.'
    usuario = data.get('usuario')
    if usuario and (not isinstance(usuario, str) or not usuario.strip() or len(usuario.strip()) > 50):
        return 'El usuario admite hasta 50 caracteres.'
    if data.get('telefono') and not re.fullmatch(r'[0-9]{9}', str(data['telefono'])):
        return 'El teléfono debe contener 9 números.'
    if 'turno' in data:
        turnos = data['turno'] or []
        if isinstance(turnos, str):
            turnos = [t.strip() for t in turnos.split(',') if t.strip()]
        if not isinstance(turnos, list) or any(t not in ('Tarde', 'Noche') for t in turnos):
            return 'Los turnos disponibles son Tarde y Noche.'
    if crear or data.get('clave'):
        clave = data.get('clave')
        if not isinstance(clave, str) or len(clave) < 8 or len(clave.encode('utf-8')) > 72:
            return 'La contraseña es obligatoria: mínimo 8 caracteres y máximo 72 bytes.'
    return None


def numero(valor, minimo=0):
    resultado = float(valor)
    if not math.isfinite(resultado) or resultado < minimo:
        raise ValueError('Número fuera de rango')
    return resultado


def cantidad_decimal(valor, minimo=0, existente=False):
    try:
        cantidad = Decimal(str(valor))
        if not cantidad.is_finite() or cantidad < Decimal(str(minimo)) or cantidad > Decimal('999999999.999'):
            raise ValueError('Cantidad fuera de rango')
        redondeado = cantidad.quantize(Decimal('.001'))
        if not existente and redondeado != cantidad:
            raise ValueError('La cantidad admite hasta tres decimales')
        return redondeado
    except (InvalidOperation, TypeError):
        raise ValueError('Cantidad no válida')
