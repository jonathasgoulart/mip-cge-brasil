
import shutil
import os
import json
import numpy as np

def run():
    print("=== RESETTING AND PATCHING (CLEAN RUN) ===")
    
    # 1. Sources (Clean)
    src_vab = 'output/vab_regional_67s.json'
    src_tax = 'output/tax_data.json'
    
    # 2. Destinations (Working)
    dst_vab = 'data/processed/2021_final/vab_regional.json'
    dst_tax = 'data/processed/2021_final/tax_matrix.json'
    
    # Restore
    if os.path.exists(src_vab):
        shutil.copy(src_vab, dst_vab)
        print("Restored clean VAB.")
    else:
        print("FATAL: Source VAB not found.")
        return

    if os.path.exists(src_tax):
        shutil.copy(src_tax, dst_tax)
        print("Restored clean Tax Matrix.")
    else:
        print("FATAL: Source Tax not found.")
        return
        
    # 3. Apply VAB Patch
    print("... Applying VAB Patch ...")
    with open(dst_vab, 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
    
    # Factors (Validated)
    vab_factors = {
        7: 18.0, 16: 20.0, 24: 9.0, # Original
        9: 5.0, 22: 3.0, 30: 3.0, 12: 3.0, 32: 2.5, 13: 2.2 # New
    }
    
    for uf, vec in vab_data.items():
        if isinstance(vec, list) and len(vec) == 67:
            for idx, factor in vab_factors.items():
                vec[idx] = vec[idx] * factor
                
    with open(dst_vab, 'w', encoding='utf-8') as f:
        json.dump(vab_data, f, indent=2)
        
    # 4. Apply Telecom Calibration
    print("... Calibrating Telecom Tax (0.5x) ...")
    with open(dst_tax, 'r') as f:
        tax_data = json.load(f)
        
    IDX_TELECOM = 49
    FACTOR_TEL = 0.5
    types_tel = ["PIS_PASEP", "COFINS", "ISS", "IPI"]
    
    taxes = tax_data.get('taxes_by_type', {})
    for k in types_tel:
        if k in taxes and len(taxes[k]) > IDX_TELECOM:
            taxes[k][IDX_TELECOM] = float(taxes[k][IDX_TELECOM]) * FACTOR_TEL
            
    with open(dst_tax, 'w') as f:
        json.dump(tax_data, f, indent=2)
        
    print("Reset and Patch Successful.")

if __name__ == "__main__":
    run()
