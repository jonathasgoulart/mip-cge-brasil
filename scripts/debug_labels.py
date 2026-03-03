import pandas as pd
import json

# Ler o Excel
df = pd.read_excel('data/raw/mip_2015_67.xls', sheet_name='14', skiprows=3)

print("="*60)
print("DEBUG: Extração de labels da MIP 2015")
print("="*60)

# Ver linhas 47-54 (região onde aparecem os setores audiovisuais)
print("\nLinhas 47-54 do DataFrame (após skiprows=3):")
for i in range(47, 55):
    label = df.iloc[i, 1]
    print(f"iloc[{i}] -> [{i-1}] {label}")

print("\n" + "="*60)
print("Extração atual do script (iloc[1:68, 1]):")
labels_extracted = df.iloc[1:68, 1].values
print(f"Total: {len(labels_extracted)}")
print("\nPosições audiovisuais esperadas:")
print(f"[50] {labels_extracted[50]}")  
print(f"[51] {labels_extracted[51]}")
print(f"[64] {labels_extracted[64]}")

print("\n" + "="*60)
print("JSON atual salvo:")
with open('output/intermediary/perfectionist_base_2015.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
    
print(f"[50] {d['labels'][50]}")
print(f"[51] {d['labels'][51]}")
print(f"[64] {d['labels'][64]}")

# Procurar onde está "Edição"
print("\n" + "="*60)
print("Buscando 'Edição' nas labels extraídas:")
for i, label in enumerate(labels_extracted):
    if 'Edição' in label or 'Edi' in label:
        print(f"  [{i}] {label}")

print("\nBuscando 'televisão' nas labels extraídas:")
for i, label in enumerate(labels_extracted):
    if 'televisão' in label or 'televis' in label:
        print(f"  [{i}] {label}")

print("\nBuscando 'artísticas' nas labels extraídas:")
for i, label in enumerate(labels_extracted):
    if 'artísticas' in label or 'art' in label.lower():
        print(f"  [{i}] {label}")
