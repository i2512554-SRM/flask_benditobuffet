import importlib
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from marshmallow import Schema

result = []
for path in sorted((ROOT / 'schemas').glob('*.py')):
    module = importlib.import_module('schemas.' + path.stem)
    for name, item in vars(module).items():
        if not inspect.isclass(item) or item.__module__ != module.__name__ or not issubclass(item, Schema):
            continue
        schema = item()
        fields = []
        for field_name, field in schema.fields.items():
            fields.append({'nombre': field_name, 'tipo_marshmallow': type(field).__name__, 'nullable_declarado': field.allow_none, 'atributo': field.attribute, 'solo_salida': field.dump_only})
        result.append({'nombre': name, 'fuente': path.relative_to(ROOT).as_posix(), 'campos': fields})
(ROOT / 'docs/movil/esquemas_respuesta.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'esquemas': len(result), 'campos': sum(len(s['campos']) for s in result)}))
