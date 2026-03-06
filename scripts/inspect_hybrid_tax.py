"""
Inspeciona tax_matrix_hybrid_by_state.json para entender a estrutura
e verificar quais tributos e estados estao disponíveis.
"""
import json, sys, numpy as np
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
p = BASE / 'data' / 'processed' / '2021_final' / 'tax_matrix_hybrid_by_state.json'

with open(p, encoding='utf-8') as f:
    d = json.load(f)

print('=== ESTRUTURA tax_matrix_hybrid_by_state.json ===')
print(f'Tipo raiz: {type(d).__name__}')
print(f'Chaves de topo ({len(d)}): {list(d.keys())}')

# Verificar estrutura de cada chave
first_key = list(d.keys())[0]
val = d[first_key]
print(f'\nEstrutura de d["{first_key}"] tipo={type(val).__name__}')

if isinstance(val, dict):
    print(f'  Sub-chaves: {list(val.keys())}')
    for sk, sv in list(val.items())[:3]:
        if isinstance(sv, list):
            print(f'    {sk}: lista com {len(sv)} itens, ex: {[round(x,1) for x in sv[:5]]}')
        else:
            print(f'    {sk}: {str(sv)[:80]}')
elif isinstance(val, list):
    print(f'  Lista com {len(val)} itens')
    print(f'  Primeiros 5: {[round(x, 2) if isinstance(x, (int,float)) else x for x in val[:5]]}')

# Verificar se é {UF: {tributo: [67 valores]}} ou {UF: [67 valores]} ou outra
# Coletar todas as UFs e a estrutura interna
states = [k for k in d.keys() if len(k) == 2 and k.isupper()]
others = [k for k in d.keys() if k not in states]
print(f'\nEstados encontrados ({len(states)}): {states}')
print(f'Outras chaves: {others}')

# Mostrar estrutura completa do RJ
if 'RJ' in d:
    rj = d['RJ']
    print(f'\nd["RJ"] tipo: {type(rj).__name__}')
    if isinstance(rj, dict):
        print(f'  Sub-chaves: {list(rj.keys())}')
        for k, v in rj.items():
            if isinstance(v, list):
                print(f'  {k}: {len(v)} itens  total={sum(v):,.0f}  ex={[round(x,1) for x in v[:5]]}')
    elif isinstance(rj, list):
        print(f'  {len(rj)} itens, total={sum(rj):,.0f}')
        print(f'  Ex: {[round(x,1) for x in rj[:10]]}')

# Verificar totais BR por setor
print('\n=== TOTAIS ICMS 2021 por setor (primeiros 10) ===')
if states:
    total_icms_br = np.zeros(67)
    for uf in states:
        arr = d[uf]
        if isinstance(arr, dict):
            icms = np.array(arr.get('ICMS', arr.get('icms', [0]*67))[:67])
        elif isinstance(arr, list):
            icms = np.array(arr[:67])
        else:
            continue
        total_icms_br += icms
    
    labels_path = BASE / 'output' / 'intermediary' / 'sector_labels.txt'
    with open(labels_path, encoding='utf-8') as f:
        labels = [l.strip() for l in f if l.strip()]
    
    for i in range(10):
        lbl = labels[i][:40] if i < len(labels) else f'S{i+1}'
        print(f'  M{i+1:02d} {lbl:<40} R$ {total_icms_br[i]:,.0f} Mi')
    print(f'  ...')
    print(f'  Total BR: R$ {total_icms_br.sum():,.0f} Mi')
