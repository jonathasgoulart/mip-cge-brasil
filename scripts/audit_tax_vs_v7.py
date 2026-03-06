"""
Auditoria da Matriz de Impostos vs MRIO v7.0.
Verifica 4 tipos de inconsistência com a mudança de ano-base:
  1. Dimensão: tax_matrix tem 70 entradas vs 67 setores MRIO
  2. Ano-base: valores nominais são de MIP 2015, VBP agora é IIOAS 2019
  3. Coeficientes fiscais implícitos (tax/VBP): divergência por setor
  4. Impacto nos resultados das simulações fiscais
"""
import numpy as np, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE   = Path(r'C:\Users\jonat\Documents\MIP e CGE')
TAX    = BASE / 'data' / 'processed' / '2021_final' / 'tax_matrix.json'
VBP_19 = BASE / 'output' / 'crosswalk' / 'vbp_iioas_all_ufs.npy'
X_NAS  = BASE / 'output' / 'intermediary' / 'X_nas.npy'   # VBP 2019 MIP Nacional
LABELS = BASE / 'output' / 'intermediary' / 'sector_labels.txt'

with open(TAX, encoding='utf-8') as f:
    tax_data = json.load(f)

with open(LABELS, encoding='utf-8') as f:
    labels = [l.strip() for l in f if l.strip()]

taxes = tax_data['taxes_by_type']
N_TAX = len(next(iter(taxes.values())))  # quantas entradas por imposto?
print(f"Metadata: {tax_data.get('metadata','?')}")
print(f"Impostos disponíveis: {list(taxes.keys())}")
print(f"Entradas por imposto: {N_TAX}")

# ── INCONSISTÊNCIA 1: Dimensão ────────────────────────────────────────────────
print()
print("=" * 65)
print("INCONSISTÊNCIA 1 — Dimensão (tax tem 70 entradas vs 67 setores MRIO)")
print("=" * 65)
print(f"  tax_matrix: {N_TAX} entradas por imposto")
print(f"  MRIO v7.0:  67 setores")
diff_dim = N_TAX - 67
print(f"  Diferença:  {diff_dim} entradas a mais")
if diff_dim > 0:
    print(f"  → As últimas {diff_dim} entradas da tax_matrix provavelmente são")
    print(f"    setores extras (impostos importados, ajustes) que NÃO correspondem")
    print(f"    aos 67 setores produtivos da MRIO.")
    # Verificar se as extras são zero
    for tname, tvals in taxes.items():
        extras = tvals[67:]
        non_zero = [v for v in extras if abs(v) > 0.01]
        print(f"  {tname}: extras[67:] = {[round(v,1) for v in extras[:5]]}... "
              f"{'⚠ tem valores!' if non_zero else '✅ todas zero'}")

# ── INCONSISTÊNCIA 2: Ano-base dos valores nominais ───────────────────────────
print()
print("=" * 65)
print("INCONSISTÊNCIA 2 — Ano-base (valores nominais: MIP 2015 vs VBP 2019)")
print("=" * 65)

# VBP nacional MIP 2019 (67 setores)
X_nas = np.load(X_NAS)   # R$ Mi de 2019
print(f"  VBP MIP 2019 (X_nas): total R$ {X_nas.sum():,.0f} Mi  (67 setores)")

# VBP IIOAS 2019 (27 UFs × 68 setores → agregar para BR 67)
vbp_all = np.load(VBP_19)   # (27, 68)
vbp_br68 = vbp_all.sum(axis=0)
vbp_br67 = np.zeros(67)
for ii in range(68):
    mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
    if mi < 67:
        vbp_br67[mi] += vbp_br68[ii]
print(f"  VBP IIOAS 2019 (BR):  total R$ {vbp_br67.sum():,.0f} Mi  (67 setores)")

# Total de receita fiscal na tax_matrix
total_tax = {t: sum(v[:67]) for t, v in taxes.items()}
total_geral = sum(total_tax.values())
print(f"\n  Receita fiscal total na tax_matrix: R$ {total_geral:,.0f} Mi")
print(f"  → Se os valores são de 2015, são ~30-40% menores que 2019 em termos nominais")

# Verificar alinhamento: ICMS/VBP implícito
ICMS = np.array(taxes['ICMS'][:67])
coef_icms_xnas   = np.where(X_nas > 0, ICMS / X_nas, 0)
coef_icms_iioas  = np.where(vbp_br67 > 0, ICMS / vbp_br67, 0)

print(f"\n  Coeficiente ICMS/VBP implícito:")
print(f"    Usando VBP MIP 2019 (X_nas): média={coef_icms_xnas.mean():.4f}  max={coef_icms_xnas.max():.4f}")
print(f"    Usando VBP IIOAS 2019:       média={coef_icms_iioas.mean():.4f}  max={coef_icms_iioas.max():.4f}")

# ── INCONSISTÊNCIA 3: Coeficientes por setor — maiores divergências ───────────
print()
print("=" * 65)
print("INCONSISTÊNCIA 3 — Coeficientes fiscais implícitos por setor (ICMS/VBP)")
print("=" * 65)
print(f"  {'M#':<4} {'Setor':<44} {'VBP_MIP':>10} {'VBP_IIOAS':>10} {'ICMS':>8} {'coef_MIP':>9} {'coef_IIOAS':>10} {'Diff%':>7}")
print("  " + "-" * 107)

diffs = []
for i in range(67):
    lbl = labels[i][:42] if i < len(labels) else f'S{i+1}'
    xm  = X_nas[i]
    xi  = vbp_br67[i]
    ic  = ICMS[i]
    cm  = ic / xm  if xm > 0 else 0
    ci  = ic / xi  if xi > 0 else 0
    dp  = (ci - cm) / cm * 100 if cm > 0 else 0
    diffs.append({'idx': i, 'label': lbl, 'vbp_mip': xm, 'vbp_iioas': xi,
                  'icms': ic, 'coef_mip': cm, 'coef_iioas': ci, 'diff_pct': dp})

# Ordenar por diferença absoluta
diffs.sort(key=lambda x: abs(x['diff_pct']), reverse=True)
for d in diffs[:20]:
    flag = ' ❌' if abs(d['diff_pct']) > 50 else (' ⚠' if abs(d['diff_pct']) > 20 else '')
    print(f"  M{d['idx']+1:02d} {d['label']:<44} {d['vbp_mip']:10,.0f} {d['vbp_iioas']:10,.0f} "
          f"{d['icms']:8,.0f} {d['coef_mip']:9.4f} {d['coef_iioas']:10.4f} {d['diff_pct']:7.1f}%{flag}")

# ── INCONSISTÊNCIA 4: Impacto nas simulações fiscais ─────────────────────────
print()
print("=" * 65)
print("INCONSISTÊNCIA 4 — Impacto nos resultados das simulações fiscais")
print("=" * 65)
# Simular choque Carnaval simples
y = np.zeros(67)
y[64] = 1500; y[45] = 1000; y[46] = 800; y[41] = 400; y[40] = 300

A7 = np.load(BASE / 'output' / 'final' / 'A_mrio_official_v7_0.npy')
rj = 18
B7 = A7[rj*67:(rj+1)*67, rj*67:(rj+1)*67].astype(np.float64)
L7 = np.linalg.inv(np.eye(67) - B7)
x = L7 @ y

# Receita fiscal estimada: coeficientes com VBP_MIP vs VBP_IIOAS
ICMS_arr = np.array(taxes['ICMS'][:67])
rev_mip   = np.sum(np.where(X_nas > 0, ICMS_arr / X_nas, 0) * x)
rev_iioas = np.sum(np.where(vbp_br67 > 0, ICMS_arr / vbp_br67, 0) * x)
print(f"  Impacto ICMS estimado (choque Carnaval R$ 4 bi, RJ):")
print(f"    Usando coef com VBP MIP 2019:   R$ {rev_mip:,.1f} Mi")
print(f"    Usando coef com VBP IIOAS 2019: R$ {rev_iioas:,.1f} Mi")
print(f"    Diferença:                      R$ {rev_iioas - rev_mip:,.1f} Mi  ({(rev_iioas-rev_mip)/rev_mip*100:+.1f}%)")

print()
print("=" * 65)
print("RESUMO DAS INCONSISTÊNCIAS")
print("=" * 65)
n_grandes = sum(1 for d in diffs if abs(d['diff_pct']) > 50)
n_medias  = sum(1 for d in diffs if 20 < abs(d['diff_pct']) <= 50)
n_ok      = sum(1 for d in diffs if abs(d['diff_pct']) <= 20)
print(f"  1. Dimensão: {N_TAX} entradas vs 67 setores → {diff_dim} extras (verificar uso)")
print(f"  2. Valores nominais de MIP 2015: subvaloriza ~30% vs valores 2019")
print(f"  3. Coeficientes fiscais por setor:")
print(f"     Setores com diff > 50%: {n_grandes} (inconsistência crítica)")
print(f"     Setores com diff 20-50%: {n_medias} (inconsistência moderada)")
print(f"     Setores OK (< 20%): {n_ok}")
print(f"  4. Erro estimado no cálculo de ICMS por simulação: "
      f"{(rev_iioas-rev_mip)/rev_mip*100:+.1f}%")
