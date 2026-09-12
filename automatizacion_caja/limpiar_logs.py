#!/usr/bin/env python3
"""
Revisa accesos antiguos de intentos_login según RETENCION_LOGS_DIAS (90 días).
Conserva el historial de operaciones actividad_usuario.
Uso: python -m automatizacion_caja.limpiar_logs
Para eliminar con respaldo: añadir --aplicar --respaldo logs/respaldos
Se puede programar con cron o el Programador de tareas de Windows.
"""

import os
import sys
from datetime import datetime, timedelta

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

from bd import db
from models import IntentoLogin
import argparse
import json
from pathlib import Path
from datetime import timezone
from uuid import uuid4


def limpiar_accesos(dias=90, aplicar=False, respaldo=None, instante=None):
    if not isinstance(dias, int) or dias < 1:
        raise ValueError('La retención debe ser de al menos un día')
    if aplicar and not respaldo:
        raise ValueError('Debe indicar una carpeta de respaldo')
    corte = (instante or datetime.now(timezone.utc)) - timedelta(days=dias)
    consulta = IntentoLogin.query.filter(IntentoLogin.fecha < corte)
    total = consulta.count()
    if not aplicar or not total:
        return {'encontrados': total, 'eliminados': 0, 'corte': corte.isoformat()}
    carpeta = Path(respaldo)
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = carpeta / f'accesos-{uuid4().hex}.jsonl'
    eliminados = 0
    with archivo.open('x', encoding='utf-8') as salida:
        while True:
            lote = consulta.order_by(IntentoLogin.id).limit(1000).all()
            if not lote:
                break
            for registro in lote:
                salida.write(json.dumps({'id': registro.id, 'identificador': registro.identificador,
                    'ip': registro.ip, 'resultado': registro.resultado,
                    'fecha': registro.fecha.isoformat()}, ensure_ascii=False) + '\n')
            salida.flush()
            os.fsync(salida.fileno())
            try:
                cantidad = IntentoLogin.query.filter(IntentoLogin.id.in_([r.id for r in lote])).delete(synchronize_session=False)
                db.session.commit()
                eliminados += cantidad
            except Exception:
                db.session.rollback()
                raise
    return {'encontrados': total, 'eliminados': eliminados, 'corte': corte.isoformat(), 'respaldo': str(archivo)}


def main():
    parser = argparse.ArgumentParser(description='Revisar accesos antiguos; aplicar solo con respaldo. Conserva actividad_usuario.')
    parser.add_argument('--dias', type=int, default=int(os.getenv('RETENCION_LOGS_DIAS', '90')))
    parser.add_argument('--aplicar', action='store_true')
    parser.add_argument('--respaldo', type=Path)
    args = parser.parse_args()
    if args.dias < 1 or (args.aplicar and not args.respaldo):
        parser.error('Use --dias mayor que cero y --respaldo para aplicar')
    from app import app
    with app.app_context():
        print(json.dumps(limpiar_accesos(args.dias, args.aplicar, args.respaldo), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
