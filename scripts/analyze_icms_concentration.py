import json
import numpy as np

def analyze_icms_concentration():
    """
    Analyze why SP has 68.8% of ICMS (seems too concentrated)
    """
    
    print("="*70)
    print("ICMS CONCENTRATION ANALYSIS")
    print("="*70)
    
    # Load data
    with open('output/icms_regional_full.json', 'r', encoding='utf-8') as f:
        icms_regional = json.load(f)
    
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    
    with open('output/icms_regional_factors.json', 'r', encoding='utf-8') as f:
        factors = json.load(f)
    
    # Analyze SP dominance
    print(f"\n[Analysis: Why SP has 68.8%?]\n")
    
    sp_factor = factors['regional_factors']['SP']
    sp_vab_total = np.sum(vab_regional['SP'])
    total_vab = sum(np.sum(vab) for vab in vab_regional.values())
    sp_vab_share = sp_vab_total / total_vab * 100
    
    print(f"1. SP Economic Size:")
    print(f"   VAB share: {sp_vab_share:.1f}% (would give ~R$ {537 * sp_vab_share/100:.0f} Bi base)")
    
    print(f"\n2. SP Regional Factor:")
    print(f"   Factor: {sp_factor:.2f}x national average")
    print(f"   This multiplies base by {sp_factor:.2f}")
    
    print(f"\n3. Before Renormalization:")
    sp_pre_renorm = 537 * (sp_vab_share/100) * sp_factor
    print(f"   SP ICMS: ~R$ {sp_pre_renorm:.0f} Bi")
    
    print(f"\n4. Issue:")
    print(f"   Factor 7.76x is TOO HIGH relative to other states")
    print(f"   This is creating extreme concentration")
    
    # Compare with other states
    print(f"\n{'='*70}")
    print("COMPARISON WITH OTHER STATES:")
    print("="*70)
    
    states_comparison = []
    for uf in ['SP', 'RJ', 'MG', 'PR', 'RS']:
        uf_vab = np.sum(vab_regional[uf])
        uf_vab_share = uf_vab / total_vab * 100
        uf_factor = factors['regional_factors'][uf]
        uf_icms_share = icms_regional['by_uf'][uf]['share_pct']
        
        states_comparison.append({
            'uf': uf,
            'vab_share': uf_vab_share,
            'factor': uf_factor,
            'icms_share': uf_icms_share,
            'amplification': uf_icms_share / uf_vab_share
        })
    
    for state in states_comparison:
        print(f"\n{state['uf']}:")
        print(f"  VAB share:  {state['vab_share']:.1f}%")
        print(f"  Factor:     {state['factor']:.2f}x")
        print(f"  ICMS share: {state['icms_share']:.1f}%")
        print(f"  Amplification: {state['amplification']:.2f}x (ICMS/VAB ratio)")
    
    # Recommendation
    print(f"\n{'='*70}")
    print("DIAGNOSIS:")
    print("="*70)
    print(f"""
The issue is that the regional factors from CONFAZ are based on TOTAL ICMS
collection (R$ 776 Bi in 2024), while our model uses only the CTB-defined
ICMS (R$ 537 Bi in 2021).

CONFAZ 2024 includes:
- ICMS on goods + energy + telecom
- Possibly different accounting methodologies
- Different base year

The factor 7.76x for SP means SP collects 7.76x MORE per unit of economic
activity than the national average in CONFAZ data. This is creating extreme
concentration when applied to our more restrictive ICMS definition.

RECOMMENDATION:
We should either:
1. Use ICMS SHARE (not factors) from CONFAZ for distribution
2. Dampen the regional factors (e.g., use sqrt or log transformation)
3. Validate against known state-level ICMS data
""")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    analyze_icms_concentration()
