from datetime import timedelta
from unittest.mock import patch, Mock
from tests.test_flows import BaseFlujos, instante
from models import db, Usuario, PagoEmpleado, PagoPersonal, Adelanto, DescuentoSemanal, CierreCaja, SolicitudInsumo, SueldoSemanal, SesionUsuario, TransaccionCaja, InventarioMovimiento, CompraInventario
from api.sesiones import crear_sesion
import bcrypt


class RevisionFlujosTest(BaseFlujos):
    def test_filtro_de_pagos_rechaza_meses_invalidos_y_respeta_lima(self):
        for ruta in ('/personal/pagos', '/personal/pagos/empleado/2'):
            for parametros in ('mes=13', 'mes=0', 'anio=abc', 'anio=9999'):
                respuesta = self.call('get', f'{ruta}?{parametros}')
                self.assertEqual(respuesta.status_code, 400)
                self.assertEqual(respuesta.json['message'], 'Mes o año no válido.')

        db.session.add(PagoEmpleado(id_usuario=2, monto=25,
            fecha_pago=instante('2026-09-21T02:00:00'), estado='Pendiente'))
        db.session.commit()
        with patch('api.personal.ahora', return_value=instante('2026-09-21T01:00:00')):
            self.assertEqual(self.call('get', '/personal/pagos').json['data']['proximo_pago'], 0)

        PagoEmpleado.query.delete()
        db.session.add(PagoEmpleado(id_usuario=2, monto=25,
            fecha_pago=instante('2026-09-21T06:00:00'), estado='Pendiente'))
        db.session.commit()
        with patch('api.personal.ahora', return_value=instante('2026-09-21T01:00:00')):
            self.assertEqual(self.call('get', '/personal/pagos').json['data']['proximo_pago'], 1)

    def test_fechas_se_muestran_en_espanol_y_con_zona_horaria(self):
        with patch('api.cocina._ahora', return_value=instante('2026-09-21T02:00:00')):
            cocina = self.call('get', '/cocina/dashboard', role=3).json['data']
        with patch('api.trabajador._ahora', return_value=instante('2026-09-21T02:00:00')):
            trabajador = self.call('get', '/trabajador/dashboard', role=4).json['data']
        self.assertEqual(cocina['fecha'], 'domingo, 20 de septiembre de 2026')
        self.assertEqual(trabajador['fecha'], cocina['fecha'])
        db.session.add(TransaccionCaja(id_usuario=2, tipo='Venta', monto=10,
            metodo_pago='Efectivo', fecha=instante('2025-06-01T00:00:00')))
        db.session.commit()
        reporte = self.call('get', '/caja/reportes?periodo=mes&fecha=2025-05-15', role=2).json['data']
        self.assertEqual(reporte['transacciones'][0]['fecha'], '2025-06-01T00:00:00+00:00')

    def test_turnos_respetan_el_lunes_en_lima(self):
        with patch('api.trabajador._ahora', return_value=instante('2026-09-21T02:00:00')):
            semana = self.call('get', '/trabajador/turnos', role=4).json['data']['semana']
        self.assertEqual(semana[0]['fecha'], '14/09/2026')
        self.assertEqual(semana[-1]['fecha'], '20/09/2026')

    def test_panel_y_reporte_comparten_el_mismo_calculo(self):
        db.session.add_all([
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=25, fecha=instante('2026-09-10T16:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Gasto', monto=7, fecha=instante('2026-09-10T17:00:00')),
        ])
        db.session.commit()
        reporte = self.call('get', '/caja/reportes?periodo=mes&fecha=2026-09-10', role=2).json['data']
        with patch('api.caja._historial', side_effect=AssertionError('El panel no debe cargar cierres')):
            panel = self.call('get', '/rendimiento?periodo=mes&fecha=2026-09-10', role=2).json['data']
        self.assertEqual(panel, reporte['puntos'])

    def test_historial_limita_la_consulta_al_ultimo_cierre(self):
        cierre = instante('2025-04-01T16:00:00')
        db.session.add(CierreCaja(id_usuario=1, estado='cerrada',
            fecha=instante('2025-04-01T15:00:00'), fecha_cierre=cierre,
            total_ventas=0, total_gastos=0))
        db.session.commit()
        from api import caja as caja_api
        real = caja_api._movimientos
        limites = []

        def registrar(inicio, fin):
            limites.append((inicio, fin))
            return real(inicio, fin)

        with patch('api.caja._movimientos', side_effect=registrar):
            self.assertEqual(self.call('get', '/caja/historial').status_code, 200)
        self.assertEqual(limites, [(instante('2025-04-01T15:00:00'), cierre)])

    def test_reintento_de_caja_no_duplica_movimiento(self):
        self.call('post', '/caja/abrir', role=2, json={'monto_inicial': 0})
        datos = {'tipo': 'Venta', 'monto': 20, 'metodo_pago': 'Yape',
                 'descripcion': 'Almuerzo', 'clave_operacion': '73a294b3-7a75-4d04-8349-fdb5eb2608fc'}
        primera = self.call('post', '/caja/transacciones', role=2, json=datos)
        segunda = self.call('post', '/caja/transacciones', role=2, json=datos)
        self.assertEqual((primera.status_code, segunda.status_code), (200, 200))
        self.assertTrue(segunda.json['repetida'])
        self.assertEqual(TransaccionCaja.query.count(), 1)
        self.assertEqual(self.call('post', '/caja/transacciones', role=2,
            json={**datos, 'monto': 21}).status_code, 409)

    def test_importes_decimales_no_acumulan_error_binario(self):
        self.call('post', '/caja/abrir', role=2, json={'monto_inicial': 0})
        for monto, clave in ((0.1, 'b6c70902-134d-4f4a-bccd-68669687e75f'),
                             (0.2, '23e8d6f0-f8d9-4548-ad22-cdc680c182c3')):
            self.assertEqual(self.call('post', '/caja/transacciones', role=2, json={
                'tipo': 'Venta', 'monto': monto, 'metodo_pago': 'Efectivo',
                'descripcion': 'Prueba decimal', 'clave_operacion': clave}).status_code, 200)
        cierre = self.call('post', '/caja/cerrar', role=2).json['data']
        self.assertEqual(cierre['total_ventas'], 0.3)

    def test_reintento_de_stock_no_modifica_dos_veces(self):
        self.producto(10)
        datos = {'cantidad': 4, 'motivo': 'Reposición',
                 'clave_operacion': '9812f479-ab44-42d1-9f0e-2c84652b5e79'}
        for _ in range(2):
            self.assertEqual(self.call('post', '/inventario/productos/1/stock/entrada', role=3,
                json=datos).status_code, 200)
        self.assertEqual(float(self.producto_actual().stock), 14)
        self.assertEqual(InventarioMovimiento.query.count(), 1)
        self.assertEqual(self.call('post', '/inventario/productos/1/stock/entrada', role=3,
            json={**datos, 'cantidad': 5}).status_code, 409)

    def test_reintento_de_compra_no_duplica_compra_ni_stock(self):
        self.producto(0)
        datos = {'detalle': [{'id_producto': 1, 'cantidad': 2, 'precio_unitario': 4}],
                 'notas': 'Mercado', 'clave_operacion': '0a9615ab-d611-4648-bb5b-52591b63bf75'}
        primera = self.call('post', '/inventario/compras', json=datos)
        segunda = self.call('post', '/inventario/compras', json=datos)
        self.assertEqual((primera.status_code, segunda.status_code), (201, 200))
        self.assertTrue(segunda.json['repetida'])
        self.assertEqual(CompraInventario.query.count(), 1)
        self.assertEqual(float(self.producto_actual().stock), 2)

    def test_compra_suma_subtotales_redondeados_por_linea(self):
        self.producto(0)
        datos = {'detalle': [
            {'id_producto': 1, 'cantidad': 0.126, 'precio_unitario': 1},
            {'id_producto': 1, 'cantidad': 0.126, 'precio_unitario': 1},
        ]}
        respuesta = self.call('post', '/inventario/compras', json=datos)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json['data']['total_compra'], 0.26)
        self.assertEqual([d['subtotal'] for d in respuesta.json['data']['detalle']], [0.13, 0.13])

    def test_reintento_de_pago_y_dos_pagos_legitimos_iguales(self):
        datos = {'id_usuario': 2, 'fecha': '2026-09-10', 'monto': 25,
                 'tipo': 'Bono', 'estado': 'Pagado', 'descripcion': 'Rendimiento',
                 'clave_operacion': 'e24c270b-ff3f-44d7-a891-e2494bcd0059'}
        primera = self.call('post', '/personal/pagos', json=datos)
        segunda = self.call('post', '/personal/pagos', json=datos)
        self.assertEqual((primera.status_code, segunda.status_code), (200, 200))
        self.assertTrue(segunda.json['repetida'])
        self.assertEqual(PagoEmpleado.query.count(), 1)
        self.assertEqual(PagoPersonal.query.count(), 1)
        self.assertEqual(self.call('post', '/personal/pagos', json={**datos, 'monto': 30}).status_code, 409)
        tercero = self.call('post', '/personal/pagos', json={**datos,
            'clave_operacion': 'd3907898-0872-450a-9b90-533694b6f374'})
        self.assertEqual(tercero.status_code, 200)
        self.assertEqual(PagoEmpleado.query.count(), 2)

    def producto_actual(self):
        from models import Producto
        return db.session.get(Producto, 1)

    def test_desactivar_usuario_o_rol_bloquea_sesion_anterior(self):
        usuario = db.session.get(Usuario, 2)
        token, refresh = crear_sesion(usuario)
        self.tokens[2] = (token, refresh)
        db.session.add(Adelanto(id_usuario=2, monto=15, motivo='Prueba', estado='Pendiente', fecha=instante('2026-09-20T12:00:00')))
        db.session.commit()
        adelanto = Adelanto.query.one()
        for objeto in (usuario, usuario.rol):
            objeto.estado = False
            db.session.commit()
            self.assertEqual(self.call('delete', f'/perfil/adelantos/{adelanto.id_adelanto}', role=2).status_code, 401)
            self.assertEqual(self.client.post('/api/auth/refresh', headers={'Authorization':'Bearer '+refresh}).status_code, 401)
            self.assertEqual(db.session.get(Adelanto, adelanto.id_adelanto).estado, 'Pendiente')
            objeto.estado = True
            db.session.commit()

    def test_pagos_iguales_distinguen_concepto_y_semana(self):
        datos = {'id_usuario':2, 'monto':25, 'fecha':'2026-09-20', 'tipo':'Salario semanal'}
        self.assertEqual(self.call('post','/personal/pagos',json=datos).status_code, 200)
        datos['tipo'] = 'Bono'
        self.assertEqual(self.call('post','/personal/pagos',json=datos).status_code, 200)
        self.assertEqual(self.call('post','/personal/pagos',json=datos).status_code, 400)
        datos.update(tipo='Salario semanal', semana='2026-09-07')
        self.assertEqual(self.call('post','/personal/pagos',json=datos).status_code, 200)

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
