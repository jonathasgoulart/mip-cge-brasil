import json
import numpy as np
from pathlib import Path
import sys

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
TAX_JSON = BASE / 'data' / 'processed' / '2021_final' / 'tax_matrix_2019.json'
VBP_UF = BASE / 'output' / 'crosswalk' / 'vbp_iioas_all_ufs.npy'
N_SEC = 67

with open(TAX_JSON, 'r', encoding='utf-8') as f:
    tax_data = json.load(f).get('taxes_by_type', {})

tax_totals = np.zeros(N_SEC)
for tax_type, values in tax_data.items():
    vals = list(values.values())[:N_SEC] if isinstance(values, dict) else values[:N_SEC]
    if len(vals) >= N_SEC:
        tax_totals += np.array(vals[:N_SEC])

vbp_all68 = np.load(VBP_UF)
vbp_nat_68 = vbp_all68.sum(axis=0)

X_nat = np.zeros(N_SEC)
for ii in range(68):
    mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
    if mi < N_SEC: X_nat[mi] += vbp_nat_68[ii]

carga_tributaria = np.zeros(N_SEC)
valid = X_nat > 0
carga_tributaria[valid] = (tax_totals[valid] / X_nat[valid]) * 100

sys.path.insert(0, str(BASE))
try:
    from frontend.src.labels import DETAILED_SECTORS
    labels = DETAILED_SECTORS
except:
    labels = [f'Setor {i}' for i in range(N_SEC)]

results = []
for i in range(N_SEC):
    results.append({'id': i, 'name': labels[i], 'carga': carga_tributaria[i], 'imposto': tax_totals[i], 'vbp': X_nat[i]})

results.sort(key=lambda x: x['carga'], reverse=True)

print('--- CARGA TRIBUTÁRIA NACIONAL POR SETOR DA MATRIZ ---')
print(f'| Posição | Setor | Carga (%) | Imposto (Mi) | VBP (Mi)')
for idx, r in enumerate(results[:15], 1):
    print(f"| {idx:3d} | {r['name'][:40]:<40} | {r['carga']:>7.2f}% | R$ {r['imposto']:9,.0f} | R$ {r['vbp']:10,.0f}")

media_br = (tax_totals.sum() / X_nat.sum()) * 100
print(f'\nCarga Tributária Média Direta na Produção: {media_br:.2f}%')
