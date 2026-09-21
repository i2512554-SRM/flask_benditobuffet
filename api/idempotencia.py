import uuid


def normalizar_clave(data):
    valor = (data or {}).get('clave_operacion')
    if valor in (None, ''):
        return None
    try:
        return str(uuid.UUID(str(valor)))
    except (ValueError, TypeError, AttributeError):
        raise ValueError('Identificador de operación no válido')
