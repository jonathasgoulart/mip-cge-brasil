"""
Inspeciona tax_matrix_hybrid_by_state.json e ctb_1990-2024 para entender 
o que ja temos de dados fiscais e o que precisamos completar com o ICMS 2019.
"""
import json, sys, openpyxl
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')

# --- 1. tax_matrix_hybrid_by_state.json ---
p = BASE / 'data' / 'processed' / '2021_final' / 'tax_matrix_hybrid_by_state.json'
with open(p, encoding='utf-8') as f:
    d = json.load(f)

print('=== tax_matrix_hybrid_by_state.json ===')
print('Chaves de topo:', list(d.keys())[:10])
if 'metadata' in d:
    print('Metadata:', d['metadata'])
if 'year' in d:
    print('Year:', d['year'])

# Verificar estrutura interna
for key in list(d.keys())[:3]:
    val = d[key]
    if isinstance(val, dict):
        print(f'  [{key}]: sub-keys = {list(val.keys())[:8]}')
        inner = list(val.values())[0]
        if isinstance(inner, list):
            print(f'    -> lista com {len(inner)} items, ex: {inner[:3]}')
    elif isinstance(val, list):
        print(f'  [{key}]: lista com {len(val)} items')
    else:
        print(f'  [{key}]: {str(val)[:100]}')

if 'RJ' in d:
    rj = d['RJ']
    print()
    print('Estrutura d[RJ]:', type(rj))
    if isinstance(rj, dict):
        print('  Sub-chaves:', list(rj.keys())[:10])
        for k, v in list(rj.items())[:3]:
            print(f'  {k}: {str(v)[:60]}')

# --- 2. CTB 1990-2024 ---
print()
print('=== ctb_1990-2024_0.xlsx ===')
wb = openpyxl.load_workbook(BASE / 'data' / 'ctb_1990-2024_0.xlsx', read_only=True)
print('Abas:', wb.sheetnames)
ws = wb.active
rows = list(ws.iter_rows(min_row=1, max_row=8, values_only=True))
for i, row in enumerate(rows):
    vals = [str(v)[:25] if v is not None else '' for v in list(row)[:10]]
    print(f'  L{i+1}: {vals}')
wb.close()
