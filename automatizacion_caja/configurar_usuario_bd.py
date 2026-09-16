"""Crea una cuenta limitada y actualiza .env solo después de verificar acceso.

Requiere --aplicar y la conexión administrativa actual. No imprime secretos.
"""
import argparse
import os
import secrets
from pathlib import Path
from flask import Flask
from dotenv import dotenv_values
from psycopg import sql
from sqlalchemy import create_engine, text
from bd import db, init_db
from models import db as modelos_db


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--aplicar', action='store_true', required=True)
    p.parse_args()
    ruta = Path(__file__).resolve().parents[1] / '.env'
    contenido = ruta.read_text(encoding='utf-8')
    valores = dotenv_values(ruta)
    if any(valores.get(k) != os.environ.get(k) for k in ('DB_USER','DB_PASSWORD','DB_HOST')):
        raise SystemExit('La configuración del proceso difiere de .env; no se cambió nada.')
    rol = 'buffet_backend'
    clave = secrets.token_urlsafe(48)
    usuario = rol + ('.' + os.environ['DB_USER'].split('.',1)[1] if '.' in os.environ['DB_USER'] else '')
    app = Flask('configurar_usuario_bd')
    init_db(app)
    with app.app_context():
        raw = db.engine.raw_connection()
        try:
            with raw.cursor() as cur:
                cur.execute('SELECT 1 FROM pg_roles WHERE rolname=%s', (rol,))
                if cur.fetchone():
                    raise RuntimeError('La cuenta ya existe; no se reemplaza automáticamente')
                cur.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT').format(sql.Identifier(rol),sql.Literal(clave)))
                cur.execute(sql.SQL('GRANT USAGE ON SCHEMA public TO {}').format(sql.Identifier(rol)))
                for tabla in sorted(modelos_db.metadata.tables):
                    cur.execute(sql.SQL('GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.{} TO {}').format(sql.Identifier(tabla),sql.Identifier(rol)))
                    cur.execute(sql.SQL('CREATE POLICY buffet_backend_acceso ON public.{} FOR ALL TO {} USING (true) WITH CHECK (true)').format(sql.Identifier(tabla),sql.Identifier(rol)))
                    for columna in modelos_db.metadata.tables[tabla].primary_key.columns:
                        cur.execute('SELECT pg_get_serial_sequence(%s,%s)',('public.'+tabla,columna.name))
                        secuencia = cur.fetchone()[0]
                        if secuencia:
                            cur.execute(sql.SQL('GRANT USAGE, SELECT ON SEQUENCE {} TO {}').format(sql.Identifier(*secuencia.split('.')),sql.Identifier(rol)))
            raw.commit()
            print('Cuenta limitada y políticas específicas creadas.', flush=True)
        except Exception as e:
            raw.rollback()
            print('No se cambió .env. Error al preparar cuenta: '+type(e).__name__)
            raise SystemExit(1)
        finally:
            raw.close()
        engine = create_engine(db.engine.url.set(username=usuario,password=clave),connect_args={'connect_timeout':15})
        try:
            with engine.connect() as c:
                atributos=c.execute(text('SELECT rolsuper,rolcreatedb,rolcreaterole,rolbypassrls FROM pg_roles WHERE rolname=current_user')).one()
                assert not any(atributos)
                assert not c.execute(text("SELECT has_schema_privilege(current_user,'public','CREATE')")).scalar()
                for tabla in sorted(modelos_db.metadata.tables):
                    c.execute(text('SELECT 1 FROM public.'+tabla+' LIMIT 1'))
                    assert not c.execute(text("SELECT has_table_privilege(current_user,:t,'TRUNCATE')"),{'t':'public.'+tabla}).scalar()
                c.execute(text("INSERT INTO public.sesiones_usuario (id,id_usuario,huella_clave,expira,revocada) SELECT :id,id_usuario,repeat('0',64),now()+interval '1 minute',false FROM public.usuarios LIMIT 1"),{'id':secrets.token_hex(16)})
                c.rollback()
            print('Acceso a 25 tablas y escritura de sesión verificados; prueba revertida.',flush=True)
            lineas=contenido.splitlines(keepends=True)
            for k,v in [('DB_USER',usuario),('DB_PASSWORD',clave)]:
                encontrados=[i for i,l in enumerate(lineas) if l.strip().startswith(k+'=') or l.strip().startswith('export '+k+'=')]
                if len(encontrados)!=1:
                    raise ValueError('Configuración ambigua')
                lineas[encontrados[0]]=k+"='"+v+"'\n"
            temporal=ruta.with_name('.env.backend-pendiente')
            temporal.write_text(''.join(lineas),encoding='utf-8')
            os.replace(temporal,ruta)
            print('.env actualizado con la cuenta limitada. Reiniciar el servidor para activarla.',flush=True)
        except Exception as e:
            print('La configuración anterior se conserva; cuenta preparada pendiente de revisión. Error: '+type(e).__name__)
            raise SystemExit(1)
        finally:
            engine.dispose()
            db.engine.dispose()


if __name__ == '__main__':
    main()
