"""Recorrido diagnóstico aislado; no conecta a la base real."""
import json
import re
from collections import Counter
from tests.test_flows import BaseFlujos


def main():
    f = BaseFlujos()
    f.setUp()
    try:
        f.producto()
        resultados = []
        for regla in f.app.url_map.iter_rules():
            if 'GET' not in regla.methods or not regla.rule.startswith('/api/') or '/dni/' in regla.rule:
                continue
            ruta = re.sub(r'<[^>]+>', '1', regla.rule)
            for rol in (1, 2, 3, 4):
                try:
                    r = f.call('get', ruta[4:], role=rol)
                    resultados.append({'ruta':ruta,'rol':rol,'estado':r.status_code})
                except Exception as e:
                    f.app.logger.disabled = True
                    from models import db
                    db.session.rollback()
                    resultados.append({'ruta':ruta,'rol':rol,'estado':type(e).__name__})
        print(json.dumps({'solicitudes':len(resultados),'rutas':len({x['ruta'] for x in resultados}),
                         'estados':dict(Counter(str(x['estado']) for x in resultados)),
                         'fallos':[x for x in resultados if not isinstance(x['estado'],int) or x['estado']>=500]},ensure_ascii=False))
        from models import db, Usuario, Adelanto
        from api.fechas import ahora
        pendiente = Adelanto(id_usuario=4, monto=10, estado='Pendiente', fecha=ahora(), motivo='Diagnóstico aislado')
        db.session.add(pendiente)
        db.session.commit()
        identificador = pendiente.id_adelanto
        db.session.get(Usuario,4).estado = False
        db.session.commit()
        r = f.call('delete', '/perfil/adelantos/'+str(identificador), role=4)
        # La ruta de perfil no usa un prefijo /perfil en todos los endpoints.
        if r.status_code == 404:
            r = f.call('delete', '/adelantos/'+str(identificador), role=4)
        print('Cancelación con usuario desactivado:', r.status_code)
        pago = {'id_usuario':2,'monto':25,'fecha':'2026-09-20','estado':'Pagado','tipo':'Salario semanal'}
        primero = f.call('post','/personal/pagos',json=pago)
        pago['tipo'] = 'Bono'
        segundo = f.call('post','/personal/pagos',json=pago)
        print('Salario y bono del mismo importe:', primero.status_code, segundo.status_code)
    finally:
        f.tearDown()


if __name__ == '__main__':
    main()
