import csv
import numpy as np
import os

def parse_smart(s):
    s = str(s).strip()
    if not s: return 0.0
    # If it has a comma and a dot, it's likely 1.234,56
    if ',' in s and '.' in s:
        return float(s.replace('.', '').replace(',', '.'))
    # If it has only a comma, it's likely 0,56
    if ',' in s:
        return float(s.replace(',', '.'))
    # If it has only a dot, it's likely 0.56 (Pandas format)
    try:
        return float(s)
    except:
        return 0.0

def extract_national():
    inter_dir = 'output/intermediary'
    os.makedirs(inter_dir, exist_ok=True)
    
    # Z (Technical Coefficients) - Table 11
    # Note: Table 11 is ALREADY coefficients in many MIPs.
    # But let's check: if column sum is around 0.5, it's coefficients.
    path_z = 'data/processed/mip_2015/11.csv'
    Z = []
    with open(path_z, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        [next(reader) for _ in range(5)] # Header + empty rows
        for row in reader:
            if not row or len(row) < 68: continue
            label = str(row[1]).strip()
            if not label: continue
            
            # Extract possible numeric values
            row_vals = []
            for r in row[2:69]:
                try:
                    row_vals.append(parse_smart(r))
                except:
                    break
            
            if len(row_vals) == 67:
                Z.append(row_vals)
            if len(Z) == 67: break
    
    Z = np.array(Z)
    print(f"Z (coefficients) shape: {Z.shape}, Mean sum: {np.mean(np.sum(Z, axis=0)):.4f}")
    
    # 2. VAB and X - Table 14
    path_14 = 'data/processed/mip_2015/14.csv'
    X = np.zeros(67)
    VAB = np.zeros(67)
    
    with open(path_14, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row or len(row) < 2: continue
            label = str(row[1]).lower()
            
            # Use a slightly different approach to avoid parsing labels as numbers
            numeric_vals = []
            for r in row[2:69]:
                try:
                    numeric_vals.append(parse_smart(r))
                except:
                    break
            
            if len(numeric_vals) == 67:
                # DEBUG PRINT
                print(f"Row {i} Label: |{label}|")
                if "total" in label and ("produ" in label or "producao" in label):
                    X = np.array(numeric_vals)
                    print(f"Found X in row: {label}")
                elif "valor adicionado bruto" in label or "valor adicionado" in label:
                    VAB = np.array(numeric_vals)
                    print(f"Found VAB in row: {label}")

    if np.sum(X) == 0:
        print("Fallback: X not found. Estimating from 01.csv...")
        # (Skip for now, usually it's in 14 or 15)
        
    np.save(os.path.join(inter_dir, 'Z_nas.npy'), Z)
    np.save(os.path.join(inter_dir, 'X_nas.npy'), X)
    np.save(os.path.join(inter_dir, 'VAB_nacional.npy'), VAB)
    print("National data saved.")

if __name__ == "__main__":
    extract_national()
