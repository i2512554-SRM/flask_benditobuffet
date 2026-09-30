import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / '.env')
out = ROOT / 'docs/movil/muestras_anonimizadas.json'
queries = {
    'origen_demo': "SELECT 'transacciones_caja' AS tabla, count(*) AS total, count(*) FILTER (WHERE descripcion LIKE '%[demo histórico]%') AS marcados_demo FROM transacciones_caja UNION ALL SELECT 'pagos_empleados', count(*), count(*) FILTER (WHERE descripcion LIKE '%[demo histórico]%') FROM pagos_empleados UNION ALL SELECT 'inventario_movimientos', count(*), count(*) FILTER (WHERE motivo LIKE '%[demo histórico]%' OR observacion LIKE '%[demo histórico]%') FROM inventario_movimientos UNION ALL SELECT 'productos', count(*), count(*) FILTER (WHERE descripcion LIKE '%[demo histórico]%' OR nombre LIKE '%(demo)%') FROM productos",
    'roles': 'SELECT id_rol, nombre, estado FROM roles ORDER BY id_rol',
    'usuarios_por_rol': 'SELECT id_rol, estado, count(*) AS cantidad FROM usuarios GROUP BY id_rol, estado ORDER BY id_rol, estado',
    'productos_resumen': 'SELECT estado, unidad_medida, count(*) AS cantidad, count(*) FILTER (WHERE costo IS NULL) AS sin_costo FROM productos GROUP BY estado, unidad_medida ORDER BY estado, unidad_medida',
    'productos': 'SELECT precio, costo, stock, unidad_medida, estado FROM productos ORDER BY fecha_edicion DESC LIMIT 3',
    'caja': "SELECT tipo, monto, metodo_pago, fecha, coalesce(descripcion LIKE '%[demo histórico]%', false) AS marcado_demo FROM transacciones_caja ORDER BY fecha DESC LIMIT 3",
    'cierres': 'SELECT estado, monto_inicial, total_ventas, total_gastos, neto, efectivo_contado, fecha, fecha_cierre FROM cierres_caja ORDER BY fecha DESC LIMIT 2',
    'pagos': "SELECT monto, estado, tipo, semana, fecha_pago, coalesce(descripcion LIKE '%[demo histórico]%', false) AS marcado_demo FROM pagos_empleados ORDER BY fecha_pago DESC LIMIT 3",
    'adelantos': 'SELECT monto, estado, fecha, fecha_gestion FROM adelantos ORDER BY fecha DESC LIMIT 3',
    'solicitudes_insumos': 'SELECT cantidad, estado, fecha FROM solicitudes_insumos ORDER BY fecha DESC LIMIT 3',
    'compras': 'SELECT total_compra, estado, fecha FROM compras_inventario ORDER BY fecha DESC LIMIT 2',
    'inversiones': 'SELECT monto, estado, fecha FROM inversiones ORDER BY fecha DESC LIMIT 2',
    'movimientos': 'SELECT tipo, cantidad, stock_anterior, stock_posterior, fecha FROM inventario_movimientos ORDER BY fecha DESC LIMIT 3',
    'notificaciones_resumen': 'SELECT leida, count(*) AS cantidad FROM notificaciones GROUP BY leida',
    'sueldos_resumen': 'SELECT count(*) AS cantidad, min(desde) AS primera_vigencia, max(desde) AS ultima_vigencia FROM sueldos_semanales',
    'descuentos_resumen': 'SELECT anulado, count(*) AS cantidad FROM descuentos_semanales GROUP BY anulado',
    'metas': 'SELECT codigo, limite_atencion, limite_revisar FROM metas_indicadores ORDER BY codigo',
}
def serial(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    raise TypeError(type(value).__name__)

try:
    conn = psycopg.connect(user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'], host=os.environ['DB_HOST'], port=int(os.getenv('DB_PORT', '6543')), dbname=os.getenv('DB_NAME', 'postgres'), sslmode='require', connect_timeout=15, prepare_threshold=None, row_factory=dict_row)
    conn.read_only = True
    conn.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
    data = {'fecha_revision': '2026-09-30', 'origen': 'Base configurada en el entorno local; entorno productivo no confirmado', 'solo_lectura': True, 'anonimizacion': 'No se consultaron identificadores personales, nombres, DNI, correos, teléfonos, IP, contraseñas, sesiones ni textos libres. Importes, fechas y estados conservan su valor; estas muestras no se deben publicar como datos abiertos.', 'resultados': {}}
    with conn:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '15000ms'")
            cur.execute('SELECT current_timestamp AS consulta_utc')
            data.update(cur.fetchone())
            for name, query in queries.items():
                with conn.transaction():
                    try:
                        cur.execute(query)
                        data['resultados'][name] = cur.fetchall()
                    except psycopg.Error as exc:
                        data['resultados'][name] = {'no_disponible': exc.sqlstate}
                        raise
    out.write_text(json.dumps(data, default=serial, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'archivo': str(out), 'grupos': len(data['resultados']), 'consulta_utc': str(data['consulta_utc'])}, ensure_ascii=False))
except Exception as exc:
    print(json.dumps({'error_tipo': type(exc).__name__, 'sqlstate': getattr(exc, 'sqlstate', None), 'detalle': 'No se muestran credenciales ni cadena de conexión.'}, ensure_ascii=False))
    raise SystemExit(1)
