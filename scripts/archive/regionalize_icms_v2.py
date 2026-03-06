import json
import numpy as np

def regionalize_icms_v2():
    """
    Alternative regionalization using CONFAZ SHARES (not factors)
    
    Instead of: ICMS_UF = ICMS_base * Factor * Renorm
    Use: ICMS_UF = ICMS_2021_total * CONFAZ_share_UF
    
    Then distribute within each UF by VAB sector shares
    """
    
    print("="*70)
    print("REGIONAL ICMS MATRIX CONSTRUCTION V2 (Share-based)")
    print("="*70)
    
    # ================================================================
    # STEP 1: LOAD DATA
    # ================================================================
    
    print("\n[1/4] Loading input data...")
    
    # National ICMS 2021
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        tax_data = json.load(f)
    
    icms_nacional = np.array(tax_data['taxes_by_type']['ICMS'])
    total_icms_2021 = np.sum(icms_nacional)
    
    print(f"  ICMS Nacional 2021: R$ {total_icms_2021/1e3:.2f} Bi")
    
    # Regional VAB
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
    
    ufs = list(vab_data.keys())
    n_ufs = len(ufs)
    n_setores = 67
    
    vab_matrix = np.zeros((n_ufs, n_setores))
    for i, uf in enumerate(ufs):
        vab_matrix[i, :] = np.array(vab_data[uf])
    
    total_vab = np.sum(vab_matrix)
    print(f"  VAB Regional: {n_ufs} UFs x {n_setores} setores")
    
    # CONFAZ 2024 shares
    with open('output/confaz_icms_2024_by_uf.json', 'r', encoding='utf-8') as f:
        confaz = json.load(f)
    
    confaz_shares = {}
    total_confaz = confaz['total_brasil_bilhoes']
    
    for uf in ufs:
        confaz_shares[uf] = confaz['by_uf_bilhoes'][uf] / total_confaz
    
    print(f"  CONFAZ 2024 shares calculated for {len(confaz_shares)} UFs")
    
    # ================================================================
    # STEP 2: DISTRIBUTE TOTAL ICMS BY CONFAZ SHARES
    # ================================================================
    
    print("\n[2/4] Distributing total ICMS by CONFAZ shares...")
    
    icms_by_uf_total = {}
    for uf in ufs:
        icms_by_uf_total[uf] = total_icms_2021 * confaz_shares[uf]
    
    # Verify
    check_total = sum(icms_by_uf_total.values())
    print(f"  Total distributed: R$ {check_total/1e3:.2f} Bi")
    print(f"  Deviation: {abs(check_total - total_icms_2021)/total_icms_2021*100:.6f}%")
    
    # Show top 5
    sorted_ufs = sorted(icms_by_uf_total.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  Top 5 UFs:")
    for uf, total in sorted_ufs[:5]:
        share_pct = total / total_icms_2021 * 100
        print(f"    {uf}: R$ {total/1e3:.2f} Bi ({share_pct:.1f}%)")
    
    # ================================================================
    # STEP 3: DISTRIBUTE WITHIN EACH UF BY VAB SECTOR SHARES
    # ================================================================
    
    print("\n[3/4] Distributing within states by sector VAB shares...")
    
    icms_regional = np.zeros((n_ufs, n_setores))
    
    for i, uf in enumerate(ufs):
        uf_vab_total = np.sum(vab_matrix[i, :])
        uf_icms_total = icms_by_uf_total[uf]
        
        if uf_vab_total > 0:
            for j in range(n_setores):
                sector_share = vab_matrix[i, j] / uf_vab_total
                icms_regional[i, j] = uf_icms_total * sector_share
        else:
            icms_regional[i, :] = 0
    
    total_check = np.sum(icms_regional)
    print(f"  Total ICMS (all UFs, all sectors): R$ {total_check/1e3:.2f} Bi")
    print(f"  Deviation from target: {abs(total_check - total_icms_2021)/total_icms_2021*100:.6f}%")
    
    # ================================================================
    # STEP 4: CALCULATE COEFFICIENTS
    # ================================================================
    
    print("\n[4/4] Calculating coefficients...")
    
    tau_icms = np.zeros((n_ufs, n_setores))
    
    for i in range(n_ufs):
        for j in range(n_setores):
            if vab_matrix[i, j] > 0:
                tau_icms[i, j] = icms_regional[i, j] / vab_matrix[i, j]
    
    mean_tau = np.mean(tau_icms[tau_icms > 0])
    max_tau = np.max(tau_icms)
    min_tau = np.min(tau_icms[tau_icms > 0])
    
    print(f"  Mean coefficient: {mean_tau*100:.2f}%")
    print(f"  Min coefficient:  {min_tau*100:.2f}%")
    print(f"  Max coefficient:  {max_tau*100:.2f}%")
    
    # ================================================================
    # SAVE RESULTS
    # ================================================================
    
    print("\n[Saving results...]")
    
    results = {
        "year": 2021,
        "calibration_source": "CTB 2021 (total) + CONFAZ 2024 (regional shares)",
        "methodology": "Direct share-based distribution",
        "total_icms_milhoes": float(total_check),
        "total_icms_bilhoes": float(total_check / 1e3),
        "by_uf": {},
        "by_sector_by_uf": {},
        "coefficients": {},
        "confaz_shares": confaz_shares
    }
    
    # By UF
    for i, uf in enumerate(ufs):
        uf_total = np.sum(icms_regional[i, :])
        results["by_uf"][uf] = {
            "icms_by_sector_milhoes": icms_regional[i, :].tolist(),
            "total_icms_milhoes": float(uf_total),
            "total_icms_bilhoes": float(uf_total / 1e3),
            "share_pct": float(uf_total / total_check * 100),
            "confaz_share_2024": float(confaz_shares[uf])
        }
    
    # By sector
    for j in range(n_setores):
        setor_id = f"setor_{j+1:02d}"
        results["by_sector_by_uf"][setor_id] = {
            uf: float(icms_regional[i, j]) for i, uf in enumerate(ufs)
        }
    
    # Coefficients
    for i, uf in enumerate(ufs):
        results["coefficients"][uf] = tau_icms[i, :].tolist()
    
    # Save
    output_path = 'output/icms_regional_v2.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: {output_path}")
    
    # Summary
    summary = {
        "total_brasil_bilhoes": float(total_check / 1e3),
        "methodology": "Share-based (CONFAZ 2024 shares applied to CTB 2021 total)",
        "top_5_ufs": [],
        "bottom_5_ufs": [],
        "statistics": {
            "mean_coefficient_pct": float(mean_tau * 100),
            "min_coefficient_pct": float(min_tau * 100),
            "max_coefficient_pct": float(max_tau * 100),
            "n_ufs": n_ufs,
            "n_sectors": n_setores
        }
    }
    
    for uf, total in sorted_ufs[:5]:
        summary["top_5_ufs"].append({
            "uf": uf,
            "icms_bilhoes": float(icms_by_uf_total[uf] / 1e3),
            "share_pct": float(icms_by_uf_total[uf] / total_icms_2021 * 100)
        })
    
    for uf, total in sorted_ufs[-5:]:
        summary["bottom_5_ufs"].append({
            "uf": uf,
            "icms_bilhoes": float(icms_by_uf_total[uf] / 1e3),
            "share_pct": float(icms_by_uf_total[uf] / total_icms_2021 * 100)
        })
    
    summary_path = 'output/icms_regional_v2_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] Saved: {summary_path}")
    
    # Display
    print(f"\n{'='*70}")
    print("RESULTADOS FINAIS (V2)")
    print("="*70)
    
    print(f"\nTop 5 Estados:")
    for item in summary["top_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.1f}%)")
    
    print(f"\nBottom 5 Estados:")
    for item in summary["bottom_5_ufs"]:
        print(f"  {item['uf']}: R$ {item['icms_bilhoes']:.2f} Bi ({item['share_pct']:.2f}%)")
    
    print(f"\n{'='*70}\n")
    
    return results

if __name__ == "__main__":
    regionalize_icms_v2()
