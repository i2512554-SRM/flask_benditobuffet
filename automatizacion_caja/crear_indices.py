#!/usr/bin/env python3
"""
Crea los índices faltantes en tablas existentes de la base de datos.
Idempotente: solo agrega los índices que no existen aún.
Uso: python automatizacion_caja/crear_indices.py
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

from sqlalchemy import text

from bd import db
import app as app_module

INDICES = {
    "transacciones_caja": [
        ("ix_transacciones_caja_usuario", ["id_usuario"]),
        ("ix_transacciones_caja_fecha", ["fecha"]),
    ],
    "cierres_caja": [
        ("ix_cierres_caja_fecha", ["fecha"]),
    ],
    "pagos_empleados": [
        ("ix_pagos_empleados_usuario", ["id_usuario"]),
        ("ix_pagos_empleados_fecha", ["fecha_pago"]),
    ],
    "pagos_personal": [
        ("ix_pagos_personal_usuario", ["id_usuario"]),
        ("ix_pagos_personal_fecha", ["fecha"]),
    ],
    "adelantos": [
        ("ix_adelantos_usuario", ["id_usuario"]),
        ("ix_adelantos_fecha", ["fecha"]),
        ("ix_adelantos_estado", ["estado"]),
    ],
    "actividad_usuario": [
        ("ix_actividad_usuario_usuario", ["id_usuario"]),
        ("ix_actividad_usuario_fecha", ["fecha"]),
    ],
    "intentos_login": [
        ("ix_intentos_login_fecha", ["fecha"]),
    ],
    "inversiones": [
        ("ix_inversiones_fecha", ["fecha"]),
    ],
    "productos": [
        ("ix_productos_fecha_registro", ["fecha_registro"]),
    ],
}


def main():
    app = app_module.app
    creados = []
    omitidos = []
    errores = []

    with app.app_context():
        inspector = db.inspect(db.engine)
        for tabla, indices in INDICES.items():
            try:
                existentes = {i["name"] for i in inspector.get_indexes(tabla)}
            except Exception as exc:
                errores.append(f"{tabla}: {exc}")
                continue
            for nombre, columnas in indices:
                if nombre in existentes:
                    omitidos.append(nombre)
                    continue
                try:
                    ddl = f"CREATE INDEX {nombre} ON {tabla} ({', '.join(columnas)})"
                    db.session.execute(text(ddl))
                    creados.append(nombre)
                except Exception as exc:
                    errores.append(f"{nombre}: {exc}")
        db.session.commit()

    print(f"Indices creados ({len(creados)}):")
    for nombre in creados:
        print(f"  + {nombre}")
    print(f"Indices ya existentes ({len(omitidos)}): {len(omitidos)} omitidos")
    if errores:
        print("Errores:")
        for e in errores:
            print(f"  ! {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
