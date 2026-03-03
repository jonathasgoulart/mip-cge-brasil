import csv

def extract_correct_labels():
    path = r'c:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\14.csv'
    activities = []
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)
        
        # As atividades estao nas linhas 75 a 141 (0-indexed no list)
        # Exemplo: linha 75 no CSV -> 75: 0191,"Agricultura..."
        # Elas estao na coluna 1 (index 1)
        
        for i in range(75, 142):
            if i >= len(lines): break
            name = lines[i][1] if len(lines[i]) > 1 else ""
            if name:
                activities.append(name.strip())
            
    print(f"Total atividades extraídas: {len(activities)}")
    for i, act in enumerate(activities[:10]):
        print(f"  {i:02d}: {act}")
        
    return activities

if __name__ == "__main__":
    labels = extract_correct_labels()
    # Salvar em um arquivo para uso futuro
    with open(r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\sector_labels.txt', 'w', encoding='utf-8') as f:
        for l in labels:
            f.write(l + '\n')
