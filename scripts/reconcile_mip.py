import csv
import numpy as np
import os

def reconcile():
    inter_dir = 'output/intermediary'
    os.makedirs(inter_dir, exist_ok=True)
    
    # 1. Load Z (Technical Coefficients / Inter-industry)
    # Tabela 11: Z rows are 3 to 69 (67 sectors)
    path_z = 'data/processed/mip_2015/11.csv'
    Z = []
    with open(path_z, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        [next(reader) for _ in range(3)] # Header
        for row in reader:
            if not row or not row[1].strip(): continue # Skip empty or summary rows
            # Columns 3 to 69 are the 67 sectors
            line = []
            for i in range(3, 70):
                try:
                    v = float(row[i].replace('.', '').replace(',', '.'))
                except:
                    v = 0.0
                line.append(v)
            if len(line) == 67:
                Z.append(line)
            if len(Z) == 67: break
            
    Z = np.array(Z)
    print(f"Z shape: {Z.shape}")
    
    # 2. Load X (Production Total) and VAB
    path_x = 'data/processed/mip_2015/14.csv'
    X = np.array([])
    VAB = np.array([])
    
    with open(path_x, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 68: continue
            label = row[1].lower()
            
            # Extract possible numeric values
            vals = []
            for i in range(2, 69):
                try:
                    s = row[i].replace('.', '').replace(',', '.')
                    if not s: s = '0'
                    vals.append(float(s))
                except:
                    break
            
            if len(vals) == 67:
                if "total" in label and ("produ" in label or "producao" in label):
                    X = np.array(vals)
                elif "valor adicionado bruto" in label:
                    VAB = np.array(vals)
    
    print(f"X shape: {X.shape}")
    print(f"VAB Nacional shape: {VAB.shape}")
    
    np.save(os.path.join(inter_dir, 'Z_nacional.npy'), Z)
    np.save(os.path.join(inter_dir, 'X_nacional.npy'), X)
    np.save(os.path.join(inter_dir, 'VAB_nacional.npy'), VAB)
    print("National data saved.")

if __name__ == "__main__":
    reconcile()
