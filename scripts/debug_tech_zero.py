
import json
import numpy as np
import pandas as pd

def debug():
    print("=== DEBUGGING TECH SECTOR (IDX 50) ===")
    
    # 1. Check VAB
    with open('data/processed/2021_final/vab_regional.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    
    vab_rj = np.array(vab_regional['RJ'])
    print(f"VAB RJ (Idx 50): {vab_rj[50]:.2f} M")
    
    # Sum of all VAB
    vab_nas_total = np.zeros(67)
    for uf, vec in vab_regional.items():
        vab_nas_total += np.array(vec)
    print(f"VAB Nacional (Idx 50): {vab_nas_total[50]:.2f} M")

    # 2. Check VBP (National)
    vbp_path = 'data/processed/mip_2015/01.csv'
    vbp_nacional = pd.read_csv(vbp_path, skiprows=3)
    X_nas = vbp_nacional.iloc[:67, 75].apply(pd.to_numeric, errors='coerce').fillna(0).values
    print(f"VBP Nacional (Idx 50): {X_nas[50]:.2f} M")
    
    # 3. Check Flow (National)
    ci_path = 'data/processed/mip_2015/05.csv'
    ci_nacional = pd.read_csv(ci_path, skiprows=3)
    Z_nas = ci_nacional.iloc[:67, 3:70].apply(pd.to_numeric, errors='coerce').fillna(0).values
    
    row_sum = np.sum(Z_nas[50, :])
    col_sum = np.sum(Z_nas[:, 50])
    print(f"Z_nas Row Sum (Idx 50): {row_sum:.2f} M")
    print(f"Z_nas Col Sum (Idx 50): {col_sum:.2f} M")
    
    # 4. Check Index Labels again
    with open('output/intermediary/sector_labels.txt', 'r', encoding='latin1') as f:
        labels = [line.strip() for line in f if line.strip()]
    if len(labels) > 50:
        print(f"Label at Index 50: {labels[50]}")

if __name__ == "__main__":
    debug()
