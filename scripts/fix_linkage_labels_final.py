import json
import os

def fix_linkages():
    path_14 = r'c:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\14.csv'
    real_labels = []
    
    with open(path_14, 'r', encoding='latin-1') as f:
        lines = f.readlines()
        
    # Os nomes das atividades estao entre as linhas 76 e 142 do CSV original
    # No readlines (0-indexed), isso e 75 a 141
    # Vamos extrair o texto entre a primeira e a segunda virgula, cuidando das aspas
    for i in range(75, 142):
        if i >= len(lines): break
        line = lines[i].strip()
        if not line: continue
        
        # Pega a parte da descricao
        # Formato esperado: Codigo,"Nome",... ou Codigo,Nome,...
        parts = line.split(',')
        if len(parts) < 2: continue
        
        # Se comeca com aspas, pega ate a proxima aspa
        desc = line.split('"')[1] if '"' in line else parts[1]
        real_labels.append(desc.strip())
    
    # Salvar labels para uso em outros scripts
    with open(r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\sector_labels.txt', 'w', encoding='utf-8') as f:
        for label in real_labels:
            f.write(label + '\n')
            
    print(f"Extraídos {len(real_labels)} labels.")
    for i, l in enumerate(real_labels[:5]):
        print(f"  {i}: {l}")

    # Carregar e atualizar
    json_path = r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\linkages.json'
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for region in data:
            # Corrigir key_sectors
            for sector in data[region]['key_sectors']:
                idx = sector['id']
                if idx < len(real_labels):
                    sector['nome'] = real_labels[idx]
            
            # Corrigir all_indices
            for i, sector in enumerate(data[region]['all_indices']):
                if i < len(real_labels):
                    sector['nome'] = real_labels[i]

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        # Exportar para dashboard
        dash_json = r'c:\Users\jonat\Documents\MIP e CGE\dashboard\data\linkages.json'
        os.makedirs(os.path.dirname(dash_json), exist_ok=True)
        with open(dash_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Linkages atualizados!")

if __name__ == "__main__":
    fix_linkages()
