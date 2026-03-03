import pandas as pd

df = pd.read_excel('data/raw/mip_2015_67.xls', sheet_name='14', skiprows=3)

print("Extração ATUAL: iloc[1:68, 1]")
print("="*60)

labels = df.iloc[1:68, 1].values

print(f"\nTotal: {len(labels)} labels\n")

print("Verificando setores mencionados pelo usuário:")
print(f"[0]  = {labels[0]}")  # Deve ser Agricultura
print(f"[1]  = {labels[1]}")  # Deve ser Pecuária?
print(f"[39] = {labels[39]}")  # Deve ser Construção
print(f"[40] = {labels[40]}")  
print(f"[45] = {labels[45]}")
print(f"[46] = {labels[46]}")  # Deve ser Alojamento

print("\n" + "="*60)
print("Lista COMPLETA dos 67 setores:")
print("="*60)
for i, label in enumerate(labels):
    print(f"{i:2d} - {label}")
