import io
from datetime import date
from pathlib import Path
from unittest.mock import patch

from bd import db
from models import (
    ActividadUsuario, Adelanto, AtencionInsumo, BloqueoLogin, Categoria,
    CompraInventario, IntentoLogin, InventarioMovimiento, Inversion, Notificacion,
    PagoEmpleado, PagoPersonal, Producto, Proveedor, SolicitudInsumo, TransaccionCaja,
    Usuario, UsuarioPerfil,
)
from tests.test_flows import BaseFlujos, instante


class CalidadDatosTest(BaseFlujos):
    def test_consultar_perfil_no_marca_notificaciones(self):
        for i in range(2):
            db.session.add(Notificacion(id_usuario=2, titulo=f'Aviso {i}', mensaje='Adelanto aprobado',
                                        leida=False, fecha=instante(f'2026-09-10T1{i}:00:00')))
        db.session.commit()

        primera = self.call('get', '/perfil', role=2)
        segunda = self.call('get', '/perfil', role=2)
        self.assertEqual(len(primera.json['data']['notificaciones']), 2)
        self.assertEqual(len(segunda.json['data']['notificaciones']), 2)
        self.assertEqual(Notificacion.query.filter_by(leida=False).count(), 2)

        id_primera = primera.json['data']['notificaciones'][0]['id_notificacion']
        self.assertEqual(self.call('post', '/perfil/notificaciones/leer', role=2,
                                   json={'id_notificacion': id_primera}).status_code, 204)
        self.assertEqual(Notificacion.query.filter_by(leida=False).count(), 1)
        self.assertEqual(self.call('post', '/perfil/notificaciones/leer', role=2).status_code, 204)
        self.assertEqual(Notificacion.query.filter_by(leida=False).count(), 0)

    def test_foto_nueva_se_compensa_si_falla_el_commit(self):
        anterior = Path(self.folder.name) / 'anterior.png'
        anterior.write_bytes(b'foto anterior')
        db.session.add(UsuarioPerfil(id_usuario=2, foto_perfil=anterior.name))
        db.session.commit()
        self.call('get', '/perfil', role=2)

        with patch('api.perfil.db.session.commit', side_effect=RuntimeError('fallo simulado')):
            respuesta = self.call('put', '/perfil', role=2, data={
                'correo': 'u2@example.test',
                'telefono': '999999999',
                'foto_perfil': (io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\0' * 32), 'nueva.png'),
            }, content_type='multipart/form-data')

        self.assertEqual(respuesta.status_code, 500)
        db.session.expire_all()
        self.assertEqual(db.session.get(UsuarioPerfil, 1).foto_perfil, anterior.name)
        self.assertEqual([p.name for p in Path(self.folder.name).iterdir()], [anterior.name])

    def test_historial_y_totales_usan_fecha_de_gestion_del_adelanto(self):
        db.session.add(Adelanto(
            id_usuario=2, monto=30, motivo='Viaje', estado='Aprobado',
            fecha=instante('2026-08-31T18:00:00'),
            fecha_gestion=instante('2026-09-01T15:00:00'),
        ))
        db.session.commit()

        agosto = self.call('get', '/personal/pagos?mes=8&anio=2026').json['data']
        septiembre = self.call('get', '/personal/pagos?mes=9&anio=2026').json['data']
        self.assertEqual(agosto['totales']['adelantos'], 0)
        self.assertFalse(any(str(x['id_pago']).startswith('adelanto-') for x in agosto['historial']))
        self.assertEqual(septiembre['totales']['adelantos'], 30)
        adelanto = next(x for x in septiembre['historial'] if str(x['id_pago']).startswith('adelanto-'))
        self.assertEqual(adelanto['fecha'], '2026-09-01T15:00:00+00:00')

    def test_perfil_emite_datetime_utc_y_date_sin_hora(self):
        usuario = db.session.get(Usuario, 2)
        usuario.fecha_creacion = instante('2026-09-08T13:00:00')
        db.session.add_all([
            UsuarioPerfil(id_usuario=2, fecha_ingreso=date(2026, 9, 8)),
            PagoEmpleado(
                id_usuario=2, monto=40, estado='Pagado',
                fecha_pago=instante('2026-09-10T15:00:00'),
            ),
            Adelanto(
                id_usuario=2, monto=20, motivo='Transporte', estado='Pendiente',
                fecha=instante('2026-09-10T16:00:00'),
            ),
            ActividadUsuario(
                id_usuario=2, accion='Actividad de prueba',
                fecha=instante('2026-09-10T17:00:00'),
            ),
        ])
        db.session.commit()

        datos = self.call('get', '/perfil', role=2).json['data']

        self.assertEqual(datos['usuario']['fecha_creacion'], '2026-09-08T13:00:00+00:00')
        self.assertEqual(datos['usuario']['perfil']['fecha_ingreso'], '2026-09-08')
        self.assertEqual(datos['pagos'][0]['fecha_pago'], '2026-09-10T15:00:00+00:00')
        self.assertEqual(datos['adelantos'][0]['fecha'], '2026-09-10T16:00:00+00:00')
        self.assertEqual(datos['actividades'][0]['fecha'], '2026-09-10T17:00:00+00:00')

    def test_admin_emite_fechas_iso_utc(self):
        db.session.get(Usuario, 1).rol.fecha_creacion = instante('2026-09-01T12:00:00')
        db.session.add_all([
            ActividadUsuario(
                id_usuario=2, accion='Actividad de prueba',
                fecha=instante('2026-09-10T13:00:00'),
            ),
            PagoEmpleado(
                id_usuario=2, monto=30, estado='Pagado',
                fecha_pago=instante('2026-09-10T14:00:00'),
            ),
            Adelanto(
                id_usuario=2, monto=20, motivo='Transporte', estado='Aprobado',
                fecha=instante('2026-09-10T15:00:00'),
                fecha_gestion=instante('2026-09-10T16:00:00'),
            ),
            Inversion(
                descripcion='Equipo', monto=50,
                fecha=instante('2026-09-10T17:00:00'),
            ),
            IntentoLogin(
                identificador='user2', ip='192.0.2.5', resultado='fallo',
                fecha=instante('2026-09-10T18:00:00'),
            ),
            BloqueoLogin(
                usuario='user2', ip='192.0.2.5', intentos=5, tipo='usuario',
                fecha=instante('2026-09-10T18:00:00'),
                bloqueado_hasta=instante('2026-09-10T20:00:00'),
            ),
        ])
        db.session.commit()

        roles = self.call('get', '/admin/roles').json['data']
        rol = next(item for item in roles if item['id_rol'] == 1)
        self.assertEqual(rol['fecha_creacion'], '2026-09-01T12:00:00+00:00')
        actividad = self.call('get', '/admin/actividad').json['data'][0]
        self.assertEqual(actividad['fecha'], '2026-09-10T13:00:00+00:00')
        recientes = self.call('get', '/admin/actividad-reciente').json['data']
        self.assertTrue(all(item['fecha'].endswith('+00:00') for item in recientes))
        adelanto = self.call('get', '/admin/adelantos').json['data'][0]
        self.assertEqual(adelanto['fecha'], '2026-09-10T15:00:00+00:00')
        self.assertEqual(adelanto['fecha_gestion'], '2026-09-10T16:00:00+00:00')
        with patch('api.admin.ahora', return_value=instante('2026-09-10T19:00:00')):
            seguridad = self.call('get', '/admin/seguridad').json['data']
        self.assertEqual(seguridad['intentos'][0]['fecha'], '2026-09-10T18:00:00+00:00')
        self.assertEqual(seguridad['bloqueos'][0]['fecha'], '2026-09-10T18:00:00+00:00')
        self.assertEqual(seguridad['bloqueos'][0]['bloqueado_hasta'], '2026-09-10T20:00:00+00:00')

    def test_personal_conserva_datetime_y_date_segun_modelo(self):
        db.session.add_all([
            PagoEmpleado(
                id_usuario=2, monto=30, estado='Pagado', tipo='Bono',
                semana=date(2026, 9, 7),
                fecha_pago=instante('2026-09-10T15:00:00'),
            ),
            PagoPersonal(
                id_usuario=2, monto=30, estado='Pagado', tipo='Bono',
                fecha=date(2026, 9, 10),
            ),
            Adelanto(
                id_usuario=2, monto=20, motivo='Transporte', estado='Aprobado',
                fecha=instante('2026-09-10T16:00:00'),
                fecha_gestion=instante('2026-09-10T17:00:00'),
            ),
        ])
        db.session.commit()

        resumen = self.call('get', '/personal/pagos?mes=9&anio=2026').json['data']
        pago = next(item for item in resumen['historial'] if not str(item['id_pago']).startswith('adelanto-'))
        adelanto = next(item for item in resumen['historial'] if str(item['id_pago']).startswith('adelanto-'))
        self.assertEqual(pago['fecha'], '2026-09-10T15:00:00+00:00')
        self.assertEqual(pago['semana'], '2026-09-07')
        self.assertEqual(adelanto['fecha'], '2026-09-10T17:00:00+00:00')

        detalle = self.call('get', '/personal/pagos/empleado/2?mes=9&anio=2026').json['data']
        self.assertEqual(detalle['pagos'][0]['fecha'], '2026-09-10T15:00:00+00:00')
        self.assertEqual(detalle['pagos_personal'][0]['fecha'], '2026-09-10')
        self.assertEqual(detalle['adelantos'][0]['fecha'], '2026-09-10T17:00:00+00:00')
        listado = self.call('get', '/personal/adelantos').json['data']
        self.assertEqual(listado[0]['fecha'], '2026-09-10T16:00:00+00:00')

        creado = self.call('post', '/personal/pagos', json={
            'id_usuario': 3,
            'monto': 77,
            'tipo': 'Bono',
            'fecha': '2026-09-11',
        })
        self.assertEqual(creado.status_code, 200)
        self.assertEqual(creado.json['data']['fecha'], '2026-09-11T05:00:00+00:00')

    def test_inventario_normaliza_fechas_de_esquemas(self):
        self.producto(5)
        producto = db.session.get(Producto, 1)
        producto.fecha_registro = instante('2026-09-10T12:00:00')
        producto.fecha_edicion = instante('2026-09-10T13:00:00')
        db.session.add_all([
            InventarioMovimiento(
                id_producto=1, id_usuario=1, tipo='Entrada', cantidad=5,
                fecha=instante('2026-09-10T14:00:00'),
            ),
            CompraInventario(
                codigo='COMPRA-PRUEBA', id_usuario=1, total_compra=10,
                fecha=instante('2026-09-10T15:00:00'),
            ),
            Inversion(
                descripcion='Equipo', monto=20,
                fecha=instante('2026-09-10T16:00:00'),
            ),
        ])
        db.session.commit()

        producto_json = self.call('get', '/inventario/productos/1').json['data']
        self.assertEqual(producto_json['fecha_registro'], '2026-09-10T12:00:00+00:00')
        self.assertEqual(producto_json['fecha_edicion'], '2026-09-10T13:00:00+00:00')
        movimiento = self.call('get', '/inventario/movimientos').json['data'][0]
        self.assertEqual(movimiento['fecha'], '2026-09-10T14:00:00+00:00')
        compra = self.call('get', '/inventario/compras').json['data'][0]
        self.assertEqual(compra['fecha'], '2026-09-10T15:00:00+00:00')
        inversion = self.call('get', '/inventario/inversiones').json['data'][0]
        self.assertEqual(inversion['fecha'], '2026-09-10T16:00:00+00:00')
        resumen = self.call('get', '/inventario/resumen').json['data']
        self.assertEqual(resumen['ultima_inversion']['fecha'], '2026-09-10T16:00:00+00:00')

    def test_compra_acumula_lineas_repetidas_para_atender_solicitud(self):
        self.producto(0)
        db.session.add(SolicitudInsumo(
            id_usuario=3, id_producto=1, cantidad=5, estado='Pendiente',
            fecha=instante('2026-09-10T15:00:00'),
        ))
        db.session.commit()

        respuesta = self.call('post', '/inventario/compras', json={'detalle': [
            {'id_producto': 1, 'cantidad': 3, 'precio_unitario': 4},
            {'id_producto': 1, 'cantidad': 2, 'precio_unitario': 4},
        ]})
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(SolicitudInsumo.query.one().estado, 'Atendida')
        self.assertEqual(AtencionInsumo.query.count(), 1)
        self.assertEqual(float(db.session.get(Producto, 1).stock), 5)

    def test_catalogos_e_inversiones_validan_json_y_campos(self):
        for ruta in ('/inventario/inversiones', '/inventario/categorias', '/inventario/proveedores'):
            respuesta = self.call('post', ruta, data='[]', content_type='application/json')
            self.assertEqual(respuesta.status_code, 400)

        self.assertEqual(self.call('post', '/inventario/inversiones', json={}).status_code, 400)
        self.assertEqual(self.call('post', '/inventario/inversiones', json={
            'descripcion': 'Equipo', 'monto': 10, 'id_proveedor': 999,
        }).status_code, 400)
        self.assertEqual(self.call('post', '/inventario/categorias', json={'nombre': ' ingredientes '}).status_code, 409)
        self.assertEqual(self.call('post', '/inventario/proveedores', json={'nombre': 'Proveedor', 'correo': 'correo-invalido'}).status_code, 400)

        proveedor = self.call('post', '/inventario/proveedores', json={
            'nombre': 'Proveedor Uno', 'ruc': '20123456789',
            'telefono': '999999999', 'correo': 'VENTAS@EJEMPLO.TEST',
        })
        self.assertEqual(proveedor.status_code, 200)
        datos = proveedor.json['data']
        self.assertEqual(datos['correo'], 'ventas@ejemplo.test')
        self.assertEqual(self.call('post', '/inventario/inversiones', json={
            'descripcion': 'Equipo', 'monto': 10.125,
            'id_proveedor': datos['id_proveedor'],
        }).status_code, 400)
        self.assertEqual(self.call('post', '/inventario/inversiones', json={
            'descripcion': 'Equipo', 'monto': 10.12,
            'id_proveedor': datos['id_proveedor'],
        }).status_code, 200)
        listado = self.call('get', '/inventario/proveedores').json['data']
        self.assertEqual(listado[0]['ruc'], '20123456789')

    def test_productos_y_stock_validan_json_y_precision(self):
        for datos in (
            [],
            {'nombre': 'Aceite', 'precio': 'nan'},
            {'nombre': 'Aceite', 'stock': -1},
            {'nombre': 'Aceite', 'estado': 'false'},
            {'nombre': 'Aceite', 'id_categoria': 999},
            {'nombre': 'Aceite', 'costo': 1.2345},
        ):
            respuesta = self.call('post', '/inventario/productos', json=datos)
            self.assertEqual(respuesta.status_code, 400)

        self.producto(5)
        for datos in ([], {'precio': 1.234}, {'id_categoria': 999}, {'estado': 'false'}):
            respuesta = self.call('put', '/inventario/productos/1', json=datos)
            self.assertEqual(respuesta.status_code, 400)
        for datos in ([], {}, {'stock': -1}, {'stock': 1.2345}):
            respuesta = self.call('put', '/inventario/productos/1/stock', json=datos)
            self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(self.call(
            'post', '/inventario/productos/1/stock/entrada', json=[]
        ).status_code, 400)
        self.assertEqual(self.call(
            'post', '/inventario/productos/1/stock/salida', json=[]
        ).status_code, 400)

    def test_endpoints_mutables_rechazan_json_no_objeto(self):
        self.producto(5)
        adelanto = Adelanto(
            id_usuario=2, monto=20, motivo='Transporte', estado='Pendiente',
            fecha=instante('2026-09-10T15:00:00'),
        )
        db.session.add(adelanto)
        db.session.commit()
        pago = self.call('post', '/personal/pagos', json={
            'id_usuario': 2, 'monto': 10, 'tipo': 'Bono',
        }).json['data']

        casos = (
            ('post', '/personal/', 1),
            ('put', '/personal/2', 1),
            ('post', '/personal/pagos', 1),
            ('put', f"/personal/pagos/{pago['id_pago']}", 1),
            ('post', '/personal/pagos/adelanto', 1),
            ('post', '/personal/salarios/sueldo', 1),
            ('post', '/personal/salarios/descuentos', 1),
            ('put', f'/admin/adelantos/{adelanto.id_adelanto}', 1),
            ('post', '/admin/seguridad/desbloquear', 1),
            ('post', '/caja/abrir', 2),
            ('post', '/cocina/solicitudes', 3),
            ('put', '/perfil', 2),
            ('put', '/perfil/contrasena', 2),
            ('post', '/perfil/adelantos', 2),
        )
        for metodo, ruta, rol in casos:
            respuesta = self.call(metodo, ruta, role=rol, json=['dato'])
            self.assertEqual(respuesta.status_code, 400, ruta)

        self.assertEqual(self.call('post', '/caja/abrir', role=2, json={}).status_code, 200)
        self.assertEqual(self.call('post', '/caja/transacciones', role=2, json=['dato']).status_code, 400)
        self.assertEqual(self.call('post', '/caja/cerrar', role=2, json=['dato']).status_code, 400)

    def test_importes_financieros_respetan_precision_de_la_base(self):
        self.assertEqual(self.call('post', '/perfil/adelantos', role=2, json={
            'motivo': 'Transporte', 'monto': 10.001,
        }).status_code, 400)
        self.assertEqual(self.call('post', '/personal/pagos/adelanto', json={
            'id_usuario': 2, 'motivo': 'Transporte', 'monto': 10.001,
        }).status_code, 400)
        self.assertEqual(self.call('post', '/personal/pagos', json={
            'id_usuario': 2, 'monto': 10.001,
        }).status_code, 400)
        self.assertEqual(self.call('post', '/caja/abrir', role=2, json={
            'monto_inicial': 10.001,
        }).status_code, 400)
        self.assertEqual(self.call('post', '/caja/abrir', role=2, json={
            'monto_inicial': 10,
        }).status_code, 200)
        self.assertEqual(self.call('post', '/caja/transacciones', role=2, json={
            'tipo': 'Venta', 'metodo_pago': 'Efectivo', 'monto': 10.001,
        }).status_code, 400)
        self.assertEqual(self.call('post', '/caja/cerrar', role=2, json={
            'efectivo_contado': 10.001,
        }).status_code, 400)

    def test_alertas_excluyen_cancelados_y_respetan_el_dia_de_lima(self):
        db.session.add_all([
            PagoEmpleado(id_usuario=2, monto=10, estado='Pendiente', fecha_pago=instante('2026-09-09T15:00:00')),
            PagoEmpleado(id_usuario=2, monto=10, estado='Cancelado', fecha_pago=instante('2026-09-09T16:00:00')),
            PagoEmpleado(id_usuario=2, monto=10, estado='Pagado', fecha_pago=instante('2026-09-01T03:00:00')),
            PagoEmpleado(id_usuario=2, monto=10, estado='Pagado', fecha_pago=instante('2026-09-01T06:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=10, fecha=instante('2026-09-09T23:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=10, fecha=instante('2026-09-09T04:00:00')),
        ])
        db.session.commit()

        with patch('api.admin.ahora', return_value=instante('2026-09-10T04:30:00')):
            datos = self.call('get', '/admin/alertas-resumen').json['data']
        self.assertEqual(datos['pagos_pendientes'], 1)
        self.assertEqual(datos['pagos_mes'], 1)
        self.assertEqual(datos['movimientos_hoy'], 1)

    def test_limites_de_actividad_se_validan(self):
        for ruta in ('/admin/actividad?limit=abc', '/admin/actividad?limit=0',
                     '/admin/actividad-reciente?limit=51'):
            self.assertEqual(self.call('get', ruta).status_code, 400)

    def test_seguridad_identifica_bloqueos_activos(self):
        db.session.add(BloqueoLogin(
            usuario='u2', ip='192.0.2.10', intentos=5, tipo='usuario',
            fecha=instante('2026-09-10T04:00:00'),
            bloqueado_hasta=instante('2026-09-10T05:00:00'),
        ))
        db.session.commit()

        with patch('api.admin.ahora', return_value=instante('2026-09-10T04:30:00')):
            respuesta = self.call('get', '/admin/seguridad').json
        self.assertTrue(respuesta['data']['bloqueos'][0]['activo'])

    def test_resumen_inventario_respeta_lima_y_excluye_inactivos(self):
        self.producto(5)
        db.session.get(Producto, 1).estado = False
        db.session.add_all([
            Inversion(descripcion='Fuera de agosto', monto=10, fecha=instante('2026-09-01T03:00:00')),
            Inversion(descripcion='Dentro de septiembre', monto=20, fecha=instante('2026-09-01T06:00:00')),
            Inversion(descripcion='Después del día local', monto=40, fecha=instante('2026-09-10T06:00:00')),
        ])
        db.session.commit()

        with patch('api.inventario.ahora', return_value=instante('2026-09-10T04:30:00')):
            datos = self.call('get', '/inventario/resumen').json['data']
        self.assertEqual(datos['inversiones_mes'], 20)
        self.assertEqual(datos['inversiones_mes_cantidad'], 1)
        self.assertEqual(datos['articulos_registrados'], 0)
        self.assertEqual(sum(datos['stock_estados'].values()), 0)

    def test_trabajador_y_cocina_emiten_datetime_utc(self):
        self.producto(5)
        db.session.add_all([
            Notificacion(
                id_usuario=4, titulo='Aviso', mensaje='Mensaje', leida=False,
                fecha=instante('2026-09-10T15:00:00'),
            ),
            SolicitudInsumo(
                id_usuario=3, id_producto=1, cantidad=2, estado='Pendiente',
                fecha=instante('2026-09-10T16:00:00'),
            ),
        ])
        db.session.commit()

        with patch('api.trabajador._ahora', return_value=instante('2026-09-10T17:00:00')):
            trabajador = self.call('get', '/trabajador/dashboard', role=4).json['data']
        self.assertEqual(trabajador['fecha'], '2026-09-10T17:00:00+00:00')
        self.assertEqual(trabajador['notificaciones'][0]['fecha'], '2026-09-10T15:00:00+00:00')
        notificaciones = self.call('get', '/trabajador/notificaciones', role=4).json['data']
        self.assertEqual(notificaciones[0]['fecha'], '2026-09-10T15:00:00+00:00')

        with patch('api.cocina._ahora', return_value=instante('2026-09-10T17:00:00')):
            cocina = self.call('get', '/cocina/dashboard', role=3).json['data']
        self.assertEqual(cocina['fecha'], '2026-09-10T17:00:00+00:00')
        self.assertEqual(cocina['pendientes'][0]['fecha'], '2026-09-10T16:00:00+00:00')


if __name__ == '__main__':
    import unittest
    unittest.main()
