"""Pruebas aisladas: SQLite en memoria, sin conexiones ni cambios en Supabase."""
import io
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles
from bd import db
from models import (Rol, Usuario, DocumentoIdentidad, Producto, Categoria, CierreCaja,
                    TransaccionCaja, PagoEmpleado, Adelanto)
from api.caja import caja_bp
from api.personal import personal_bp
from api.perfil import perfil_bp
from api.inventario import inventario_bp
from api.trabajador import trabajador_bp
from api.admin import admin_bp
from api.rendimiento import rendimiento_bp


@compiles(BigInteger, 'sqlite')
def sqlite_integer(element, compiler, **kw):
    return 'INTEGER'


def instante(d):
    return datetime.fromisoformat(d).replace(tzinfo=timezone.utc)


class FlujosTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.app = Flask(__name__)
        self.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite://',
                               JWT_SECRET_KEY='test-only-key-at-least-thirty-two-characters', UPLOAD_FOLDER=self.folder.name)
        db.init_app(self.app)
        JWTManager(self.app)
        for bp, prefix in [(caja_bp, '/api/caja'), (personal_bp, '/api/personal'),
                           (inventario_bp, '/api/inventario'), (perfil_bp, None),
                           (trabajador_bp, None), (admin_bp, None), (rendimiento_bp, '/api')]:
            self.app.register_blueprint(bp, **({'url_prefix': prefix} if prefix else {}))
        self.ctx = self.app.app_context()
        self.ctx.push()
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
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()
        self.folder.cleanup()

    def call(self, method, path, role=1, **kwargs):
        headers={'Authorization': 'Bearer ' + create_access_token(identity=str(role))}
        return getattr(self.client, method)('/api' + path, headers=headers, **kwargs)

    def producto(self, stock=10):
        p = Producto(id_producto=1, nombre='Arroz', precio=4, stock=stock, unidad_medida='Kg', id_categoria=1,
                     fecha_registro=datetime.now(timezone.utc), fecha_edicion=datetime.now(timezone.utc), estado=True)
        db.session.add(p); db.session.commit()

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
        datos = {'id_usuario': 2, 'fecha': '2026-09-10', 'monto': 350}
        self.assertEqual(self.call('post', '/personal/salarios/sueldo', role=2, json=datos).status_code, 403)
        self.assertEqual(self.call('post', '/personal/salarios/sueldo', json=datos).status_code, 200)
        self.assertEqual(self.call('post', '/personal/salarios/descuentos', json={**datos, 'monto': 15, 'motivo': 'Platos'}).status_code, 200)
        self.assertEqual(self.call('post', '/personal/salarios/descuentos', json={**datos, 'monto': -5, 'motivo': 'Falta'}).status_code, 400)
        db.session.add_all([
            PagoEmpleado(id_usuario=2, monto=100, fecha_pago=instante('2026-09-09T12:00:00'), estado='Pagado'),
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


if __name__ == '__main__':
    unittest.main()
