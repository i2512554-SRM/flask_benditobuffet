"""Genera SQL revisable para PostgreSQL; no conecta ni aplica cambios.

Uso: python -m automatizacion_caja.preparar_nomina
Revisar/aplicar en la base de pruebas y registrar con el flujo de migraciones
del entorno antes de desplegar la funcionalidad semanal.
"""
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import postgresql
from models import SueldoSemanal, DescuentoSemanal


def sql_nomina():
    dialecto = postgresql.dialect()
    sentencias = ['BEGIN;', 'SET LOCAL search_path = public;']
    for modelo in (SueldoSemanal, DescuentoSemanal):
        tabla = modelo.__table__
        sentencias.append(str(CreateTable(tabla, if_not_exists=True).compile(dialect=dialecto)) + ';')
        for indice in sorted(tabla.indexes, key=lambda i: i.name):
            sentencias.append(str(CreateIndex(indice, if_not_exists=True).compile(dialect=dialecto)) + ';')
        sentencias.append(f'ALTER TABLE public.{tabla.name} ENABLE ROW LEVEL SECURITY;')
        # La aplicación usa su backend Flask; no se da acceso directo al cliente.
        sentencias.append(f'REVOKE ALL ON TABLE public.{tabla.name} FROM PUBLIC;')
        sentencias.append(f'''DO $$ BEGIN
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON TABLE public.{tabla.name} FROM anon;
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON TABLE public.{tabla.name} FROM authenticated;
    END IF;
END $$;''')
    sentencias.append('COMMIT;')
    return '\n'.join(sentencias)


if __name__ == '__main__':
    print(sql_nomina())
