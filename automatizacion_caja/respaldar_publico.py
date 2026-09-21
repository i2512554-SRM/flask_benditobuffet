"""Respalda el esquema public a un archivo local, sin imprimir datos ni credenciales.

Requiere binarios oficiales pg_dump/pg_restore de la misma versión mayor que
PostgreSQL. El archivo contiene datos personales: conservarlo fuera de Git.

Uso: python -m automatizacion_caja.respaldar_publico --bin-dir RUTA_BIN
"""
import argparse
import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


TABLAS_CRITICAS = (
    'transacciones_caja', 'inventario_movimientos', 'compras_inventario',
    'pagos_empleados', 'usuario_perfiles', 'cierres_caja', 'solicitudes_insumos',
)


def respaldar(bin_dir, destino):
    load_dotenv()
    entorno = os.environ.copy()
    requeridas = ('DB_HOST', 'DB_USER', 'DB_PASSWORD')
    if any(not entorno.get(clave) for clave in requeridas):
        raise RuntimeError('Falta configuración de conexión a la base de datos.')

    carpeta_bin = Path(bin_dir).resolve()
    pg_dump = carpeta_bin / 'pg_dump.exe'
    pg_restore = carpeta_bin / 'pg_restore.exe'
    if not pg_dump.is_file() or not pg_restore.is_file():
        raise RuntimeError('No se encontraron pg_dump.exe y pg_restore.exe.')

    carpeta = Path(destino).resolve()
    carpeta.mkdir(parents=True, exist_ok=True)
    instante = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archivo = carpeta / f'benditobuffet_public_{instante}.dump'
    if archivo.exists():
        raise RuntimeError('El archivo de respaldo ya existe.')

    entorno['PGPASSWORD'] = entorno['DB_PASSWORD']
    entorno['PGSSLMODE'] = 'require'
    conexion = [
        '-h', entorno['DB_HOST'], '-p', entorno.get('DB_PORT', '6543'),
        '-U', entorno['DB_USER'], '-d', entorno.get('DB_NAME', 'postgres'),
    ]
    try:
        subprocess.run([
            str(pg_dump), *conexion, '--format=custom', '--compress=6',
            '--schema=public', '--no-owner', '--no-acl',
            '--enable-row-security', '--no-password', '--file', str(archivo),
        ], env=entorno, check=True, capture_output=True)
        if archivo.stat().st_size < 1024:
            raise RuntimeError('El respaldo generado es demasiado pequeño.')
        lista = subprocess.run([str(pg_restore), '--list', str(archivo)],
            check=True, capture_output=True, text=True).stdout
        faltantes = [nombre for nombre in TABLAS_CRITICAS
            if f'TABLE DATA public {nombre} ' not in lista]
        if faltantes:
            raise RuntimeError('Faltan tablas críticas en el respaldo: ' + ', '.join(faltantes))
        # Descomprime todas las entradas sin dejar una copia en texto plano.
        subprocess.run([str(pg_restore), '--file', 'NUL', str(archivo)],
            check=True, capture_output=True)
        resumen = hashlib.sha256()
        with archivo.open('rb') as flujo:
            for bloque in iter(lambda: flujo.read(1024 * 1024), b''):
                resumen.update(bloque)
        print(f'Respaldo verificado: {archivo}')
        print(f'Tamaño: {archivo.stat().st_size} bytes')
        print(f'SHA256: {resumen.hexdigest()}')
        print('Alcance: esquema public; no incluye Storage ni contraseñas de roles.')
        return archivo
    except (subprocess.CalledProcessError, RuntimeError) as error:
        if archivo.exists():
            archivo.unlink()
        if isinstance(error, subprocess.CalledProcessError):
            mensaje = (error.stderr or b'').decode('utf-8', errors='replace')
            raise RuntimeError('No se pudo crear o verificar el respaldo: ' + mensaje[:500]) from None
        raise


if __name__ == '__main__':
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument('--bin-dir', required=True)
    analizador.add_argument('--destino', default=str(Path(os.environ['LOCALAPPDATA']) / 'BenditoBuffet' / 'backups'))
    argumentos = analizador.parse_args()
    respaldar(argumentos.bin_dir, argumentos.destino)
