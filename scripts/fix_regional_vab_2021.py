
import json
import numpy as np
import os
import shutil

def run():
    print("=== CORREÇÃO DA MATRIZ REGIONAL (VAB 2021 OFICIAL) ===")
    
    # 1. Official 2021 Totals (Extracted from Audit) - R$ Millions
    # Source: IBGE Contas Regionais 2021 (Tabela F54)
    OFFICIAL_VAB_2021 = {
        'RO': 51055.0,
        'AC': 19295.7,
        'AM': 109237.2,
        'RR': 16309.7,
        'PA': 240097.2,
        'AP': 18505.4,
        'TO': 46695.3,
        'MA': 110229.9,
        'PI': 57488.9,
        'CE': 167056.9,
        'RN': 71064.3,
        'PB': 67766.4,
        'PE': 185865.2,
        'AL': 68492.0,
        'SE': 45894.9,
        'BA': 307323.9,
        'MG': 754065.6,
        'ES': 155644.2,
        'RJ': 819846.1,
        'SP': 2246365.4,
        'PR': 474589.6,
        'SC': 347534.9,
        'RS': 502104.5,
        'MS': 125944.0,
        'MT': 210344.6,
        'GO': 238153.7,
        'DF': 257028.4
    }
    
    # 2. Load Existing Matrix (2015 distribution)
    input_path = 'output/vab_regional_67s.json'
    backup_path = 'output/vab_regional_67s_OLD_2015.json'
    
    if not os.path.exists(backup_path):
        shutil.copy(input_path, backup_path)
        print(f"Backup saved to {backup_path}")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
        
    # 3. Apply Scaling
    new_vab_data = {}
    total_diff = 0.0
    
    print(f"{'UF':<3} | {'Old Sum':<10} | {'New Target':<10} | {'Factor':<8}")
    print("-" * 45)
    
    for uf, target in OFFICIAL_VAB_2021.items():
        if uf in vab_data:
            current_vals = np.array(vab_data[uf])
            current_sum = np.sum(current_vals)
            
            if current_sum > 0:
                factor = target / current_sum
            else:
                factor = 1.0
                
            new_vals = current_vals * factor
            new_vab_data[uf] = new_vals.tolist()
            
            print(f"{uf:<3} | {current_sum/1e3:<10.1f} | {target/1e3:<10.1f} | {factor:<8.4f}")
            total_diff += (target - current_sum)
        else:
            print(f"Warning: UF {uf} not found in matrix.")
            
    # 4. Save
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(new_vab_data, f, indent=2)
        
    print("-" * 45)
    print(f"Correction Applied. Matrix updated to 2021 Values.")
    print(f"Total VAB Added: R$ {total_diff/1e6:.2f} Trillions")
    
    # Update National VAB NPY as well
    vab_national = np.zeros(67)
    for vals in new_vab_data.values():
        vab_national += np.array(vals)
        
    np.save('output/intermediary/VAB_nacional.npy', vab_national)
    print("Updated output/intermediary/VAB_nacional.npy")

if __name__ == "__main__":
    run()
