from datetime import datetime, time, timedelta, timezone

LIMA = timezone(timedelta(hours=-5))


def ahora():
    return datetime.now(timezone.utc)


def utc(valor):
    return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor.astimezone(timezone.utc)


def limites_dia(fecha=None):
    fecha = fecha or ahora().astimezone(LIMA).date()
    inicio = datetime.combine(fecha, time.min, LIMA)
    return inicio.astimezone(timezone.utc), (inicio + timedelta(days=1)).astimezone(timezone.utc)


def periodo_financiero(periodo, fecha):
    inicio, _ = limites_dia(fecha)
    local = inicio.astimezone(LIMA)
    if periodo == 'dia':
        fin = local + timedelta(days=1)
        paso = timedelta(hours=1)
    elif periodo == 'semana':
        local -= timedelta(days=local.weekday())
        fin = local + timedelta(days=7)
        paso = timedelta(days=1)
    elif periodo == 'mes':
        local = local.replace(day=1)
        fin = (local.replace(day=28) + timedelta(days=4)).replace(day=1)
        paso = timedelta(days=1)
    elif periodo == 'anio':
        local = local.replace(month=1, day=1)
        fin = local.replace(year=local.year + 1)
        paso = None
    else:
        raise ValueError('Periodo no válido')
    puntos = []
    cursor = local
    while cursor < fin:
        siguiente = cursor + paso if paso else (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
        etiqueta = cursor.strftime('%H:%M' if periodo == 'dia' else '%m/%Y' if periodo == 'anio' else '%d/%m')
        puntos.append((etiqueta, cursor.astimezone(timezone.utc), siguiente.astimezone(timezone.utc)))
        cursor = siguiente
    return local.astimezone(timezone.utc), fin.astimezone(timezone.utc), puntos
