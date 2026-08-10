#!/usr/bin/env python3
"""
Limpia los registros antiguos de las tablas de log (actividad_usuario e
intentos_login) según RETENCION_LOGS_DIAS (por defecto 90 días).
Uso: python automatizacion_caja/limpiar_logs.py
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
from models import ActividadUsuario, IntentoLogin
import app as app_module


def main():
    app = app_module.app
    dias = int(os.getenv("RETENCION_LOGS_DIAS", "90"))
    corte = datetime.now() - timedelta(days=dias)

    with app.app_context():
        n_actividad = ActividadUsuario.query.filter(
            ActividadUsuario.fecha < corte
        ).delete(synchronize_session=False)
        n_intentos = IntentoLogin.query.filter(
            IntentoLogin.fecha < corte
        ).delete(synchronize_session=False)
        db.session.commit()

    print(f"Retención configurada: {dias} días (corte {corte.date()})")
    print(f"  actividad_usuario: {n_actividad} registros eliminados")
    print(f"  intentos_login:    {n_intentos} registros eliminados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
