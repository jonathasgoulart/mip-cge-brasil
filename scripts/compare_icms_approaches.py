import json

def compare_approaches():
    """
    Compare V1 (factor-based) vs V2 (share-based) regionalization
    """
    
    print("="*70)
    print("COMPARISON: V1 (Factors) vs V2 (Shares)")
    print("="*70)
    
    # Load both versions
    with open('output/icms_regional_summary.json', 'r') as f:
        v1 = json.load(f)
    
    with open('output/icms_regional_v2_summary.json', 'r') as f:
        v2 = json.load(f)
    
    print(f"\n{'Metric':<40} {'V1 (Factors)':<20} {'V2 (Shares)'}")
    print("-"*70)
    
    # Total (should be same)
    print(f"{'Total ICMS':<40} {'R$ 537.00 Bi':<20} {'R$ 537.00 Bi'}")
    
    # Coefficients
    v1_mean = v1['statistics']['mean_coefficient_pct']
    v2_mean = v2['statistics']['mean_coefficient_pct']
    print(f"{'Mean coefficient':<40} {f'{v1_mean:.2f}%':<20} {f'{v2_mean:.2f}%'}")
    
    v1_max = v1['statistics']['max_coefficient_pct']
    v2_max = v2['statistics']['max_coefficient_pct']
    print(f"{'Max coefficient':<40} {f'{v1_max:.2f}%':<20} {f'{v2_max:.2f}%'}")
    
    # SP share
    v1_sp = v1['top_5_ufs'][0]['share_pct']
    v2_sp = v2['top_5_ufs'][0]['share_pct']
    print(f"{'SP share':<40} {f'{v1_sp:.1f}%':<20} {f'{v2_sp:.1f}%'}")
    
    print(f"\n{'='*70}")
    print("TOP 5 COMPARISON")
    print("="*70)
    
    print(f"\n{'UF':<10} {'V1 (Factor-based)':<25} {'V2 (Share-based)'}")
    print("-"*70)
    
    for i in range(5):
        uf = v2['top_5_ufs'][i]['uf']
        v1_val = next((item['icms_bilhoes'] for item in v1['top_5_ufs'] if item['uf'] == uf), 0)
        v2_val = v2['top_5_ufs'][i]['icms_bilhoes']
        v1_share = next((item['share_pct'] for item in v1['top_5_ufs'] if item['uf'] == uf), 0)
        v2_share = v2['top_5_ufs'][i]['share_pct']
        
        print(f"{uf:<10} R$ {v1_val:6.2f} Bi ({v1_share:5.1f}%)   R$ {v2_val:6.2f} Bi ({v2_share:5.1f}%)")
    
    print(f"\n{'='*70}")
    print("RECOMMENDATION")
    print("="*70)
    
    print(f"""
V1 (Factor-based):
  - Amplifies regional differences using 7.76x factor for SP
  - Creates extreme concentration (SP = 68.8%)
  - Max coefficient: 43.8% (unrealistic)
  - Mean coefficient: 2.13%
  
V2 (Share-based):
  - Uses CONFAZ 2024 shares directly
  - More balanced distribution (SP = 28.7%)
  - Max coefficient: 6.30% (reasonable)
  - Mean coefficient: 4.26%
  - Matches actual CONFAZ proportions

RECOMMENDED: V2 (Share-based)
  
Rationale:
1. Preserves actual state-level ICMS distribution from CONFAZ
2. Avoids artificial amplification from multiplicative factors
3. Coefficients are within realistic ranges (1.7% - 6.3%)
4. SP share (28.7%) matches both its economic size AND tax collection reality
5. More stable for simulations (won't create extreme sectoral distortions)
""")
    
    print(f"{'='*70}\n")

if __name__ == "__main__":
    compare_approaches()
