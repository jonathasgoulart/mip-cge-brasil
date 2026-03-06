import json
import numpy as np

def regionalize_icms_v3_make():
    """
    V3 MAKE: Final ICMS regionalization using Make matrix
    
    CNAE divisions -> Activities -> Products
    """
    
    print("="*70)
    print("REGIONAL ICMS V3 MAKE: USING OFFICIAL MATRICES")
    print("="*70)
    
    # Load data
    print("\n[1/5] Loading data...")
    
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        tax_data = json.load(f)
    icms_2021_target = np.sum(tax_data['taxes_by_type']['ICMS'])
    print(f"  Target ICMS 2021: R$ {icms_2021_target/1e3:.2f} Bi")
    
    with open('output/confaz_icms_2024_by_uf.json', 'r', encoding='utf-8') as f:
        confaz = json.load(f)
    print(f"  CONFAZ 2024: {len(confaz['by_uf_by_cnae'])} UFs")
    
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    print(f"  VAB regional: {len(vab_regional)} UFs")
    
    with open('output/cnae_to_products_final.json', 'r', encoding='utf-8') as f:
        cnae_mapping = json.load(f)
    cnae_to_products = {int(k): v for k, v in cnae_mapping['mapping'].items()}
    print(f"  CNAE->Products mapping: {len(cnae_to_products)} divisions")
    
    # Map CNAE to Products by UF
    print("\n[2/5] Mapping CNAE to Products by UF...")
    
    UFS = sorted(confaz['by_uf_by_cnae'].keys())
    n_setores = 67
    
    icms_matrix = np.zeros((len(UFS), n_setores))
    
    for i, uf in enumerate(UFS):
        uf_cnae_data = confaz['by_uf_by_cnae'][uf]
        
        for cnae_col_name, icms_reais in uf_cnae_data.items():
            try:
                cnae_div = int(cnae_col_name.split(": ")[1].split(" -")[0])
            except:
                continue
            
            icms_milhoes = icms_reais / 1e6
            
            # Get product distribution for this CNAE
            product_dist = cnae_to_products.get(cnae_div)
            
            if product_dist:
                # Distribute ICMS across products
                for prod_num_str, share in product_dist.items():
                    prod_num = int(prod_num_str)
                    if 1 <= prod_num <= 67:
                        icms_matrix[i, prod_num-1] += icms_milhoes * share
            else:
                # Unmapped CNAE: distribute by VAB
                vab_uf = vab_regional[uf]
                total_vab = sum(vab_uf)
                if total_vab > 0:
                    for j in range(n_setores):
                        icms_matrix[i, j] += icms_milhoes * (vab_uf[j] / total_vab)
    
    total_mapped = np.sum(icms_matrix)
    print(f"  Total mapped: R$ {total_mapped/1e3:.2f} Bi")
    print(f"  Deviation from CONFAZ: {(total_mapped/(icms_2021_target*1.4) - 1)*100:+.1f}%")
    
    # Normalize to 2021
    print("\n[3/5] Normalizing to CTB 2021...")
    
    norm_factor = icms_2021_target / total_mapped
    icms_final = icms_matrix * norm_factor
    
    total_final = np.sum(icms_final)
    print(f"  Final total: R$ {total_final/1e3:.2f} Bi")
    print(f"  Deviation: {abs(total_final - icms_2021_target)/icms_2021_target*100:.8f}%")
    
    # Calculate coefficients
    print("\n[4/5] Calculating coefficients...")
    
    vab_matrix = np.zeros((len(UFS), n_setores))
    for i, uf in enumerate(UFS):
        vab_matrix[i, :] = vab_regional[uf]
    
    with np.errstate(divide='ignore', invalid='ignore'):
        tau_icms = icms_final / vab_matrix
        tau_icms = np.nan_to_num(tau_icms)
    
    mean_tau = np.mean(tau_icms[tau_icms > 0])
    max_tau = np.max(tau_icms)
    min_tau = np.min(tau_icms[tau_icms > 0]) if np.any(tau_icms > 0) else 0
    
    print(f"  Mean coefficient: {mean_tau*100:.2f}%")
    print(f"  Min coefficient:  {min_tau*100:.4f}%")
    print(f"  Max coefficient:  {max_tau*100:.2f}%")
    
    # Check for extremes
    extreme_count = np.sum(tau_icms > 0.30)  # > 30%
    print(f"  Coefficients > 30%: {extreme_count}")
    
    # Save
    print("\n[5/5] Saving results...")
    
    results = {
        "version": "v3_make",
        "year": 2021,
        "methodology": "CNAE -> Activities -> Products using Make matrix",
        "total_icms_milhoes": float(total_final),
        "total_icms_bilhoes": float(total_final / 1e3),
        "by_uf": {},
        "coefficients": {}
    }
    
    for i, uf in enumerate(UFS):
        uf_total = np.sum(icms_final[i, :])
        results["by_uf"][uf] = {
            "icms_by_sector_milhoes": icms_final[i, :].tolist(),
            "total_icms_milhoes": float(uf_total),
            "total_icms_bilhoes": float(uf_total / 1e3),
            "share_pct": float(uf_total / total_final * 100)
        }
        results["coefficients"][uf] = tau_icms[i, :].tolist()
    
    with open('output/icms_regional_v3_make.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: output/icms_regional_v3_make.json")
    
    # Summary
    sorted_ufs = sorted([(uf, np.sum(icms_final[i, :])) for i, uf in enumerate(UFS)], 
                        key=lambda x: x[1], reverse=True)
    
    summary = {
        "version": "v3_make",
        "total_brasil_bilhoes": float(total_final / 1e3),
        "methodology": "Official IBGE Make matrix",
        "top_5_ufs": [{"uf": uf, "icms_bilhoes": float(val/1e3), "share_pct": float(val/total_final*100)} 
                      for uf, val in sorted_ufs[:5]],
        "statistics": {
            "mean_coefficient_pct": float(mean_tau * 100),
            "min_coefficient_pct": float(min_tau * 100),
            "max_coefficient_pct": float(max_tau * 100),
            "extreme_coefficients_count": int(extreme_count)
        }
    }
    
    with open('output/icms_regional_v3_make_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: output/icms_regional_v3_make_summary.json")
    
    # Display
    print(f"\n{'='*70}")
    print("RESULTS V3 MAKE (FINAL)")
    print("="*70)
    
    print(f"\nTop 5 Estados:")
    for item in summary["top_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.1f}%)")
    
    print(f"\nCoefficients:")
    print(f"  Mean: {mean_tau*100:.2f}%")
    print(f"  Range: {min_tau*100:.4f}% - {max_tau*100:.2f}%")
    print(f"  Extremes (>30%): {extreme_count}")
    
    print(f"\n{'='*70}\n")
    
    return results

if __name__ == "__main__":
    regionalize_icms_v3_make()
