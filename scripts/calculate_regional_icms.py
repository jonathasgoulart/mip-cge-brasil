import json
import numpy as np

def calculate_regional_icms_factors():
    """
    Calculate Regional ICMS Adjustment Factors
    
    Logic:
    - Base model has national ICMS coefficient (from CTB 2021: R$ 537 Bi)
    - CONFAZ 2024 has actual collection by UF (R$ 2.4 Tri)
    - Create adjustment factor per UF: Factor_UF = (ICMS_UF_2024 / ICMS_Total_2024) / (VAB_UF / VAB_Total)
    
    This captures:
    1. States with higher-than-average ICMS pressure (mining, energy)
    2. States with tax incentives (lower effective rates)
    """
    
    print("="*70)
    print("REGIONAL ICMS COEFFICIENT CALCULATION")
    print("="*70)
    
    # Load CONFAZ data
    with open('output/confaz_icms_2024_by_uf.json', 'r', encoding='utf-8') as f:
        confaz = json.load(f)
    
    icms_by_uf = confaz['by_uf_bilhoes']  # Use billions for easier calculation
    icms_total_2024 = confaz['total_brasil_bilhoes']
    
    print(f"\nCONFAZ 2024 Total: R$ {icms_total_2024/1e6:.2f} Trillion")
    
    # Load VAB Regional data (from our MRIO model)
    # For simplicity, use uniform distribution for now
    # (TODO: Load actual VAB by UF from extract_vab_real outputs)
    
    # For now, assume ICMS share ≈ VAB share (first approximation)
    # Regional factor = ICMS_share / Avg (=1.0 for proportional states)
    
    regional_factors = {}
    
    for uf, icms_val in icms_by_uf.items():
        share = icms_val / icms_total_2024
        # National average would be 1/27 ≈ 0.037
        # If UF has share > avg → high ICMS state
        # If UF has share < avg → lowICMS state
        
        # Factor ranges from ~0.1 (low-ICMS states) to ~7.0 (SP)
        # This will multiply the national ICMS coefficient
        factor = share * 27.0  # Normalize to avg=1.0
        
        regional_factors[uf] = float(factor)
    
    # Validation
    print(f"\n[Regional Factors]:")
    print("-"*70)
    
    sorted_factors = sorted(regional_factors.items(), key=lambda x: x[1], reverse=True)
    
    print("Top 5 (Highest ICMS Pressure):")
    for uf, factor in sorted_factors[:5]:
        print(f"  {uf}: {factor:.2f}x (ICMS share: {icms_by_uf[uf]/icms_total_2024*100:.1f}%)")
    
    print("\nBottom 5 (Lowest ICMS Pressure):")
    for uf, factor in sorted_factors[-5:]:
        print(f"  {uf}: {factor:.3f}x (ICMS share: {icms_by_uf[uf]/icms_total_2024*100:.2f}%)")
    
    # Save
    output = {
        "year": 2024,
        "source": "CONFAZ 2024",
        "regional_factors": regional_factors,
        "validation": {
            "sum_shares": sum(icms_by_uf.values()) / icms_total_2024,
            "mean_factor": np.mean(list(regional_factors.values())),
            "std_factor": np.std(list(regional_factors.values()))
        }
    }
    
    with open('output/icms_regional_factors.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[OK] Saved to: output/icms_regional_factors.json")
    print(f"\nValidation:")
    print(f"  Mean factor: {output['validation']['mean_factor']:.2f} (should be ~1.0)")
    print(f"  Std dev: {output['validation']['std_factor']:.2f}")
    
    return output

if __name__ == "__main__":
    calculate_regional_icms_factors()
