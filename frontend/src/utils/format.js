export function formatFecha(value) {
  if (!value) return '—'
  if (/^\d{2}\/\d{2}\/\d{4}/.test(value)) return value
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value.split('-').reverse().join('/')
  const fecha = new Date(value)
  if (Number.isNaN(fecha.getTime())) return value
  return fecha.toLocaleString('es-PE', { timeZone: 'America/Lima', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })
}
export function fechaLocal(value = new Date()) {
  if (!value) return ''
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) return value
  const fecha = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(fecha.getTime())) return ''
  const partes = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(fecha)
  const valores = Object.fromEntries(partes.map(({ type, value: parte }) => [type, parte]))
  return `${valores.year}-${valores.month}-${valores.day}`
}
export function soloFecha(value) {
  if (!value) return '—'
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value.split('-').reverse().join('/')
  const fecha = new Date(value)
  if (Number.isNaN(fecha.getTime())) return value
  return fecha.toLocaleString('es-PE', { timeZone: 'America/Lima', day: '2-digit', month: '2-digit', year: 'numeric' })
}
export function soloHora(value) {
  if (!value) return '—'
  const fecha = new Date(value)
  if (Number.isNaN(fecha.getTime())) return value
  return fecha.toLocaleString('es-PE', { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', hour12: false })
}

export function fechaLarga(value) {
  if (!value) return '—'
  const fecha = new Date(value)
  if (Number.isNaN(fecha.getTime())) return value
  return fecha.toLocaleDateString('es-PE', {
    timeZone: 'America/Lima', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  })
}

export function horaLima(value = new Date()) {
  const fecha = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(fecha.getTime())) return null
  return Number(new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Lima', hour: '2-digit', hour12: false
  }).format(fecha))
}

export function saludoSegunHora(value = new Date()) {
  const hora = horaLima(value) ?? 12
  if (hora >= 5 && hora < 12) return 'Buenos días'
  if (hora >= 12 && hora < 19) return 'Buenas tardes'
  return 'Buenas noches'
}
