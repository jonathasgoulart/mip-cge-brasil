import csv
import numpy as np
import os

def parse_smart(s):
    s = str(s).strip()
    if not s: return 0.0
    if ',' in s and '.' in s: return float(s.replace('.', '').replace(',', '.'))
    if ',' in s: return float(s.replace(',', '.'))
    try: return float(s)
    except: return 0.0

def finalize_national():
    inter_dir = 'output/intermediary'
    os.makedirs(inter_dir, exist_ok=True)
    
    # 1. Get X_j from 01.csv (Supply Matrix)
    # Activities are in columns 7 to 73 (0-based: index 7 is 8th column)
    X_j = np.zeros(67)
    with open('data/processed/mip_2015/01.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            # Row index 133 is the row starts with "Total"
            if row[0].strip().lower() == "total":
                for j in range(67):
                    X_j[j] = parse_smart(row[j+7])
                break
    print(f"X_j extracted. Total: {np.sum(X_j):,.0f}")
    
    # 2. Get Intermediary Consumption Sum from 02.csv (Usos Matrix)
    # The sum of columns 2 to 68 in the Total row
    Z_sum_j = np.zeros(67)
    with open('data/processed/mip_2015/02.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            if row[0].strip().lower() == "total":
                for j in range(67):
                    Z_sum_j[j] = parse_smart(row[j+2])
                break
    print(f"Z_sum extracted. Total: {np.sum(Z_sum_j):,.0f}")
    
    # 3. VAB_j
    VAB_nas = X_j - Z_sum_j
    print(f"VAB calculated. Total: {np.sum(VAB_nas):,.0f}")
    
    # 4. A_nas (National Coefficients) from 14.csv (Industry-by-Industry)
    # Rows 5 to 71, Col 2 to 68
    A_nas = []
    with open('data/processed/mip_2015/14.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        [next(reader) for _ in range(5)]
        for row in reader:
            if not row or not row[1].strip(): continue
            vals = [parse_smart(r) for r in row[2:69]]
            if len(vals) == 67: A_nas.append(vals)
            if len(A_nas) == 67: break
    A_nas = np.array(A_nas)
    print(f"A_nas extracted. Shape: {A_nas.shape}")
    
    # Save EVERYTHING
    np.save(os.path.join(inter_dir, 'A_nas.npy'), A_nas)
    np.save(os.path.join(inter_dir, 'X_nas.npy'), X_j)
    np.save(os.path.join(inter_dir, 'VAB_nacional.npy'), VAB_nas)
    # Z_nas = A_nas * X_j (needed for Flegg)
    np.save(os.path.join(inter_dir, 'Z_nas.npy'), A_nas * X_j[None, :])
    
    print("National Baseline Saved Successfully.")

if __name__ == "__main__":
    finalize_national()
