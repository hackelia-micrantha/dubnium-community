"""Generic, data-driven validation for public HTTP contract bundles."""
from __future__ import annotations
import argparse, json, math, re, sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID
MAX_BYTES = 1000000
MAX_DEPTH = 64
DRAFT = 'https://json-schema.org/draft/2020-12/schema'
OPENAPI = '3.1.2'
MARKERS = re.compile('^Status: (?:experimental|v1alpha|v1beta|stable)$.*?^Content: normative$.*?^Canonical source: .+$.*?^Generated: (?:no|yes from .+)$', re.M | re.S)
BCP14 = re.compile('\\b(?:MUST|MUST NOT|SHOULD|SHOULD NOT|MAY)\\b')
METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'}
KEYS = {'id', 'status', 'spec', 'openapi', 'schemas', 'examples', 'openapi_expectations'}

class BundleError(ValueError):
    pass

def load(path: Path) -> Any:
    if path.stat().st_size > MAX_BYTES:
        raise BundleError(f'{path}: file too large')

    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise BundleError(f'{path}: duplicate key {k}')
            out[k] = v
        return out

    def constant(v):
        raise BundleError(f'{path}: non-finite number {v}')
    try:
        return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise BundleError(f'{path}: invalid JSON: {e}') from e

def pointer(doc: Any, ref: str) -> Any:
    frag = ref[1:] if ref.startswith('#') else ref
    if not frag:
        return doc
    if not frag.startswith('/'):
        raise BundleError(f'unsupported pointer {ref}')
    cur = doc
    for raw in frag[1:].split('/'):
        token = raw.replace('~1', '/').replace('~0', '~')
        if isinstance(cur, dict) and token in cur:
            cur = cur[token]
        elif isinstance(cur, list) and token.isdigit() and (int(token) < len(cur)):
            cur = cur[int(token)]
        else:
            raise BundleError(f'unresolved pointer {ref}')
    return cur

def resolve(ref: str, source: Path, root: Path, cache: dict[Path, Any]) -> tuple[Any, Path]:
    if '://' in ref or ref.startswith('//'):
        raise BundleError(f'remote reference prohibited: {ref}')
    file, sep, frag = ref.partition('#')
    target = source if not file else (source.parent / file).resolve()
    try:
        target.relative_to(root)
    except ValueError as e:
        raise BundleError(f'reference escapes repository: {ref}') from e
    cache.setdefault(target, load(target))
    return (pointer(cache[target], f'#{frag}' if sep else ''), target)

def type_ok(v: Any, t: str) -> bool:
    return {'null': v is None, 'boolean': isinstance(v, bool), 'integer': isinstance(v, int) and (not isinstance(v, bool)), 'number': isinstance(v, (int, float)) and (not isinstance(v, bool)), 'string': isinstance(v, str), 'array': isinstance(v, list), 'object': isinstance(v, dict)}.get(t, False)

def validate(v: Any, s: Any, source: Path, root: Path, cache: dict[Path, Any] | None=None, loc: str='$', depth: int=0) -> list[str]:
    if depth > MAX_DEPTH:
        return [f'{loc}: recursion limit']
    if not isinstance(s, dict):
        return [f'{loc}: schema is not object']
    cache = cache or {source: load(source)}
    if '$ref' in s:
        try:
            t, p = resolve(s['$ref'], source, root, cache)
        except BundleError as e:
            return [f'{loc}: {e}']
        return validate(v, t, p, root, cache, loc, depth + 1)
    errs = []
    for name in ('allOf',):
        for branch in s.get(name, []):
            errs += validate(v, branch, source, root, cache, loc, depth + 1)
    for name, exact in (('anyOf', False), ('oneOf', True)):
        if name in s:
            results = [validate(v, b, source, root, cache, loc, depth + 1) for b in s[name]]
            count = sum((not x for x in results))
            if exact and count != 1 or (not exact and count == 0):
                return [f'{loc}: does not satisfy {name}']
    if 'not' in s and (not validate(v, s['not'], source, root, cache, loc, depth + 1)):
        return [f'{loc}: prohibited value']
    if 'const' in s and v != s['const']:
        errs.append(f'{loc}: const mismatch')
    if 'enum' in s and v not in s['enum']:
        errs.append(f'{loc}: enum mismatch')
    types = s.get('type')
    if types is not None:
        types = [types] if isinstance(types, str) else types
        if not isinstance(types, list) or not any((type_ok(v, t) for t in types)):
            return errs + [f'{loc}: type mismatch']
    if isinstance(v, dict):
        for k in s.get('required', []):
            if k not in v:
                errs.append(f'{loc}: missing {k}')
        props = s.get('properties', {})
        additional = s.get('additionalProperties', True)
        for k, item in v.items():
            if k in props:
                errs += validate(item, props[k], source, root, cache, f'{loc}.{k}', depth + 1)
            elif additional is False:
                errs.append(f'{loc}.{k}: additional property')
            elif isinstance(additional, dict):
                errs += validate(item, additional, source, root, cache, f'{loc}.{k}', depth + 1)
    if isinstance(v, list):
        if isinstance(s.get('minItems'), int) and len(v) < s['minItems']:
            errs.append(f'{loc}: too few items')
        if isinstance(s.get('maxItems'), int) and len(v) > s['maxItems']:
            errs.append(f'{loc}: too many items')
        if s.get('uniqueItems') and len({json.dumps(x, sort_keys=True, separators=(',', ':')) for x in v}) != len(v):
            errs.append(f'{loc}: duplicate items')
        if isinstance(s.get('items'), dict):
            for i, item in enumerate(v):
                errs += validate(item, s['items'], source, root, cache, f'{loc}[{i}]', depth + 1)
    if isinstance(v, str):
        if isinstance(s.get('minLength'), int) and len(v) < s['minLength']:
            errs.append(f'{loc}: too short')
        if isinstance(s.get('maxLength'), int) and len(v) > s['maxLength']:
            errs.append(f'{loc}: too long')
        if isinstance(s.get('pattern'), str) and (not re.search(s['pattern'], v)):
            errs.append(f'{loc}: pattern mismatch')
        try:
            if s.get('format') == 'uuid':
                UUID(v)
            elif s.get('format') == 'date-time':
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            elif s.get('format') == 'uri' and (not urlsplit(v).scheme):
                raise ValueError
        except (ValueError, TypeError):
            errs.append(f"{loc}: invalid {s.get('format')}")
    if isinstance(v, (int, float)) and (not isinstance(v, bool)):
        if isinstance(s.get('minimum'), (int, float)) and v < s['minimum']:
            errs.append(f'{loc}: below minimum')
        if isinstance(s.get('maximum'), (int, float)) and v > s['maximum']:
            errs.append(f'{loc}: above maximum')
    return errs

def refs(v: Any):
    if isinstance(v, dict):
        if isinstance(v.get('$ref'), str):
            yield v['$ref']
        for x in v.values():
            yield from refs(x)
    elif isinstance(v, list):
        for x in v:
            yield from refs(x)

def check_spec(path: Path) -> list[str]:
    text = path.read_text()
    head = '\n'.join(text.splitlines()[:12])
    out = []
    if not MARKERS.search(head):
        out.append(f'{path}: invalid normative markers')
    if not BCP14.search(text):
        out.append(f'{path}: missing BCP 14 requirement')
    return out

def check_schema(path: Path) -> list[str]:
    doc = load(path)
    out = []
    if not isinstance(doc, dict):
        return [f'{path}: schema root is not object']
    if doc.get('$schema') != DRAFT:
        out.append(f'{path}: wrong schema draft')
    if not isinstance(doc.get('$id'), str) or not doc['$id'].startswith('https://schemas.micrantha.com/dubnium/'):
        out.append(f'{path}: invalid $id')
    return out

def assertion(doc: Any, item: dict[str, Any]) -> bool:
    try:
        value = pointer(doc, item['pointer'])
        found = True
    except BundleError:
        value = None
        found = False
    op = item.get('operator')
    return op == 'present' and found or (op == 'absent' and (not found)) or (op == 'equals' and found and (value == item.get('value'))) or (op == 'contains' and found and isinstance(value, list) and (item.get('value') in value))

def check_openapi(path: Path, bundle: dict[str, Any], root: Path) -> list[str]:
    doc = load(path)
    out = []
    if not isinstance(doc, dict) or doc.get('openapi') != OPENAPI:
        return [f'{path}: invalid OpenAPI version']
    paths = doc.get('paths')
    if not isinstance(paths, dict):
        return [f'{path}: missing paths']
    cache = {path: doc}
    for ref in refs(doc):
        try:
            resolve(ref, path, root, cache)
        except BundleError as e:
            out.append(f'{path}: {e}')
    ops = []
    for route, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, operation in item.items():
            if method.lower() in METHODS:
                if not isinstance(operation, dict) or not isinstance(operation.get('operationId'), str):
                    out.append(f'{path}: {method} {route} missing operationId')
                else:
                    ops.append(operation['operationId'])
    if len(ops) != len(set(ops)):
        out.append(f'{path}: duplicate operationId')
    exp = bundle.get('openapi_expectations', {})
    for route in exp.get('paths', []):
        if route not in paths:
            out.append(f'{path}: missing path {route}')
    components = doc.get('components', {}).get('schemas', {})
    for name in exp.get('components', []):
        if name not in components:
            out.append(f'{path}: missing component {name}')
    for item in exp.get('assertions', []):
        if not assertion(doc, item):
            out.append(f'{path}: failed assertion {item}')
    return out

def check_example(path: Path, valid: bool, schemas: set[Path], root: Path) -> list[str]:
    doc = load(path)
    if not isinstance(doc, dict) or not isinstance(doc.get('$schema'), str):
        return [f'{path}: missing $schema']
    file, sep, frag = doc['$schema'].partition('#')
    schema = (path.parent / file).resolve()
    if schema not in schemas:
        return [f'{path}: schema outside bundle']
    target = pointer(load(schema), f'#{frag}' if sep else '')
    errors = validate(doc, target, schema, root)
    if valid and errors:
        return [f'{path}: positive example failed: {e}' for e in errors]
    if not valid and (not errors):
        return [f'{path}: negative example passed']
    return []

def validate_catalog(catalog_path: Path) -> list[str]:
    catalog_path = catalog_path.resolve()
    root = catalog_path.parent.parent.resolve()
    catalog = load(catalog_path)
    if not isinstance(catalog, dict) or catalog.get('version') != 1:
        return [f'{catalog_path}: catalog version must be 1']
    bundles = catalog.get('bundles')
    if not isinstance(bundles, list):
        return [f'{catalog_path}: bundles must be array']
    out = []
    seen = set()
    for b in bundles:
        if not isinstance(b, dict):
            out.append('bundle must be object')
            continue
        unknown = set(b) - KEYS
        if unknown:
            out.append(f"{b.get('id')}: code hooks/unknown keys prohibited: {sorted(unknown)}")
        bid = b.get('id')
        if not isinstance(bid, str) or not bid:
            out.append('bundle id required')
            continue
        if bid in seen:
            out.append(f'duplicate bundle {bid}')
        seen.add(bid)
        spec = root / b.get('spec', '')
        api = root / b.get('openapi', '')
        raw = b.get('schemas')
        if not spec.is_file() or not api.is_file():
            out.append(f'{bid}: missing spec or OpenAPI')
            continue
        if not isinstance(raw, list) or not raw:
            out.append(f'{bid}: schemas required')
            continue
        schemas = {(root / x).resolve() for x in raw if isinstance(x, str)}
        out += check_spec(spec) + check_openapi(api, b, root)
        for schema in schemas:
            out += check_schema(schema) if schema.is_file() else [f'{bid}: missing {schema}']
        examples = b.get('examples')
        if not isinstance(examples, dict):
            out.append(f'{bid}: examples required')
            continue
        for category, valid in (('positive', True), ('negative', False)):
            paths = examples.get(category)
            if not isinstance(paths, list) or not paths:
                out.append(f'{bid}: {category} examples required')
                continue
            for item in paths:
                p = (root / item).resolve() if isinstance(item, str) else Path()
                out += check_example(p, valid, schemas, root) if p.is_file() else [f'{bid}: missing example {item}']
    return out

def main(argv: list[str] | None=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', nargs='?', type=Path, default=Path(__file__).with_name('service-bundles.json'))
    args = parser.parse_args(argv)
    try:
        errors = validate_catalog(args.catalog)
    except (BundleError, OSError) as e:
        errors = [str(e)]
    if errors:
        print('contract bundle validation failed:', file=sys.stderr)
        for e in sorted(set(errors)):
            print(f'- {e}', file=sys.stderr)
        return 1
    print('contract bundle validation passed')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
