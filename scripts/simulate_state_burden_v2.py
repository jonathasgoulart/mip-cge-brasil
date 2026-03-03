
import json
import numpy as np
import csv

def run():
    print("=== SIMULANDO CARGA TRIBUTARIA POR ESTADO (MATRIZ HÍBRIDA) ===")
    
    path_matrix = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    path_vab = 'data/processed/2021_final/vab_regional.json'
    
    with open(path_matrix, 'r') as f:
        tax_matrix = json.load(f)
        
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
        
    # Load Structural Taxes (for Non-ICMS)
    path_tax_struct = 'data/processed/2021_final/tax_matrix.json'
    with open(path_tax_struct, 'r') as f:
        tax_struct = json.load(f).get('taxes_by_type', {})
        
    other_taxes_keys = ["IPI", "ISS", "PIS_PASEP", "COFINS", "CIDE", "IOF"]
    other_tax_vectors = {k: np.array(tax_struct[k]) for k in other_taxes_keys if k in tax_struct}
    
    # Calculate National Rates for Other Taxes
    # Rate = Tax_Vec / Sum(Regional_VAB)
    # We need Sum of Regional VAB
    total_vab_vec = np.zeros(67)
    for v in vab_regional.values():
        total_vab_vec += np.array(v)
        
    other_rates = {}
    with np.errstate(divide='ignore', invalid='ignore'):
         for k, vec in other_tax_vectors.items():
             other_rates[k] = vec / total_vab_vec
             other_rates[k][np.isnan(other_rates[k])] = 0.0
             
    # Headers
    print(f"{'UF':<5} | {'VAB (Bi)':<10} | {'Tax (Bi)':<10} | {'Carga %':<10}")
    print("-" * 50)
    
    results = []
    
    for uf, icms_vec in tax_matrix.items():
        if uf not in vab_regional: continue
        
        vab_vec = np.array(vab_regional[uf])
        icms_vec = np.array(icms_vec) # Hybrid ICMS
        
        # Calculate Other Taxes for this State (Structural Estimate)
        other_tax_sum = 0.0
        for rate in other_rates.values():
            other_tax_sum += np.sum(vab_vec * rate)
            
        # Total State
        total_vab = np.sum(vab_vec)
        total_icms = np.sum(icms_vec)
        total_tax = total_icms + other_tax_sum
        
        # Units: Both are in Millions.
        burden = (total_tax / total_vab) * 100 if total_vab > 0 else 0
        
        # Store
        results.append({
            "UF": uf,
            "VAB": total_vab,
            "Tax": total_tax,
            "Burden": burden
        })
        
    # Sort by Burden
    results.sort(key=lambda x: x['Burden'], reverse=True)
    
    for r in results:
        print(f"{r['UF']:<5} | {r['VAB']/1000:<10.1f} | {r['Tax']/1000:<10.1f} | {r['Burden']:<10.2f}%")
        
    # Export CSV
    with open('output/impacto_regional_hibrido.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["UF", "VAB (Bi)", "Tax (Bi)", "Carga (%)"])
        for r in results:
            writer.writerow([r['UF'], r['VAB']/1000, r['Tax']/1000, r['Burden']])
            
    print("\nRelatório salvo em output/impacto_regional_hibrido.csv")
    
if __name__ == "__main__":
    run()
