import numpy as np
import os
import json

def run_tax_reform(exemption_indices: list = None):
    # Paths (consistent with simulate_reform_scenarios.py)
    path_vab = 'data/processed/2021_final/vab_regional.json'
    path_tax_hybrid = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    path_tax_struct = 'data/processed/2021_final/tax_matrix.json'
    path_labels = 'output/intermediary/sector_labels.txt'

    # 1. Load Data
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    
    vab_by_sector = np.zeros(67)
    for vec in vab_regional.values():
        vab_by_sector += np.array(vec)

    with open(path_tax_hybrid, 'r') as f:
        icms_data = json.load(f)
    icms_by_sector = np.zeros(67)
    for vec in icms_data.values():
        icms_by_sector += np.array(vec)

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

    # 2. Scenario A: Flat Tax (Neutro)
    flat_rate = total_revenue_target / total_vab_base

    # 3. Scenario B: Realistic (with chosen exemptions)
    if exemption_indices is None:
        # Default exemptions (similar to CLI script)
        exemption_indices = [0, 1, 2, 7, 8, 9, 41, 42, 60, 61, 62, 63]
    
    factors = np.ones(67)
    factors[exemption_indices] = 0.4 # 60% discount
    
    weighted_base = np.sum(vab_by_sector * factors)
    standard_rate = total_revenue_target / weighted_base
    
    reduction_factor = 0.4
    reduced_rate = standard_rate * reduction_factor
    
    burden_realistic = factors * standard_rate # in decimal
    current_burden = total_current_tax / vab_by_sector
    current_burden[np.isnan(current_burden)] = 0
    current_burden[np.isinf(current_burden)] = 0

    # 4. Results
    with open(path_labels, 'r', encoding='latin1') as f:
        labels = [line.strip() for line in f if line.strip()]

    sector_results = []
    for i in range(67):
        sector_results.append({
            "id": i,
            "name": labels[i] if i < len(labels) else f"Setor {i+1}",
            "vab": float(vab_by_sector[i]),
            "current_burden_pct": float(current_burden[i] * 100),
            "flat_burden_pct": float(flat_rate * 100),
            "realistic_burden_pct": float(burden_realistic[i] * 100),
            "is_exempt": i in exemption_indices
        })

    return {
        "summary": {
            "total_revenue_bn": float(total_revenue_target / 1000),
            "flat_neutral_rate_pct": float(flat_rate * 100),
            "standard_rate_pct": float(standard_rate * 100),
            "reduced_rate_pct": float(reduced_rate * 100)
        },
        "sectors": sector_results
    }
