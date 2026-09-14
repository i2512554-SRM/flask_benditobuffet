from datetime import timedelta
from unittest.mock import patch, Mock
from tests.test_flows import BaseFlujos, instante
from models import db, Usuario, PagoEmpleado, PagoPersonal, Adelanto, DescuentoSemanal, CierreCaja, SolicitudInsumo, SueldoSemanal, SesionUsuario
from api.sesiones import crear_sesion
import bcrypt


class RevisionFlujosTest(BaseFlujos):
    def test_retencion_limpia_accesos_duplicados_sin_borrar_pagos(self):
        from models import ActividadUsuario
        from automatizacion_caja.limpiar_logs import limpiar_accesos
        import json
        from pathlib import Path
        vieja = instante('2026-01-01T12:00:00')
        db.session.add_all([
            ActividadUsuario(id_usuario=2,accion='Inició sesión',fecha=vieja),
            ActividadUsuario(id_usuario=2,accion='Registró pago',fecha=vieja),
            SesionUsuario(id='sesion-vencida-ficticia',id_usuario=2,huella_clave='0'*64,expira=vieja,revocada=True)])
        db.session.commit()
        r=limpiar_accesos(aplicar=True,respaldo=self.folder.name,instante=instante('2026-09-13T12:00:00'))
        self.assertEqual(r['eliminados'],2)
        self.assertEqual(ActividadUsuario.query.one().accion,'Registró pago')
        self.assertEqual(len(Path(r['respaldo']).read_text(encoding='utf-8').splitlines()),2)

    def nomina(self, fecha='2026-09-10'):
        return next(x for x in self.call('get', '/personal/salarios?fecha=' + fecha).json['data'] if x['id_usuario'] == 2)

    def sueldo(self):
        self.assertEqual(self.call('post', '/personal/salarios/sueldo', json={'id_usuario':2, 'monto':350, 'fecha':'2026-09-10'}).status_code, 200)

    def test_bono_no_reduce_sueldo(self):
        self.sueldo()
        self.assertEqual(self.call('post', '/personal/pagos', json={'id_usuario':2,'monto':50,'tipo':'Bono','fecha':'2026-09-10'}).status_code, 200)
        self.assertEqual(self.nomina()['saldo'], 350)
        self.assertEqual(self.nomina()['total_pagos'], 50)

    def test_adelanto_resuelto_no_cambia_estado(self):
        self.call('post','/perfil/adelantos',role=2,json={'monto':20,'motivo':'Transporte'})
        a=Adelanto.query.first()
        self.assertEqual(self.call('delete', f'/perfil/adelantos/{a.id_adelanto}', role=2).status_code, 200)
        self.assertEqual(self.call('put', f'/admin/adelantos/{a.id_adelanto}', json={'accion':'aprobar'}).status_code, 409)
        a.estado='Pendiente'; db.session.commit()
        self.assertEqual(self.call('put', f'/admin/adelantos/{a.id_adelanto}', json={'accion':'aprobar'}).status_code, 200)
        self.assertEqual(self.call('put', f'/admin/adelantos/{a.id_adelanto}', json={'accion':'rechazar'}).status_code, 409)
        self.assertEqual(a.estado, 'Aprobado')

    def test_adelanto_se_descuenta_al_entregar(self):
        db.session.add(Adelanto(id_usuario=2,monto=30,motivo='Viaje',fecha=instante('2026-09-06T18:00:00'),estado='Pendiente'))
        db.session.commit()
        with patch('api.admin.ahora', return_value=instante('2026-09-07T15:00:00')):
            self.call('put',f'/admin/adelantos/{Adelanto.query.first().id_adelanto}',json={'accion':'aprobar'})
        self.assertEqual(self.nomina('2026-09-06')['total_adelantos'], 0)
        self.assertEqual(self.nomina()['total_adelantos'], 30)

    def test_no_desactivar_ni_degradar_ultimo_admin(self):
        self.assertEqual(self.call('delete','/personal/1').status_code,409)
        self.assertEqual(self.call('put','/personal/1',json={'id_rol':2}).status_code,409)
        self.assertEqual(Usuario.query.filter_by(id_rol=1,estado=True).count(),1)

    def test_logout_revoca_access_y_refresh(self):
        token, refresh=crear_sesion(db.session.get(Usuario,2))
        headers={'Authorization':'Bearer '+token}
        self.assertEqual(self.client.post('/api/auth/logout',headers=headers).status_code,200)
        self.assertEqual(self.client.get('/api/auth/me',headers=headers).status_code,401)
        self.assertEqual(self.client.post('/api/auth/refresh',headers={'Authorization':'Bearer '+refresh}).status_code,401)

    def test_cambio_clave_revoca_sesiones_y_valida_longitud(self):
        u=db.session.get(Usuario,2); u.clave=bcrypt.hashpw(b'clave-actual',bcrypt.gensalt()).decode(); db.session.commit()
        token, refresh=crear_sesion(u); headers={'Authorization':'Bearer '+token}
        datos={'contrasena_actual':'clave-actual','contrasena_nueva':'a','contrasena_verificar':'a'}
        self.assertEqual(self.client.put('/api/perfil/contrasena',json=datos,headers=headers).status_code,400)
        datos.update(contrasena_nueva='otra-clave-segura',contrasena_verificar='otra-clave-segura')
        self.assertEqual(self.client.put('/api/perfil/contrasena',json=datos,headers=headers).status_code,200)
        self.assertEqual(self.client.post('/api/auth/refresh',headers={'Authorization':'Bearer '+refresh}).status_code,401)

    def test_salida_fraccionaria_y_filtros_combinados(self):
        self.producto(.3)
        self.assertEqual(self.call('get','/inventario/productos?cat=Ingredientes&q=arroz').status_code,200)
        for cantidad in (.1,.2):
            self.assertEqual(self.call('post','/inventario/productos/1/stock/salida',role=3,json={'cantidad':cantidad,'motivo':'Cocina'}).status_code,200)
        self.assertEqual(self.call('get','/inventario/productos/1').json['data']['stock'],0)

    def test_anular_compra_reabre_solicitud(self):
        self.producto(0)
        self.call('post','/cocina/solicitudes',role=3,json={'id_producto':1,'cantidad':5})
        r=self.call('post','/inventario/compras',json={'detalle':[{'id_producto':1,'cantidad':5,'precio_unitario':4}]})
        self.assertEqual(r.status_code,201)
        self.assertEqual(SolicitudInsumo.query.first().estado,'Atendida')
        self.call('delete',f"/inventario/compras/{r.json['data']['id_compra']}")
        self.assertEqual(SolicitudInsumo.query.first().estado,'Pendiente')

    def test_reporte_cierre_fuera_de_ultimos_200(self):
        inicio=instante('2025-01-01T12:00:00')
        for i in range(201):
            fecha=inicio+timedelta(days=i)
            db.session.add(CierreCaja(id_usuario=1,estado='cerrada',fecha=fecha,fecha_cierre=fecha+timedelta(hours=1),total_ventas=0,total_gastos=0))
        db.session.commit()
        r=self.call('get','/caja/reportes?fecha=2025-01-01&periodo=dia')
        self.assertEqual(len(r.json['data']['cierres']),1)

    def test_descuento_idempotente(self):
        datos={'id_usuario':2,'fecha':'2026-09-10','monto':15,'motivo':'Platos','clave_operacion':'28c424b3-8a64-4f8e-a18c-0b4027290b35'}
        for _ in range(2):
            self.assertEqual(self.call('post','/personal/salarios/descuentos',json=datos).status_code,200)
        self.assertEqual(DescuentoSemanal.query.count(),1)
        self.assertEqual(self.call('post','/personal/salarios/descuentos',json={**datos,'monto':20}).status_code,409)

    def test_dni_duplicado_rechazado_sin_error_interno(self):
        self.assertEqual(self.call('put','/personal/2',json={'dni':'00000003'}).status_code,409)
        self.assertEqual(db.session.get(Usuario,2).dni,'00000002')

    def test_completar_pendiente_no_duplica_y_conserva_semana(self):
        datos={'id_usuario':2,'fecha':'2026-09-10','monto':100,'tipo':'Salario semanal','estado':'Pendiente'}
        r=self.call('post','/personal/pagos',json=datos)
        self.assertEqual(r.status_code,200)
        self.assertEqual(self.call('post','/personal/pagos',json={**datos,'estado':'Pagado'}).status_code,409)
        for _ in range(2):
            self.assertEqual(self.call('put',f"/personal/pagos/{r.json['data']['id_pago']}",json={'estado':'Pagado'}).status_code,200)
        self.assertEqual(PagoEmpleado.query.count(),1)
        self.assertEqual(PagoPersonal.query.first().estado,'Pagado')
        self.assertEqual(self.nomina()['pagos_sueldo'],100)

    def test_pago_antiguo_requiere_clasificar(self):
        self.sueldo()
        p=PagoEmpleado(id_usuario=2,monto=50,estado='Pagado',fecha_pago=instante('2026-09-10T12:00:00'))
        db.session.add(p); db.session.commit()
        self.assertIsNone(self.nomina()['saldo'])
        self.assertEqual(self.call('put',f'/personal/pagos/{p.id_pago}',json={'tipo':'Bono'}).status_code,200)
        self.assertEqual(self.nomina()['saldo'],350)

    def test_cocina_rechaza_cantidades_no_finitas(self):
        self.producto()
        for cantidad in ('Infinity','NaN',-1,.0001):
            self.assertEqual(self.call('post','/cocina/solicitudes',role=3,json={'id_producto':1,'cantidad':cantidad}).status_code,400)
        self.assertEqual(SolicitudInsumo.query.count(),0)

    def test_falta_tabla_informa_actualizacion_pendiente(self):
        SueldoSemanal.__table__.drop(db.engine)
        self.assertEqual(self.call('get','/personal/salarios').status_code,503)

    def test_consulta_dni_exige_admin_y_limita_consumo(self):
        self.assertEqual(self.client.get('/api/dni/00000002').status_code,401)
        self.assertEqual(self.call('get','/dni/00000002',role=2).status_code,403)
        with patch.dict('os.environ',{'DNI_API_TOKEN':'token-ficticio'}), patch('api.dni.requests.get') as proveedor:
            proveedor.return_value=Mock(status_code=200, json=lambda:{'success':True,'nombres':'Ana'})
            for _ in range(10):
                self.assertEqual(self.call('get','/dni/00000002').status_code,200)
            self.assertEqual(self.call('get','/dni/00000002').status_code,429)
            self.assertEqual(proveedor.call_count,10)
