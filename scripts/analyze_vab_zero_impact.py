import json
import numpy as np

def analyze_vab_zero_impact():
    """
    Analisa quanto ICMS seria 'perdido' zerando casos com VAB=0
    """
    
    print("="*70)
    print("ANÁLISE: IMPACTO DE ZERAR ICMS ONDE VAB=0")
    print("="*70)
    
    # Load V3 Make results
    with open('output/icms_regional_v3_make.json', 'r', encoding='utf-8') as f:
        v3_data = json.load(f)
    
    # Load VAB regional
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    
    UFS = sorted(vab_regional.keys())
    n_setores = 67
    
    # Build matrices
    icms_matrix = np.zeros((len(UFS), n_setores))
    vab_matrix = np.zeros((len(UFS), n_setores))
    
    for i, uf in enumerate(UFS):
        icms_matrix[i, :] = v3_data['by_uf'][uf]['icms_by_sector_milhoes']
        vab_matrix[i, :] = vab_regional[uf]
    
    print(f"\n[1/3] Identificando casos VAB=0 com ICMS>0...")
    
    # Find where VAB=0 but ICMS>0
    vab_zero_mask = (vab_matrix < 0.01)  # Praticamente zero
    icms_positive_mask = (icms_matrix > 0)
    problematic_mask = vab_zero_mask & icms_positive_mask
    
    problematic_cells = np.sum(problematic_mask)
    total_cells = len(UFS) * n_setores
    
    print(f"  Total células: {total_cells}")
    print(f"  Celulas problematicas (VAB~=0, ICMS>0): {problematic_cells}")
    print(f"  Percentual: {problematic_cells/total_cells*100:.2f}%")
    
    # Calculate lost ICMS
    icms_lost = np.sum(icms_matrix[problematic_mask])
    icms_total = np.sum(icms_matrix)
    
    print(f"\n[2/3] ICMS que seria 'perdido':")
    print(f"  ICMS total: R$ {icms_total/1e3:.2f} Bi")
    print(f"  ICMS em células VAB=0: R$ {icms_lost/1e3:.2f} Bi")
    print(f"  Perda percentual: {icms_lost/icms_total*100:.2f}%")
    
    # Simulate zeroing and redistributing
    print(f"\n[3/3] Simulando redistribuição...")
    
    icms_adjusted = icms_matrix.copy()
    
    # Zero out problematic cells
    icms_adjusted[problematic_mask] = 0
    
    # Total after zeroing
    icms_after_zero = np.sum(icms_adjusted)
    
    print(f"  ICMS após zerar: R$ {icms_after_zero/1e3:.2f} Bi")
    print(f"  Diferença: R$ {(icms_total - icms_after_zero)/1e3:.2f} Bi")
    
    # Redistribute the lost ICMS proportionally across valid cells
    valid_mask = ~problematic_mask & (vab_matrix > 0)
    icms_to_redistribute = icms_total - icms_after_zero
    
    if icms_to_redistribute > 0:
        # Redistribute proportionally to existing ICMS in valid cells
        valid_icms_total = np.sum(icms_adjusted[valid_mask])
        
        if valid_icms_total > 0:
            redistribution_factor = (icms_total) / valid_icms_total
            icms_adjusted[valid_mask] *= redistribution_factor
    
    icms_final = np.sum(icms_adjusted)
    
    print(f"\n  ICMS após redistribuição: R$ {icms_final/1e3:.2f} Bi")
    print(f"  Conservação: {icms_final/icms_total*100:.2f}%")
    
    # Calculate new coefficients
    with np.errstate(divide='ignore', invalid='ignore'):
        tau_adjusted = icms_adjusted / vab_matrix
        tau_adjusted = np.nan_to_num(tau_adjusted)
    
    # Filter out zeros for statistics
    tau_nonzero = tau_adjusted[tau_adjusted > 0]
    
    mean_tau = np.mean(tau_nonzero)
    max_tau = np.max(tau_nonzero)
    min_tau = np.min(tau_nonzero)
    extreme_count = np.sum(tau_nonzero > 0.30)
    
    print(f"\n{'='*70}")
    print("COEFICIENTES APÓS AJUSTE")
    print("="*70)
    print(f"  Mean: {mean_tau*100:.2f}%")
    print(f"  Min:  {min_tau*100:.4f}%")
    print(f"  Max:  {max_tau*100:.2f}%")
    print(f"  Coeficientes > 30%: {extreme_count}")
    
    # Show most affected UFs
    print(f"\n{'='*70}")
    print("UFs MAIS AFETADOS")
    print("="*70)
    
    uf_lost = {}
    for i, uf in enumerate(UFS):
        lost = np.sum(icms_matrix[i, problematic_mask[i, :]])
        if lost > 0:
            uf_lost[uf] = lost
    
    top_affected = sorted(uf_lost.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for uf, lost in top_affected:
        total_uf = np.sum(icms_matrix[UFS.index(uf), :])
        print(f"  {uf}: R$ {lost/1e3:.2f} Bi perdidos ({lost/total_uf*100:.1f}% do ICMS do estado)")
    
    print(f"\n{'='*70}")
    print("CONCLUSÃO")
    print("="*70)
    
    if icms_lost / icms_total < 0.05:  # Less than 5% lost
        print(f"\n[OK] VIAVEL!")
        print(f"  - Perdemos apenas {icms_lost/icms_total*100:.2f}% do ICMS")
        print(f"  - Coeficientes extremos caem de 243 para {extreme_count}")
        print(f"  - Solucao pragmatica e economicamente defensavel")
    elif icms_lost / icms_total < 0.15:  # 5-15%
        print(f"\n[!] ACEITAVEL COM RESSALVAS")
        print(f"  - Perda de {icms_lost/icms_total*100:.2f}% e significativa")
        print(f"  - Mas resolve problema de coeficientes infinitos")
        print(f"  - Considerar caso a caso")
    else:
        print(f"\n[X] NAO RECOMENDADO")
        print(f"  - Perda de {icms_lost/icms_total*100:.2f}% e muito alta")
        print(f"  - Melhor usar V2")
    
    print(f"\n{'='*70}\n")
    
    return {
        "icms_total": icms_total,
        "icms_lost": icms_lost,
        "loss_pct": icms_lost/icms_total*100,
        "problematic_cells": int(problematic_cells),
        "new_extreme_count": int(extreme_count),
        "new_mean_tau": float(mean_tau),
        "new_max_tau": float(max_tau)
    }

if __name__ == "__main__":
    analyze_vab_zero_impact()
