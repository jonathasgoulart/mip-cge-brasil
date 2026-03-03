
import json
import numpy as np
import pandas as pd

def run():
    print("=== SIMULATING TAX REFORM SCENARIOS ===")
    
    # 1. Load Data
    path_vab = 'data/processed/2021_final/vab_regional.json'
    path_tax_hybrid = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    path_tax_struct = 'data/processed/2021_final/tax_matrix.json'
    path_labels = 'output/intermediary/sector_labels.txt'
    
    # Load Labels
    with open(path_labels, 'r', encoding='latin1') as f:
        labels = [line.strip() for line in f if line.strip()]
        
    # Load VAB (Aggregated by Sector)
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    
    vab_by_sector = np.zeros(67)
    for vec in vab_regional.values():
        vab_by_sector += np.array(vec)
        
    # Load Current Tax (Total per Sector)
    # ICMS (Hybrid)
    with open(path_tax_hybrid, 'r') as f:
        icms_data = json.load(f)
    icms_by_sector = np.zeros(67)
    for vec in icms_data.values():
        icms_by_sector += np.array(vec)
        
    # Structural (PIS/COFINS/IPI/ISS)
    with open(path_tax_struct, 'r') as f:
        struct_data = json.load(f).get('taxes_by_type', {})
        
    target_taxes = ["PIS_PASEP", "COFINS", "IPI", "ISS"]
    struct_by_sector = np.zeros(67)
    for k in target_taxes:
        if k in struct_data:
            struct_by_sector += np.array(struct_data[k])
            
    total_current_tax = icms_by_sector + struct_by_sector
    total_revenue_target = np.sum(total_current_tax)
    total_vab_base = np.sum(vab_by_sector)
    
    print(f"Total Target Revenue: R$ {total_revenue_target/1000:.1f} Bi")
    print(f"Total Base VAB: R$ {total_vab_base/1000:.1f} Bi")
    
    # --- SCENARIO A: FLAT TAX ---
    flat_rate = total_revenue_target / total_vab_base
    print(f"Flat Neutral Rate: {flat_rate*100:.2f}%")
    
    burden_flat = np.full(67, flat_rate * 100)
    
    # --- SCENARIO B: REALISTIC (EXEMPTIONS) ---
    # Discount 60% (Pay 40%) for: Agro, Food, Health, Education, Public Transport
    
    # Define Indices (0-based) based on labels
    # Agro: 1, 2, 3 (Forest), 8 (Meat), 9 (Sugar), 10 (Food) -> Indices 0,1,2, 7,8,9
    # Transport: 42 (Land), 43 (Water) -> Indices 41, 42
    # Education: 61, 62 -> Indices 60, 61
    # Health: 63, 64 -> Indices 62, 63
    
    # Adjust Indices (-1 from Label Line Number)
    idxs_exempt = [
        0, 1, 2, # Agro Primary
        7, 8, 9, # Food Industry
        41, 42,  # Transport
        60, 61,  # Education
        62, 63   # Health
    ]
    
    # 0.4 Factor (60% discount)
    factors = np.ones(67)
    factors[idxs_exempt] = 0.4
    
    # Calculate Standard Rate
    # Revenue = Rate * Sum(VAB_i * Factor_i)
    # Rate = Revenue / Weighted_Base
    
    weighted_base = np.sum(vab_by_sector * factors)
    standard_rate = total_revenue_target / weighted_base
    
    print(f"Weighted Base VAB: R$ {weighted_base/1000:.1f} Bi")
    print(f"Standard Rate (Realistic): {standard_rate*100:.2f}%")
    print(f"Reduced Rate: {standard_rate * 0.4 * 100:.2f}%")
    
    burden_realistic = factors * standard_rate * 100
    
    # --- OUTPUT ---
    current_burden_pct = (total_current_tax / vab_by_sector) * 100
    # Fix NaNs or Inf
    current_burden_pct[np.isnan(current_burden_pct)] = 0
    current_burden_pct[np.isinf(current_burden_pct)] = 0
    
    results = []
    for i in range(67):
        results.append({
            "ID": i+1,
            "Setor": labels[i] if i < len(labels) else f"Setor {i+1}",
            "VAB_Bi": vab_by_sector[i] / 1000,
            "Tax_Current_Bi": total_current_tax[i] / 1000,
            "Burden_Current": current_burden_pct[i],
            "Burden_Flat": burden_flat[i],
            "Burden_Realistic": burden_realistic[i],
            "Change_vs_Current": burden_realistic[i] - current_burden_pct[i]
        })
        
    df = pd.DataFrame(results)
    
    # Save CSV
    df.to_csv('output/simulacao_reforma_setorial.csv', index=False, encoding='utf-8')
    print("Saved reform simulation to output/simulacao_reforma_setorial.csv")
    
    # Print Movers
    print("\n--- BIGGEST LOSERS (Tax Increase) ---")
    print(df.sort_values('Change_vs_Current', ascending=False)[['Setor', 'Burden_Current', 'Burden_Realistic']].head(5))
    
    print("\n--- BIGGEST WINNERS (Tax Decrease) ---")
    print(df.sort_values('Change_vs_Current', ascending=True)[['Setor', 'Burden_Current', 'Burden_Realistic']].head(5))

if __name__ == "__main__":
    run()
