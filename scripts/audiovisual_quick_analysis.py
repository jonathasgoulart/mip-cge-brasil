"""
Análise Rápida e Simples do Setor Audiovisual Brasileiro
Usando apenas os dados já disponíveis
"""

import numpy as np
import json

# Paths
BASE = r"c:\Users\jonat\Documents\MIP e CGE"
A_nas = np.load(f"{BASE}/output/intermediary/A_nas.npy")
X_nas = np.load(f"{BASE}/output/intermediary/X_nas.npy")
VAB_nas = np.load(f"{BASE}/output/intermediary/VAB_nacional.npy")

# Carregar labels
with open(f"{BASE}/output/intermediary/perfectionist_base_2015.json", 'r', encoding='utf-8') as f:
    data = json.load(f)
    LABELS = data['labels']

# Setores audiovisuais (CORRETO: debug confirmou!)
CORE_AV = {
    47: "Edição e edição integrada à impressão",
    48: "Atividades de televisão, rádio, cinema e gravação/edição de som e imagem",
    64: "Atividades artísticas, criativas e de espetáculos"
}

print("="*80)
print("SETOR AUDIOVISUAL BRASILEIRO - ANÁLISE PRELIMINAR")
print("="*80)

print("\n1. SETORES IDENTIFICADOS:")
for idx, nome in CORE_AV.items():
    print(f"  [{idx}] {LABELS[idx]}")
    print(f"      VAB 2015: R$ {VAB_nas[idx]:,.0f} milhões")
    print(f"      Produção: R$ {X_nas[idx]:,.0f} milhões")

vab_total = sum(VAB_nas[idx] for idx in CORE_AV.keys())
x_total = sum(X_nas[idx] for idx in CORE_AV.keys())
print(f"\n{'='*60}")
print(f"TOTAL AUDIOVISUAL CORE:")
print(f"  VAB: R$ {vab_total:,.0f} milhões ({vab_total/VAB_nas.sum()*100:.2f}% do PIB)")
print(f"  Produção: R$ {x_total:,.0f} milhões")

# Multiplicadores
print("\n2. MULTIPLICADORES DE PRODUÇÃO:")
I = np.eye(67)
L = np.linalg.inv(I - A_nas)

for idx in CORE_AV.keys():
    mult = L[:, idx].sum()
    print(f"  [{idx}] {LABELS[idx][:50]}: {mult:.3f}")

# CONFAZ ICMS
print("\n3. ARRECADAÇÃO ICMS 2024 (Divisão 90 - CNAE Audiovisual):")
with open(f"{BASE}/output/confaz_icms_2024_by_uf.json", 'r', encoding='utf-8') as f:
    confaz = json.load(f)

cnae_key = "Soma de Divisão: 90 - ATIVIDADES ARTÍSTICAS, CRIATIVAS E DE ESPETÁCULOS"
by_uf_cnae = confaz['by_uf_by_cnae']

icms_by_uf = {}
for uf, dados in by_uf_cnae.items():
    icms_by_uf[uf] = dados.get(cnae_key, 0) / 1000  # Converter para milhões

total_icms = sum(icms_by_uf.values())
sorted_icms = sorted(icms_by_uf.items(), key=lambda x: x[1], reverse=True)

print(f"\n{'UF':<4} {'ICMS (R$ milhões)':<20} {'% Brasil':<10}")
print("-"*40)
for uf, icms in sorted_icms[:10]:
    pct = (icms / total_icms * 100) if total_icms > 0 else 0
    print(f"{uf:<4} R$ {icms:>14,.1f}   {pct:>6.2f}%")

print("-"*40)
print(f"BRASIL:  R$ {total_icms:>14,.1f}   100.00%")

print("\n" + "="*80)
print("RESUMO EXECUTIVO")
print("="*80)
print(f"""
[OK] VAB Audiovisual (2015):  R$ {vab_total:,.0f} milhoes ({vab_total/VAB_nas.sum()*100:.2f}% do PIB)
[OK] Multiplicador Medio:     {np.mean([L[:, idx].sum() for idx in CORE_AV.keys()]):.2f}x
[OK] ICMS Arrecadado (2024):  R$ {total_icms:,.1f} milhoes
[OK] Top 3 Estados ICMS:      {sorted_icms[0][0]} (R$ {sorted_icms[0][1]:.1f} Mi), {sorted_icms[1][0]} (R$ {sorted_icms[1][1]:.1f} Mi), {sorted_icms[2][0]} (R$ {sorted_icms[2][1]:.1f} Mi)

PROXIMOS PASSOS:
-> Analise MRIO (spillovers interestaduais)
-> Decomposicao musica/cinema/eventos
-> Multiplicadores de emprego detalhados
""")
