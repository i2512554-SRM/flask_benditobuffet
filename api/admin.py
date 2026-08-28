from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from calendar import monthrange
from bd import db
from models import TransaccionCaja, CierreCaja

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/panel-stats', methods=['GET'])
@jwt_required()
def get_panel_stats():
    try:
        # Obtener mes y año actual
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Calcular primer y ultimo dia del mes
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        # Obtener transacciones del mes
        transacciones = TransaccionCaja.query.filter(
            TransaccionCaja.fecha >= first_day,
            TransaccionCaja.fecha <= last_day
        ).all()
        
        # Calcular totales
        ventas_mes = sum(t.monto for t in transacciones if t.tipo == 'ingreso')
        egresos_mes = sum(t.monto for t in transacciones if t.tipo == 'egreso')
        neto_mes = ventas_mes - egresos_mes
        
        return jsonify({
            'success': True,
            'data': {
                'ventas_mes': float(ventas_mes),
                'egresos_mes': float(egresos_mes),
                'neto_mes': float(neto_mes)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
