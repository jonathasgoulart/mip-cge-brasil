import numpy as np
import os
import json

def calculate_multipliers():
    regions = ["Rio_de_Janeiro", "Sao_Paulo", "Centro_Oeste", "Sul", "Norte_Nordeste", "Minas_EspiritoSanto"]
    base_dir = r"c:\Users\jonat\Documents\MIP e CGE\output\final"
    labels_path = r"c:\Users\jonat\Documents\MIP e CGE\output\intermediary\sector_labels.txt"
    
    if not os.path.exists(labels_path):
        print("Labels not found.")
        return

    with open(labels_path, 'r', encoding='utf-8') as f:
        labels = [line.strip() for line in f.readlines()]

    report = {}

    print("--- VALIDATION: PRODUCTION MULTIPLIERS ---")
    
    for region in regions:
        a_path = os.path.join(base_dir, f"A_{region}.npy")
        if not os.path.exists(a_path):
            continue
            
        A = np.load(a_path)
        I = np.eye(A.shape[0])
        # L = (I - A)^-1
        try:
            L = np.linalg.inv(I - A)
            multipliers = L.sum(axis=0)
            
            top_idx = np.argsort(multipliers)[-5:][::-1]
            report[region] = {
                "mean": float(multipliers.mean()),
                "max": {labels[i]: float(multipliers[i]) for i in top_idx},
                "min": float(multipliers.min())
            }
            
            print(f"\nRegion: {region}")
            print(f"  Mean Multiplier: {multipliers.mean():.3f}")
            print(f"  Max: {labels[top_idx[0]]} ({multipliers[top_idx[0]]:.3f})")
            
            # Check for sanity
            if multipliers.mean() > 3.0 or multipliers.min() < 0.99:
                print(f"  [WARNING] Unusually high/low values in {region}")
                
        except np.linalg.LinAlgError:
            print(f"  [ERROR] Matrix (I-A) for {region} is singular!")

    # Save validation results
    with open(r"c:\Users\jonat\Documents\MIP e CGE\output\intermediary\validation_multipliers.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    calculate_multipliers()
