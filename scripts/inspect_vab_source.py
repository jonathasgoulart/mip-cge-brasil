
import numpy as np
import json
import os

def run():
    print("=== INSPEÇÃO DA ORIGEM DO VAB (SETORIAL) ===")
    
    path_vab = 'data/processed/2021_final/vab_nacional.npy'
    path_labels = 'output/intermediary/sector_labels.txt'
    
    vab_vec = np.load(path_vab)
    
    labels = []
    try:
        with open(path_labels, 'r', encoding='latin1') as f:
            labels = [l.strip() for l in f if l.strip()]
    except: pass
    
    print(f"Total VAB Loaded: {np.sum(vab_vec)/1000:,.1f} Bi")
    print(f"Vector Shape: {vab_vec.shape}")
    
    # Check suspected sectors
    suspects = {
        8: "Abate (Meat)",
        17: "Celulose",
        25: "Borracha"
    }
    
    print("\n--- Setores Suspeitos ---")
    for idx, name in suspects.items():
        # Adjust for 0-index? ID 8 is likely Index 7?
        # In the CSV output, ID 8 was printed.
        # My report loop: `for i in range(67): ... "id": i+1`.
        # So "ID 8" is Index 7.
        
        real_idx = idx - 1
        val = vab_vec[real_idx]
        lbl = labels[real_idx] if real_idx < len(labels) else "?"
        
        try:
            safe_lbl = lbl.encode('ascii', 'ignore').decode('ascii')
        except:
            safe_lbl = "Label_Err"
        print(f"ID {idx} | {safe_lbl} | VAB = {val/1000:.2f} Bi")
        
    print("\n--- Comparação com Grandes Setores ---")
    top_indices = np.argsort(vab_vec)[-5:][::-1]
    for i in top_indices:
        print(f"ID {i+1} | {labels[i]} | VAB = {vab_vec[i]/1000:.1f} Bi")

if __name__ == "__main__":
    run()
