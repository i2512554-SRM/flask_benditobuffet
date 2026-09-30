import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'movil'
prefixes = {k: '/api/' + k for k in ('auth', 'admin', 'caja', 'personal', 'inventario', 'perfil', 'cocina', 'trabajador')}
prefixes.update(rendimiento='/api', indicadores='/api')
roles = {'admin_required': ['ADMIN'], '_solo_admin': ['ADMIN'], '_cocinero': ['COCINA'], '_trabajador': ['CAJERA', 'COCINA', 'TRABAJADOR'], '_caja': ['ADMIN', 'CAJERA'], '_inventario_stock': ['ADMIN', 'COCINA']}
endpoints = []
for path in sorted((ROOT / 'api').glob('*.py')):
    source = path.read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        route = next((d for d in node.decorator_list if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == 'route'), None)
        if route is None and path.stem != 'dni':
            continue
        decorators = [ast.unparse(d) for d in node.decorator_list if d is not route]
        allowed = []
        for d in decorators:
            allowed.extend(roles.get(d, []))
        if '_permitido' in decorators:
            allowed = ['ADMIN'] if path.stem == 'indicadores' else ['ADMIN', 'CAJERA']
        auth = 'JWT de acceso y sesión vigente'
        if not decorators:
            auth = 'Público' if node.name == 'login' else 'Bearer firmado incluso expirado para revocar su propia sesión'
        elif any('refresh=True' in d for d in decorators):
            auth = 'JWT de renovación y sesión vigente'
        fields = []
        for item in ast.walk(node):
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute) and item.func.attr == 'get' and item.args and isinstance(item.args[0], ast.Constant):
                owner = ast.unparse(item.func.value)
                if owner in ('data', 'request.args', 'origen', 'request.files', 'linea'):
                    fields.append({'origen': owner, 'campo': item.args[0].value, 'expresion': ast.unparse(item)})
            if isinstance(item, ast.Subscript) and isinstance(item.slice, ast.Constant) and ast.unparse(item.value) in ('data', 'request.args'):
                fields.append({'origen': ast.unparse(item.value), 'campo': item.slice.value, 'expresion': ast.unparse(item)})
        methods = next((ast.literal_eval(k.value) for k in route.keywords if k.arg == 'methods'), ['GET']) if route else ['GET']
        url = prefixes[path.stem] + ast.literal_eval(route.args[0]) if route else '/api/dni/<dni>'
        endpoints.append({'metodos': methods, 'ruta': url, 'roles': allowed or ['Cualquier rol activo'], 'autenticacion': auth, 'fuente': path.relative_to(ROOT).as_posix(), 'linea': node.lineno, 'funcion': node.name, 'decoradores': decorators, 'entradas_detectadas': fields, 'respuestas': [ast.unparse(x.value) for x in ast.walk(node) if isinstance(x, ast.Return)], 'codigo_fuente': ast.get_source_segment(source, node)})

schemas = []
for path in sorted((ROOT / 'schemas').glob('*.py')):
    source = path.read_text(encoding='utf-8-sig')
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef):
            schemas.append({'nombre': node.name, 'fuente': path.relative_to(ROOT).as_posix(), 'linea': node.lineno, 'definicion': ast.get_source_segment(source, node)})

router = (ROOT / 'frontend/src/router/index.js').read_text(encoding='utf-8-sig')
views = []
for match in re.finditer(r'\{\s*path:\s*(.+?),\s*name:\s*[\'\"](.+?)[\'\"],\s*component:\s*\(\)\s*=>\s*import\([\'\"](.+?)[\'\"]\)(.*?)(?=\n  \})', router, re.S):
    path = (ROOT / 'frontend/src/router' / match[3]).resolve()
    source = path.read_text(encoding='utf-8-sig')
    script = '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', source, re.S))
    views.append({'nombre': match[2], 'link': match[1], 'meta': match[4].strip().strip(','), 'fuente': path.relative_to(ROOT).as_posix(), 'llamadas': [line.strip() for line in source.splitlines() if re.search(r'api\.(get|post|put|delete)\(', line)], 'campos_ui': sorted(set(re.findall(r'v-model(?:\:[\w-]+)?="([^"]+)"', source))), 'script': script})

files = sorted(set([e['fuente'] for e in endpoints] + [s['fuente'] for s in schemas] + [v['fuente'] for v in views] + ['models.py', 'app.py', 'api/roles.py', 'api/sesiones.py', 'frontend/src/router/index.js', 'frontend/src/router/links.js', 'frontend/src/config/roles.js', 'frontend/src/config/axios.js']))
catalog = {'fecha_revision': '2026-09-30', 'naturaleza': 'Extracción estática de código, no OpenAPI ni validación de despliegue. Las entradas detectadas pueden depender de helpers; leer reglas del documento.', 'endpoints': endpoints, 'esquemas': schemas, 'vistas': views, 'huellas_sha256': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}}
(OUT / 'catalogo_codigo.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'endpoints': len(endpoints), 'esquemas': len(schemas), 'vistas': len(views)}, ensure_ascii=False))
