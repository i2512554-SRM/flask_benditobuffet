"""Auditoría de solo lectura: metadatos y conteos, sin valores personales."""
import json
from flask import Flask
from sqlalchemy import text, inspect
from bd import db, init_db
from models import db as modelos_db


def main():
    app = Flask('auditoria')
    init_db(app)
    with app.app_context(), db.engine.connect() as con:
        con.execute(text('SET TRANSACTION READ ONLY'))
        con.execute(text("SET LOCAL statement_timeout = '20s'"))
        def q(sql):
            return [dict(r) for r in con.execute(text(sql)).mappings()]
        resultado = {}
        consultas = {
            'conexion': "SELECT current_user AS rol, current_setting('server_version') AS version, (SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS ssl, (SELECT rolbypassrls FROM pg_roles WHERE rolname=current_user) AS bypass_rls",
            'tablas_permisos': "SELECT c.relname AS tabla,c.relrowsecurity AS rls,pg_get_userbyid(c.relowner) AS propietario,has_table_privilege('anon',c.oid,'SELECT') AS anon_lee,has_table_privilege('anon',c.oid,'INSERT,UPDATE,DELETE') AS anon_escribe,has_table_privilege('authenticated',c.oid,'SELECT') AS auth_lee,has_table_privilege('authenticated',c.oid,'INSERT,UPDATE,DELETE') AS auth_escribe FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY c.relname",
            'politicas': "SELECT tablename,policyname,roles,cmd,qual,with_check FROM pg_policies WHERE schemaname='public'",
            'funciones_privilegiadas': "SELECT p.proname,p.prosecdef,p.proconfig,has_function_privilege('anon',p.oid,'EXECUTE') AS anon_ejecuta,has_function_privilege('authenticated',p.oid,'EXECUTE') AS auth_ejecuta FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.prosecdef",
            'vistas': "SELECT c.relname,c.reloptions,has_table_privilege('anon',c.oid,'SELECT') AS anon_lee FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind IN ('v','m')",
            'restricciones_invalidas': "SELECT conrelid::regclass::text AS tabla,conname FROM pg_constraint WHERE NOT convalidated AND connamespace='public'::regnamespace",
            'indices_invalidos': "SELECT indexrelid::regclass::text AS indice FROM pg_index WHERE NOT indisvalid AND indrelid IN (SELECT oid FROM pg_class WHERE relnamespace='public'::regnamespace)",
            'tamano': "SELECT pg_size_pretty(pg_database_size(current_database())) AS base, count(*) FILTER (WHERE state='active') AS conexiones_activas FROM pg_stat_activity",
            'usuarios': "SELECT count(*) AS total,count(*) FILTER(WHERE clave IS NULL OR clave !~ '^\\$2[aby]\\$[0-9]{2}\\$[./A-Za-z0-9]{53}$') AS clave_no_bcrypt,count(*) FILTER(WHERE estado AND id_rol=1) AS admins_activos FROM public.usuarios",
            'pagos': "SELECT count(*) AS total,count(*) FILTER(WHERE tipo IS NULL) AS sin_clasificar,count(*) FILTER(WHERE id_pago_personal IS NULL) AS sin_vinculo,count(*) FILTER(WHERE monto<=0 OR monto::text IN ('NaN','Infinity','-Infinity')) AS monto_invalido FROM public.pagos_empleados",
            'stock': "SELECT count(*) FILTER(WHERE stock<0 OR stock::text IN ('NaN','Infinity','-Infinity')) AS stock_invalido FROM public.productos",
            'caja': "SELECT count(*) FILTER(WHERE monto<=0 OR monto::text IN ('NaN','Infinity','-Infinity')) AS monto_invalido,count(*) FILTER(WHERE metodo_pago IS NULL OR btrim(metodo_pago)='') AS sin_metodo FROM public.transacciones_caja",
            'cierres': "SELECT count(*) FILTER(WHERE estado='abierta') AS abiertas,count(*) FILTER(WHERE fecha_cierre<fecha) AS cierre_anterior_apertura FROM public.cierres_caja",
            'logs': "SELECT count(*) AS total,count(*) FILTER(WHERE fecha < now()-interval '90 days') AS mayores_90_dias FROM public.intentos_login",
        }
        for nombre, sql in consultas.items():
            with con.begin_nested() as tx:
                try:
                    resultado[nombre] = q(sql)
                except Exception as e:
                    tx.rollback()
                    resultado[nombre] = {'error': type(e).__name__}
        inspector = inspect(con)
        faltantes, huerfanos, sin_indices, estructura = [], [], [], []
        quote = con.dialect.identifier_preparer.quote
        for tabla in modelos_db.metadata.sorted_tables:
            if not inspector.has_table(tabla.name, schema='public'):
                faltantes.append(tabla.name)
                continue
            columnas = inspector.get_columns(tabla.name, schema='public')
            faltantes.extend(tabla.name+'.'+c.name for c in tabla.columns if c.name not in {x['name'] for x in columnas})
            fks = inspector.get_foreign_keys(tabla.name, schema='public')
            indices = inspector.get_indexes(tabla.name, schema='public')
            estructura.append({'tabla':tabla.name,'checks':inspector.get_check_constraints(tabla.name,schema='public'),'pk':inspector.get_pk_constraint(tabla.name,schema='public')['constrained_columns'], 'filas':q('SELECT count(*) AS n FROM public.'+quote(tabla.name))[0]['n'], 'numericos_aproximados':[c['name'] for c in columnas if str(c['type']) in ('DOUBLE PRECISION','REAL')], 'fk_faltantes':[c.name for c in tabla.columns if c.foreign_keys and not any(c.name in fk['constrained_columns'] for fk in fks)]})
            for fk in fks:
                cols=fk['constrained_columns']
                if not any(x['column_names'][:len(cols)] == cols and not x.get('dialect_options',{}).get('postgresql_where') for x in indices):
                    sin_indices.append(tabla.name+'.'+','.join(cols))
                condiciones=' AND '.join('h.'+quote(a)+'=p.'+quote(b) for a,b in zip(cols,fk['referred_columns']))
                no_nulos=' AND '.join('h.'+quote(c)+' IS NOT NULL' for c in cols)
                sql='SELECT count(*) AS n FROM public.'+quote(tabla.name)+' h WHERE '+no_nulos+' AND NOT EXISTS (SELECT 1 FROM '+quote(fk['referred_schema'] or 'public')+'.'+quote(fk['referred_table'])+' p WHERE '+condiciones+')'
                n=q(sql)[0]['n']
                if n: huerfanos.append({'tabla':tabla.name,'fk':fk['name'],'filas':n})
        resultado.update(faltantes=faltantes,huerfanos=huerfanos,fk_sin_indice=sin_indices,estructura=estructura)
        for tabla,col in [('usuarios','usuario'),('usuarios','correo'),('documentos_identidad','numero')]:
            resultado['duplicados_'+tabla+'_'+col]=q('SELECT count(*) AS grupos FROM (SELECT lower(btrim('+quote(col)+')) FROM public.'+quote(tabla)+' WHERE '+quote(col)+' IS NOT NULL GROUP BY lower(btrim('+quote(col)+')) HAVING count(*)>1) d')
        print(json.dumps(resultado,ensure_ascii=False,default=str,indent=2))
        con.rollback()


if __name__ == '__main__':
    main()
