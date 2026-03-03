import json
import numpy as np
import os

def regionalize_icms():
    """
    Create full regional ICMS matrix: 27 UFs x 67 sectors
    
    Methodology:
    1. Distribute national ICMS by VAB share
    2. Apply regional adjustment factors
    3. Renormalize to preserve 2021 total
    4. Calculate coefficients
    """
    
    print("="*70)
    print("REGIONAL ICMS MATRIX CONSTRUCTION")
    print("="*70)
    
    # ========================================================================
    # STEP 1: LOAD DATA
    # ========================================================================
    
    print("\n[1/5] Loading input data...")
    
    # 1.1 National ICMS 2021 (67 sectors)
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        tax_data = json.load(f)
    
    icms_nacional = np.array(tax_data['taxes_by_type']['ICMS'])  # Millions
    total_nacional = np.sum(icms_nacional)
    
    print(f"  ICMS Nacional 2021: R$ {total_nacional/1e3:.2f} Bi")
    print(f"  Setores: {len(icms_nacional)}")
    
    # 1.2 Regional VAB (27 UFs x 67 sectors)
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
    
    ufs = list(vab_data.keys())
    n_ufs = len(ufs)
    n_setores = 67
    
    # Build VAB matrix
    vab_matrix = np.zeros((n_ufs, n_setores))
    for i, uf in enumerate(ufs):
        vab_matrix[i, :] = np.array(vab_data[uf])
    
    print(f"  VAB Regional: {n_ufs} UFs x {n_setores} setores")
    print(f"  Total VAB: R$ {np.sum(vab_matrix)/1e6:.2f} Tri")
    
    # 1.3 Regional factors (27 UFs)
    with open('output/icms_regional_factors.json', 'r', encoding='utf-8') as f:
        factors_data = json.load(f)
    
    regional_factors = factors_data['regional_factors']
    factors_array = np.array([regional_factors[uf] for uf in ufs])
    
    print(f"  Fatores Regionais: {len(factors_array)} UFs")
    print(f"  Média: {np.mean(factors_array):.4f}, Std: {np.std(factors_array):.2f}")
    
    # ========================================================================
    # STEP 2: DISTRIBUTE BY VAB SHARE
    # ========================================================================
    
    print("\n[2/5] Distributing ICMS by VAB share...")
    
    icms_base = np.zeros((n_ufs, n_setores))
    
    for j in range(n_setores):
        # Total VAB for this sector across all UFs
        vab_setor_total = np.sum(vab_matrix[:, j])
        
        if vab_setor_total > 0:
            # Distribute sector's ICMS proportionally to VAB share
            for i in range(n_ufs):
                share = vab_matrix[i, j] / vab_setor_total
                icms_base[i, j] = icms_nacional[j] * share
        else:
            # Sector has no production - no ICMS
            icms_base[:, j] = 0
    
    total_base = np.sum(icms_base)
    print(f"  ICMS distribuído: R$ {total_base/1e3:.2f} Bi")
    print(f"  Desvio vs nacional: {abs(total_base - total_nacional)/total_nacional*100:.4f}%")
    
    # ========================================================================
    # STEP 3: APPLY REGIONAL ADJUSTMENT
    # ========================================================================
    
    print("\n[3/5] Applying regional factors...")
    
    icms_adjusted = np.zeros((n_ufs, n_setores))
    
    for i in range(n_ufs):
        icms_adjusted[i, :] = icms_base[i, :] * factors_array[i]
    
    total_adjusted = np.sum(icms_adjusted)
    print(f"  ICMS ajustado: R$ {total_adjusted/1e3:.2f} Bi")
    print(f"  Diferença vs nacional: {(total_adjusted/total_nacional - 1)*100:+.2f}%")
    
    # ========================================================================
    # STEP 4: RENORMALIZE TO PRESERVE 2021 TOTAL
    # ========================================================================
    
    print("\n[4/5] Renormalizing to preserve 2021 calibration...")
    
    normalization_factor = total_nacional / total_adjusted
    icms_final = icms_adjusted * normalization_factor
    
    total_final = np.sum(icms_final)
    print(f"  Fator de normalização: {normalization_factor:.6f}")
    print(f"  ICMS final: R$ {total_final/1e3:.2f} Bi")
    print(f"  Desvio vs target: {abs(total_final - total_nacional)/total_nacional*100:.6f}%")
    
    # ========================================================================
    # STEP 5: CALCULATE COEFFICIENTS
    # ========================================================================
    
    print("\n[5/5] Calculating ICMS coefficients...")
    
    tau_icms = np.zeros((n_ufs, n_setores))
    
    for i in range(n_ufs):
        for j in range(n_setores):
            if vab_matrix[i, j] > 0:
                tau_icms[i, j] = icms_final[i, j] / vab_matrix[i, j]
            else:
                tau_icms[i, j] = 0
    
    # Statistics
    mean_tau = np.mean(tau_icms[tau_icms > 0])
    max_tau = np.max(tau_icms)
    
    print(f"  Coeficiente médio: {mean_tau*100:.2f}%")
    print(f"  Coeficiente máximo: {max_tau*100:.2f}%")
    
    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    
    print("\n[Saving results...]")
    
    # Prepare output structure
    results = {
        "year": 2021,
        "calibration_source": "CTB 2021 + CONFAZ 2024 regional patterns",
        "total_icms_milhoes": float(total_final),
        "total_icms_bilhoes": float(total_final / 1e3),
        "methodology": {
            "step_1": "VAB-based distribution",
            "step_2": "Regional factor adjustment (CONFAZ 2024)",
            "step_3": "Renormalization to preserve 2021 total",
            "normalization_factor": float(normalization_factor)
        },
        "by_uf": {},
        "by_sector_by_uf": {},
        "coefficients": {}
    }
    
    # By UF
    for i, uf in enumerate(ufs):
        uf_total = np.sum(icms_final[i, :])
        results["by_uf"][uf] = {
            "icms_by_sector_milhoes": icms_final[i, :].tolist(),
            "total_icms_milhoes": float(uf_total),
            "total_icms_bilhoes": float(uf_total / 1e3),
            "share_pct": float(uf_total / total_final * 100),
            "regional_factor": float(factors_array[i])
        }
    
    # By sector (all UFs)
    for j in range(n_setores):
        setor_id = f"setor_{j+1:02d}"
        results["by_sector_by_uf"][setor_id] = {
            uf: float(icms_final[i, j]) for i, uf in enumerate(ufs)
        }
    
    # Coefficients
    for i, uf in enumerate(ufs):
        results["coefficients"][uf] = tau_icms[i, :].tolist()
    
    # Save full results
    output_path = 'output/icms_regional_full.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: {output_path}")
    
    # Save summary
    summary = {
        "total_brasil_bilhoes": float(total_final / 1e3),
        "top_5_ufs": [],
        "bottom_5_ufs": [],
        "statistics": {
            "mean_coefficient_pct": float(mean_tau * 100),
            "max_coefficient_pct": float(max_tau * 100),
            "n_ufs": n_ufs,
            "n_sectors": n_setores
        }
    }
    
    # Rankings
    uf_totals = [(uf, np.sum(icms_final[i, :])) for i, uf in enumerate(ufs)]
    uf_totals_sorted = sorted(uf_totals, key=lambda x: x[1], reverse=True)
    
    for uf, total in uf_totals_sorted[:5]:
        summary["top_5_ufs"].append({
            "uf": uf,
            "icms_bilhoes": float(total / 1e3),
            "share_pct": float(total / total_final * 100)
        })
    
    for uf, total in uf_totals_sorted[-5:]:
        summary["bottom_5_ufs"].append({
            "uf": uf,
            "icms_bilhoes": float(total / 1e3),
            "share_pct": float(total / total_final * 100)
        })
    
    summary_path = 'output/icms_regional_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: {summary_path}")
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    print(f"\n{'='*70}")
    print("RESULTADOS FINAIS")
    print("="*70)
    
    print(f"\nTop 5 Estados (ICMS):")
    for item in summary["top_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.1f}%)")
    
    print(f"\nBottom 5 Estados (ICMS):")
    for item in summary["bottom_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.2f}%)")
    
    print(f"\n{'='*70}\n")
    
    return results, summary

if __name__ == "__main__":
    regionalize_icms()
