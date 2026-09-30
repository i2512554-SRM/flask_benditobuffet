"""Prueba bloqueos transaccionales PostgreSQL sin modificar filas."""
from sqlalchemy import text
from app import app
from bd import db


def probar():
    resultado = []
    with db.engine.connect() as primera, db.engine.connect() as segunda:
        primera.execute(text('SET TRANSACTION READ ONLY'))
        segunda.execute(text('SET TRANSACTION READ ONLY'))
        for clave, nombre in ((72451001, 'caja'), (72451002, 'inventario'), (72500000, 'personal')):
            adquirida = primera.scalar(text('SELECT pg_try_advisory_xact_lock(:clave)'), {'clave': clave})
            bloqueada = not segunda.scalar(text('SELECT pg_try_advisory_xact_lock(:clave)'), {'clave': clave})
            primera.rollback()
            liberada = segunda.scalar(text('SELECT pg_try_advisory_xact_lock(:clave)'), {'clave': clave})
            segunda.rollback()
            resultado.append((nombre, bool(adquirida and bloqueada and liberada)))
    return resultado


if __name__ == '__main__':
    with app.app_context():
        resultados = probar()
        for nombre, correcto in resultados:
            print(f'{nombre}=' + ('ok' if correcto else 'fallo'))
        if not all(correcto for _, correcto in resultados):
            raise SystemExit(1)
