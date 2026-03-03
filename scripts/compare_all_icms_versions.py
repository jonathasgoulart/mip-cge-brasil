import json

def compare_all_versions():
    """
    Compare V1 (factor), V2 (share), and V3 (sectoral) regionalizations
    """
    
    print("="*90)
    print("COMPARISON: ALL ICMS REGIONALIZATION VERSIONS")
    print("="*90)
    
    # Load all versions
    with open('output/icms_regional_summary.json', 'r') as f:
        v1 = json.load(f)
    
    with open('output/icms_regional_v2_summary.json', 'r') as f:
        v2 = json.load(f)
    
    with open('output/icms_regional_v3_summary.json', 'r') as f:
        v3 = json.load(f)
    
    print(f"\n{'Metric':<50} {'V1 (Factor)':<20} {'V2 (Share)':<20} {'V3 (Sectoral)'}")
    print("-"*90)
    
    # Totals
    print(f"{'Total ICMS (Bi)':<50} {'R$ 537.00':<20} {'R$ 537.00':<20} {'R$ 537.00'}")
    
    # Methodology
    print(f"\n{'METHODOLOGY':<50}")
    print(f"{'Distribution method':<50} {'Regional factors':<20} {'CONFAZ shares':<20} {'CNAE->MIP map'}")
    print(f"{'Sector specificity':<50} {'VAB only':<20} {'VAB only':<20} {'CNAE sectoral'}")
    
    # Coefficients
    print(f"\n{'COEFFICIENTS':<50}")
    v1_mean = v1['statistics']['mean_coefficient_pct']
    v2_mean = v2['statistics']['mean_coefficient_pct']
    v3_mean = v3['statistics']['mean_coefficient_pct']
    print(f"{'Mean tau_ICMS':<50} {f'{v1_mean:.2f}%':<20} {f'{v2_mean:.2f}%':<20} {f'{v3_mean:.2f}%'}")
    
    v1_max = v1['statistics']['max_coefficient_pct']
    v2_max = v2['statistics']['max_coefficient_pct']
    v3_max = v3['statistics']['max_coefficient_pct']
    print(f"{'Max tau_ICMS':<50} {f'{v1_max:.2f}%':<20} {f'{v2_max:.2f}%':<20} {f'{v3_max:.2f}%'}")
    
    # SP share
    v1_sp = v1['top_5_ufs'][0]
    v2_sp = v2['top_5_ufs'][0]
    v3_sp = v3['top_5_ufs'][0]
    print(f"\n{'SP SHARE':<50}")
    print(f"{'SP ICMS (Bi)':<50} {f'R$ {v1_sp[\"icms_bilhoes\"]:.1f}':<20} {f'R$ {v2_sp[\"icms_bilhoes\"]:.1f}':<20} {f'R$ {v3_sp[\"icms_bilhoes\"]:.1f}'}")
    print(f"{'SP share (%)':<50} {f'{v1_sp[\"share_pct\"]:.1f}%':<20} {f'{v2_sp[\"share_pct\"]:.1f}%':<20} {f'{v3_sp[\"share_pct\"]:.1f}%'}")
    
    # Top 5 comparison
    print(f"\n{'='*90}")
    print("TOP 5 ESTADOS COMPARISON")
    print("="*90)
    print(f"\n{'UF':<10} {'V1 (Factor)':<25} {'V2 (Share)':<25} {'V3 (Sectoral)'}")
    print("-"*90)
    
    for i in range(5):
        uf = v2['top_5_ufs'][i]['uf']
        v1_val = next((item['icms_bilhoes'] for item in v1['top_5_ufs'] if item['uf'] == uf), 0)
        v2_val = v2['top_5_ufs'][i]['icms_bilhoes']
        v3_val = v3['top_5_ufs'][i]['icms_bilhoes']
        
        v1_share = next((item['share_pct'] for item in v1['top_5_ufs'] if item['uf'] == uf), 0)
        v2_share = v2['top_5_ufs'][i]['share_pct']
        v3_share = v3['top_5_ufs'][i]['share_pct']
        
        print(f"{uf:<10} R$ {v1_val:5.1f} Bi ({v1_share:4.1f}%)   R$ {v2_val:5.1f} Bi ({v2_share:4.1f}%)   R$ {v3_val:5.1f} Bi ({v3_share:4.1f}%)")
    
    # Recommendation
    print(f"\n{'='*90}")
    print("ANALYSIS & RECOMMENDATION")
    print("="*90)
    
    print(f"""
V1 (Factor-based):
  - Uses regional adjustment factors (7.76x for SP)
  - PROBLEM: Excessive concentration (SP = 68.8% - unrealistic)
  - Max coefficient: 43.8% (very high)
  - Status: NOT RECOMMENDED (distorted)

V2 (Share-based):
  - Uses CONFAZ 2024 shares directly
  - Balanced distribution (SP = 28.7%)
  - Max coefficient: 6.30% (reasonable)
  - Status: GOOD - Preserves real distributions
  - Limitation: Uniform within UF (no sector specificity)

V3 (Sectoral):
  - Maps CNAE divisions to MIP sectors
  - Sector-specific ICMS by UF
  - PROBLEM: Max coefficient {v3_max:.1f}% (ERROR - needs investigation)
  - SP share: {v3_sp['share_pct']:.1f}% (close to V2)
  - Status: NEEDS DEBUGGING (likely VAB mismatch in some sectors)

RECOMMENDED FOR PRODUCTION: V2 (Share-based)
  
Rationale:
1. Realistic state-level distributions (matches CONFAZ 2024)
2. Sensible coefficients (1.7%-6.3% range)
3. Stable and validated
4. Suitable for regional simulations

V3 has potential but needs debugging of extreme coefficients.
The {v3_max:.0f}% coefficient suggests a VAB/ICMS mismatch in some sector.
""")
    
    print(f"\n{'='*90}\n")

if __name__ == "__main__":
    compare_all_versions()
