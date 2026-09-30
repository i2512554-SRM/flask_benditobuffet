from datetime import date, datetime, timezone
import bcrypt
from unittest.mock import patch

from bd import db
from models import (Adelanto, InventarioMovimiento, Notificacion, PagoEmpleado, Producto, SolicitudInsumo,
                    SueldoSemanal, TransaccionCaja, Usuario)
from tests.test_flows import BaseFlujos, instante


class CorreccionesTest(BaseFlujos):
    def test_cambiar_contrasena_entrega_sesion_nueva(self):
        usuario = db.session.get(Usuario, 2)
        usuario.clave = bcrypt.hashpw(b'unused', bcrypt.gensalt()).decode()
        db.session.commit()
        anterior = self.call('get', '/auth/me', role=2)
        self.assertEqual(anterior.status_code, 200)
        respuesta = self.call('put', '/perfil/contrasena', role=2, json={
            'contrasena_actual': 'unused', 'contrasena_nueva': 'nueva-clave-segura',
            'contrasena_verificar': 'nueva-clave-segura'})
        self.assertEqual(respuesta.status_code, 200)
        nuevo = respuesta.json['data']['token']
        self.assertTrue(respuesta.json['data']['refresh_token'])
        self.assertEqual(self.call('get', '/auth/me', role=2).status_code, 401)
        con_nuevo = self.client.get('/api/auth/me', headers={'Authorization': 'Bearer ' + nuevo})
        self.assertEqual(con_nuevo.status_code, 200)

    def test_kpi05_ignora_semanas_previas_al_primer_sueldo(self):
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:00:00')):
            self.call('post', '/caja/abrir', json={})
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:01:00')):
            self.call('post', '/caja/transacciones', role=2, json={'tipo': 'Venta', 'monto': 1000, 'metodo_pago': 'Yape'})
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:02:00')):
            self.call('post', '/caja/cerrar')
        db.session.get(Usuario, 4).estado = False
        db.session.add(SueldoSemanal(id_usuario=2, desde=date(2026, 8, 31), monto=100,
                                     registrado_por=1, fecha=instante('2026-08-31T12:00:00')))
        db.session.add(SueldoSemanal(id_usuario=3, desde=date(2026, 9, 14), monto=70,
                                     registrado_por=1, fecha=instante('2026-09-14T12:00:00')))
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-10-02T00:00:00')):
            kpis = {k['codigo']: k for k in self.call('get', '/indicadores?periodo=mes&fecha=2026-09-10').json['data']['kpis']}
        self.assertEqual(kpis['KPI-05']['detalle']['empleados_sin_sueldo'], 0)
        self.assertIsNotNone(kpis['KPI-05']['valor'])
        self.assertGreater(kpis['KPI-05']['detalle']['costo_laboral'], 428.57)

    def test_kpi05_marca_empleado_sin_ningun_sueldo(self):
        db.session.add(SueldoSemanal(id_usuario=2, desde=date(2026, 8, 31), monto=100,
                                     registrado_por=1, fecha=instante('2026-08-31T12:00:00')))
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-10-02T00:00:00')):
            kpis = {k['codigo']: k for k in self.call('get', '/indicadores?periodo=mes&fecha=2026-09-10').json['data']['kpis']}
        self.assertEqual(kpis['KPI-05']['detalle']['empleados_sin_sueldo'], 2)
        self.assertIsNone(kpis['KPI-05']['valor'])

    def test_eliminar_producto_con_solicitudes_lo_desactiva(self):
        self.producto(stock=0)
        db.session.add(SolicitudInsumo(id_usuario=3, id_producto=1, cantidad=2, estado='Pendiente',
                                       fecha=datetime.now(timezone.utc)))
        db.session.commit()
        respuesta = self.call('delete', '/inventario/productos/1')
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(db.session.get(Producto, 1).estado)

    def test_eliminar_producto_sin_historial_lo_borra(self):
        self.producto(stock=0)
        self.assertEqual(self.call('delete', '/inventario/productos/1').status_code, 200)
        self.assertIsNone(db.session.get(Producto, 1))

    def test_motivo_de_stock_se_valida(self):
        self.producto()
        for datos in ({'cantidad': 1, 'motivo': 123}, {'cantidad': 1, 'motivo': 'x' * 256},
                      {'cantidad': 1, 'motivo': 'ok', 'observacion': ['x']}):
            self.assertEqual(self.call('post', '/inventario/productos/1/stock/entrada', json=datos).status_code, 400)
            self.assertEqual(self.call('post', '/inventario/productos/1/stock/salida', json=datos).status_code, 400)
        self.assertEqual(self.call('post', '/inventario/productos/1/stock/salida', json={'cantidad': 1}).status_code, 400)
        self.assertEqual(self.call('post', '/inventario/productos/1/stock/entrada', json={'cantidad': 1}).status_code, 200)

    def test_respuesta_de_adelanto_limitada(self):
        db.session.add(Adelanto(id_usuario=2, motivo='Salud', monto=50, estado='Pendiente',
                                fecha=datetime.now(timezone.utc)))
        db.session.commit()
        larga = self.call('put', '/admin/adelantos/1', json={'accion': 'aprobar', 'respuesta': 'x' * 301})
        self.assertEqual(larga.status_code, 400)
        valida = self.call('put', '/admin/adelantos/1', json={'accion': 'aprobar', 'respuesta': 'x' * 300})
        self.assertEqual(valida.status_code, 200)
        self.assertLessEqual(len(Notificacion.query.one().mensaje), 500)

    def test_crear_empleado_rol_no_numerico(self):
        respuesta = self.call('post', '/personal/', json={
            'dni': '12345678', 'nombres': 'Luis', 'apellido': 'Rojas', 'clave': 'clave-segura', 'id_rol': 'abc'})
        self.assertEqual(respuesta.status_code, 400)

    def test_estado_invalido_de_pago_y_adelanto(self):
        pago = self.call('post', '/personal/pagos', json={'id_usuario': 2, 'monto': 50, 'estado': 'Regalado'})
        self.assertEqual(pago.status_code, 400)
        self.assertEqual(PagoEmpleado.query.count(), 0)
        adelanto = self.call('post', '/personal/pagos/adelanto', json={
            'id_usuario': 2, 'monto': 50, 'motivo': 'Salud', 'estado': 'Pagado'})
        self.assertEqual(adelanto.status_code, 400)

    def test_resumen_de_perfil_cuenta_todo(self):
        for i in range(8):
            db.session.add(PagoEmpleado(id_usuario=2, monto=10, estado='Pagado',
                                        fecha_pago=datetime(2026, 9, i + 1, tzinfo=timezone.utc)))
        db.session.commit()
        datos = self.call('get', '/perfil', role=2).json['data']
        self.assertEqual(len(datos['pagos']), 6)
        self.assertEqual(datos['resumen']['pagos'], 8)

    def test_editar_perfil_parcial_conserva_campos(self):
        usuario = db.session.get(Usuario, 2)
        usuario.telefono = '987654321'
        db.session.commit()
        respuesta = self.call('put', '/perfil', role=2, data={}, content_type='multipart/form-data')
        self.assertEqual(respuesta.status_code, 200)
        self.call('put', '/perfil', role=2, json={'telefono': '912345678'})
        db.session.expire_all()
        usuario = db.session.get(Usuario, 2)
        self.assertEqual(usuario.correo, 'u2@example.test')
        self.assertEqual(usuario.telefono, '912345678')

    def test_permisos_responden_con_error(self):
        for ruta in ('/personal/', '/admin/roles', '/indicadores'):
            respuesta = self.call('get', ruta, role=2)
            self.assertEqual(respuesta.status_code, 403, ruta)
            self.assertIn('error', respuesta.json, ruta)
        self.assertEqual(self.call('get', '/cocina/dashboard', role=4).status_code, 403)
        self.assertEqual(self.call('get', '/cocina/dashboard', role=3).status_code, 200)
        self.assertEqual(self.call('get', '/trabajador/dashboard', role=1).status_code, 403)
        self.assertEqual(self.call('get', '/trabajador/dashboard', role=4).status_code, 200)

    def test_indicadores_no_consultan_por_cada_punto(self):
        from sqlalchemy import event
        consultas = []
        contar = lambda *args, **kwargs: consultas.append(1)
        event.listen(db.engine, 'before_cursor_execute', contar)
        try:
            with patch('api.indicadores.ahora', return_value=instante('2026-10-02T00:00:00')):
                respuesta = self.call('get', '/indicadores?inicio=2025-09-01&fin=2026-09-30')
        finally:
            event.remove(db.engine, 'before_cursor_execute', contar)
        self.assertEqual(respuesta.status_code, 200)
        self.assertLess(len(consultas), 40)

    def test_login_rechaza_claves_en_texto_plano(self):
        usuario = db.session.get(Usuario, 2)
        usuario.clave = 'clave-en-texto'
        db.session.commit()
        plano = self.client.post('/api/auth/login', json={'usuario': 'user2', 'clave': 'clave-en-texto'})
        self.assertEqual(plano.status_code, 401)
        usuario.clave = bcrypt.hashpw(b'clave-segura-1', bcrypt.gensalt()).decode()
        db.session.commit()
        valido = self.client.post('/api/auth/login', json={'usuario': 'user2', 'clave': 'clave-segura-1'})
        self.assertEqual(valido.status_code, 200)
        inexistente = self.client.post('/api/auth/login', json={'usuario': 'nadie', 'clave': 'x'})
        self.assertEqual(inexistente.status_code, 401)

    def test_anular_inversion_conserva_historial(self):
        creada = self.call('post', '/inventario/inversiones', json={'descripcion': 'Cocina nueva', 'monto': 500})
        id_inversion = creada.json['data']['id_inversion']
        self.assertEqual(self.call('get', '/inventario/resumen').json['data']['inversiones_mes'], 500)
        anulada = self.call('delete', f'/inventario/inversiones/{id_inversion}')
        self.assertEqual(anulada.status_code, 200)
        self.assertEqual(anulada.json['data']['estado'], 'Anulada')
        self.assertIsNotNone(anulada.json['data']['fecha_anulacion'])
        self.assertEqual(self.call('delete', f'/inventario/inversiones/{id_inversion}').status_code, 409)
        resumen = self.call('get', '/inventario/resumen').json['data']
        self.assertEqual(resumen['inversiones_mes'], 0)
        self.assertIsNone(resumen['ultima_inversion'])
        listado = self.call('get', '/inventario/inversiones').json['data']
        self.assertEqual([i['estado'] for i in listado], ['Anulada'])

    def test_compras_usan_costo_promedio_ponderado(self):
        self.producto(stock=10)
        producto = db.session.get(Producto, 1)
        producto.costo = 2
        db.session.commit()
        compra = self.call('post', '/inventario/compras', json={'detalle': [
            {'id_producto': 1, 'cantidad': 10, 'precio_unitario': 4}]})
        self.assertEqual(compra.status_code, 201)
        db.session.expire_all()
        self.assertEqual(float(db.session.get(Producto, 1).costo), 3.0)
        self.assertEqual(float(db.session.get(Producto, 1).stock), 20.0)
        self.assertEqual(self.call('delete', f"/inventario/compras/{compra.json['data']['id_compra']}").status_code, 200)
        db.session.expire_all()
        self.assertEqual(float(db.session.get(Producto, 1).costo), 2.0)
        self.assertEqual(float(db.session.get(Producto, 1).stock), 10.0)

    def test_consulta_dni_solo_devuelve_campos_necesarios(self):
        cuerpo = {'success': True, 'dni': '12345678', 'nombres': 'ANA', 'apellidoPaterno': 'PEREZ',
                  'apellidoMaterno': 'ROJAS', 'direccion': 'Av. Siempre Viva 123', 'ubigeo': '150101'}
        with patch.dict('os.environ', {'DNI_API_TOKEN': 'token-ficticio'}), patch('api.dni.requests.get') as proveedor:
            proveedor.return_value.status_code = 200
            proveedor.return_value.json.return_value = cuerpo
            respuesta = self.call('get', '/dni/12345678')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(set(respuesta.json), {'success', 'dni', 'nombres', 'apellidoPaterno', 'apellidoMaterno'})

    def test_listado_de_compras_incluye_cantidad_de_productos(self):
        self.producto(stock=0)
        compra = self.call('post', '/inventario/compras', json={'detalle': [
            {'id_producto': 1, 'cantidad': 2, 'precio_unitario': 3},
            {'id_producto': 1, 'cantidad': 1, 'precio_unitario': 3}]})
        self.assertEqual(compra.status_code, 201)
        self.assertEqual(compra.json['data']['n_detalle'], 2)
        self.assertEqual(self.call('get', '/inventario/compras').json['data'][0]['n_detalle'], 2)

    def test_indicadores_reutilizan_calculo_hasta_que_cambian_los_datos(self):
        from sqlalchemy import event
        consultas = []
        contar = lambda *args, **kwargs: consultas.append(1)
        ruta = '/indicadores?periodo=mes&fecha=2026-09-10'
        event.listen(db.engine, 'before_cursor_execute', contar)
        try:
            with patch('api.indicadores.ahora', return_value=instante('2026-09-20T15:00:00')):
                primera = self.call('get', ruta)
                antes = len(consultas)
                segunda = self.call('get', ruta)
                reutilizada = len(consultas) - antes
                self.assertEqual(self.call('post', '/caja/abrir', json={}).status_code, 200)
                tras_cambio = self.call('get', ruta)
                forzada = self.call('get', ruta + '&refrescar=1')
        finally:
            event.remove(db.engine, 'before_cursor_execute', contar)
        self.assertFalse(primera.json['data']['desde_cache'])
        self.assertTrue(segunda.json['data']['desde_cache'])
        self.assertLess(reutilizada, 5)
        self.assertEqual(primera.json['data']['kpis'], segunda.json['data']['kpis'])
        self.assertFalse(tras_cambio.json['data']['desde_cache'])
        self.assertFalse(forzada.json['data']['desde_cache'])
        self.assertTrue(primera.json['data']['calculado'])

    def test_despensa_informa_el_producto_de_cada_insumo_critico(self):
        self.producto(stock=2)
        db.session.get(Producto, 1).fecha_registro = instante('2026-08-01T00:00:00')
        db.session.add(InventarioMovimiento(id_producto=1, id_usuario=3, tipo='Salida', cantidad=-4,
                                            motivo='Preparación', fecha=instante('2026-09-15T12:00:00')))
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-09-20T15:00:00')):
            kpis = {k['codigo']: k for k in self.call('get', '/indicadores?periodo=mes&fecha=2026-09-10').json['data']['kpis']}
        self.assertEqual(kpis['KPI-03']['serie'][0]['id_producto'], 1)

    def test_mercaderia_sin_moverse_excluye_equipamiento(self):
        from models import Categoria
        db.session.add(Categoria(id_categoria=2, nombre='Equipamiento', fecha_creacion=instante('2026-01-01T00:00:00')))
        self.producto(stock=10)
        producto = db.session.get(Producto, 1)
        producto.costo = 2
        producto.fecha_registro = instante('2026-08-01T00:00:00')
        db.session.add(Producto(id_producto=2, nombre='Cocina industrial', precio=0, costo=2500, stock=1,
                                unidad_medida='Un', id_categoria=2, estado=True,
                                fecha_registro=instante('2026-08-01T00:00:00'), fecha_edicion=instante('2026-08-01T00:00:00')))
        db.session.add(InventarioMovimiento(id_producto=1, id_usuario=3, tipo='Salida', cantidad=-1,
                                            motivo='Preparación', fecha=instante('2026-09-15T12:00:00')))
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-09-20T15:00:00')):
            kpis = {k['codigo']: k for k in self.call('get', '/indicadores?periodo=mes&fecha=2026-09-10').json['data']['kpis']}
        self.assertEqual(kpis['KPI-08']['valor'], 0)
        self.assertEqual(kpis['KPI-08']['detalle']['valor_total'], 20)

    def test_periodo_en_curso_se_compara_con_el_mismo_tramo(self):
        self.call('post', '/caja/abrir', json={})
        for fecha, monto in (('2026-08-05T17:00:00', 100), ('2026-08-25T17:00:00', 900), ('2026-09-05T17:00:00', 110)):
            db.session.add(TransaccionCaja(id_usuario=2, tipo='Venta', monto=monto, metodo_pago='Yape', fecha=instante(fecha)))
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-09-10T15:00:00')):
            data = self.call('get', '/indicadores?periodo=mes&fecha=2026-09-10&refrescar=1').json['data']
        kpis = {k['codigo']: k for k in data['kpis']}
        self.assertTrue(data['comparacion_parcial'])
        self.assertTrue(data['prev_fin'].startswith('2026-08-10'))
        self.assertEqual(kpis['KPI-02']['detalle']['ventas_anterior'], 100)
        self.assertEqual(kpis['KPI-02']['valor'], 10)

    def test_historial_y_reportes_de_caja_no_consultan_usuarios_por_fila(self):
        from sqlalchemy import event
        from models import CierreCaja
        for dia in range(1, 21):
            db.session.add(CierreCaja(id_usuario=2, monto_inicial=100, total_ventas=0, total_gastos=0, estado='cerrada',
                                      fecha=instante(f'2026-09-{dia:02d}T16:00:00'), fecha_cierre=instante(f'2026-09-{dia:02d}T23:00:00')))
            db.session.add(TransaccionCaja(id_usuario=2 if dia % 2 else 1, tipo='Venta', monto=10, metodo_pago='Yape',
                                           fecha=instante(f'2026-09-{dia:02d}T18:00:00')))
        db.session.commit()
        db.session.expunge_all()
        consultas = []
        contar = lambda conexion, cursor, sql, *resto: consultas.append(sql)
        event.listen(db.engine, 'before_cursor_execute', contar)
        try:
            historial = self.call('get', '/caja/historial', role=2)
            reporte = self.call('get', '/caja/reportes?periodo=mes&fecha=2026-09-15', role=2)
        finally:
            event.remove(db.engine, 'before_cursor_execute', contar)
        self.assertEqual(len(historial.json['data']), 20)
        self.assertEqual(len(reporte.json['data']['transacciones']), 20)
        consultas_usuarios = [sql for sql in consultas if 'FROM usuarios' in sql and 'sesiones_usuario' not in sql]
        self.assertLess(len(consultas_usuarios), 12)

    def _kpis(self, ruta='/indicadores?periodo=mes&fecha=2026-09-10'):
        with patch('api.indicadores.ahora', return_value=instante('2026-09-20T15:00:00')):
            return {k['codigo']: k for k in self.call('get', ruta).json['data']['kpis']}

    def test_metas_de_indicadores_se_ajustan_y_restauran(self):
        limites = self._kpis()['KPI-04']['limites']
        self.assertEqual((limites['atencion'], limites['revisar'], limites['personalizada']), (5, 10, False))
        self.assertEqual(limites['sugerido'], {'atencion': 5, 'revisar': 10})
        self.assertFalse(limites['mayor_es_mejor'])

        respuesta = self.call('put', '/indicadores/metas/KPI-04', json={'atencion': 8, 'revisar': '12.345'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json['data']['revisar'], 12.35)
        self.assertEqual(respuesta.json['data']['actualizado_por'], 'Ana Pérez')

        limites = self._kpis()['KPI-04']['limites']
        self.assertEqual((limites['atencion'], limites['revisar'], limites['personalizada']), (8, 12.35, True))
        self.assertTrue(limites['actualizado_en'].endswith('+00:00'))
        self.assertEqual(self._kpis()['KPI-05']['limites']['personalizada'], False)

        restaurada = self.call('delete', '/indicadores/metas/KPI-04')
        self.assertEqual(restaurada.status_code, 200)
        self.assertFalse(restaurada.json['data']['personalizada'])
        self.assertEqual(self._kpis()['KPI-04']['limites']['atencion'], 5)

    def test_metas_de_indicadores_validan_orden_rango_y_permisos(self):
        casos = [
            ('KPI-03', {'atencion': 2, 'revisar': 5}, 400),
            ('KPI-04', {'atencion': 12, 'revisar': 8}, 400),
            ('KPI-04', {'atencion': 50, 'revisar': 150}, 400),
            ('KPI-04', {'atencion': 5}, 400),
            ('KPI-04', {'atencion': True, 'revisar': 10}, 400),
            ('KPI-04', {'atencion': 'nan', 'revisar': 10}, 400),
            ('KPI-99', {'atencion': 5, 'revisar': 10}, 404),
        ]
        for codigo, cuerpo, estado in casos:
            with self.subTest(codigo=codigo, cuerpo=cuerpo):
                respuesta = self.call('put', f'/indicadores/metas/{codigo}', json=cuerpo)
                self.assertEqual(respuesta.status_code, estado)
                self.assertFalse(respuesta.json['success'])
                self.assertTrue(respuesta.json['error'])
        self.assertEqual(self.call('put', '/indicadores/metas/KPI-04', role=2, json={'atencion': 5, 'revisar': 10}).status_code, 403)
        self.assertEqual(self.call('delete', '/indicadores/metas/KPI-04', role=2).status_code, 403)

    def test_despensa_cuenta_insumos_criticos_con_la_meta_ajustada(self):
        self.producto(stock=5)
        db.session.get(Producto, 1).fecha_registro = instante('2026-08-01T00:00:00')
        db.session.add(InventarioMovimiento(id_producto=1, id_usuario=3, tipo='Salida', cantidad=-1,
                                            motivo='Preparación', fecha=instante('2026-09-15T12:00:00')))
        db.session.commit()
        antes = self._kpis()['KPI-03']['detalle']
        self.assertEqual((antes['productos_bajo_umbral'], antes['umbral_dias']), (1, 7))
        self.assertEqual(self.call('put', '/indicadores/metas/KPI-03', json={'atencion': 4, 'revisar': 2}).status_code, 200)
        despues = self._kpis()['KPI-03']['detalle']
        self.assertEqual((despues['productos_bajo_umbral'], despues['umbral_dias']), (0, 4))
