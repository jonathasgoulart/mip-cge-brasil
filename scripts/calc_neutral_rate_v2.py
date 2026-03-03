
import json
import numpy as np

def run():
    print("=== CALCULATING REVENUE NEUTRAL RATE (IBS/CBS) ===")
    
    # 1. Load Current Tax Revenue (The Target)
    # We must sum:
    # - Hybrid ICMS (from tax_matrix_hybrid_by_state.json)
    # - Structural PIS/COFINS/IPI/ISS (from tax_matrix.json)
    
    # Load Hybrid ICMS
    path_hybrid = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    with open(path_hybrid, 'r') as f:
        icms_data = json.load(f)
    
    total_icms = 0.0
    for vec in icms_data.values():
        total_icms += np.sum(vec)
        
    # Load Structural Taxes
    path_struct = 'data/processed/2021_final/tax_matrix.json'
    with open(path_struct, 'r') as f:
        struct_data = json.load(f).get('taxes_by_type', {})
        
    # Note: Structural Matrix is NATIONAL total.
    # We sum the relevant types: PIS_PASEP, COFINS, IPI, ISS.
    # We DO NOT include ICMS from here (already in Hybrid).
    # We do NOT include II (Import Tax remains), IOF (Financial Tax remains?). 
    # Usually Reform replaces: ICMS, ISS, IPI, PIS, COFINS.
    
    reform_taxes = ["PIS_PASEP", "COFINS", "IPI", "ISS"]
    total_federal_muni = 0.0
    
    print(f"Aggregating Reform Taxes: {reform_taxes}")
    for k in reform_taxes:
        val = np.sum(struct_data.get(k, []))
        print(f"  {k}: R$ {val/1000:.1f} Bi")
        total_federal_muni += val
        
    total_revenue_target = total_icms + total_federal_muni
    print(f"Total ICMS (Hybrid): R$ {total_icms/1000:.1f} Bi")
    print(f"TOTAL TARGET REVENUE: R$ {total_revenue_target/1000:.1f} Bi")
    
    # 2. Load Base (Total VAB)
    path_vab = 'data/processed/2021_final/vab_regional.json'
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
        
    total_vab = 0.0
    for vec in vab_data.values():
        total_vab += np.sum(vec)
        
    print(f"TOTAL VAB (Base): R$ {total_vab/1000:.1f} Bi")
    
    # 3. Calculate Neutral Rate
    # Rate = Target / Base
    neutral_rate = total_revenue_target / total_vab
    
    print("-" * 30)
    print(f"NEUTRAL RATE (Flat VAB Base): {neutral_rate*100:.2f}%")
    print("-" * 30)
    
    # Save Rate
    res = {
        "target_revenue_millions": total_revenue_target,
        "base_vab_millions": total_vab,
        "neutral_rate": neutral_rate
    }
    
    with open('output/neutral_rate_v2.json', 'w') as f:
        json.dump(res, f, indent=2)

if __name__ == "__main__":
    run()
