import json
import numpy as np
from cnae_to_mip_v3_parcial import distribute_icms_v3

def regionalize_icms_v3_final():
    """
    V3 FINAL: ICMS regional usando mapeamento parcial CNAE→MIP produtos
    
    Foca nos setores produtivos onde ICMS realmente incide
    """
    
    print("="*70)
    print("REGIONAL ICMS V3 FINAL: PRODUTOS (CNAE -> MIP PARCIAL)")
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
    
    # Calculate national VAB
    vab_nacional = {}
    for uf_vab in vab_regional.values():
        for i, val in enumerate(uf_vab):
            vab_nacional[i+1] = vab_nacional.get(i+1, 0) + val
    
    print(f"  VAB nacional: {len(vab_nacional)} setores")
    
    # Map CNAE to MIP
    print("\n[2/5] Mapping CNAE to MIP products...")
    
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
            
            distribution = distribute_icms_v3(cnae_div, icms_milhoes, vab_nacional)
            
            for mip_sector, value in distribution.items():
                if 1 <= mip_sector <= 67:
                    icms_matrix[i, mip_sector-1] += value
    
    total_before = np.sum(icms_matrix)
    print(f"  Total mapped: R$ {total_before/1e3:.2f} Bi")
    
    # Normalize
    print("\n[3/5] Normalizing...")
    
    norm_factor = icms_2021_target / total_before
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
    print(f"  Min coefficient:  {min_tau*100:.2f}%")
    print(f"  Max coefficient:  {max_tau*100:.2f}%")
    
    # Save
    print("\n[5/5] Saving...")
    
    results = {
        "version": "v3_final_parcial",
        "year": 2021,
        "methodology": "CNAE-MIP parcial (produtos onde ICMS incide)",
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
    
    with open('output/icms_regional_v3_final.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: output/icms_regional_v3_final.json")
    
    # Summary
    sorted_ufs = sorted([(uf, np.sum(icms_final[i, :])) for i, uf in enumerate(UFS)], 
                        key=lambda x: x[1], reverse=True)
    
    summary = {
        "version": "v3_final",
        "total_brasil_bilhoes": float(total_final / 1e3),
        "top_5_ufs": [{"uf": uf, "icms_bilhoes": float(val/1e3), "share_pct": float(val/total_final*100)} 
                      for uf, val in sorted_ufs[:5]],
        "statistics": {
            "mean_coefficient_pct": float(mean_tau * 100),
            "min_coefficient_pct": float(min_tau * 100),
            "max_coefficient_pct": float(max_tau * 100)
        }
    }
    
    with open('output/icms_regional_v3_final_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: output/icms_regional_v3_final_summary.json")
    
    # Display
    print(f"\n{'='*70}")
    print("RESULTS V3 FINAL")
    print("="*70)
    
    print(f"\nTop 5 Estados:")
    for item in summary["top_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.1f}%)")
    
    print(f"\nCoefficients:")
    print(f"  Mean: {mean_tau*100:.2f}%")
    print(f"  Range: {min_tau*100:.2f}% - {max_tau*100:.2f}%")
    
    print(f"\n{'='*70}\n")
    
    return results

if __name__ == "__main__":
    regionalize_icms_v3_final()
