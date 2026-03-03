import pandas as pd
import json
import os

def fix_linkages():
    path_14 = r'c:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\14.csv'
    import csv
    real_labels = []
    with open(path_14, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)
        # Os dados comecam na linha 76 do CSV (index 75)
        for i in range(75, 142):
            if i < len(lines):
                row = lines[i]
                if len(row) > 1:
                    real_labels.append(row[1].strip())
    
    print(f"Extraídos {len(real_labels)} labels.")
    for i, l in enumerate(real_labels[:5]):
        print(f"  {i}: {l}")

    # 2. Carregar o linkages.json atual
    json_path = r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\linkages.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. Corrigir os nomes em todas as regiões
    for region in data:
        # Corrigir key_sectors
        for sector in data[region]['key_sectors']:
            idx = sector['id']
            if idx < len(real_labels):
                sector['nome'] = real_labels[idx]
        
        # Corrigir all_indices
        for sector in data[region]['all_indices']:
            # all_indices no JSON original nao tem ID, assume ordem de 0 a 66
            # Vamos verificar a ordem no script original calculate_linkages.py
            pass
            
    # Na verdade, e melhor RECALCULAR os linkages com os labels corretos 
    # ou simplesmente mapear all_indices por ordem.
    
    for region in data:
        for i, sector in enumerate(data[region]['all_indices']):
            if i < len(real_labels):
                sector['nome'] = real_labels[i]

    # Salvar o JSON corrigido
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # Exportar para o dashboard tmb
    dash_json = r'c:\Users\jonat\Documents\MIP e CGE\dashboard\data\linkages.json'
    os.makedirs(os.path.dirname(dash_json), exist_ok=True)
    with open(dash_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Linkages atualizados com labels corretos!")

if __name__ == "__main__":
    fix_linkages()
