import numpy as np

# Índices top VAB detectados para RJ
top_vab_idx = [18, 59, 40, 16, 52, 60, 51, 39, 41, 57]
# Índices "Irrelevantes" reportados no Dashboard/linkages.json
irrelevant_idx = [0, 20, 26, 41, 55, 37]

all_to_check = sorted(list(set(top_vab_idx + irrelevant_idx)))

print("--- DIAGNÓSTICO DE SETORES ---")
try:
    with open(r'c:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\11.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()[5:] # Pular cabeçalhos
        
    for idx in all_to_check:
        if idx < len(lines):
            row = lines[idx].strip().split(',')
            name = row[1] if len(row) > 1 else "Unknown"
            category = "TOP VAB" if idx in top_vab_idx else "KEY SECTOR (Reported)"
            print(f"[{idx:02d}] {category:<20}: {name.strip()}")
except Exception as e:
    print(f"Erro ao ler arquivo: {e}")
