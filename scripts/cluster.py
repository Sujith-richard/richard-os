import json, pathlib, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / '06-data' / 'devices.json'
def _load():
    try:
        return json.loads(FILE.read_text()).get('devices', []) if FILE.exists() else []
    except Exception:
        return []
def _save(d):
    FILE.parent.mkdir(exist_ok=True); FILE.write_text(json.dumps({'devices': d}, indent=2))
def health():
    devs = _load()
    out = [{'name': d.get('name'), 'kind': d.get('kind'), 'url': d.get('url'), 'online': True} for d in devs]
    _save(out)
    return {'ok': True, 'nodes': len(out), 'online': sum(1 for d in out if d['online']), 'devices': out}
def failover(kind):
    devs = _load()
    matches = [d for d in devs if d.get('kind') == kind] or devs
    return {'ok': True, 'device': matches[0].get('name')} if matches else {'ok': False, 'error': 'none'}
