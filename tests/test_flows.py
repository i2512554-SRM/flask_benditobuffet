"""Pruebas aisladas: SQLite en memoria o un PostgreSQL desechable (TEST_POSTGRES_URL), nunca Supabase."""
import io
import os
import tempfile
import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import BigInteger, Integer, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.compiler import compiles
from bd import db
from models import (Rol, Usuario, DocumentoIdentidad, Producto, Categoria, CierreCaja,
                    TransaccionCaja, PagoEmpleado, PagoPersonal, Adelanto,
                    SueldoSemanal, DescuentoSemanal, InventarioMovimiento)
from api.caja import caja_bp
from api.personal import personal_bp
from api.perfil import perfil_bp
from api.inventario import inventario_bp
from api.trabajador import trabajador_bp
from api.admin import admin_bp
from api.rendimiento import rendimiento_bp
from api.auth import auth_bp
from api.cocina import cocina_bp
from api.indicadores import indicadores_bp
from api.sesiones import crear_sesion, configurar_sesiones
from api.dni import consultar_dni
from api.errores_bd import configurar_errores_bd


@compiles(BigInteger, 'sqlite')
def sqlite_integer(element, compiler, **kw):
    return 'INTEGER'


def instante(d):
    return datetime.fromisoformat(d).replace(tzinfo=timezone.utc)


def url_pruebas():
    valor = os.getenv('TEST_POSTGRES_URL', '').strip()
    if not valor:
        return 'sqlite://'
    url = make_url(valor)
    if not url.drivername.startswith('postgresql'):
        raise RuntimeError('TEST_POSTGRES_URL debe apuntar a PostgreSQL.')
    if 'supabase' in (url.host or '').lower() or not any(p in (url.database or '').lower() for p in ('prueba', 'test')):
        raise RuntimeError('TEST_POSTGRES_URL debe ser una base desechable cuyo nombre contenga "prueba" o "test"; '
                           'las pruebas borran todas las tablas.')
    return valor


def _sincronizar_secuencias(session, contexto_flush):
    tablas = {obj.__table__ for obj in session.new if hasattr(obj, '__table__')}
    conexion = session.connection()
    for tabla in tablas:
        for columna in tabla.primary_key.columns:
            if not isinstance(columna.type, Integer) or columna.autoincrement is False:
                continue
            conexion.execute(text(
                f'SELECT setval(pg_get_serial_sequence(:tabla, :columna), '
                f'GREATEST((SELECT MAX("{columna.name}") FROM "{tabla.name}"), 1)) '
                f'WHERE pg_get_serial_sequence(:tabla, :columna) IS NOT NULL'
            ), {'tabla': tabla.name, 'columna': columna.name})


class BaseFlujos(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.app = Flask(__name__)
        self.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI=url_pruebas(),
                               JWT_SECRET_KEY='test-only-key-at-least-thirty-two-characters', UPLOAD_FOLDER=self.folder.name)
        db.init_app(self.app)
        configurar_sesiones(JWTManager(self.app))
        configurar_errores_bd(self.app)
        self.tokens = {}
        for bp, prefix in [(caja_bp, '/api/caja'), (personal_bp, '/api/personal'),
                           (inventario_bp, '/api/inventario'), (perfil_bp, None),
                           (trabajador_bp, None), (admin_bp, None), (rendimiento_bp, '/api'), (auth_bp, None), (cocina_bp, None),
                           (indicadores_bp, '/api')]:
            self.app.register_blueprint(bp, **({'url_prefix': prefix} if prefix else {}))
        self.app.add_url_rule('/api/dni/<dni>', view_func=consultar_dni)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.postgres = db.engine.dialect.name == 'postgresql'
        if self.postgres:
            db.drop_all()
            event.listen(db.session, 'after_flush', _sincronizar_secuencias)
        db.create_all()
        for i in range(1, 5):
            db.session.add(Rol(id_rol=i, nombre=f'Rol {i}', estado=True, fecha_creacion=datetime.now(timezone.utc)))
            db.session.add(DocumentoIdentidad(id_documento=i, numero=f'{i:08}', tipo_documento='DNI'))
            db.session.add(Usuario(id_usuario=i, nombres='Ana', apellido='Pérez', id_documento=i,
                usuario=f'user{i}', correo=f'u{i}@example.test', clave='unused', id_rol=i,
                fecha_creacion=datetime.now(timezone.utc), estado=True))
        db.session.add(Categoria(id_categoria=1, nombre='Ingredientes', fecha_creacion=datetime.now(timezone.utc)))
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        if self.postgres:
            event.remove(db.session, 'after_flush', _sincronizar_secuencias)
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()
        self.folder.cleanup()

    def call(self, method, path, role=1, **kwargs):
        if role not in self.tokens:
            self.tokens[role] = crear_sesion(db.session.get(Usuario, role))
        headers={'Authorization': 'Bearer ' + self.tokens[role][0]}
        return getattr(self.client, method)('/api' + path, headers=headers, **kwargs)

    def producto(self, stock=10):
        p = Producto(id_producto=1, nombre='Arroz', precio=4, stock=stock, unidad_medida='Kg', id_categoria=1,
                     fecha_registro=datetime.now(timezone.utc), fecha_edicion=datetime.now(timezone.utc), estado=True)
        db.session.add(p); db.session.commit()

class FlujosTest(BaseFlujos):
    def test_dos_aperturas_no_duplican_ventas(self):
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:00:00')):
            self.assertEqual(self.call('post', '/caja/abrir', json={}).status_code, 200)
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:01:00')):
            self.assertEqual(self.call('post', '/caja/transacciones', role=2,
                json={'tipo':'Venta','monto':300,'metodo_pago':'Yape'}).status_code,200)
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:02:00')):
            self.assertEqual(self.call('post', '/caja/cerrar').json['data']['total_ventas'],300)
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:03:00')):
            self.call('post','/caja/abrir',json={})
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:04:00')):
            self.assertEqual(self.call('post','/caja/cerrar').json['data']['total_ventas'],0)
        reporte=self.call('get','/caja/reportes?fecha=2026-09-10&periodo=mes',role=2).json['data']
        self.assertEqual(reporte['ventas_mes'],300)
        self.assertEqual(sum(c['total_ventas'] for c in reporte['cierres']),300)

    def test_requiere_apertura_y_metodo(self):
        self.assertEqual(self.call('post','/caja/transacciones',json={'tipo':'Venta','monto':10,'metodo_pago':'Efectivo'}).status_code,409)
        self.call('post','/caja/abrir',json={})
        self.assertEqual(self.call('post','/caja/transacciones',json={'tipo':'Venta','monto':10}).status_code,400)
        self.assertEqual(self.call('post','/caja/abrir',json={}).status_code,409)

    def test_rutas_adelantos_comparten_validacion(self):
        for ruta in ('/personal/adelantos', '/personal/pagos/adelanto'):
            for datos in ({}, {'id_usuario': 1, 'monto': 20, 'motivo': 'Prueba'},
                          {'id_usuario': 2, 'monto': -10, 'motivo': 'Prueba'}):
                self.assertEqual(self.call('post', ruta, json=datos).status_code, 400)
        datos = {'id_usuario': 2, 'monto': 20, 'descripcion': 'Prueba', 'fecha': '2026-09-10'}
        self.assertEqual(self.call('post', '/personal/adelantos', json=datos).status_code, 200)
        self.assertEqual(self.call('post', '/personal/pagos/adelanto', json=datos).status_code, 400)
        self.assertEqual(Adelanto.query.count(), 1)

    def test_apertura_antigua_no_duplica_cierres_posteriores(self):
        db.session.add_all([
            CierreCaja(id_cierre=1,id_usuario=1,estado='abierta',fecha=instante('2026-09-07T15:00:00'),total_ventas=0,total_gastos=0),
            CierreCaja(id_cierre=2,id_usuario=1,estado='cerrada',fecha=instante('2026-09-08T15:00:00'),fecha_cierre=instante('2026-09-08T17:00:00'),total_ventas=100,total_gastos=0),
            TransaccionCaja(id_usuario=2,tipo='Venta',monto=100,fecha=instante('2026-09-08T16:00:00'))])
        db.session.commit()
        datos=self.call('get','/caja/historial').json['data']
        self.assertEqual(sum(c['total_ventas'] for c in datos),100)
        self.assertEqual(datos[1]['estado'],'pendiente de revisión')
        self.assertEqual(self.call('get','/caja/actual').json['data']['abierta'],False)

    def test_reporte_incluye_ultimo_dia_lima(self):
        db.session.add_all([
            TransaccionCaja(id_usuario=2,tipo='Venta',monto=12.5,fecha=instante('2026-10-01T04:59:00')),
            TransaccionCaja(id_usuario=2,tipo='Venta',monto=99,fecha=instante('2026-10-01T05:00:00'))])
        db.session.commit()
        data=self.call('get','/caja/reportes?fecha=2026-09-01&periodo=mes').json['data']
        self.assertEqual(data['ventas_mes'],12.5)
        self.assertEqual(sum(p['ingresos'] for p in data['puntos']),12.5)

    def test_permisos_creacion_empleado(self):
        self.assertEqual(self.call('post','/personal/',role=2,json={}).status_code,403)
        self.assertEqual(self.call('post','/personal/',json={'dni':'abcdefgh'}).status_code,400)
        base={'dni':'12345678','nombres':'Ana','apellido':'Pérez','id_rol':2}
        self.assertEqual(self.call('post','/personal/',json=base).status_code,400)
        base.update(clave='clave-test-123', telefono='999999999')
        self.assertEqual(self.call('post','/personal/',json={**base,'nombres':'Ana123'}).status_code,400)
        self.assertEqual(self.call('post','/personal/',json=base).status_code,200)

    def test_administrador_no_solicita_adelanto(self):
        self.assertEqual(self.call('post','/perfil/adelantos',json={'monto':15,'motivo':'Viaje'}).status_code,403)

    def test_adelanto_pendiente_visible_y_cancelacion(self):
        r=self.call('post','/perfil/adelantos',role=2,json={'monto':15,'motivo':'Viaje'})
        self.assertEqual(r.status_code,200)
        registros=self.call('get','/trabajador/pagos',role=2).json['data']['adelantos']
        self.assertEqual(registros[0]['estado'],'Pendiente')
        a=db.session.get(Adelanto,registros[0]['id_adelanto']); a.estado='Aprobado'; db.session.commit()
        self.assertEqual(self.call('delete',f'/perfil/adelantos/{a.id_adelanto}',role=2).status_code,409)

    def test_compra_sin_proveedor_y_validacion(self):
        self.producto()
        for cantidad in [-2,0,'NaN','Infinity']:
            self.assertEqual(self.call('post','/inventario/compras',json={'detalle':[{'id_producto':1,'cantidad':cantidad,'precio_unitario':4}]}).status_code,400)
        self.assertEqual(self.call('post','/inventario/compras',json={'detalle':[{'id_producto':1,'cantidad':2,'precio_unitario':4}]}).status_code,201)
        self.assertEqual(db.session.get(Producto,1).stock,12)
        self.assertEqual(db.session.get(Producto,1).costo,4)

    def test_producto_registra_y_actualiza_costo(self):
        self.assertEqual(self.call('post','/inventario/productos',json={'nombre':'Aceite','unidad_medida':'Lt','precio':12,'stock':3,'costo':10}).status_code,201)
        self.assertEqual(db.session.get(Producto,1).costo,10)
        self.assertEqual(self.call('post','/inventario/productos',json={'nombre':'Sal','unidad_medida':'Kg','precio':2}).status_code,201)
        self.assertIsNone(db.session.get(Producto,2).costo)
        self.assertEqual(self.call('put','/inventario/productos/2',json={'costo':1.5}).status_code,200)
        self.assertEqual(db.session.get(Producto,2).costo,1.5)

    def test_indicadores_permisos_y_valores(self):
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:00:00')):
            self.assertEqual(self.call('post','/caja/abrir',json={}).status_code,200)
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:01:00')):
            self.assertEqual(self.call('post','/caja/transacciones',role=2,json={'tipo':'Venta','monto':300,'metodo_pago':'Yape'}).status_code,200)
            self.assertEqual(self.call('post','/caja/transacciones',role=2,json={'tipo':'Gasto','monto':50,'metodo_pago':'Efectivo'}).status_code,200)
        with patch('api.caja.ahora', return_value=instante('2026-09-10T15:02:00')):
            self.call('post','/caja/cerrar')
        db.session.get(Usuario, 3).estado = False
        db.session.get(Usuario, 4).estado = False
        db.session.add(SueldoSemanal(id_usuario=2, desde=date(2026, 8, 31), monto=100,
                                     registrado_por=1, fecha=instante('2026-08-31T12:00:00')))
        db.session.add(DescuentoSemanal(id_usuario=2, semana=date(2026, 9, 7), monto=10,
                                        motivo='Platos', registrado_por=1,
                                        fecha=instante('2026-09-08T12:00:00'), anulado=False))
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-10-02T00:00:00')):
            r=self.call('get','/indicadores?periodo=mes&fecha=2026-09-10')
            self.assertEqual(r.status_code,200)
            data=r.json['data']
            self.assertEqual(data['periodo'],'mes')
            self.assertTrue(data['inicio'].startswith('2026-09-01'))
            self.assertTrue(data['fin'].startswith('2026-10-01'))
            kpis={k['codigo']:k for k in data['kpis']}
            self.assertEqual(set(kpis), {'KPI-01','KPI-02','KPI-03','KPI-04','KPI-05','KPI-06','KPI-07','KPI-08'})
            self.assertAlmostEqual(kpis['KPI-01']['valor'],83.33,places=2)
            self.assertEqual(kpis['KPI-01']['detalle']['cobros'],300)
            self.assertEqual(kpis['KPI-01']['detalle']['egresos'],50)
            self.assertEqual(kpis['KPI-05']['detalle']['costo_laboral'],418.57)
            self.assertEqual(kpis['KPI-05']['detalle']['empleados_sin_sueldo'],0)
            self.assertEqual(kpis['KPI-05']['detalle']['semanas_empleado'],5)
            self.assertAlmostEqual(kpis['KPI-05']['valor'],139.52,places=2)
            self.assertIsNone(kpis['KPI-06']['valor'])
            self.assertIsNone(kpis['KPI-07']['valor'])
        with patch('api.indicadores.ahora', return_value=instante('2026-09-15T00:00:00')):
            historicos = self.call('get','/indicadores?periodo=mes&fecha=2025-04-10').json['data']['kpis']
            cobertura = next(k for k in historicos if k['codigo'] == 'KPI-03')
            self.assertEqual(cobertura['detalle']['corte_datos'], '2025-05-01')
        self.assertEqual(self.call('get','/indicadores',role=2).status_code,403)
        self.assertEqual(self.call('get','/indicadores?periodo=trimestre').status_code,400)
        self.assertEqual(self.call('get','/indicadores?fecha=2026-13-01').status_code,400)

    def test_indicadores_comparan_mes_calendario_y_excluyen_reversas(self):
        db.session.add_all([
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=100, metodo_pago='Efectivo',
                            fecha=instante('2026-03-01T17:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=200, metodo_pago='Efectivo',
                            fecha=instante('2026-04-15T17:00:00')),
        ])
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-05-02T00:00:00')):
            datos = self.call('get', '/indicadores?periodo=mes&fecha=2026-04-10').json['data']['kpis']
        variacion = next(k for k in datos if k['codigo'] == 'KPI-02')
        self.assertEqual(variacion['detalle']['ventas_anterior'], 100)
        self.assertEqual(variacion['valor'], 100)

        TransaccionCaja.query.delete()
        self.producto(stock=0)
        producto = db.session.get(Producto, 1)
        producto.costo = 2
        producto.fecha_registro = instante('2026-08-01T12:00:00')
        db.session.add_all([
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=100, metodo_pago='Efectivo',
                            fecha=instante('2026-09-10T17:00:00')),
            CierreCaja(id_usuario=2, monto_inicial=0, total_ventas=100, total_gastos=0,
                       estado='cerrada', fecha=instante('2026-09-01T04:30:00'),
                       fecha_cierre=instante('2026-09-01T05:30:00')),
            InventarioMovimiento(id_producto=1, id_usuario=3, tipo='Salida', cantidad=-4,
                                 stock_anterior=10, stock_posterior=6, motivo='Merma por vencimiento',
                                 fecha=instante('2026-09-09T17:00:00')),
            InventarioMovimiento(id_producto=1, id_usuario=3, tipo='Salida', cantidad=-6,
                                 stock_anterior=6, stock_posterior=0, motivo='Preparación de cocina',
                                 fecha=instante('2026-09-10T17:00:00')),
            InventarioMovimiento(id_producto=1, id_usuario=1, tipo='Salida', cantidad=-5,
                                 stock_anterior=5, stock_posterior=0,
                                 motivo='Anulación de compra DEMO (reversa de stock)', id_compra=999,
                                 fecha=instante('2026-09-11T17:00:00')),
        ])
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-10-02T00:00:00')):
            datos = self.call('get', '/indicadores?periodo=mes&fecha=2026-09-10').json['data']['kpis']
        kpis = {k['codigo']: k for k in datos}
        self.assertEqual(kpis['KPI-03']['valor'], 0)
        self.assertEqual(kpis['KPI-03']['detalle']['productos_bajo_umbral'], 1)
        self.assertEqual(kpis['KPI-04']['valor'], 40)
        self.assertEqual(kpis['KPI-06']['valor'], 88)
        self.assertEqual(kpis['KPI-06']['detalle']['salidas_consideradas'], 1)
        self.assertEqual(kpis['KPI-07']['detalle']['cierres_sin_conteo'], 1)

    def test_cierre_registra_efectivo_contado(self):
        self.call('post', '/caja/abrir', role=2, json={'monto_inicial': 0})
        cierre = self.call('post', '/caja/cerrar', role=2, json={'efectivo_contado': 45}).json['data']
        self.assertEqual(cierre['efectivo_contado'], 45.0)

    def test_cierre_efectivo_contado_invalido(self):
        self.assertEqual(self.call('post', '/caja/cerrar', role=2, json={'efectivo_contado': -5}).status_code, 409)
        self.call('post', '/caja/abrir', role=2, json={'monto_inicial': 0})
        self.assertEqual(self.call('post', '/caja/cerrar', role=2, json={'efectivo_contado': -5}).status_code, 400)

    def test_kpi_07_diferencia_con_conteo(self):
        self.producto(stock=0)
        db.session.add_all([
            CierreCaja(id_usuario=2, monto_inicial=50, total_ventas=100, total_gastos=0,
                       efectivo_contado=160, estado='cerrada', fecha=instante('2026-09-02T09:00:00'),
                       fecha_cierre=instante('2026-09-02T18:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=100, metodo_pago='Efectivo',
                            fecha=instante('2026-09-02T12:00:00')),
        ])
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-10-02T00:00:00')):
            datos = self.call('get', '/indicadores?periodo=mes&fecha=2026-09-10').json['data']['kpis']
        kpi = next(k for k in datos if k['codigo'] == 'KPI-07')
        self.assertAlmostEqual(kpi['valor'], 6.67, places=2)
        self.assertEqual(kpi['unidad'], '%')
        self.assertEqual(kpi['detalle']['cierres_sin_conteo'], 0)
        self.assertEqual(kpi['detalle']['sobrante_total'], 10)
        self.assertEqual(kpi['detalle']['faltante_total'], 0)
        self.assertAlmostEqual(kpi['detalle']['diferencia_global'], 10, places=2)
        self.assertEqual(len(kpi['serie']), 1)
        self.assertAlmostEqual(kpi['serie'][0]['diferencia_abs'], 10, places=2)
        self.assertEqual(kpi['serie'][0]['contado'], 160)
        self.assertEqual(kpi['serie'][0]['esperado'], 150)

    def test_indicadores_incluyen_campos_nuevos_y_tendencia(self):
        db.session.add_all([
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=100, metodo_pago='Efectivo',
                            fecha=instante('2026-03-10T17:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=200, metodo_pago='Efectivo',
                            fecha=instante('2026-04-10T17:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Gasto', monto=100, metodo_pago='Efectivo',
                            fecha=instante('2026-04-10T18:00:00')),
        ])
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-05-02T00:00:00')):
            datos = self.call('get', '/indicadores?periodo=mes&fecha=2026-04-10').json['data']['kpis']
        kpis = {k['codigo']: k for k in datos}
        for codigo in kpis:
            for campo in ('variacion', 'tendencia', 'comparacion', 'serie'):
                self.assertIn(campo, kpis[codigo])
        kpi_01 = kpis['KPI-01']
        self.assertAlmostEqual(kpi_01['valor'], 50, places=1)
        self.assertAlmostEqual(kpi_01['variacion'], -50, places=1)
        self.assertEqual(kpi_01['tendencia'], 'baja')
        self.assertEqual(kpi_01['comparacion']['margen_anterior'], 100.0)
        self.assertEqual(len(kpi_01['serie']), 30)
        self.assertIn('ingresos', kpi_01['serie'][0])
        self.assertIn('egresos', kpi_01['serie'][0])
        punto_venta = next(s for s in kpi_01['serie'] if s['ingresos'])
        self.assertEqual(punto_venta['ingresos'], 200)
        self.assertEqual(punto_venta['egresos'], 100)
        kpi_02 = kpis['KPI-02']
        self.assertAlmostEqual(kpi_02['valor'], 100, places=1)
        self.assertEqual(kpi_02['tendencia'], 'sube')
        self.assertEqual(kpi_02['comparacion']['ventas_anterior'], 100)

    def test_indicadores_rango_personalizado(self):
        db.session.add_all([
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=100, metodo_pago='Efectivo',
                            fecha=instante('2026-09-10T17:00:00')),
            TransaccionCaja(id_usuario=2, tipo='Venta', monto=50, metodo_pago='Efectivo',
                            fecha=instante('2026-09-12T17:00:00')),
        ])
        db.session.commit()
        with patch('api.indicadores.ahora', return_value=instante('2026-10-02T00:00:00')):
            r = self.call('get', '/indicadores?inicio=2026-09-10&fin=2026-09-12')
        self.assertEqual(r.status_code, 200)
        data = r.json['data']
        self.assertEqual(data['periodo'], 'rango')
        self.assertEqual(data['inicio'], '2026-09-10T05:00:00+00:00')
        self.assertEqual(data['fin'], '2026-09-13T05:00:00+00:00')
        self.assertEqual(data['prev_fin'], '2026-09-10T05:00:00+00:00')
        kpi_02 = next(k for k in data['kpis'] if k['codigo'] == 'KPI-02')
        self.assertEqual(kpi_02['detalle']['ventas_periodo'], 150)
        self.assertEqual(len(kpi_02['serie']), 3)
        por_etiqueta = {s['etiqueta']: s['valor'] for s in kpi_02['serie']}
        self.assertEqual(por_etiqueta.get('10/09'), 100)
        self.assertEqual(por_etiqueta.get('11/09'), 0)
        self.assertEqual(por_etiqueta.get('12/09'), 50)

    def test_indicadores_rango_invalido(self):
        self.assertEqual(self.call('get', '/indicadores?inicio=2026-09-12&fin=2026-09-10').status_code, 400)
        self.assertEqual(self.call('get', '/indicadores?inicio=2025-01-01&fin=2026-09-12').status_code, 400)
        self.assertEqual(self.call('get', '/indicadores?inicio=2026-09-10').status_code, 400)
        self.assertEqual(self.call('get', '/indicadores?inicio=abc&fin=2026-09-12').status_code, 400)

    def test_cocina_producto_y_unidad(self):
        r=self.call('post','/inventario/productos',role=3,json={'nombre':'Azúcar','unidad_medida':'Kg','precio':3,'stock':2})
        self.assertEqual(r.status_code,201)
        self.assertEqual(self.call('get','/inventario/resumen',role=3).status_code,200)
        self.assertEqual(self.call('get','/inventario/categorias',role=3).status_code,200)
        self.assertEqual(self.call('get','/inventario/movimientos',role=3).status_code,200)

    def test_salida_no_excede_stock(self):
        self.producto(stock=3)
        self.assertEqual(self.call('post','/inventario/productos/1/stock/salida',role=3,json={'cantidad':4,'motivo':'Cocina'}).status_code,400)
        self.assertEqual(db.session.get(Producto,1).stock,3)

    def test_historial_semanal_no_cuenta_pendientes(self):
        db.session.add_all([
            PagoEmpleado(id_usuario=2,monto=100,fecha_pago=instante('2026-09-08T05:00:00'),estado='Pagado'),
            PagoEmpleado(id_usuario=2,monto=100,fecha_pago=instante('2026-09-08T05:00:00'),estado='Pendiente'),
            Adelanto(id_usuario=2,monto=20,motivo='Viaje',fecha=instante('2026-09-09T12:00:00'),estado='Aprobado')])
        db.session.commit()
        r=self.call('get','/personal/salarios?fecha=2026-09-10')
        data=next(x for x in r.json['data'] if x['id_usuario']==2)
        self.assertEqual(data['neto'],120)
        self.assertEqual(r.json['inicio'],'2026-09-07')
        self.assertEqual(next(x for x in self.call('get','/personal/salarios?fecha=2026-09-17').json['data'] if x['id_usuario']==2)['neto'],0)

    def test_foto_multipart_y_clave_por_flujo_seguro(self):
        r=self.call('put','/perfil',role=2,data={'correo':'u2@example.test','telefono':'999999999',
            'foto_perfil':(io.BytesIO(b'\x89PNG\r\n\x1a\n'+b'\0'*32),'avatar.png')},content_type='multipart/form-data')
        self.assertEqual(r.status_code,200)
        self.assertIn('/uploads/perfiles/',r.json['data']['perfil']['foto_perfil'])
        self.assertEqual(self.call('put','/perfil',role=2,json={'correo':'u2@example.test','clave':'new-password'}).status_code,400)

    def test_sueldo_fijo_descuentos_y_vigencia(self):
        datos = {'id_usuario': 2, 'fecha': '2026-09-10', 'monto': 350, 'clave_operacion': '45b74608-2507-40cc-a660-32f92d51e3c5'}
        self.assertEqual(self.call('post', '/personal/salarios/sueldo', role=2, json=datos).status_code, 403)
        self.assertEqual(self.call('post', '/personal/salarios/sueldo', json=datos).status_code, 200)
        self.assertEqual(self.call('post', '/personal/salarios/descuentos', json={**datos, 'monto': 15, 'motivo': 'Platos'}).status_code, 200)
        self.assertEqual(self.call('post', '/personal/salarios/descuentos', json={**datos, 'monto': -5, 'motivo': 'Falta'}).status_code, 400)
        db.session.add_all([
            PagoEmpleado(id_usuario=2, monto=100, fecha_pago=instante('2026-09-09T12:00:00'), estado='Pagado', tipo='Salario semanal'),
            Adelanto(id_usuario=2, monto=20, motivo='Viaje', fecha=instante('2026-09-09T12:00:00'), estado='Aprobado'),
            Adelanto(id_usuario=2, monto=90, motivo='Pendiente', fecha=instante('2026-09-09T12:00:00'), estado='Pendiente')])
        db.session.commit()
        def consultar(fecha):
            return next(x for x in self.call('get', '/personal/salarios?fecha=' + fecha).json['data'] if x['id_usuario'] == 2)
        self.assertEqual(consultar('2026-09-10')['saldo'], 215)
        self.call('post', '/personal/salarios/sueldo', json={**datos, 'fecha': '2026-09-17', 'monto': 400})
        self.assertEqual(consultar('2026-09-10')['sueldo_base'], 350)
        self.assertEqual(consultar('2026-09-17')['saldo'], 400)
        self.assertIsNone(consultar('2026-09-03')['saldo'])
        descuento = consultar('2026-09-10')['descuentos'][0]['id']
        self.assertEqual(self.call('post', f'/personal/salarios/descuentos/{descuento}/anular').status_code, 200)
        self.assertEqual(consultar('2026-09-10')['saldo'], 230)

    def test_retencion_respalda_y_conserva_historial(self):
        from models import IntentoLogin, ActividadUsuario
        from automatizacion_caja.limpiar_logs import limpiar_accesos
        import json
        from pathlib import Path
        db.session.add_all([
            IntentoLogin(identificador='user2', resultado='exito', fecha=instante('2026-01-01')),
            IntentoLogin(identificador='user2', resultado='fallido', fecha=instante('2026-09-10')),
            ActividadUsuario(id_usuario=2, accion='Pago registrado', fecha=instante('2026-01-01'))])
        db.session.commit()
        ahora = instante('2026-09-11')
        self.assertEqual(limpiar_accesos(instante=ahora)['encontrados'], 1)
        self.assertEqual(IntentoLogin.query.count(), 2)
        with self.assertRaises(ValueError):
            limpiar_accesos(aplicar=True, instante=ahora)
        r = limpiar_accesos(aplicar=True, respaldo=self.folder.name, instante=ahora)
        self.assertEqual(r['eliminados'], 1)
        self.assertEqual(IntentoLogin.query.count(), 1)
        self.assertEqual(ActividadUsuario.query.count(), 1)
        self.assertEqual(json.loads(Path(r['respaldo']).read_text(encoding='utf-8'))['identificador'], 'user2')

    def test_costo_mensual_devuelve_12_meses(self):
        r = self.call('get', '/personal/costo-mensual')
        self.assertEqual(r.status_code, 200)
        datos = r.json['data']
        self.assertEqual(len(datos), 12)
        for mes in datos:
            self.assertEqual(sorted(mes.keys()), ['adelantos', 'anio', 'etiqueta', 'mes', 'neto', 'pagado'])
        secuencia = [(m['anio'], m['mes']) for m in datos]
        self.assertEqual(sorted(secuencia), secuencia)

    def test_valor_stock_por_categoria(self):
        self.producto(stock=10)
        self.assertEqual(self.call('get', '/inventario/resumen').json['data']['valor_total'], 0)
        r = self.call('get', '/inventario/valor-stock')
        self.assertEqual(r.status_code, 200)
        d = r.json['data']
        self.assertEqual(d['sin_costo'], 1)
        self.assertEqual(d['categorias'], [])
        self.call('put', '/inventario/productos/1', json={'costo': 4})
        resumen = self.call('get', '/inventario/resumen').json['data']
        self.assertEqual(resumen['valor_total'], 40)
        self.assertEqual(resumen['productos_sin_costo'], 0)
        d = self.call('get', '/inventario/valor-stock').json['data']
        self.assertEqual(d['con_costo'], 1)
        self.assertEqual(d['categorias'], [{'categoria': 'Ingredientes', 'valor_stock': 40.0}])


if __name__ == '__main__':
    unittest.main()
