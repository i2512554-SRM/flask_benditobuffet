import importlib
import os
import unittest
from datetime import timedelta
from unittest.mock import patch

from flask import Flask
from flask_jwt_extended import create_access_token, decode_token

from api.auth import _obtener_ip
from api.sesiones import crear_sesion
from bd import db, init_db
from models import BloqueoLogin, IntentoLogin, SesionUsuario, Usuario
from tests.test_flows import BaseFlujos


class ConfiguracionRuntimeTest(unittest.TestCase):
    def test_pooler_6543_deshabilita_sentencias_preparadas(self):
        flask_app = Flask(__name__)
        entorno = {
            'DB_USER': 'usuario-prueba',
            'DB_PASSWORD': 'clave-prueba',
            'DB_HOST': 'db.example.test',
            'DB_PORT': '6543',
            'DB_NAME': 'postgres',
        }
        with patch.dict(os.environ, entorno, clear=False):
            init_db(flask_app)
        opciones = flask_app.config['SQLALCHEMY_ENGINE_OPTIONS']
        self.assertTrue(opciones['pool_pre_ping'])
        self.assertIsNone(opciones['connect_args']['prepare_threshold'])

    def test_produccion_exige_secret_y_api_inexistente_devuelve_json_404(self):
        entorno = {
            'APP_ENV': 'test',
            'FLASK_DEBUG': 'false',
            'SECRET_KEY': 'test-only-key-at-least-thirty-two-characters',
            'DB_USER': 'usuario-prueba',
            'DB_PASSWORD': 'clave-prueba',
            'DB_HOST': 'db.example.test',
            'DB_PORT': '6543',
            'DB_NAME': 'postgres',
        }
        with patch.dict(os.environ, entorno, clear=False):
            modulo_app = importlib.import_module('app')
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'FLASK_ENV': '',
            'FLASK_DEBUG': 'true',
            'SECRET_KEY': '',
        }, clear=False):
            with self.assertRaises(RuntimeError):
                modulo_app._resolver_secret_key()
        respuesta = modulo_app.app.test_client().get('/api/ruta-inexistente')
        self.assertEqual(respuesta.status_code, 404)
        self.assertTrue(respuesta.is_json)
        self.assertEqual(respuesta.json['error'], 'Recurso no encontrado')


class SeguridadAuthTest(BaseFlujos):
    def test_x_forwarded_for_solo_desde_proxy_confiable(self):
        self.app.config['TRUSTED_PROXY_IPS'] = ()
        with self.app.test_request_context(
            '/',
            headers={'X-Forwarded-For': '203.0.113.7'},
            environ_base={'REMOTE_ADDR': '198.51.100.20'},
        ):
            self.assertEqual(_obtener_ip(), '198.51.100.20')

        self.app.config['TRUSTED_PROXY_IPS'] = ('10.0.0.0/8',)
        with self.app.test_request_context(
            '/',
            headers={'X-Forwarded-For': '203.0.113.7, 10.1.1.8'},
            environ_base={'REMOTE_ADDR': '10.2.2.9'},
        ):
            self.assertEqual(_obtener_ip(), '203.0.113.7')

    def test_usuarios_aleatorios_se_limitan_por_ip_sin_filas_por_usuario(self):
        respuestas = []
        with patch('api.auth.MAX_INTENTOS_IP', 3):
            for numero in range(4):
                respuestas.append(self.client.post(
                    '/api/auth/login',
                    json={'usuario': f'inexistente-{numero}', 'clave': 'incorrecta'},
                    headers={'X-Forwarded-For': f'203.0.113.{numero + 1}'},
                ))

        self.assertEqual([r.status_code for r in respuestas], [401, 401, 429, 429])
        bloqueos = BloqueoLogin.query.all()
        self.assertEqual(len(bloqueos), 1)
        self.assertEqual(bloqueos[0].tipo, 'ip')
        self.assertEqual(bloqueos[0].ip, '127.0.0.1')
        self.assertEqual(IntentoLogin.query.count(), 3)

    def test_logout_con_access_expirado_revoca_refresh(self):
        usuario = db.session.get(Usuario, 2)
        token, refresh = crear_sesion(usuario)
        sid = decode_token(token)['sid']
        expirado = create_access_token(
            identity=str(usuario.id_usuario),
            additional_claims={'sid': sid},
            expires_delta=timedelta(seconds=-1),
        )

        respuesta = self.client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {expirado}'},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(db.session.get(SesionUsuario, sid).revocada)
        respuesta_refresh = self.client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh}'},
        )
        self.assertEqual(respuesta_refresh.status_code, 401)


if __name__ == '__main__':
    unittest.main()
