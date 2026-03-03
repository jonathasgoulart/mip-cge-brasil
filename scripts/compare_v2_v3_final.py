import json

print("="*70)
print("FINAL COMPARISON: V2 (SHARE) vs V3 (PARCIAL)")
print("="*70)

# Load both
with open('output/icms_regional_v2_summary.json', 'r') as f:
    v2 = json.load(f)

with open('output/icms_regional_v3_final_summary.json', 'r') as f:
    v3 = json.load(f)

print(f"\n{'Metric':<40} {'V2 (Share)':<20} {'V3 (Parcial)'}")
print("-"*70)
print(f"{'Total ICMS (Bi)':<40} {'R$ 537.00':<20} {'R$ 537.00'}")
print(f"{'Mean coefficient':<40} {f'{v2[\"statistics\"][\"mean_coefficient_pct\"]:.2f}%':<20} {f'{v3[\"statistics\"][\"mean_coefficient_pct\"]:.2f}%'}")
print(f"{'Max coefficient':<40} {f'{v2[\"statistics\"][\"max_coefficient_pct\"]:.2f}%':<20} {f'{v3[\"statistics\"][\"max_coefficient_pct\"]:.0f}%'}")

print(f"\nTop 5:")
for i in range(5):
    v2_uf = v2['top_5_ufs'][i]
    v3_uf = v3['top_5_ufs'][i]
    print(f"  {v2_uf['uf']}: R$ {v2_uf['icms_bilhoes']:.1f} Bi ({v2_uf['share_pct']:.1f}%)  vs  {v3_uf['uf']}: R$ {v3_uf['icms_bilhoes']:.1f} Bi ({v3_uf['share_pct']:.1f}%)")

print(f"\n{'='*70}")
print("CONCLUSAO")
print("="*70)

print(f"""
V2 (Share-based) - RECOM ENDADO:
  Prós:
  - Coeficientes realistas (4.26% médio, máx 6.30%)
  - Distribuição estável por UF
  - Simples e validada
  - Funciona para todos os setores
  
  Contras:
  - Não tem especificidade setorial dentro de cada UF
  - Assume ICMS/VAB uniforme por estado

V3 (Parcial) - EXPERIMENTAL:
  Prós:
  - Tenta mapear setores CNAE para produtos MIP
  - Potencial para mais precisão setorial
  
  Contras:
  - Coeficientes irrealistas (max {v3["statistics"]["max_coefficient_pct"]:.0f}%)  
  - Incompatibilidade estrutural: CONFAZ tem 87 setores (atividades)
    vs MIP tem 67 produtos (bens físicos)
  - Serviços não têm produto MIP correspondente
  - Precisa mais desenvolvimento

RECOMENDACAO FINAL: Use V2 (share-based) para produção

Arquivo: output/icms_regional_v2.json
""")

print(f"{'='*70}\n")
