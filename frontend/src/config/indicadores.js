import { links } from '../router/links'

const soles = (valor) => 'S/ ' + Number(valor || 0).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const numero = (valor, decimales = 1) => Number(valor || 0).toLocaleString('es-PE', { maximumFractionDigits: decimales })
const porcentaje = (valor) => numero(valor) + '%'

const insumosCriticos = (k, limites) => {
  if (limites.atencion === k.limites?.atencion) return { cantidad: k.detalle?.productos_bajo_umbral ?? 0, alMenos: false }
  const serie = (k.serie || []).filter((fila) => fila.valor !== null && fila.valor !== undefined)
  const cantidad = serie.filter((fila) => fila.valor <= limites.atencion).length
  return { cantidad, alMenos: cantidad > 0 && cantidad === serie.length && serie.length >= 10 }
}

export const AREAS = [
  { id: 'ventas', titulo: 'Ventas y caja', icono: 'fa-solid fa-cash-register' },
  { id: 'cocina', titulo: 'Cocina e inventario', icono: 'fa-solid fa-kitchen-set' },
  { id: 'personal', titulo: 'Personal', icono: 'fa-solid fa-people-group' }
]

export const ESTADOS = {
  bien: { etiqueta: 'Bien', icono: 'fa-solid fa-circle-check', ollita: 'celebrando' },
  atencion: { etiqueta: 'Atención', icono: 'fa-solid fa-circle-exclamation', ollita: 'pensando' },
  revisar: { etiqueta: 'Revisar', icono: 'fa-solid fa-triangle-exclamation', ollita: 'preocupada' },
  sin_datos: { etiqueta: 'Sin datos', icono: 'fa-solid fa-circle-question', ollita: 'pensando' }
}

const INDICADORES = {
  'KPI-01': {
    nombre: 'Ganancia por cada S/ 100 vendidos',
    pregunta: '¿Cuánto me queda de lo que cobro?',
    area: 'ventas',
    icono: 'fa-solid fa-sack-dollar',
    formato: (v) => 'S/ ' + numero(v) + ' de cada S/ 100',
    calculo: (d) => `Cobraste ${soles(d.cobros)} y tuviste egresos por ${soles(d.egresos)}. Te quedan ${soles(d.neto)}.`,
    anterior: (k) => k.comparacion?.margen_anterior,
    formatoAnterior: (v) => porcentaje(v),
    acciones: {
      bien: 'Buen margen. Mantén el control de gastos y revisa qué días venden más para reforzarlos.',
      atencion: 'El margen es ajustado. Revisa los gastos más grandes del periodo en Caja → Movimientos.',
      revisar: 'Los gastos superan lo cobrado. Revisa los egresos del periodo y posterga gastos que no sean urgentes.',
      sin_datos: 'Aún no hay ventas registradas en el periodo.'
    },
    desglose: { titulo: 'Detalle por día', columnas: [['etiqueta', 'Periodo'], ['ingresos', 'Cobros', 'soles'], ['egresos', 'Egresos', 'soles'], ['valor', 'Margen', 'porcentaje']] }
  },
  'KPI-02': {
    nombre: '¿Vendimos más o menos que antes?',
    pregunta: 'Comparación con el mismo tramo del periodo anterior',
    area: 'ventas',
    icono: 'fa-solid fa-chart-line',
    formato: (v) => (v > 0 ? '+' : '') + porcentaje(v),
    formatoLimite: (v) => (v > 0 ? '+' : '') + porcentaje(v),
    calculo: (d) => `En este periodo vendiste ${soles(d.ventas_periodo)}; en el mismo tramo del periodo anterior, ${soles(d.ventas_anterior)}.`,
    anterior: (k) => k.comparacion?.ventas_anterior,
    formatoAnterior: (v) => soles(v),
    acciones: {
      bien: 'Las ventas crecen. Identifica qué funcionó (días, promociones, platos) para repetirlo.',
      atencion: 'Las ventas están estables o bajaron un poco. Revisa los días con menos ventas.',
      revisar: 'Las ventas cayeron bastante. Compara por día y considera promociones en los días flojos.',
      sin_datos: 'No hay ventas del periodo anterior para comparar.'
    },
    desglose: { titulo: 'Ventas por día', columnas: [['etiqueta', 'Periodo'], ['valor', 'Ventas', 'soles']] }
  },
  'KPI-03': {
    nombre: 'Días que alcanza la despensa',
    pregunta: 'Con el consumo reciente, ¿para cuántos días hay insumos?',
    area: 'cocina',
    icono: 'fa-solid fa-box-open',
    formato: (v) => numero(v) + ' días',
    formatoLimite: (v) => numero(v) + ' días',
    sufijoLimite: ' días',
    calculo: (d) => `Según el consumo de los últimos ${d.ventana_dias} días, ${d.productos_bajo_umbral} de ${d.productos_con_consumo} insumos ${d.productos_bajo_umbral === 1 ? 'alcanza' : 'alcanzan'} para ${numero(d.umbral_dias ?? 7)} días o menos. ${d.productos_sin_consumo} ${d.productos_sin_consumo === 1 ? 'no tuvo' : 'no tuvieron'} consumo.`,
    ajustarEstado: (estado, k, limites) => (estado === 'bien' && insumosCriticos(k, limites).cantidad > 0 ? 'atencion' : estado),
    motivoAjuste: (k, limites) => {
      const { cantidad, alMenos } = insumosCriticos(k, limites)
      const insumos = cantidad === 1 && !alMenos ? '1 insumo se acaba' : `${alMenos ? 'al menos ' : ''}${cantidad} insumos se acaban`
      return `Queda en «Atención» aunque cumple la meta, porque ${insumos} en ${numero(limites.atencion)} días o menos.`
    },
    acciones: {
      bien: 'La despensa está bien surtida.',
      atencion: 'Algunos insumos se acaban pronto. Revisa la tabla y planifica la próxima compra.',
      revisar: 'Hay insumos a punto de agotarse. Registra una compra para los primeros de la lista.',
      sin_datos: 'No hubo salidas de inventario recientes para calcular el consumo.'
    },
    desglose: {
      titulo: 'Insumos que se acaban primero',
      columnas: [['etiqueta', 'Insumo'], ['valor', 'Días que alcanza', 'dias']],
      accion: { etiqueta: 'Comprar', icono: 'fa-solid fa-cart-plus', ruta: (fila) => links.inventario.nuevaCompra(fila.id_producto), mostrar: (fila, kpi) => fila.id_producto && fila.valor <= (kpi.limites?.atencion ?? 7) }
    }
  },
  'KPI-04': {
    nombre: 'Insumos perdidos (merma)',
    pregunta: '¿Cuánto de lo que sale del almacén se pierde?',
    area: 'cocina',
    icono: 'fa-solid fa-trash-can',
    formato: (v) => porcentaje(v),
    calculo: (d) => `De ${soles(d.valor_salidas)} en salidas de inventario, se perdieron ${soles(d.valor_merma)} (${d.registros_merma} registros de merma).`,
    anterior: (k) => k.comparacion?.merma_anterior,
    formatoAnterior: (v) => porcentaje(v),
    acciones: {
      bien: 'La merma está controlada.',
      atencion: 'La merma está subiendo. Revisa fechas de vencimiento y cómo se almacenan los insumos.',
      revisar: 'Se pierde mucho inventario. Revisa los motivos de salida y ajusta las compras a lo que se consume.',
      sin_datos: 'No hubo salidas de inventario en el periodo, o faltan costos de productos.'
    },
    desglose: { titulo: 'Merma por mes', columnas: [['etiqueta', 'Mes'], ['valor', 'Merma', 'porcentaje']] }
  },
  'KPI-05': {
    nombre: 'Sueldos frente a ventas',
    pregunta: '¿Qué parte de lo que vendo se va en sueldos?',
    area: 'personal',
    icono: 'fa-solid fa-user-clock',
    formato: (v) => porcentaje(v),
    calculo: (d) => `Los sueldos del periodo suman ${soles(d.costo_laboral)} frente a ${soles(d.ventas_netas)} en ventas.`,
    anterior: (k) => k.comparacion?.ratio_anterior,
    formatoAnterior: (v) => porcentaje(v),
    acciones: {
      bien: 'El costo del personal está en un buen nivel.',
      atencion: 'Los sueldos pesan bastante. Revisa si los turnos coinciden con las horas de más venta.',
      revisar: 'Los sueldos se llevan gran parte de las ventas. Ajusta turnos en horas flojas o impulsa las ventas.',
      sin_datos: 'Faltan sueldos semanales configurados o ventas en el periodo.'
    },
    desglose: { titulo: 'Por semana', columnas: [['etiqueta', 'Semana'], ['valor', 'Sueldos / ventas', 'porcentaje']] }
  },
  'KPI-06': {
    nombre: 'Ganancia descontando insumos',
    pregunta: 'De cada venta, ¿cuánto queda tras pagar los insumos?',
    area: 'cocina',
    icono: 'fa-solid fa-bowl-food',
    formato: (v) => porcentaje(v),
    calculo: (d) => `Vendiste ${soles(d.ventas_netas)} y los insumos usados costaron aproximadamente ${soles(d.costo_directo_estimado)}.`,
    anterior: (k) => k.comparacion?.margen_anterior,
    formatoAnterior: (v) => porcentaje(v),
    acciones: {
      bien: 'Los insumos están bien aprovechados frente al precio de venta.',
      atencion: 'El costo de insumos es algo alto. Compara precios de proveedores y revisa porciones.',
      revisar: 'Los insumos cuestan demasiado frente a lo que vendes. Revisa precios, porciones y desperdicio.',
      sin_datos: 'Faltan ventas, salidas de inventario o costos de productos para estimarlo.'
    },
    desglose: { titulo: 'Por día', columnas: [['etiqueta', 'Periodo'], ['valor', 'Margen', 'porcentaje']] }
  },
  'KPI-07': {
    nombre: 'Cuadre de caja',
    pregunta: '¿El efectivo contado coincide con lo esperado?',
    area: 'ventas',
    icono: 'fa-solid fa-scale-balanced',
    formato: (v) => (v > 0 ? '+' : '') + porcentaje(v),
    calculo: (d) => `En ${d.cierres_con_conteo} cierres se esperaban ${soles(d.esperado_total)} y se contaron ${soles(d.contado_total)}: faltaron ${soles(d.faltante_total)} y sobraron ${soles(d.sobrante_total)}.` + (d.cierres_sin_conteo ? (d.cierres_sin_conteo === 1 ? ' 1 cierre no registró el efectivo contado.' : ` ${d.cierres_sin_conteo} cierres no registraron el efectivo contado.`) : ''),
    anterior: (k) => k.comparacion?.diferencia_relativa_anterior,
    formatoAnterior: (v) => porcentaje(v),
    acciones: {
      bien: 'La caja cuadra. Sigue registrando el efectivo contado en cada cierre.',
      atencion: 'Hay pequeñas diferencias. Verifica vueltos y que todos los gastos en efectivo se registren.',
      revisar: 'Hay diferencias importantes en caja. Revisa los cierres con faltante y quién estuvo a cargo.',
      sin_datos: 'No hay cierres con efectivo contado en el periodo. Pide registrarlo al cerrar caja.'
    },
    desglose: { titulo: 'Cierres del periodo', columnas: [['etiqueta', 'Apertura'], ['esperado', 'Esperado', 'soles'], ['contado', 'Contado', 'soles'], ['diferencia_abs', 'Diferencia', 'soles']] }
  },
  'KPI-08': {
    nombre: 'Mercadería sin moverse',
    pregunta: '¿Cuánto dinero está guardado en productos que no se usan?',
    area: 'cocina',
    icono: 'fa-solid fa-boxes-stacked',
    formato: (v) => porcentaje(v),
    calculo: (d) => `${soles(d.valor_inmovilizado)} de ${soles(d.valor_total)} en mercadería no tuvo salidas en los últimos ${d.ventana_dias} días (${d.productos_sin_movimiento} productos).`,
    acciones: {
      bien: 'Casi toda la mercadería se está usando.',
      atencion: 'Hay productos que no se mueven. Úsalos en el menú antes de volver a comprarlos.',
      revisar: 'Mucho dinero está detenido en productos sin uso. Evita recomprarlos y planifica cómo usarlos.',
      sin_datos: 'No hay inventario activo con costo registrado.'
    },
    desglose: { titulo: 'Sin moverse por categoría', columnas: [['etiqueta', 'Categoría'], ['valor', 'Valor detenido', 'soles']] }
  }
}

const FORMATOS = { soles, porcentaje, dias: (v) => numero(v) + ' días', numero: (v) => numero(v) }

export const infoIndicador = (codigo) => INDICADORES[codigo] || {
  nombre: codigo, pregunta: '', area: 'ventas', icono: 'fa-solid fa-chart-simple',
  formato: (v) => numero(v), acciones: {}, desglose: null
}

export const formatoCelda = (valor, tipo) => {
  if (valor === null || valor === undefined || valor === '') return '—'
  return FORMATOS[tipo] ? FORMATOS[tipo](valor) : valor
}

export const valorIndicador = (kpi) => {
  if (kpi.valor === null || kpi.valor === undefined) return 'Sin datos'
  return infoIndicador(kpi.codigo).formato(kpi.valor)
}

export const estadoIndicador = (kpi, limites = kpi.limites) => {
  const info = infoIndicador(kpi.codigo)
  const estado = estadoPorLimites(kpi.valor, limites)
  return info.ajustarEstado ? info.ajustarEstado(estado, kpi, limites) : estado
}

export const motivoEstado = (kpi, limites = kpi.limites) => {
  const info = infoIndicador(kpi.codigo)
  if (!info.motivoAjuste) return ''
  return estadoPorLimites(kpi.valor, limites) !== estadoIndicador(kpi, limites) ? info.motivoAjuste(kpi, limites) : ''
}

const estadoPorLimites = (valorKpi, limites) => {
  if (valorKpi === null || valorKpi === undefined || !limites) return 'sin_datos'
  const valor = limites.absoluto ? Math.abs(valorKpi) : valorKpi
  const { revisar, atencion } = limites
  if (limites.mayor_es_mejor) {
    if (valor < revisar) return 'revisar'
    return valor < atencion ? 'atencion' : 'bien'
  }
  if (valor >= revisar) return 'revisar'
  return valor > atencion ? 'atencion' : 'bien'
}

export const etiquetasLimites = (limites) => {
  if (!limites) return { atencion: '', revisar: '' }
  if (limites.mayor_es_mejor) return { atencion: 'Bien desde', revisar: 'Revisar por debajo de' }
  if (limites.absoluto) return { atencion: 'Bien con diferencia de hasta', revisar: 'Revisar con diferencia desde' }
  return { atencion: 'Bien hasta', revisar: 'Revisar desde' }
}

export const formatoLimite = (codigo, valor) => (infoIndicador(codigo).formatoLimite || porcentaje)(valor)

export const sufijoLimite = (codigo) => infoIndicador(codigo).sufijoLimite ?? '%'

export const textoMeta = (kpi, valores = kpi.limites) => {
  if (!kpi.limites || !valores) return ''
  const etiquetas = etiquetasLimites(kpi.limites)
  return `${etiquetas.atencion} ${formatoLimite(kpi.codigo, valores.atencion)}; ${etiquetas.revisar.toLowerCase()} ${formatoLimite(kpi.codigo, valores.revisar)}`
}

export const errorLimites = (limites, valores) => {
  const { atencion, revisar } = valores
  if (typeof atencion !== 'number' || typeof revisar !== 'number') return 'Ingresa ambos límites de la meta.'
  if ([atencion, revisar].some((v) => v < limites.minimo || v > limites.maximo)) {
    return `Los límites deben estar entre ${limites.minimo} y ${limites.maximo}.`
  }
  if (limites.mayor_es_mejor && revisar >= atencion) return 'El valor para "Revisar" debe ser menor que el valor desde el que está "Bien".'
  if (!limites.mayor_es_mejor && revisar <= atencion) return 'El valor para "Revisar" debe ser mayor que el valor hasta el que está "Bien".'
  return ''
}

export const calculoIndicador = (kpi) => {
  const info = infoIndicador(kpi.codigo)
  if (!info.calculo || !kpi.detalle || !Object.keys(kpi.detalle).length) return ''
  try {
    return info.calculo(kpi.detalle)
  } catch {
    return ''
  }
}

export const anteriorIndicador = (kpi) => {
  const info = infoIndicador(kpi.codigo)
  const valor = info.anterior ? info.anterior(kpi) : null
  return valor === null || valor === undefined ? '' : info.formatoAnterior(valor)
}
