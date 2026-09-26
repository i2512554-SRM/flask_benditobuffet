from datetime import date, timedelta
from bisect import bisect_left, bisect_right
from decimal import Decimal

from flask import Blueprint, request, jsonify

from bd import db
from models import (Usuario, Producto, InventarioMovimiento, SueldoSemanal, DescuentoSemanal,
                    CierreCaja, TransaccionCaja, Categoria)
from api.fechas import ahora, utc, LIMA, periodo_financiero, limites_dia
from api.caja import _movimientos, _totales, _prefijos_movimientos, _totales_intervalo
from api.roles import ADMIN, requiere_roles
from schemas.indicadores import kpis_schema

indicadores_bp = Blueprint('indicadores', __name__)

VENTANA_DIAS = 30
UMBRAL_COBERTURA_DIAS = 7
UMBRAL_MERMA_PCT = 10
UMBRAL_COSTO_LABORAL_PCT = 45
UMBRAL_INMOVILIZADO_PCT = 30
PALABRAS_MERMA = ('merma', 'deterioro', 'vencid', 'dañ', 'desperdicio', 'faltante', 'caduc', 'avaria', 'robo')


_permitido = requiere_roles(ADMIN, mensaje='Acceso restringido a indicadores')


def _costo_unidad(producto):
    if producto.costo is not None:
        return float(producto.costo), False
    return None, True


def _salidas_rango(inicio, fin):
    return (InventarioMovimiento.query
            .filter(InventarioMovimiento.tipo == 'Salida',
                    InventarioMovimiento.id_compra.is_(None),
                    InventarioMovimiento.fecha >= inicio,
                    InventarioMovimiento.fecha < fin)
            .all())


def _prefijos_caja(inicio, fin):
    return _prefijos_movimientos(_movimientos(inicio, fin)
                                 .order_by(TransaccionCaja.fecha, TransaccionCaja.id_transaccion).all())


class _Datos:
    def __init__(self, inicio_salidas, fin_salidas):
        self.productos = {int(p.id_producto): p for p in Producto.query.all()}
        self.salidas = sorted(_salidas_rango(inicio_salidas, fin_salidas), key=lambda s: utc(s.fecha))
        self._fechas = [utc(s.fecha) for s in self.salidas]

    def salidas_entre(self, inicio, fin):
        return self.salidas[bisect_left(self._fechas, utc(inicio)):bisect_left(self._fechas, utc(fin))]


DESCRIPCIONES = {
    'KPI-01': 'De cada S/ 100 que se cobran, lo que queda como ganancia después de restar los gastos del periodo.',
    'KPI-02': 'Cuánto crecieron o cayeron las ventas con respecto al periodo anterior.',
    'KPI-03': 'Días que alcanza el stock actual al ritmo de consumo registrado recientemente.',
    'KPI-04': 'Porcentaje del valor de las salidas de inventario que se pierde por merma, vencimiento o deterioro.',
    'KPI-05': 'Porcentaje de los cobros que se destina a sueldos del personal. Cuanto menor, más eficiente.',
    'KPI-06': 'Aproximación de lo que queda por cada sol vendido después de restar el costo de los insumos usados.',
    'KPI-07': 'Cuánto varía el efectivo contado en caja frente a lo esperado al momento de cerrar. Cerca de 0% es lo ideal.',
    'KPI-08': 'Porcentaje del valor del inventario que no ha tenido movimiento en los últimos días. Alto indica capital "atado" sin uso.',
}


def _kpi(codigo, nombre, valor, unidad, detalle=None, alerta=None, nota=None, estimado=False,
         variacion=None, tendencia=None, comparacion=None, serie=None):
    return {
        'codigo': codigo,
        'nombre': nombre,
        'descripcion': DESCRIPCIONES.get(codigo, ''),
        'valor': round(valor, 2) if isinstance(valor, (int, float)) else None,
        'unidad': unidad,
        'alerta': alerta,
        'nota': nota,
        'estimado': bool(estimado),
        'detalle': detalle or {},
        'variacion': round(variacion, 2) if isinstance(variacion, (int, float)) else None,
        'tendencia': tendencia or 'sin_base',
        'comparacion': comparacion or {},
        'serie': serie or [],
    }


def _tendencia(valor, variacion):
    if valor is None:
        return 'sin_datos'
    if variacion is None:
        return 'sin_base'
    if variacion > 0.05:
        return 'sube'
    if variacion < -0.05:
        return 'baja'
    return 'estable'


def _serie_financiera(puntos, prefijos):
    serie = []
    for etiqueta, b_inicio, b_fin in puntos:
        t = _totales_intervalo(prefijos, b_inicio, b_fin)
        margen = 100 * (t['ventas'] - t['gastos']) / t['ventas'] if t['ventas'] > 0 else None
        serie.append({
            'etiqueta': etiqueta,
            'ventas': round(t['ventas'], 2),
            'gastos': round(t['gastos'], 2),
            'neto': round(t['neto'], 2),
            'valor': round(margen, 2) if margen is not None else None,
        })
    return serie


def _kpi_01_02(inicio, fin, prev_inicio, prev_fin, puntos, prefijos):
    actuales = _totales(_movimientos(inicio, fin).all())
    previos = _totales(_movimientos(prev_inicio, prev_fin).all())
    ventas, gastos = actuales['ventas'], actuales['gastos']
    ventas_previas, gastos_previos = previos['ventas'], previos['gastos']

    margen = None
    if ventas > 0:
        margen = 100 * (ventas - gastos) / ventas
    margen_anterior = None
    if ventas_previas > 0:
        margen_anterior = 100 * (ventas_previas - gastos_previos) / ventas_previas

    variacion_margen = None
    if margen is not None and margen_anterior is not None:
        variacion_margen = margen - margen_anterior
    alerta_margen = 'Margen negativo: los egresos superan los cobros' if margen is not None and margen < 0 else None

    financiera = _serie_financiera(puntos, prefijos)
    kpi_01 = _kpi(
        'KPI-01', 'Margen operativo de caja', margen, '%',
        detalle={'cobros': round(ventas, 2), 'egresos': round(gastos, 2),
                 'neto': round(ventas - gastos, 2),
                 'margen_anterior': round(margen_anterior, 2) if margen_anterior is not None else None},
        alerta=alerta_margen,
        variacion=variacion_margen,
        tendencia=_tendencia(margen, variacion_margen),
        comparacion={'margen_anterior': margen_anterior,
                     'ventas_anterior': round(ventas_previas, 2),
                     'egresos_anterior': round(gastos_previos, 2)},
        serie=[{'etiqueta': x['etiqueta'], 'valor': x['valor'],
                'ingresos': x['ventas'], 'egresos': x['gastos']} for x in financiera]
    )

    variacion_ventas = None
    if ventas_previas > 0:
        variacion_ventas = 100 * (ventas - ventas_previas) / ventas_previas
    alerta_var = None
    if variacion_ventas is None:
        alerta_var = 'Sin base de comparación con el periodo anterior'
    elif variacion_ventas < 0:
        alerta_var = 'Descenso de ventas respecto al periodo anterior'

    kpi_02 = _kpi(
        'KPI-02', 'Variación de ventas', variacion_ventas, '%',
        detalle={'ventas_periodo': round(ventas, 2),
                 'ventas_anterior': round(ventas_previas, 2)},
        alerta=alerta_var,
        variacion=variacion_ventas,
        tendencia=_tendencia(variacion_ventas, variacion_ventas),
        comparacion={'ventas_anterior': round(ventas_previas, 2)},
        serie=[{'etiqueta': x['etiqueta'], 'valor': x['ventas']} for x in financiera]
    )
    return kpi_01, kpi_02, ventas, gastos, ventas_previas


def _kpi_03(corte, datos):
    inicio = corte - timedelta(days=VENTANA_DIAS)
    salidas = datos.salidas_entre(inicio, corte)
    dias_operativos = len({utc(s.fecha).astimezone(LIMA).date() for s in salidas}) or 1

    consumo = {}
    for s in salidas:
        clave = int(s.id_producto)
        consumo[clave] = consumo.get(clave, 0) + abs(float(s.cantidad))

    suma_coberturas = 0.0
    bajo_umbral, sin_consumo = 0, 0
    productos_con_consumo = 0
    criticos = []

    productos = [p for p in datos.productos.values()
                 if p.estado and utc(p.fecha_registro) < utc(corte)]
    for producto in productos:
        stock = float(producto.stock or 0)
        salidas_producto = consumo.get(int(producto.id_producto), 0)
        if salidas_producto <= 0:
            sin_consumo += 1
            continue
        ritmo = salidas_producto / dias_operativos
        cobertura = stock / ritmo if ritmo > 0 else None
        if cobertura is None:
            continue
        productos_con_consumo += 1
        suma_coberturas += cobertura
        criticos.append({'etiqueta': producto.nombre, 'valor': round(cobertura, 2)})
        if cobertura <= UMBRAL_COBERTURA_DIAS:
            bajo_umbral += 1

    criticos.sort(key=lambda x: x['valor'])
    valor = suma_coberturas / productos_con_consumo if productos_con_consumo else None
    alerta = None
    if valor is None:
        alerta = 'Sin consumo registrado en la ventana reciente'
    elif valor <= UMBRAL_COBERTURA_DIAS:
        alerta = 'Cobertura baja: reposición próxima'

    return _kpi(
        'KPI-03', 'Cobertura de inventario', valor, 'días',
        detalle={'dias_operativos': dias_operativos, 'ventana_dias': VENTANA_DIAS,
                 'productos_con_consumo': productos_con_consumo,
                 'productos_bajo_umbral': bajo_umbral, 'productos_sin_consumo': sin_consumo,
                 'corte_datos': corte.astimezone(LIMA).date().isoformat()},
        alerta=alerta,
        nota='Usa el stock actual y el consumo registrado antes de la fecha de corte.',
        estimado=True,
        tendencia='sin_base',
        serie=criticos[:10]
    )


def _merma_periodo(inicio, fin, datos):
    salidas = datos.salidas_entre(inicio, fin)
    productos = datos.productos

    valor_merma, valor_salidas, registros_merma, salidas_sin_costo = 0.0, 0.0, 0, 0
    por_mes = {}

    for salida in salidas:
        producto = productos.get(int(salida.id_producto))
        if producto is None or producto.costo is None:
            salidas_sin_costo += 1
            continue
        costo = float(producto.costo)
        monto = abs(float(salida.cantidad)) * costo
        valor_salidas += monto
        motivo = (salida.motivo or '').lower()
        es_merma = any(palabra in motivo for palabra in PALABRAS_MERMA)
        if es_merma:
            valor_merma += monto
            registros_merma += 1
        clave_mes = utc(salida.fecha).astimezone(LIMA).strftime('%Y-%m')
        bucket = por_mes.setdefault(clave_mes, {'costo_merma': 0.0, 'costo_salidas': 0.0})
        bucket['costo_merma'] += monto if es_merma else 0
        bucket['costo_salidas'] += monto

    porcentaje = 100 * valor_merma / valor_salidas if valor_salidas > 0 and not salidas_sin_costo else None
    serie = [{'etiqueta': clave, 'valor': round(100 * b['costo_merma'] / b['costo_salidas'], 2)
                   if b['costo_salidas'] > 0 else None}
             for clave, b in sorted(por_mes.items())]
    return {'valor_merma': valor_merma, 'valor_salidas': valor_salidas,
            'registros_merma': registros_merma, 'salidas_sin_costo': salidas_sin_costo,
            'porcentaje': porcentaje, 'serie': serie}


def _kpi_04(inicio, fin, prev_inicio, prev_fin, datos):
    actual = _merma_periodo(inicio, fin, datos)
    anterior = _merma_periodo(prev_inicio, prev_fin, datos)

    variacion = None
    if actual['porcentaje'] is not None and anterior['porcentaje'] is not None:
        variacion = actual['porcentaje'] - anterior['porcentaje']
    alerta = None
    if actual['salidas_sin_costo']:
        alerta = 'Falta registrar el costo de productos con salidas en el periodo'
    elif actual['porcentaje'] is None:
        alerta = 'Sin salidas de inventario en el periodo'
    elif actual['porcentaje'] > UMBRAL_MERMA_PCT:
        alerta = 'Merma alta: revisar pérdidas del periodo'

    return _kpi(
        'KPI-04', 'Tasa de merma', actual['porcentaje'], '%',
        detalle={'valor_merma': round(actual['valor_merma'], 2),
                 'valor_salidas': round(actual['valor_salidas'], 2),
                 'registros_merma': actual['registros_merma'],
                 'salidas_sin_costo': actual['salidas_sin_costo']},
        alerta=alerta,
        nota='Clasifica la merma por el motivo de la salida y usa el costo promedio ponderado actual; excluye reversas de compras.',
        estimado=True,
        variacion=variacion,
        tendencia=_tendencia(actual['porcentaje'], variacion),
        comparacion={'merma_anterior': round(anterior['porcentaje'], 2) if anterior['porcentaje'] is not None else None},
        serie=actual['serie']
    )


def _costo_laboral_periodo(inicio, fin):
    empleados = Usuario.query.filter(Usuario.estado.is_(True), Usuario.id_rol != ADMIN).all()
    ids = [e.id_usuario for e in empleados]
    tarifas = (SueldoSemanal.query.filter(
        SueldoSemanal.id_usuario.in_(ids),
        SueldoSemanal.desde < fin.astimezone(LIMA).date()
    ).order_by(SueldoSemanal.id_usuario, SueldoSemanal.desde).all()) if ids else []
    tarifas_por_usuario = {}
    for tarifa in tarifas:
        tarifas_por_usuario.setdefault(tarifa.id_usuario, []).append(tarifa)

    inicio_local = inicio.astimezone(LIMA)
    fin_local = fin.astimezone(LIMA)
    lunes = inicio_local.date() - timedelta(days=inicio_local.weekday())
    ultimo_lunes = (fin_local - timedelta(microseconds=1)).date()
    ultimo_lunes -= timedelta(days=ultimo_lunes.weekday())
    descuentos = DescuentoSemanal.query.filter(
        DescuentoSemanal.id_usuario.in_(ids),
        DescuentoSemanal.semana >= lunes,
        DescuentoSemanal.semana <= ultimo_lunes,
        DescuentoSemanal.anulado.is_(False)
    ).all() if ids else []
    descuentos_por_semana = {}
    for descuento in descuentos:
        clave = (descuento.id_usuario, descuento.semana)
        descuentos_por_semana[clave] = descuentos_por_semana.get(clave, 0.0) + float(descuento.monto)

    def inicio_de(dia):
        return inicio_local.replace(year=dia.year, month=dia.month, day=dia.day,
                                    hour=0, minute=0, second=0, microsecond=0)

    prefijos = _prefijos_caja(inicio_de(lunes), inicio_de(ultimo_lunes) + timedelta(days=7)) if lunes <= ultimo_lunes else None
    costo_laboral = 0.0
    semanas_calculadas = 0
    empleados_sin_sueldo = set()
    serie = []
    semana = lunes
    while semana <= ultimo_lunes:
        semana_inicio = inicio_de(semana)
        semana_fin = semana_inicio + timedelta(days=7)
        solape_inicio = max(inicio_local, semana_inicio)
        solape_fin = min(fin_local, semana_fin)
        proporcion = max(0.0, (solape_fin - solape_inicio).total_seconds() / (7 * 86400))
        if proporcion:
            ventas_semana = _totales_intervalo(prefijos, semana_inicio, semana_fin)['ventas']
            costo_semana = 0.0
            for empleado in empleados:
                historial = tarifas_por_usuario.get(empleado.id_usuario, [])
                vigentes = [t for t in historial if t.desde <= semana]
                if not vigentes:
                    if not historial:
                        empleados_sin_sueldo.add(empleado.id_usuario)
                    continue
                base = float(vigentes[-1].monto)
                deduccion = descuentos_por_semana.get((empleado.id_usuario, semana), 0.0)
                costo_semana += max(base - deduccion, 0.0) * proporcion
                semanas_calculadas += 1
            costo_laboral += costo_semana
            serie.append({
                'etiqueta': semana.strftime('%d/%m'),
                'valor': round(100 * costo_semana / ventas_semana, 2) if ventas_semana > 0 else None,
            })
        semana += timedelta(days=7)

    return {'costo_laboral': costo_laboral, 'semanas_calculadas': semanas_calculadas,
            'empleados_sin_sueldo': empleados_sin_sueldo, 'serie': serie}


def _kpi_05(inicio, fin, ventas, prev_inicio, prev_fin, prev_ventas):
    actual = _costo_laboral_periodo(inicio, fin)
    anterior = _costo_laboral_periodo(prev_inicio, prev_fin)

    valor = 100 * actual['costo_laboral'] / ventas if ventas > 0 and actual['semanas_calculadas'] and not actual['empleados_sin_sueldo'] else None
    valor_anterior = 100 * anterior['costo_laboral'] / prev_ventas if prev_ventas > 0 and anterior['semanas_calculadas'] and not anterior['empleados_sin_sueldo'] else None
    variacion = None
    if valor is not None and valor_anterior is not None:
        variacion = valor - valor_anterior

    alerta = None
    if actual['empleados_sin_sueldo']:
        alerta = 'Hay empleados activos sin sueldo semanal configurado'
    elif not actual['semanas_calculadas']:
        alerta = 'No hay sueldos semanales vigentes en el periodo'
    elif valor is None:
        alerta = 'Sin ventas registradas en el periodo'
    elif valor > UMBRAL_COSTO_LABORAL_PCT:
        alerta = 'Costo laboral alto respecto a las ventas'

    return _kpi(
        'KPI-05', 'Costo laboral sobre ventas', valor, '%',
        detalle={'costo_laboral': round(actual['costo_laboral'], 2), 'ventas_netas': round(ventas, 2),
                 'semanas_empleado': actual['semanas_calculadas'],
                 'empleados_sin_sueldo': len(actual['empleados_sin_sueldo'])},
        alerta=alerta,
        nota='Prorratea el sueldo semanal vigente y sus descuentos por los días del periodo. Las semanas previas al primer sueldo registrado de cada empleado no suman costo. Los adelantos no reducen el costo laboral.',
        estimado=True,
        variacion=variacion,
        tendencia=_tendencia(valor, variacion),
        comparacion={'ratio_anterior': round(valor_anterior, 2) if valor_anterior is not None else None},
        serie=actual['serie']
    )


def _costo_vendido_periodo(inicio, fin, datos):
    costo_estimado = 0.0
    registros = 0
    salidas_sin_costo = 0
    costos = []
    for salida in datos.salidas_entre(inicio, fin):
        motivo = (salida.motivo or '').lower()
        if any(palabra in motivo for palabra in PALABRAS_MERMA):
            continue
        producto = datos.productos.get(int(salida.id_producto))
        if producto is None or producto.costo is None:
            salidas_sin_costo += 1
            continue
        costo = abs(float(salida.cantidad)) * float(producto.costo)
        costo_estimado += costo
        costos.append((utc(salida.fecha), costo))
        registros += 1
    return {'costo': costo_estimado, 'registros': registros, 'salidas_sin_costo': salidas_sin_costo,
            'costos': costos}


def _kpi_06(inicio, fin, ventas, prev_inicio, prev_fin, prev_ventas, puntos, prefijos, datos):
    actual = _costo_vendido_periodo(inicio, fin, datos)
    anterior = _costo_vendido_periodo(prev_inicio, prev_fin, datos)

    valor = 100 * (ventas - actual['costo']) / ventas if ventas > 0 and actual['registros'] and not actual['salidas_sin_costo'] else None
    valor_anterior = 100 * (prev_ventas - anterior['costo']) / prev_ventas if prev_ventas > 0 and anterior['registros'] and not anterior['salidas_sin_costo'] else None
    variacion = None
    if valor is not None and valor_anterior is not None:
        variacion = valor - valor_anterior

    alerta = None
    if ventas <= 0:
        alerta = 'Sin ventas registradas en el periodo'
    elif actual['salidas_sin_costo']:
        alerta = 'Falta registrar el costo de productos con salidas en el periodo'
    elif not actual['registros']:
        alerta = 'No hay salidas operativas para estimar el costo vendido'

    inicios = [utc(b_inicio) for _, b_inicio, _ in puntos]
    costo_por_bucket = {}
    for fecha, costo in actual['costos']:
        indice = bisect_right(inicios, fecha) - 1
        if indice >= 0 and fecha < utc(puntos[indice][2]):
            costo_por_bucket[indice] = costo_por_bucket.get(indice, 0.0) + costo
    serie = []
    for indice, (etiqueta, b_inicio, b_fin) in enumerate(puntos):
        ventas_bucket = _totales_intervalo(prefijos, b_inicio, b_fin)['ventas']
        costo_bucket = costo_por_bucket.get(indice, 0.0)
        margen = 100 * (ventas_bucket - costo_bucket) / ventas_bucket if ventas_bucket > 0 else None
        serie.append({'etiqueta': etiqueta, 'valor': round(margen, 2) if margen is not None else None})

    return _kpi(
        'KPI-06', 'Margen bruto estimado', valor, '%',
        detalle={'ventas_netas': round(ventas, 2), 'costo_directo_estimado': round(actual['costo'], 2),
                 'salidas_consideradas': actual['registros'],
                 'salidas_sin_costo': actual['salidas_sin_costo']},
        alerta=alerta,
        nota='Aproximación con salidas de inventario y costo promedio ponderado actual. Falta registrar el detalle y costo histórico de cada venta.',
        estimado=True,
        variacion=variacion,
        tendencia=_tendencia(valor, variacion),
        comparacion={'margen_anterior': round(valor_anterior, 2) if valor_anterior is not None else None},
        serie=serie
    )


def _prefijos_efectivo(movimientos):
    fechas, acumulado = [], [Decimal(0)]
    for movimiento in movimientos:
        fechas.append(utc(movimiento.fecha))
        monto = Decimal(str(movimiento.monto))
        acumulado.append(acumulado[-1] + (monto if movimiento.tipo == 'Venta' else -monto))
    return fechas, acumulado


def _efectivo_intervalo(prefijos, inicio, fin):
    fechas, acumulado = prefijos
    izquierda, derecha = bisect_left(fechas, utc(inicio)), bisect_left(fechas, utc(fin))
    return float((acumulado[derecha] - acumulado[izquierda]).quantize(Decimal('.01')))


def _diferencia_cierre_periodo(inicio, fin):
    fecha_cierre = db.func.coalesce(CierreCaja.fecha_cierre, CierreCaja.fecha)
    orden = (CierreCaja.query
             .filter(CierreCaja.estado == 'cerrada', fecha_cierre >= inicio, fecha_cierre < fin)
             .order_by(CierreCaja.fecha)
             .all())
    vacio = {'cierres_con_conteo': 0, 'cierres_sin_conteo': 0, 'contado_total': 0.0,
             'esperado_total': 0.0, 'sobrante_total': 0.0, 'faltante_total': 0.0,
             'diferencia_global': 0.0, 'diferencia_relativa': None, 'serie': []}
    if not orden:
        return vacio

    ventanas = []
    for indice, cierre in enumerate(orden):
        fin_ventana = utc(cierre.fecha_cierre) if cierre.fecha_cierre else utc(ahora())
        if indice + 1 < len(orden):
            fin_ventana = min(fin_ventana, utc(orden[indice + 1].fecha))
        ventanas.append((cierre, utc(cierre.fecha), min(fin_ventana, utc(fin))))

    movimientos = (TransaccionCaja.query
                   .filter(TransaccionCaja.metodo_pago == 'Efectivo',
                           TransaccionCaja.fecha >= min(v[1] for v in ventanas),
                           TransaccionCaja.fecha < max(v[2] for v in ventanas))
                   .order_by(TransaccionCaja.fecha)
                   .all())
    prefijos = _prefijos_efectivo(movimientos)

    sin_conteo = sum(1 for c in orden if c.efectivo_contado is None)
    con_conteo = len(orden) - sin_conteo
    contado_total = esperado_total = sobrante_total = faltante_total = diferencia_global = 0.0
    relativas = []
    serie = []

    for cierre, apertura, fin_ventana in ventanas:
        esperado = float(cierre.monto_inicial or 0) + _efectivo_intervalo(prefijos, apertura, fin_ventana)
        contado = float(cierre.efectivo_contado) if cierre.efectivo_contado is not None else None
        diferencia = contado - esperado if contado is not None else None
        relativa = 100 * diferencia / esperado if contado is not None and esperado else None
        serie.append({
            'etiqueta': apertura.astimezone(LIMA).strftime('%d/%m/%Y'),
            'valor': round(relativa, 2) if relativa is not None else None,
            'contado': round(contado, 2) if contado is not None else None,
            'esperado': round(esperado, 2),
            'diferencia_abs': round(diferencia, 2) if diferencia is not None else None,
        })
        if contado is None or relativa is None:
            continue
        contado_total += contado
        esperado_total += esperado
        diferencia_global += diferencia
        relativas.append(relativa)
        if diferencia > 0:
            sobrante_total += diferencia
        elif diferencia < 0:
            faltante_total += -diferencia

    return {'cierres_con_conteo': con_conteo, 'cierres_sin_conteo': sin_conteo,
            'contado_total': contado_total, 'esperado_total': esperado_total,
            'sobrante_total': sobrante_total, 'faltante_total': faltante_total,
            'diferencia_global': diferencia_global,
            'diferencia_relativa': sum(relativas) / len(relativas) if relativas else None,
            'serie': serie}


def _kpi_07(inicio, fin, prev_inicio, prev_fin):
    actual = _diferencia_cierre_periodo(inicio, fin)
    anterior = _diferencia_cierre_periodo(prev_inicio, prev_fin)

    nota = ('Promedio de la diferencia relativa por cierre: '
            '(contado - esperado) / esperado × 100. Esperado = monto inicial + '
            'ventas en efectivo - gastos en efectivo de la sesión.')
    if not actual['cierres_con_conteo'] and not actual['cierres_sin_conteo']:
        return _kpi('KPI-07', 'Diferencia de cierre de caja', None, '%',
                    detalle={'cierres_con_conteo': 0, 'cierres_sin_conteo': 0},
                    alerta='Sin cierres de caja en el periodo', nota=nota,
                    tendencia='sin_base', serie=[])
    if actual['cierres_con_conteo'] == 0:
        return _kpi('KPI-07', 'Diferencia de cierre de caja', None, '%',
                    detalle={'cierres_con_conteo': 0, 'cierres_sin_conteo': actual['cierres_sin_conteo']},
                    alerta='Falta registrar el efectivo contado en los cierres del periodo', nota=nota,
                    tendencia='sin_base', serie=actual['serie'])

    variacion = None
    if actual['diferencia_relativa'] is not None and anterior['diferencia_relativa'] is not None:
        variacion = actual['diferencia_relativa'] - anterior['diferencia_relativa']

    alerta = None
    if actual['faltante_total'] > 0:
        alerta = f'Faltante de efectivo por revisar (S/ {round(actual["faltante_total"], 2)})'
    if actual['cierres_sin_conteo']:
        aviso = f'{actual["cierres_sin_conteo"]} cierre(s) sin registrar el efectivo contado'
        alerta = f'{alerta} · {aviso}' if alerta else aviso

    return _kpi(
        'KPI-07', 'Diferencia de cierre de caja', actual['diferencia_relativa'], '%',
        detalle={'cierres_con_conteo': actual['cierres_con_conteo'],
                 'cierres_sin_conteo': actual['cierres_sin_conteo'],
                 'contado_total': round(actual['contado_total'], 2),
                 'esperado_total': round(actual['esperado_total'], 2),
                 'sobrante_total': round(actual['sobrante_total'], 2),
                 'faltante_total': round(actual['faltante_total'], 2),
                 'diferencia_global': round(actual['diferencia_global'], 2)},
        alerta=alerta,
        nota=nota,
        variacion=variacion,
        tendencia=_tendencia(actual['diferencia_relativa'], variacion),
        comparacion={'diferencia_relativa_anterior': round(anterior['diferencia_relativa'], 2)
                     if anterior['diferencia_relativa'] is not None else None},
        serie=actual['serie']
    )


def _kpi_08(corte, datos):
    inicio = corte - timedelta(days=VENTANA_DIAS)
    salidas = datos.salidas_entre(inicio, corte)
    en_movimiento = {int(s.id_producto) for s in salidas}

    valor_total, valor_inmovilizado = 0.0, 0.0
    productos_sin_movimiento = 0
    productos_sin_costo = 0
    categorias = {c.id_categoria: (c.nombre or 'Sin categoría') for c in Categoria.query.all()}
    por_categoria = {}

    productos = [p for p in datos.productos.values()
                 if p.estado and float(p.stock or 0) > 0 and utc(p.fecha_registro) < utc(corte)]
    for producto in productos:
        costo, sin_costo = _costo_unidad(producto)
        if sin_costo:
            productos_sin_costo += 1
            continue
        valor_producto = float(producto.stock or 0) * costo
        valor_total += valor_producto
        nombre_cat = categorias.get(producto.id_categoria, 'Sin categoría')
        bucket = por_categoria.setdefault(nombre_cat, {'valor': 0.0, 'inmovilizado': 0.0})
        bucket['valor'] += valor_producto
        if int(producto.id_producto) not in en_movimiento:
            valor_inmovilizado += valor_producto
            productos_sin_movimiento += 1
            bucket['inmovilizado'] += valor_producto

    valor = 100 * valor_inmovilizado / valor_total if valor_total > 0 and not productos_sin_costo else None
    alerta = None
    if productos_sin_costo:
        alerta = 'Falta registrar el costo de productos con stock'
    elif valor is None:
        alerta = 'Sin valor de inventario activo'
    elif valor > UMBRAL_INMOVILIZADO_PCT:
        alerta = 'Alto capital sin movimiento en la ventana reciente'

    serie = [{'etiqueta': nombre, 'valor': round(b['inmovilizado'], 2)}
             for nombre, b in sorted(por_categoria.items(), key=lambda x: -x[1]['inmovilizado'])]

    return _kpi(
        'KPI-08', 'Capital inmovilizado', valor, '%',
        detalle={'valor_inmovilizado': round(valor_inmovilizado, 2), 'valor_total': round(valor_total, 2),
                 'productos_sin_movimiento': productos_sin_movimiento,
                 'productos_sin_costo': productos_sin_costo, 'ventana_dias': VENTANA_DIAS,
                 'corte_datos': corte.astimezone(LIMA).date().isoformat()},
        alerta=alerta,
        nota='Usa el stock y el costo promedio ponderado actuales con los movimientos anteriores a la fecha de corte.',
        estimado=True,
        tendencia='sin_base',
        comparacion={'valor_total': round(valor_total, 2),
                     'valor_inmovilizado': round(valor_inmovilizado, 2)},
        serie=serie
    )


@indicadores_bp.route('/indicadores', methods=['GET'])
@_permitido
def get_indicadores():
    periodo = request.args.get('periodo', 'mes').strip().lower()
    fecha_param = request.args.get('fecha')
    inicio_param = request.args.get('inicio')
    fin_param = request.args.get('fin')
    try:
        if inicio_param and fin_param:
            d_inicio = date.fromisoformat(inicio_param)
            d_fin = date.fromisoformat(fin_param)
            if d_fin < d_inicio:
                raise ValueError('Rango no válido')
            if (d_fin - d_inicio).days > 400:
                raise ValueError('Rango máximo 400 días')
            b_inicio, b_fin = limites_dia(d_inicio)
            b_fin_provisional, _ = limites_dia(d_fin + timedelta(days=1))
            inicio, fin = b_inicio, b_fin_provisional
            prev_fin, prev_inicio = b_inicio, b_inicio - (fin - inicio)
            duracion = fin - inicio
            puntos = []
            cursor = inicio
            while cursor < fin:
                siguiente = cursor + timedelta(days=1)
                etiqueta = (cursor.astimezone(LIMA).strftime('%d/%m/%Y') if duracion.days > 60
                            else cursor.astimezone(LIMA).strftime('%d/%m'))
                puntos.append((etiqueta, cursor, siguiente))
                cursor = siguiente
            fecha = d_fin
            periodo = 'rango'
        else:
            if bool(inicio_param) != bool(fin_param):
                raise ValueError('Rango incompleto')
            fecha = date.fromisoformat(fecha_param) if fecha_param else ahora().astimezone(LIMA).date()
            inicio, fin, puntos = periodo_financiero(periodo, fecha)
            referencia_anterior = inicio.astimezone(LIMA).date() - timedelta(days=1)
            prev_inicio, prev_fin, _ = periodo_financiero(periodo, referencia_anterior)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Fecha o periodo no válido'}), 400

    corte = min(fin, max(inicio, ahora()))
    ventana = corte - timedelta(days=VENTANA_DIAS)
    datos = _Datos(min(prev_inicio, ventana), max(fin, corte))
    prefijos = _prefijos_caja(puntos[0][1], puntos[-1][2]) if puntos else _prefijos_movimientos([])

    kpi_01, kpi_02, ventas, _, prev_ventas = _kpi_01_02(inicio, fin, prev_inicio, prev_fin, puntos, prefijos)
    kpis = [
        kpi_01,
        kpi_02,
        _kpi_03(corte, datos),
        _kpi_04(inicio, fin, prev_inicio, prev_fin, datos),
        _kpi_05(inicio, corte, ventas, prev_inicio, prev_fin, prev_ventas),
        _kpi_06(inicio, fin, ventas, prev_inicio, prev_fin, prev_ventas, puntos, prefijos, datos),
        _kpi_07(inicio, fin, prev_inicio, prev_fin),
        _kpi_08(corte, datos),
    ]

    return jsonify({
        'success': True,
        'data': {
            'periodo': periodo,
            'fecha': fecha.isoformat(),
            'inicio': inicio.isoformat(),
            'fin': fin.isoformat(),
            'prev_inicio': prev_inicio.isoformat(),
            'prev_fin': prev_fin.isoformat(),
            'corte': corte.isoformat(),
            'kpis': kpis_schema.dump(kpis),
        }
    })