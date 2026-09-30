"""Publica los fallos de unittest como anotaciones de GitHub Actions (visibles sin iniciar sesión)."""
import re
import sys
from collections import OrderedDict

MAX_ANOTACIONES = 9


def bloques(texto):
    partes = re.split(r'^={70}$', texto, flags=re.M)
    for parte in partes[1:]:
        cabecera = re.match(r'\s*(ERROR|FAIL): (\S+) \(([^)]+)\)', parte)
        if not cabecera:
            continue
        secciones = parte.split('-' * 70)
        cuerpo = secciones[1] if len(secciones) > 1 else ''
        lineas = [l for l in cuerpo.strip().splitlines() if l.strip()]
        excepcion = next((l for l in reversed(lineas) if not l.startswith((' ', 'Traceback', '(Background', '[SQL', '[parameters'))
                          and not l.startswith('During handling')), 'Sin detalle')
        ubicaciones = re.findall(r'File ".*?/((?:api|schemas|tests|models|app|bd)[^"]*)", line (\d+)', cuerpo)
        propia = next((f'{archivo}:{linea}' for archivo, linea in reversed(ubicaciones)
                       if not archivo.startswith('tests/')), ubicaciones[-1][0] + ':' + ubicaciones[-1][1] if ubicaciones else '')
        yield cabecera.group(1), cabecera.group(3), excepcion.strip()[:300], propia


def main(ruta):
    texto = open(ruta, encoding='utf-8', errors='replace').read()
    grupos = OrderedDict()
    for tipo, prueba, excepcion, ubicacion in bloques(texto):
        grupo = grupos.setdefault((tipo, excepcion), {'pruebas': [], 'ubicaciones': set()})
        grupo['pruebas'].append(prueba)
        if ubicacion:
            grupo['ubicaciones'].add(ubicacion)
    resumen = re.findall(r'^(Ran \d+ tests.*|FAILED \(.*\)|OK.*)$', texto, flags=re.M)
    print(f"::error title=Resumen de pruebas::{' | '.join(resumen[-2:]) or 'La ejecución terminó antes del resumen'}")
    for (tipo, excepcion), grupo in sorted(grupos.items(), key=lambda x: -len(x[1]['pruebas']))[:MAX_ANOTACIONES]:
        ejemplos = ', '.join(p.rsplit('.', 1)[-1] for p in grupo['pruebas'][:4])
        donde = ', '.join(sorted(grupo['ubicaciones'])[:3])
        mensaje = f'{excepcion}%0AEn: {donde or "-"}%0AEjemplos: {ejemplos}'
        print(f'::error title={tipo} en {len(grupo["pruebas"])} prueba(s)::{mensaje}')
    if not grupos and not resumen:
        cola = texto.strip().splitlines()[-5:]
        print('::error title=Fallo sin bloques de unittest::' + '%0A'.join(l[:200] for l in cola))


if __name__ == '__main__':
    main(sys.argv[1])
