export function formatFecha(value) {
  if (!value) return '—'
  if (/^\d{2}\/\d{2}\/\d{4}/.test(value)) return value
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value.split('-').reverse().join('/')
  const fecha = new Date(value)
  if (Number.isNaN(fecha.getTime())) return value
  return fecha.toLocaleString('es-PE', { timeZone: 'America/Lima', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })
}
export function fechaLocal(value = new Date()) {
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`
}
