
import json
import numpy as np

def run():
    print("=== DEBUGGING ARRAY SHAPES ===")
    
    path_tax = 'data/processed/2021_final/tax_matrix.json'
    path_vab = 'data/processed/2021_final/vab_regional.json'
    
    with open(path_tax, 'r') as f:
        tax_data = json.load(f).get('taxes_by_type', {})
        
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
        
    # Check lengths
    for k, v in tax_data.items():
        print(f"Tax '{k}': Length {len(v)}")
        break # Just one
        
    for k, v in vab_data.items():
        print(f"VAB State '{k}': Length {len(v)}")
        break
        
    # Check Refino Position in Tax (Huge ICMS)
    icms = tax_data['ICMS']
    max_icms_idx = np.argmax(icms)
    print(f"Max ICMS Val: {icms[max_icms_idx]:.1f} at Index {max_icms_idx}")
    
    # Check Telecom Position (Label 50)
    # If Shifted, Index 50 should be high (Structural)?
    # Or Index 49?
    print(f"Index 49 (Label 50?): {icms[49]:.1f}")
    if len(icms) > 50:
        print(f"Index 50 (Label 51?): {icms[50]:.1f}")

if __name__ == "__main__":
    run()
