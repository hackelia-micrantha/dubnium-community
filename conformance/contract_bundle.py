"""Generic, data-driven validation for public HTTP contract bundles."""
from __future__ import annotations
import argparse,json,math,re,sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

MAX_BYTES=1_000_000; MAX_DEPTH=64; MAX_ITEMS=10_000
DRAFT="https://json-schema.org/draft/2020-12/schema"; OPENAPI="3.1.2"
MARKERS=re.compile(r"^Status: (?:experimental|v1alpha|v1beta|stable)$.*?^Content: normative$.*?^Canonical source: .+$.*?^Generated: (?:no|yes from .+)$",re.M|re.S)
BCP14=re.compile(r"\b(?:MUST|MUST NOT|SHOULD|SHOULD NOT|MAY)\b")
METHODS={"get","put","post","delete","options","head","patch","trace"}
BUNDLE_KEYS={"id","status","spec","openapi","schemas","examples","operations","required_schema_defs","schema_bindings","openapi_expectations"}
KW={"$schema","$id","$defs","$ref","title","description","type","properties","required","additionalProperties","items","minItems","maxItems","uniqueItems","minLength","maxLength","pattern","format","minimum","maximum","enum","const","anyOf","oneOf","allOf","not","default","examples","deprecated","readOnly","writeOnly"}
ANN={"title","description","default","examples","deprecated","readOnly","writeOnly"}; FORMATS={"uuid","date-time","uri"}; TYPES={"null","boolean","integer","number","string","array","object"}; UNORDERED={"required","enum","type","allOf","anyOf","oneOf"}
class BundleError(ValueError):pass

def load(p:Path):
 if p.stat().st_size>MAX_BYTES:raise BundleError(f"{p}: file too large")
 def pairs(xs):
  d={}
  for k,v in xs:
   if k in d:raise BundleError(f"{p}: duplicate key {k}")
   d[k]=v
  return d
 def bad(v):raise BundleError(f"{p}: non-finite number {v}")
 try:x=json.loads(p.read_text(),object_pairs_hook=pairs,parse_constant=bad)
 except (OSError,UnicodeDecodeError,json.JSONDecodeError) as e:raise BundleError(f"{p}: invalid JSON: {e}") from e
 shape(x,p);return x

def shape(x,p,d=0):
 if d>MAX_DEPTH:raise BundleError(f"{p}: nesting exceeds {MAX_DEPTH}")
 if isinstance(x,dict):
  if len(x)>MAX_ITEMS:raise BundleError(f"{p}: object too large")
  for v in x.values():shape(v,p,d+1)
 elif isinstance(x,list):
  if len(x)>MAX_ITEMS:raise BundleError(f"{p}: array too large")
  for v in x:shape(v,p,d+1)
 elif isinstance(x,float) and not math.isfinite(x):raise BundleError(f"{p}: non-finite number")

def contained(root:Path,p:Path,label="path"):
 q=p.resolve()
 try:q.relative_to(root.resolve())
 except ValueError as e:raise BundleError(f"{label} escapes repository: {p}") from e
 return q

def ptr(doc,ref):
 f=ref[1:] if ref.startswith("#") else ref
 if not f:return doc
 if not f.startswith("/"):raise BundleError(f"unsupported pointer {ref}")
 x=doc
 for raw in f[1:].split("/"):
  k=raw.replace("~1","/").replace("~0","~")
  if isinstance(x,dict) and k in x:x=x[k]
  elif isinstance(x,list) and k.isdigit() and int(k)<len(x):x=x[int(k)]
  else:raise BundleError(f"unresolved pointer {ref}")
 return x

def resolve(ref,source,root,cache):
 if "://" in ref or ref.startswith("//"):raise BundleError(f"remote reference prohibited: {ref}")
 f,sep,frag=ref.partition("#"); p=source if not f else contained(root,source.parent/f,"reference")
 if not p.is_file():raise BundleError(f"unresolved reference: {ref}")
 cache.setdefault(p,load(p));return ptr(cache[p],f"#{frag}" if sep else ""),p

def refs(x):
 if isinstance(x,dict):
  if isinstance(x.get("$ref"),str):yield x["$ref"]
  for v in x.values():yield from refs(v)
 elif isinstance(x,list):
  for v in x:yield from refs(v)

def lint_schema_node(s,location="$"):
 if not isinstance(s,dict):return [f"{location}: schema must be an object"]
 out=[]; unknown=sorted(set(s)-KW)
 if unknown:out.append(f"{location}: unsupported schema keywords {unknown}")
 t=s.get("type")
 ts=[t] if isinstance(t,str) else t
 if t is not None and (not isinstance(ts,list) or not ts or any(not isinstance(v,str) or v not in TYPES for v in ts)):out.append(f"{location}: unsupported type")
 fmt=s.get("format")
 if fmt is not None and fmt not in FORMATS:out.append(f"{location}: unsupported format {fmt}")
 pat=s.get("pattern")
 if isinstance(pat,str):
  try:re.compile(pat)
  except re.error as e:out.append(f"{location}: invalid pattern {e}")
 req=s.get("required")
 if req is not None and (not isinstance(req,list) or any(not isinstance(v,str) for v in req) or len(req)!=len(set(req))):out.append(f"{location}: required must contain unique strings")
 for n in ("properties","$defs"):
  v=s.get(n)
  if v is not None:
   if not isinstance(v,dict):out.append(f"{location}.{n}: must be object")
   else:
    for k,c in v.items():out+=lint_schema_node(c,f"{location}.{n}.{k}")
 ap=s.get("additionalProperties")
 if isinstance(ap,dict):out+=lint_schema_node(ap,f"{location}.additionalProperties")
 it=s.get("items")
 if isinstance(it,dict):out+=lint_schema_node(it,f"{location}.items")
 elif it is not None:out.append(f"{location}.items: unsupported")
 for n in ("anyOf","oneOf","allOf"):
  v=s.get(n)
  if v is not None:
   if not isinstance(v,list) or not v:out.append(f"{location}.{n}: non-empty array required")
   else:
    for i,c in enumerate(v):out+=lint_schema_node(c,f"{location}.{n}[{i}]")
 if isinstance(s.get("not"),dict):out+=lint_schema_node(s["not"],f"{location}.not")
 elif "not" in s:out.append(f"{location}.not: schema required")
 return out

def type_ok(v,t):return {"null":v is None,"boolean":isinstance(v,bool),"integer":isinstance(v,int) and not isinstance(v,bool),"number":isinstance(v,(int,float)) and not isinstance(v,bool),"string":isinstance(v,str),"array":isinstance(v,list),"object":isinstance(v,dict)}[t]

def validate(v,s,source,root,cache=None,loc="$",depth=0):
 if depth>MAX_DEPTH:return [f"{loc}: recursion limit"]
 if not isinstance(s,dict):return [f"{loc}: schema is not object"]
 cache=cache or {source:load(source)}
 if "$ref" in s:
  try:t,p=resolve(s["$ref"],source,root,cache)
  except BundleError as e:return [f"{loc}: {e}"]
  return validate(v,t,p,root,cache,loc,depth+1)
 e=[]
 for b in s.get("allOf",[]):e+=validate(v,b,source,root,cache,loc,depth+1)
 for n,exact in (("anyOf",False),("oneOf",True)):
  if n in s:
   r=[validate(v,b,source,root,cache,loc,depth+1) for b in s[n]]; good=sum(not x for x in r)
   if (exact and good!=1) or (not exact and not good):return [f"{loc}: does not satisfy {n}"]
 if "not" in s and not validate(v,s["not"],source,root,cache,loc,depth+1):return [f"{loc}: prohibited value"]
 if "const" in s and v!=s["const"]:e.append(f"{loc}: const mismatch")
 if "enum" in s and v not in s["enum"]:e.append(f"{loc}: enum mismatch")
 t=s.get("type")
 if t is not None:
  ts=[t] if isinstance(t,str) else t
  if not any(type_ok(v,x) for x in ts):return e+[f"{loc}: type mismatch"]
 if isinstance(v,dict):
  for k in s.get("required",[]):
   if k not in v:e.append(f"{loc}: missing {k}")
  props=s.get("properties",{}); ap=s.get("additionalProperties",True)
  for k,x in v.items():
   if k in props:e+=validate(x,props[k],source,root,cache,f"{loc}.{k}",depth+1)
   elif ap is False:e.append(f"{loc}.{k}: additional property")
   elif isinstance(ap,dict):e+=validate(x,ap,source,root,cache,f"{loc}.{k}",depth+1)
 if isinstance(v,list):
  if isinstance(s.get("minItems"),int) and len(v)<s["minItems"]:e.append(f"{loc}: too few items")
  if isinstance(s.get("maxItems"),int) and len(v)>s["maxItems"]:e.append(f"{loc}: too many items")
  if s.get("uniqueItems") and len({json.dumps(x,sort_keys=True,separators=(",",":")) for x in v})!=len(v):e.append(f"{loc}: duplicate items")
  if isinstance(s.get("items"),dict):
   for i,x in enumerate(v):e+=validate(x,s["items"],source,root,cache,f"{loc}[{i}]",depth+1)
 if isinstance(v,str):
  if isinstance(s.get("minLength"),int) and len(v)<s["minLength"]:e.append(f"{loc}: too short")
  if isinstance(s.get("maxLength"),int) and len(v)>s["maxLength"]:e.append(f"{loc}: too long")
  if isinstance(s.get("pattern"),str) and not re.search(s["pattern"],v):e.append(f"{loc}: pattern mismatch")
  try:
   if s.get("format")=="uuid":UUID(v)
   elif s.get("format")=="date-time":datetime.fromisoformat(v.replace("Z","+00:00"))
   elif s.get("format")=="uri" and not urlsplit(v).scheme:raise ValueError
  except (ValueError,TypeError):e.append(f"{loc}: invalid {s.get('format')}")
 if isinstance(v,(int,float)) and not isinstance(v,bool):
  if isinstance(s.get("minimum"),(int,float)) and v<s["minimum"]:e.append(f"{loc}: below minimum")
  if isinstance(s.get("maximum"),(int,float)) and v>s["maximum"]:e.append(f"{loc}: above maximum")
 return e

def check_spec(p):
 text=p.read_text();head="\n".join(text.splitlines()[:12]);out=[]
 if not MARKERS.search(head):out.append(f"{p}: invalid normative markers")
 if not BCP14.search(text):out.append(f"{p}: missing BCP 14 requirement")
 return out

def check_schema(p):
 d=load(p);out=[]
 if not isinstance(d,dict):return [f"{p}: schema root is not object"]
 if d.get("$schema")!=DRAFT:out.append(f"{p}: wrong schema draft")
 if not isinstance(d.get("$id"),str) or not d["$id"].startswith("https://schemas.micrantha.com/dubnium/"):out.append(f"{p}: invalid $id")
 out+=lint_schema_node(d);return out

def assertion(doc,a):
 try:v=ptr(doc,a["pointer"]);found=True
 except BundleError:v=None;found=False
 op=a.get("operator")
 return (op=="present" and found) or (op=="absent" and not found) or (op=="equals" and found and v==a.get("value")) or (op=="contains" and found and isinstance(v,list) and a.get("value") in v) or (op=="contains_text" and found and isinstance(v,str) and str(a.get("value")) in v)

def operation_ids(doc):
 return [op["operationId"] for item in doc.get("paths",{}).values() if isinstance(item,dict) for m,op in item.items() if m.lower() in METHODS and isinstance(op,dict) and isinstance(op.get("operationId"),str)]

def check_openapi(p,b,root):
 d=load(p);out=[]
 if not isinstance(d,dict) or d.get("openapi")!=OPENAPI:return [f"{p}: invalid OpenAPI version"]
 if not isinstance(d.get("paths"),dict):return [f"{p}: missing paths"]
 cache={p:d}
 for r in refs(d):
  try:resolve(r,p,root,cache)
  except BundleError as x:out.append(f"{p}: {x}")
 ids=operation_ids(d)
 if len(ids)!=len(set(ids)):out.append(f"{p}: duplicate operationId")
 for route in b.get("openapi_expectations",{}).get("paths",[]):
  if route not in d["paths"]:out.append(f"{p}: missing path {route}")
 comps=d.get("components",{}).get("schemas",{})
 for n in b.get("openapi_expectations",{}).get("components",[]):
  if n not in comps:out.append(f"{p}: missing component {n}")
 for a in b.get("openapi_expectations",{}).get("assertions",[]):
  if not assertion(d,a):out.append(f"{p}: failed assertion {a}")
 return out

def check_example(p,valid,schemas,root):
 d=load(p)
 if not isinstance(d,dict) or not isinstance(d.get("$schema"),str):return [f"{p}: missing $schema"]
 f,sep,frag=d["$schema"].partition("#");s=contained(root,p.parent/f,"example schema")
 if s not in schemas:return [f"{p}: schema outside bundle"]
 errors=validate(d,ptr(load(s),f"#{frag}" if sep else ""),s,root)
 if valid and errors:return [f"{p}: positive example failed: {x}" for x in errors]
 if not valid and not errors:return [f"{p}: negative example passed"]
 return []

def normalized(s,source,root,cache):
 while isinstance(s,dict) and "$ref" in s:s,source=resolve(s["$ref"],source,root,cache)
 if isinstance(s,dict):
  out={}
  for k,v in s.items():
   if k in ANN or k in {"$schema","$id","$defs"}:continue
   x=normalized(v,source,root,cache)
   if k in UNORDERED and isinstance(x,list):x=sorted(x,key=lambda z:json.dumps(z,sort_keys=True,separators=(",",":")))
   out[k]=x
  return out
 if isinstance(s,list):return [normalized(x,source,root,cache) for x in s]
 return s

def check_bindings(b,api,schemas,root):
 out=[];docs={api:load(api)}
 for s in schemas:docs[s]=load(s)
 for x in b.get("schema_bindings",[]):
  try:
   sp=schemas[0];left=normalized(ptr(docs[sp],x["schema_pointer"]),sp,root,docs);right=normalized(ptr(docs[api],x["openapi_pointer"]),api,root,docs)
  except (BundleError,KeyError,TypeError) as e:out.append(f"{b.get('id')}: invalid schema binding {x}: {e}");continue
  if left!=right:out.append(f"{b.get('id')}: canonical/OpenAPI schema mismatch {x['schema_pointer']} != {x['openapi_pointer']}")
 return out

def validate_catalog(path:Path):
 path=path.resolve();root=path.parent.parent.resolve();cat=load(path)
 if not isinstance(cat,dict) or cat.get("version")!=1:return [f"{path}: catalog version must be 1"]
 bundles=cat.get("bundles")
 if not isinstance(bundles,list):return [f"{path}: bundles must be array"]
 out=[];seen=set()
 for b in bundles:
  if not isinstance(b,dict):out.append("bundle must be object");continue
  unknown=set(b)-BUNDLE_KEYS
  if unknown:out.append(f"{b.get('id')}: code hooks/unknown keys prohibited: {sorted(unknown)}")
  bid=b.get("id")
  if not isinstance(bid,str) or not bid:out.append("bundle id required");continue
  if bid in seen:out.append(f"duplicate bundle {bid}")
  seen.add(bid)
  try:spec=contained(root,root/b.get("spec",""),"spec");api=contained(root,root/b.get("openapi",""),"OpenAPI")
  except (BundleError,TypeError) as e:out.append(f"{bid}: {e}");continue
  raw=b.get("schemas")
  if not spec.is_file() or not api.is_file() or not isinstance(raw,list) or not raw:out.append(f"{bid}: missing spec, OpenAPI, or schemas");continue
  schemas=[]
  try:schemas=[contained(root,root/x,"schema") for x in raw if isinstance(x,str)]
  except BundleError as e:out.append(f"{bid}: {e}");continue
  if len(schemas)!=len(raw) or any(not x.is_file() for x in schemas):out.append(f"{bid}: missing schema");continue
  out+=check_spec(spec)+check_openapi(api,b,root)
  for s in schemas:out+=check_schema(s)
  defs=load(schemas[0]).get("$defs",{})
  for n in b.get("required_schema_defs",[]):
   if n not in defs:out.append(f"{bid}: missing canonical schema definition {n}")
  ex=b.get("examples")
  if not isinstance(ex,dict):out.append(f"{bid}: examples required");continue
  positive=set();schema_set=set(schemas)
  for catname,valid in (("positive",True),("negative",False)):
   items=ex.get(catname)
   if not isinstance(items,list) or not items:out.append(f"{bid}: {catname} examples required");continue
   for item in items:
    if not isinstance(item,str):out.append(f"{bid}: example path must be string");continue
    try:p=contained(root,root/item,"example")
    except BundleError as e:out.append(f"{bid}: {e}");continue
    if not p.is_file():out.append(f"{bid}: missing example {item}");continue
    if valid:positive.add(item)
    out+=check_example(p,valid,schema_set,root)
  ids=set(operation_ids(load(api)));ops=b.get("operations")
  if not isinstance(ops,dict):out.append(f"{bid}: operations mapping required")
  else:
   mapped=set(ops)
   if mapped!=ids:out.append(f"{bid}: operation coverage mismatch; missing={sorted(ids-mapped)} extra={sorted(mapped-ids)}")
   for op,items in ops.items():
    if not isinstance(items,list) or not items:out.append(f"{bid}: {op} needs examples")
    elif any(x not in positive for x in items):out.append(f"{bid}: {op} references non-positive example")
  out+=check_bindings(b,api,schemas,root)
 return out

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("catalog",nargs="?",type=Path,default=Path(__file__).with_name("service-bundles.json"));a=p.parse_args(argv)
 try:errors=validate_catalog(a.catalog)
 except (BundleError,OSError) as e:errors=[str(e)]
 if errors:
  print("contract bundle validation failed:",file=sys.stderr)
  for e in sorted(set(errors)):print(f"- {e}",file=sys.stderr)
  return 1
 print("contract bundle validation passed");return 0
if __name__=="__main__":raise SystemExit(main())
