import csv

def extract_correct_labels():
    path = r'c:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\11.csv'
    activities = []
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)
        
        # As atividades estao nas linhas 8 a 74 (0-indexed no list)
        # Exemplo: linha 8 -> "0191\nAgricultura..." 
        # Elas estao na coluna 2 (index 2) e seguem para as colunas seguintes
        # Mas as descricoes tambem estao listadas na vertical entre as linhas 8 e 75
        
        for i in range(8, 75):
            cell = lines[i][2] if len(lines[i]) > 2 else ""
            if not cell: continue
            
            # Limpar: tirar o codigo (4 digitos) e o newline
            parts = cell.split('\n')
            name = parts[1] if len(parts) > 1 else parts[0]
            activities.append(name.strip())
            
    print(f"Total atividades extraídas: {len(activities)}")
    for i, act in enumerate(activities[:5]):
        print(f"  {i:02d}: {act}")
        
    return activities

if __name__ == "__main__":
    labels = extract_correct_labels()
    # Salvar em um arquivo para uso futuro
    with open(r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\sector_labels.txt', 'w', encoding='utf-8') as f:
        for l in labels:
            f.write(l + '\n')
