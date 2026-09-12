"""Comprobación opcional de bloqueos en PostgreSQL de pruebas, sin modificar filas."""
import os
import unittest
from sqlalchemy import create_engine, text


@unittest.skipUnless(os.getenv('TEST_POSTGRES_URL'), 'Falta TEST_POSTGRES_URL de una base PostgreSQL de pruebas')
class BloqueosPostgresTest(unittest.TestCase):
    def test_bloqueos_se_liberan_al_terminar_transaccion(self):
        engine = create_engine(os.environ['TEST_POSTGRES_URL'], pool_size=2, max_overflow=0)
        try:
            with engine.connect() as primera, engine.connect() as segunda:
                for clave in (72451001, 72451002):
                    self.assertTrue(primera.scalar(text('SELECT pg_try_advisory_xact_lock(:clave)'), {'clave': clave}))
                    self.assertFalse(segunda.scalar(text('SELECT pg_try_advisory_xact_lock(:clave)'), {'clave': clave}))
                    primera.rollback()
                    self.assertTrue(segunda.scalar(text('SELECT pg_try_advisory_xact_lock(:clave)'), {'clave': clave}))
                    segunda.rollback()
        finally:
            engine.dispose()
