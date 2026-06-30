import json
from pathlib import Path

ROOT = Path.cwd()
A = ROOT / 'outputs' / 'test_20_results_before_layout.json'
B = ROOT / 'outputs' / 'test_20_results_layout.json'

def load(p):
    try:
        return json.load(open(p, 'r', encoding='utf-8'))
    except Exception as e:
        print('Error reading', p, e)
        return []

ra = load(A)
rb = load(B)
ma = {Path(p['path']).name: p for p in ra}
mb = {Path(p['path']).name: p for p in rb}

fields = ['email','phone','education','experience']
changes = []
for name in ma:
    a = ma[name].get('parsed') or {}
    b = mb.get(name, {}).get('parsed') or {}
    for f in fields:
        va = bool(a.get(f))
        vb = bool(b.get(f))
        if va != vb:
            changes.append((name, f, va, vb))

print('Total files compared:', len(ma))
print('Total changes detected:', len(changes))
for c in changes:
    print(f"{c[0]}: {c[1]} - before={c[2]} after={c[3]}")
