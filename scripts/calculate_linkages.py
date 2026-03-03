import numpy as np
import os
import json

def calculate_linkages():
    regions = ["Sao_Paulo", "Rio_de_Janeiro", "Sul", "Centro_Oeste", "Norte_Nordeste", "Minas_EspiritoSanto"]
    labels_path = r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\sector_labels.txt'
    
    if not os.path.exists(labels_path):
        print("Labels not found. Run fix_linkage_labels_final.py first.")
        return
        
    with open(labels_path, 'r', encoding='utf-8') as f:
        sector_labels = [line.strip() for line in f.readlines()]
    
    results = {}
    n = 67

    for reg in regions:
        try:
            a_path = f'c:\\Users\\jonat\\Documents\\MIP e CGE\\output\\final\\A_{reg}.npy'
            if not os.path.exists(a_path):
                print(f"FAIL: Matriz para {reg} nao encontrada.")
                continue
                
            A = np.load(a_path)
            I = np.eye(n)
            L_inv = np.linalg.inv(I - A)
            
            # Rasmussen-Hirschman Indices
            L_bar = L_inv.mean()
            
            # 1. Backwards Linkages (U_j) - Col sums
            bl = L_inv.sum(axis=0) / (n * L_bar)
            
            # 2. Forward Linkages (U_i) - Row sums
            fl = L_inv.sum(axis=1) / (n * L_bar)
            
            # Identify Key Sectors
            key_sectors = []
            for i in range(n):
                if bl[i] > 1 and fl[i] > 1:
                    key_sectors.append({
                        "id": i,
                        "nome": sector_labels[i],
                        "bl": float(bl[i]),
                        "fl": float(fl[i])
                    })
            
            # Sort by power of dispersion (BL)
            key_sectors = sorted(key_sectors, key=lambda x: x["bl"], reverse=True)
            
            results[reg] = {
                "key_sectors": key_sectors[:10],
                "all_indices": [
                    {"nome": sector_labels[i], "bl": float(bl[i]), "fl": float(fl[i])} 
                    for i in range(n)
                ]
            }
            print(f"DONE: Linkages calculados para {reg}")
            
        except Exception as e:
            print(f"ERROR em {reg}: {e}")

    # Save results
    with open(r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\linkages.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print("Linkages.json atualizado com sucesso!")

if __name__ == "__main__":
    calculate_linkages()
