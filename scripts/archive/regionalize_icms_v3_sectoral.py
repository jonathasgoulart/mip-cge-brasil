import json
import numpy as np
from cnae_to_mip_mapping import distribute_icms

def regionalize_icms_v3_sectoral():
    """
    V3: Sector-specific ICMS regionalization using CNAE-MIP mapping
    
    This version uses the actual CNAE sectoral data from CONFAZ 2024
    instead of assuming uniform distribution within each UF.
    
    Methodology:
    1. For each UF and CNAE division: get ICMS value
    2. Map CNAE to MIP sectors using validated mapping
    3. Distribute if 1:N mapping (using national VAB weights)
    4. Sum all contributions to each MIP sector
    5. Scale to match CTB 2021 total (R$ 537 Bi)
    """
    
    print("="*70)
    print("REGIONAL ICMS V3: SECTOR-SPECIFIC (CNAE -> MIP)")
    print("="*70)
    
    # ========================================================================
    # STEP 1: LOAD DATA
    # ========================================================================
    
    print("\n[1/5] Loading data...")
    
    # CTB 2021 target
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        tax_data = json.load(f)
    
    icms_2021_target = np.sum(tax_data['taxes_by_type']['ICMS'])
    print(f"  Target ICMS 2021: R$ {icms_2021_target/1e3:.2f} Bi")
    
    # CONFAZ 2024 by UF x CNAE
    with open('output/confaz_icms_2024_by_uf.json', 'r', encoding='utf-8') as f:
        confaz = json.load(f)
    
    print(f"  CONFAZ 2024: {len(confaz['by_uf_by_cnae'])} UFs")
    
    # National VAB for distribution weights
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    
    # Calculate national VAB by sector
    vab_nacional = {}
    for uf_vab in vab_regional.values():
        for i, val in enumerate(uf_vab):
            vab_nacional[i+1] = vab_nacional.get(i+1, 0) + val
    
    print(f"  VAB nacional: {len(vab_nacional)} setores")
    
    # ========================================================================
    # STEP 2: MAP CNAE TO MIP FOR EACH UF
    # ========================================================================
    
    print("\n[2/5] Mapping CNAE to MIP by UF...")
    
    UFS = sorted(confaz['by_uf_by_cnae'].keys())
    n_setores = 67
    
    # Result matrix: [27 UFs x 67 sectors]
    icms_matrix = np.zeros((len(UFS), n_setores))
    
    for i, uf in enumerate(UFS):
        uf_cnae_data = confaz['by_uf_by_cnae'][uf]
        
        # For each CNAE division in this UF
        for cnae_col_name, icms_reais in uf_cnae_data.items():
            # Extract CNAE number from column name like "Soma de Divisão: 1 - ..."
            try:
                cnae_div = int(cnae_col_name.split(": ")[1].split(" -")[0])
            except:
                continue  # Skip if can't parse
            
            icms_milhoes = icms_reais / 1e6  # Convert reais to millions
            
            # Distribute to MIP sectors
            distribution = distribute_icms(cnae_div, icms_milhoes, vab_nacional)
            
            for mip_sector, value in distribution.items():
                icms_matrix[i, mip_sector-1] += value  # 0-indexed
    
    total_before_norm = np.sum(icms_matrix)
    print(f"  Total mapped: R$ {total_before_norm/1e3:.2f} Bi")
    print(f"  Deviation from 2021: {(total_before_norm/icms_2021_target - 1)*100:+.1f}%")
    
    # ========================================================================
    # STEP 3: NORMALIZE TO 2021 TOTAL
    # ========================================================================
    
    print("\n[3/5] Normalizing to CTB 2021 total...")
    
    norm_factor = icms_2021_target / total_before_norm
    icms_matrix_final = icms_matrix * norm_factor
    
    total_final = np.sum(icms_matrix_final)
    print(f"  Normalization factor: {norm_factor:.6f}")
    print(f"  Final total: R$ {total_final/1e3:.2f} Bi")
    print(f"  Deviation: {abs(total_final - icms_2021_target)/icms_2021_target*100:.8f}%")
    
    # ========================================================================
    # STEP 4: CALCULATE COEFFICIENTS
    # ========================================================================
    
    print("\n[4/5] Calculating coefficients...")
    
    # Load VAB matrix
    vab_matrix = np.zeros((len(UFS), n_setores))
    for i, uf in enumerate(UFS):
        vab_matrix[i, :] = vab_regional[uf]
    
    # Calculate tau
    tau_icms = np.zeros((len(UFS), n_setores))
    with np.errstate(divide='ignore', invalid='ignore'):
        tau_icms = icms_matrix_final / vab_matrix
        tau_icms = np.nan_to_num(tau_icms)
    
    mean_tau = np.mean(tau_icms[tau_icms > 0])
    max_tau = np.max(tau_icms)
    min_tau = np.min(tau_icms[tau_icms > 0]) if np.any(tau_icms > 0) else 0
    
    print(f"  Mean coefficient: {mean_tau*100:.2f}%")
    print(f"  Min coefficient:  {min_tau*100:.2f}%")
    print(f"  Max coefficient:  {max_tau*100:.2f}%")
    
    # ========================================================================
    # STEP 5: SAVE RESULTS
    # ========================================================================
    
    print("\n[5/5] Saving results...")
    
    results = {
        "version": "v3_sectoral",
        "year": 2021,
        "methodology": "CNAE-MIP mapping + CTB 2021 calibration",
        "total_icms_milhoes": float(total_final),
        "total_icms_bilhoes": float(total_final / 1e3),
        "normalization_factor": float(norm_factor),
        "by_uf": {},
        "by_sector_by_uf": {},
        "coefficients": {}
    }
    
    # By UF
    for i, uf in enumerate(UFS):
        uf_total = np.sum(icms_matrix_final[i, :])
        results["by_uf"][uf] = {
            "icms_by_sector_milhoes": icms_matrix_final[i, :].tolist(),
            "total_icms_milhoes": float(uf_total),
            "total_icms_bilhoes": float(uf_total / 1e3),
            "share_pct": float(uf_total / total_final * 100)
        }
    
    # By sector
    for j in range(n_setores):
        setor_id = f"setor_{j+1:02d}"
        results["by_sector_by_uf"][setor_id] = {
            uf: float(icms_matrix_final[i, j]) for i, uf in enumerate(UFS)
        }
    
    # Coefficients
    for i, uf in enumerate(UFS):
        results["coefficients"][uf] = tau_icms[i, :].tolist()
    
    # Save full results
    with open('output/icms_regional_v3_sectoral.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: output/icms_regional_v3_sectoral.json")
    
    # Save summary
    sorted_ufs = sorted([(uf, np.sum(icms_matrix_final[i, :])) 
                         for i, uf in enumerate(UFS)], 
                        key=lambda x: x[1], reverse=True)
    
    summary = {
        "version": "v3_sectoral",
        "total_brasil_bilhoes": float(total_final / 1e3),
        "methodology": "CNAE divisions mapped to MIP sectors using validated correspondence table",
        "top_5_ufs": [
            {"uf": uf, "icms_bilhoes": float(val/1e3), 
             "share_pct": float(val/total_final*100)}
            for uf, val in sorted_ufs[:5]
        ],
        "bottom_5_ufs": [
            {"uf": uf, "icms_bilhoes": float(val/1e3),
             "share_pct": float(val/total_final*100)}
            for uf, val in sorted_ufs[-5:]
        ],
        "statistics": {
            "mean_coefficient_pct": float(mean_tau * 100),
            "min_coefficient_pct": float(min_tau * 100),
            "max_coefficient_pct": float(max_tau * 100)
        }
    }
    
    with open('output/icms_regional_v3_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: output/icms_regional_v3_summary.json")
    
    # Display
    print(f"\n{'='*70}")
    print("RESULTS V3 (Sector-Specific)")
    print("="*70)
    
    print(f"\nTop 5 Estados:")
    for item in summary["top_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.1f}%)")
    
    print(f"\nBottom 5 Estados:")
    for item in summary["bottom_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.2f}%)")
    
    print(f"\n{'='*70}\n")
    
    return results, summary

if __name__ == "__main__":
    regionalize_icms_v3_sectoral()
