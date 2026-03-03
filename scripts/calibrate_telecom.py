
import json
import numpy as np
import shutil

def run():
    print("=== CALIBRANDO IMPOSTO ESTRUTURAL DE TELECOM ===")
    
    path_tax = 'data/processed/2021_final/tax_matrix.json'
    path_backup = 'data/processed/2021_final/tax_matrix_backup_telecom.json'
    
    shutil.copy(path_tax, path_backup)
    
    with open(path_tax, 'r') as f:
        data = json.load(f)
        
    taxes = data.get('taxes_by_type', {})
    
    # Telecom Index: 49
    IDX_TELECOM = 49
    
    # Calibration Factor: 0.5 (50% reduction)
    # Rationale: Exclusion of ICMS from PIS/COFINS base + Overestimation in 2015 Matrix
    FACTOR = 0.5
    
    tax_types_to_calibrate = ["PIS_PASEP", "COFINS", "ISS", "IPI"] 
    # ICMS is handled by Hybrid Matrix (CONFAZ), so we don't touch it here?
    # Actually, apply_hybrid_tax_matrix OVERWRITES ICMS. So safe.
    
    print(f"Applying Factor {FACTOR} to Telecom (Idx {IDX_TELECOM}) for: {tax_types_to_calibrate}")
    
    for tax_name, vec in taxes.items():
        if tax_name in tax_types_to_calibrate:
            # Check length
            if len(vec) <= IDX_TELECOM:
                print(f"Error: {tax_name} vector length {len(vec)} too short.")
                continue
                
            original = float(vec[IDX_TELECOM])
            new_val = original * FACTOR
            vec[IDX_TELECOM] = new_val
            print(f"  {tax_name}: {original:.1f} M -> {new_val:.1f} M") # Removed /1e6

            
    # Save
    data['taxes_by_type'] = taxes
    with open(path_tax, 'w') as f:
        json.dump(data, f, indent=2)
        
    print("Calibration Complete.")

if __name__ == "__main__":
    run()
