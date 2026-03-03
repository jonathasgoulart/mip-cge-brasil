import json
import numpy as np

def final_temporal_audit():
    """
    Final consistency check: 2021 base data + 2024 regional patterns
    """
    
    print("="*70)
    print("AUDITORIA FINAL: CONSIST ÊNCIA TEMPORAL DOS DADOS DE ICMS")
    print("="*70)
    
    # 1. Load 2021 calibrated tax data
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        tax_2021 = json.load(f)
    
    icms_2021 = np.array(tax_2021['taxes_by_type']['ICMS'])
    total_2021 = np.sum(icms_2021)
    
    print(f"\n[1/3] Base do Modelo (CTB 2021):")
    print(f"  ICMS Total Nacional: R$ {total_2021/1e3:.2f} Bilhões")
    
    # 2. Load 2024 CONFAZ data
    with open('output/confaz_icms_2024_by_uf.json', 'r', encoding='utf-8') as f:
        confaz_2024 = json.load(f)
    
    total_2024 = confaz_2024['total_brasil_bilhoes']
    
    print(f"\n[2/3] Dados Regionais (CONFAZ 2024):")
    print(f"  ICMS Total Brasil: R$ {total_2024:.2f} Bilhões")
    print(f"  Crescimento nominal 2021-2024: +{(total_2024/(total_2021/1e3)-1)*100:.1f}%")
    print(f"  Taxa anual média: ~{((total_2024/(total_2021/1e3))**(1/3)-1)*100:.1f}%/ano")
    
    # 3. Load regional factors
    with open('output/icms_regional_factors.json', 'r', encoding='utf-8') as f:
        factors = json.load(f)
    
    regional_factors = factors['regional_factors']
    mean_factor = np.mean(list(regional_factors.values()))
    
    print(f"\n[3/3] Fatores Regionais:")
    print(f"  Fator médio: {mean_factor:.4f}")
    print(f"  Desvio padrão: {np.std(list(regional_factors.values())):.2f}")
    
    print(f"\n[Top 3 Estados - Pressão Tributária]:")
    sorted_factors = sorted(regional_factors.items(), key=lambda x: x[1], reverse=True)
    for uf, factor in sorted_factors[:3]:
        print(f"  {uf}: {factor:.2f}x (arrecada {(factor-1)*100:+.0f}% acima da média)")
    
    # 4. CRITICAL VALIDATION
    print(f"\n{'='*70}")
    print("VALIDAÇÃO DA ABORDAGEM:")
    print("="*70)
    
    print(f"\nMETODOLOGIA RECOMENDADA:")
    print(f"1. Manter ICMS total em 2021: R$ {total_2021/1e3:.2f} Bi")
    print(f"2. Usar fatores regionais 2024 para distribuição espacial")
    print(f"3. Renormalizar após aplicação para preservar total 2021")
    
    print(f"\nFORMULA DE APLICACAO:")
    print(f"  ICMS_UF_setor = (ICMS_2021_setor * VAB_UF_setor / VAB_Total_setor) * Fator_UF")
    print(f"  Depois: ICMS_final = ICMS * (Total_2021 / SUM(ICMS_UF))")
    
    # 5. Check if normalization is needed
    print(f"\n{'='*70}")
    print("STATUS:")
    print("="*70)
    
    if abs(mean_factor - 1.0) < 0.01:
        print(f"[OK] Fatores ja normalizados (media = {mean_factor:.4f})")
        print(f"[OK] Aplicacao direta preservara total nacional 2021")
    else:
        print(f"[!] Fatores precisam de ajuste (media = {mean_factor:.4f})")
        print(f"[!] Implementar renormalizacao apos aplicacao")
    
    # Save summary
    summary = {
        "base_year": 2021,
        "regional_pattern_year": 2024,
        "icms_2021_bilhoes": float(total_2021/1e3),
        "icms_2024_bilhoes": float(total_2024),
        "nominal_growth_pct": float((total_2024/(total_2021/1e3)-1)*100),
        "regional_factors_mean": float(mean_factor),
        "status": "normalized" if abs(mean_factor - 1.0) < 0.01 else "needs_adjustment",
        "recommendation": "Apply regional factors to distribute 2021 total preserving national calibration"
    }
    
    with open('output/temporal_consistency_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n[OK] Relatorio salvo: output/temporal_consistency_summary.json\n")

if __name__ == "__main__":
    final_temporal_audit()
