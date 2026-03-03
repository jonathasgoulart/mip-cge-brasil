"""
ANÁLISE DETALHADA: JSON vs NPY - Diferença de R$ 2,6 trilhões no VAB

Este script compara setor por setor os valores de VAB, VBP e CI
entre as duas fontes para identificar a causa exata da divergência.
"""

import numpy as np
import json
import pandas as pd

print("="*80)
print("ANÁLISE COMPARATIVA DETALHADA: JSON vs NPY")
print("="*80)

# Carregar dados
with open('output/intermediary/perfectionist_base_2015.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

vab_json = np.array(json_data['VAB_plus_2015'])
x_json = np.array(json_data['X_2015'])
ci_json = np.array(json_data['CI_total_2015'])
labels = json_data['labels']

vab_npy = np.load('output/intermediary/VAB_nacional.npy')
x_npy = np.load('output/intermediary/X_nas.npy')

# CI do NPY - calcular retroativamente
ci_npy = x_npy - vab_npy

print("\n1. TOTAIS GERAIS")
print("="*80)
print(f"\n{'Métrica':<20} {'JSON (Excel)':<20} {'NPY (CSV)':<20} {'Diferença':<15}")
print("-"*80)
print(f"{'VBP/X_2015':<20} R$ {x_json.sum():>15,.0f}  R$ {x_npy.sum():>15,.0f}  R$ {(x_npy.sum()-x_json.sum()):>12,.0f}")
print(f"{'CI Total':<20} R$ {ci_json.sum():>15,.0f}  R$ {ci_npy.sum():>15,.0f}  R$ {(ci_npy.sum()-ci_json.sum()):>12,.0f}")
print(f"{'VAB':<20} R$ {vab_json.sum():>15,.0f}  R$ {vab_npy.sum():>15,.0f}  R$ {(vab_npy.sum()-vab_json.sum()):>12,.0f}")

print("\n2. ANÁLISE SETORIAL - Top 20 Divergências")
print("="*80)

# Calcular diferenças
diff_vab = vab_npy - vab_json
diff_x = x_npy - x_json
diff_ci = ci_npy - ci_json

# Criar DataFrame para análise
df = pd.DataFrame({
    'Setor': labels,
    'VAB_JSON': vab_json,
    'VAB_NPY': vab_npy,
    'Diff_VAB': diff_vab,
    'Diff_%': (diff_vab / vab_json * 100),
    'X_JSON': x_json,
    'X_NPY': x_npy,
    'Diff_X': diff_x,
    'CI_JSON': ci_json,
    'CI_NPY': ci_npy,
    'Diff_CI': diff_ci
})

# Ordenar por diferença absoluta
df_sorted = df.reindex(np.argsort(np.abs(diff_vab))[::-1])

print(f"\n{'#':<3} {'Setor':<50} {'VAB JSON':<12} {'VAB NPY':<12} {'Dif R$':<12} {'Dif %':<8}")
print("-"*100)

for idx, (i, row) in enumerate(df_sorted.head(20).iterrows(), 1):
    setor_name = row['Setor'][:47] + "..." if len(row['Setor']) > 50 else row['Setor']
    print(f"{idx:<3} {setor_name:<50} {row['VAB_JSON']:>10,.0f}  {row['VAB_NPY']:>10,.0f}  {row['Diff_VAB']:>10,.0f}  {row['Diff_%']:>6.1f}%")

print("\n3. PADRÃO DE DIVERGÊNCIA")
print("="*80)

# Análise por faixa de VAB
print("\nDivergência por tamanho do setor:")
bins = [0, 50000, 100000, 200000, float('inf')]
bin_labels = ['< 50 bi', '50-100 bi', '100-200 bi', '> 200 bi']

for i in range(len(bins)-1):
    mask = (vab_json >= bins[i]) & (vab_json < bins[i+1])
    if mask.sum() > 0:
        avg_diff = diff_vab[mask].mean()
        avg_diff_pct = (diff_vab[mask] / vab_json[mask] * 100).mean()
        print(f"  {bin_labels[i]:<12}: {mask.sum():2d} setores | Dif média: R$ {avg_diff:>10,.0f} ({avg_diff_pct:>5.1f}%)")

print("\n4. COMPARAÇÃO VBP vs CI vs VAB")
print("="*80)

print(f"\nJSON (Excel direto):")
print(f"  VBP = R$ {x_json.sum():,.0f} milhões")
print(f"  CI  = R$ {ci_json.sum():,.0f} milhões")
print(f"  VAB = VBP - CI = R$ {vab_json.sum():,.0f} milhões")
print(f"  Check: {abs(vab_json.sum() - (x_json.sum() - ci_json.sum())) < 1:.0f} (diferença < 1 milhão)")

print(f"\nNPY (CSV processado):")
print(f"  VBP = R$ {x_npy.sum():,.0f} milhões")
print(f"  CI  = R$ {ci_npy.sum():,.0f} milhões (calculado retroativo)")
print(f"  VAB = R$ {vab_npy.sum():,.0f} milhões")
print(f"  Check: {abs(vab_npy.sum() - (x_npy.sum() - ci_npy.sum())) < 1:.0f}")

print("\n5. HIPÓTESES SOBRE A DIVERGÊNCIA")
print("="*80)

# Verificar se é proporcional
ratio_vab = vab_npy.sum() / vab_json.sum()
ratio_x = x_npy.sum() / x_json.sum()

print(f"\nRazão VAB_NPY / VAB_JSON: {ratio_vab:.4f} ({(ratio_vab-1)*100:+.2f}%)")
print(f"Razão X_NPY / X_JSON:     {ratio_x:.4f} ({(ratio_x-1)*100:+.2f}%)")

if abs(ratio_vab - ratio_x) < 0.01:
    print("\n✓ Divergência é PROPORCIONAL - sugere fator multiplicativo constante")
    print("  Provável: preços básicos vs preços de mercado")
else:
    print("\n✓ Divergência NÃO é proporcional - sugere processamento setorial diferente")

# Verificar se VBP são iguais
if np.allclose(x_json, x_npy, rtol=0.01):
    print("\n✓ VBP são IGUAIS entre JSON e NPY")
    print("  Divergência vem do CI diferente")
else:
    print("\n✓ VBP são DIFERENTES entre JSON e NPY")
    print("  Divergência pode vir de valorização diferente (básico vs mercado)")

print("\n6. SETORES AUDIOVISUAIS - Comparação")
print("="*80)

audiovisual_idx = [47, 48, 64]
av_names = [
    "Edição e edição integrada à impressão",
    "Atividades de televisão, rádio, cinema...",
    "Atividades artísticas, criativas e de espetáculos"
]

print(f"\n{'Setor':<50} {'VAB JSON':<12} {'VAB NPY':<12} {'Diferença':<12}")
print("-"*90)
for idx, name in zip(audiovisual_idx, av_names):
    print(f"{name[:47]+'...' if len(name)>50 else name:<50} {vab_json[idx]:>10,.0f}  {vab_npy[idx]:>10,.0f}  {diff_vab[idx]:>10,.0f}")

print(f"\n{'TOTAL AUDIOVISUAL':<50} {vab_json[audiovisual_idx].sum():>10,.0f}  {vab_npy[audiovisual_idx].sum():>10,.0f}  {diff_vab[audiovisual_idx].sum():>10,.0f}")

print("\n" + "="*80)
print("CONCLUSÕES")
print("="*80)
print("""
Para entender completamente a divergência, precisamos:
1. Verificar origem dos arquivos CSV em data/processed/
2. Identificar qual script gerou esses CSVs
3. Verificar se há conversão de preços (básico → mercado)
4. Validar qual fonte usar para cada tipo de análise
""")
