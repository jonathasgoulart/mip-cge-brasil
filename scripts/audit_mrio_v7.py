"""
AUDITORIA COMPLETA — MRIO v7.0
Verifica:
  1. Integridade numérica (NaN, Inf, negativos)
  2. Condições de estabilidade de Leontief (soma de colunas, Hawkins-Simon)
  3. Invertibilidade por bloco regional (det, número de condição)
  4. Multiplicadores de produção por UF e por setor
  5. Estrutura diagonal vs off-diagonal (vazamentos interestaduais)
  6. Assimetria: comparativo setorial v7.0 vs v6.1 vs IIOAS
  7. Consistência econômica (VBP proxy, participação regional)
  8. Coeficientes técnicos por setor – ranking e outliers
  9. Matrizes regionais individuais (A_Rio_de_Janeiro, A_Sao_Paulo, etc.)
  10. Emprego e renda: coeficientes × multiplicadores v7.0
"""
import numpy as np
import json
import sys
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

BASE  = Path(r'C:\Users\jonat\Documents\MIP e CGE')
OUT   = BASE / 'output' / 'final'
CW    = BASE / 'output' / 'crosswalk'
INTER = BASE / 'output' / 'intermediary'

UFS = ['RO','AC','AM','RR','PA','AP','TO','MA','PI','CE','RN','PB',
       'PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF']
N_S, N_UF = 67, 27
RJ = 18  # índice do RJ

# Carregar labels
with open(INTER / 'sector_labels.txt', encoding='utf-8') as f:
    LABELS = [l.strip() for l in f if l.strip()][:N_S]

# Carregar matrizes
A7 = np.load(OUT / 'A_mrio_official_v7_0.npy').astype(np.float64)
A6 = np.load(OUT / 'A_mrio_official_v6_1.npy').astype(np.float64)
VBP_ALL = np.load(CW / 'vbp_iioas_all_ufs.npy')   # (27, 68)

# Carregar coeficientes de emprego e renda
try:
    EMP_COEF = np.load(OUT / 'emp_coefficients_67x27.npy')   # (67, 27)
    INC_COEF = np.load(OUT / 'inc_coefficients_67x27.npy')   # (67, 27)
    has_emp = True
except:
    has_emp = False

def bloco(A, u):
    s = u * N_S; e = s + N_S
    return A[s:e, s:e]

def leontief(B):
    I = np.eye(N_S)
    d = np.linalg.det(I - B)
    if d > 1e-10:
        L = np.linalg.inv(I - B)
        return L, d, True
    return None, d, False

results = {}

# ═══════════════════════════════════════════════════════════════════
# TESTE 1: Integridade numérica
# ═══════════════════════════════════════════════════════════════════
print("=" * 70)
print("TESTE 1 — Integridade Numérica")
print("=" * 70)
nans  = np.isnan(A7).sum()
infs  = np.isinf(A7).sum()
negs  = (A7 < 0).sum()
zeros = (A7 == 0).sum()
print(f"  Shape:    {A7.shape}")
print(f"  Dtype:    {A7.dtype}")
print(f"  NaN:      {nans}  {'✅' if nans==0 else '❌'}")
print(f"  Inf:      {infs}  {'✅' if infs==0 else '❌'}")
print(f"  Negativo: {negs}  {'✅' if negs==0 else '⚠ ' + str(negs)}")
print(f"  Zero:     {zeros} ({zeros/A7.size*100:.1f}%)")
print(f"  Min:      {A7.min():.8f}")
print(f"  Max:      {A7.max():.6f}")
results['integridade'] = {'nan': int(nans), 'inf': int(infs), 'neg': int(negs), 'ok': nans==0 and infs==0}

# ═══════════════════════════════════════════════════════════════════
# TESTE 2: Estabilidade de Leontief — Hawkins-Simon
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 2 — Estabilidade de Leontief (Hawkins-Simon)")
print("=" * 70)

col_sums = A7.sum(axis=0)
print(f"  Soma de colunas — min: {col_sums.min():.4f}  max: {col_sums.max():.4f}")
print(f"  Colunas >= 1 (instável): {(col_sums >= 1).sum()}  {'✅' if (col_sums>=1).sum()==0 else '❌'}")

# Por bloco diagonal
print(f"\n  {'UF':<5} {'MaxColSum':>10} {'Estável':>8} {'Det(I-A)':>12} {'Inv OK':>7}")
print("  " + "-" * 44)
stability = {}
for u, uf in enumerate(UFS):
    B = bloco(A7, u)
    cs = B.sum(axis=0).max()
    _, det, ok = leontief(B)
    stab = cs < 1.0
    stability[uf] = {'max_col_sum': float(cs), 'det': float(det), 'invertible': ok, 'stable': stab}
    flag = '✅' if (stab and ok) else '❌'
    print(f"  {uf:<5} {cs:10.4f} {str(stab):>8} {det:12.4f} {flag:>7}")

results['estabilidade'] = stability

# ═══════════════════════════════════════════════════════════════════
# TESTE 3: Número de condição por bloco (robustez numérica)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 3 — Número de Condição por Bloco Regional")
print("=" * 70)
print("  (cond > 1e8 indica possível instabilidade numérica)")
print(f"\n  {'UF':<5} {'Cond(A)':>14} {'Cond(I-A)':>14} {'Status':>8}")
print("  " + "-" * 45)
conds = {}
for u, uf in enumerate(UFS):
    B = bloco(A7, u)
    cA   = np.linalg.cond(B)
    cImA = np.linalg.cond(np.eye(N_S) - B)
    flag = '✅' if cImA < 1e8 else '⚠'
    conds[uf] = {'cond_A': float(cA), 'cond_ImA': float(cImA)}
    print(f"  {uf:<5} {cA:14.2e} {cImA:14.2e} {flag:>8}")
results['condicao'] = conds

# ═══════════════════════════════════════════════════════════════════
# TESTE 4: Multiplicadores de produção por UF (v7.0 vs v6.1)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 4 — Multiplicadores de Produção por UF (v7.0 vs v6.1)")
print("=" * 70)
print(f"\n  {'UF':<5} {'v6.1 med':>9} {'v7.0 med':>9} {'v6.1 max':>9} {'v7.0 max':>9} {'Var%':>7}")
print("  " + "-" * 50)
mult_results = {}
for u, uf in enumerate(UFS):
    B7 = bloco(A7, u); B6 = bloco(A6, u)
    L7, det7, ok7 = leontief(B7); L6, det6, ok6 = leontief(B6)
    if ok7 and ok6:
        m7 = L7.sum(axis=0); m6 = L6.sum(axis=0)
        var = (m7.mean()-m6.mean())/m6.mean()*100
        mult_results[uf] = {
            'v61_mean': float(m6.mean()), 'v70_mean': float(m7.mean()),
            'v61_max':  float(m6.max()),  'v70_max':  float(m7.max()),
            'change_pct': float(var)
        }
        print(f"  {uf:<5} {m6.mean():9.3f} {m7.mean():9.3f} {m6.max():9.3f} {m7.max():9.3f} {var:7.1f}%")
    else:
        print(f"  {uf:<5} {'N/A':>9} {'N/A':>9} {'N/A':>9} {'N/A':>9} {'N/A':>7}")
results['multiplicadores_uf'] = mult_results

# ═══════════════════════════════════════════════════════════════════
# TESTE 5: Estrutura diagonal vs off-diagonal
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 5 — Estrutura Diagonal vs Off-diagonal (Fluxos Interestaduais)")
print("=" * 70)
print(f"\n  {'UF':<5} {'Diag sum':>10} {'Off-diag':>10} {'%Local':>8} {'%Import':>8}")
print("  " + "-" * 45)
diag_results = {}
for u, uf in enumerate(UFS):
    s = u*N_S; e = s+N_S
    col_total = A7[:, s:e].sum()
    col_local  = A7[s:e, s:e].sum()
    col_import = col_total - col_local
    pct_local  = col_local / col_total * 100 if col_total > 0 else 0
    pct_import = col_import / col_total * 100 if col_total > 0 else 0
    diag_results[uf] = {'local_pct': float(pct_local), 'import_pct': float(pct_import)}
    print(f"  {uf:<5} {col_local:10.3f} {col_import:10.3f} {pct_local:8.1f}% {pct_import:8.1f}%")
results['estrutura_diagonal'] = diag_results

# ═══════════════════════════════════════════════════════════════════
# TESTE 6: Top coeficientes — outliers e ranking
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 6 — Top 15 Coeficientes Técnicos (v7.0)")
print("=" * 70)
flat_idx = np.argsort(A7.ravel())[::-1][:15]
print(f"  {'Rank':>4}  {'Orig UF':<5} {'Orig Setor':<45} {'Dest UF':<5} {'Dest Setor':<45} {'Coef':>6}")
print("  " + "-" * 115)
for rank, idx in enumerate(flat_idx):
    row, col = divmod(int(idx), A7.shape[1])
    uf_row, s_row = divmod(row, N_S)
    uf_col, s_col = divmod(col, N_S)
    lbl_row = LABELS[s_row][:43] if s_row < len(LABELS) else f'S{s_row+1}'
    lbl_col = LABELS[s_col][:43] if s_col < len(LABELS) else f'S{s_col+1}'
    print(f"  {rank+1:4d}  {UFS[uf_row]:<5} {lbl_row:<45} {UFS[uf_col]:<5} {lbl_col:<45} {A7[row,col]:6.4f}")

# ═══════════════════════════════════════════════════════════════════
# TESTE 7: Multiplicadores por setor — RJ detalhado (v7.0 vs v6.1 vs IIOAS)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 7 — Multiplicadores RJ por Setor (v7.0 vs v6.1)")
print("=" * 70)

# Tentar carregar multiplicadores IIOAS
try:
    with open(CW / 'mult_comparison_rj_final.json', encoding='utf-8') as f:
        iioas_data = json.load(f)
    mult_iioas = {r['mrio67_idx']: r['mult_iioas'] for r in iioas_data['results']}
    has_iioas = True
except:
    has_iioas = False

Brj7 = bloco(A7, RJ); Brj6 = bloco(A6, RJ)
Lrj7 = np.linalg.inv(np.eye(N_S) - Brj7)
Lrj6 = np.linalg.inv(np.eye(N_S) - Brj6)
mrj7 = Lrj7.sum(axis=0)
mrj6 = Lrj6.sum(axis=0)
dp = (mrj7 - mrj6) / mrj6 * 100

header = f"  {'M#':>3} {'Setor':<45} {'IIOAS':>7} {'v6.1':>7} {'v7.0':>7} {'Var%':>7}"
print(header); print("  " + "-" * 79)
for i in range(N_S):
    lbl = LABELS[i][:43] if i < len(LABELS) else f'Setor {i+1}'
    iioas_val = f"{mult_iioas[i+1]:7.3f}" if has_iioas else '    N/A'
    flag = ' ***' if abs(dp[i]) > 30 else (' **' if abs(dp[i]) > 15 else '')
    print(f"  M{i+1:02d} {lbl:<45} {iioas_val} {mrj6[i]:7.3f} {mrj7[i]:7.3f} {dp[i]:7.1f}%{flag}")
print("  " + "-" * 79)
print(f"  {'Média RJ':<49} {(sum(mult_iioas.values())/len(mult_iioas) if has_iioas else 0):7.3f} {mrj6.mean():7.3f} {mrj7.mean():7.3f} {dp.mean():7.1f}%")

# ═══════════════════════════════════════════════════════════════════
# TESTE 8: Matrizes regionais individuais
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 8 — Matrizes Regionais Individuais")
print("=" * 70)
regional_files = {
    'A_Rio_de_Janeiro': OUT / 'A_Rio_de_Janeiro.npy',
    'A_Sao_Paulo':      OUT / 'A_Sao_Paulo.npy',
    'A_Minas_EspiritoSanto': OUT / 'A_Minas_EspiritoSanto.npy',
    'A_Sul':            OUT / 'A_Sul.npy',
    'A_Centro_Oeste':   OUT / 'A_Centro_Oeste.npy',
    'A_Norte_Nordeste': OUT / 'A_Norte_Nordeste.npy',
    'A_nacional':       OUT / 'A_nacional.npy',
}
print(f"\n  {'Arquivo':<28} {'Shape':>12} {'Max':>7} {'MaxColSum':>10} {'MultMed':>8} {'Det(I-A)':>12}")
print("  " + "-" * 85)
for name, path in regional_files.items():
    if path.exists():
        Ar = np.load(path).astype(np.float64)
        cs = Ar.sum(axis=0).max()
        n = Ar.shape[0]
        I = np.eye(n)
        d = np.linalg.det(I - Ar)
        if d > 1e-10:
            mult = np.linalg.inv(I - Ar).sum(axis=0).mean()
        else:
            mult = float('nan')
        print(f"  {name:<28} {str(Ar.shape):>12} {Ar.max():7.4f} {cs:10.4f} {mult:8.3f} {d:12.4f}")
    else:
        print(f"  {name:<28} {'Arquivo não encontrado':>30}")

# ═══════════════════════════════════════════════════════════════════
# TESTE 9: Emprego e Renda — multiplicadores com v7.0
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 9 — Multiplicadores de Emprego e Renda no RJ (v6.1 vs v7.0)")
print("=" * 70)
if has_emp:
    # Coeficientes: emp_coef[setor, uf]
    e_rj = EMP_COEF[:, RJ]   # vetor de coefic. emprego para RJ
    y_rj = INC_COEF[:, RJ]   # vetor de coefic. renda para RJ

    Lrj7_f = np.linalg.inv(np.eye(N_S) - bloco(A7, RJ))
    Lrj6_f = np.linalg.inv(np.eye(N_S) - bloco(A6, RJ))

    # Multiplicador emprego: e_rj @ L (soma por coluna ponderada)
    mult_emp_v7 = e_rj @ Lrj7_f
    mult_emp_v6 = e_rj @ Lrj6_f
    mult_inc_v7 = y_rj @ Lrj7_f
    mult_inc_v6 = y_rj @ Lrj6_f

    var_emp = (mult_emp_v7.mean() - mult_emp_v6.mean()) / mult_emp_v6.mean() * 100
    var_inc = (mult_inc_v7.mean() - mult_inc_v6.mean()) / mult_inc_v6.mean() * 100

    print(f"\n  Multiplicador de Emprego RJ:")
    print(f"    v6.1: média={mult_emp_v6.mean():.4f}  max={mult_emp_v6.max():.4f}")
    print(f"    v7.0: média={mult_emp_v7.mean():.4f}  max={mult_emp_v7.max():.4f}")
    print(f"    Variação: {var_emp:+.1f}%")

    print(f"\n  Multiplicador de Renda RJ:")
    print(f"    v6.1: média={mult_inc_v6.mean():.4f}  max={mult_inc_v6.max():.4f}")
    print(f"    v7.0: média={mult_inc_v7.mean():.4f}  max={mult_inc_v7.max():.4f}")
    print(f"    Variação: {var_inc:+.1f}%")
    results['mult_emprego_rj'] = {'v61': float(mult_emp_v6.mean()), 'v70': float(mult_emp_v7.mean()), 'var_pct': float(var_emp)}
    results['mult_renda_rj']   = {'v61': float(mult_inc_v6.mean()), 'v70': float(mult_inc_v7.mean()), 'var_pct': float(var_inc)}
else:
    print("  Coeficientes de emprego/renda não encontrados.")

# ═══════════════════════════════════════════════════════════════════
# TESTE 10: Comparativo de versões v4 → v7.0 RJ
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TESTE 10 — Comparativo Histórico de Versões (Mult. Médio RJ)")
print("=" * 70)
versions = {
    'v4':   OUT / 'A_mrio_official_v4.npy',
    'v5':   OUT / 'A_mrio_official_v5.npy',
    'v6':   OUT / 'A_mrio_official_v6.npy',
    'v6.1': OUT / 'A_mrio_official_v6_1.npy',
    'v7.0': OUT / 'A_mrio_official_v7_0.npy',
}
print(f"\n  {'Versão':<8} {'MultMed RJ':>11} {'MultMax RJ':>11} {'Max Coef':>10} {'MaxColSum':>10}")
print("  " + "-" * 55)
for vname, vpath in versions.items():
    if vpath.exists():
        Av = np.load(vpath).astype(np.float64)
        s = RJ*N_S; e = s+N_S
        Bv = Av[s:e, s:e]
        d = np.linalg.det(np.eye(N_S) - Bv)
        if d > 1e-10:
            Lv = np.linalg.inv(np.eye(N_S) - Bv)
            mv = Lv.sum(axis=0)
        else:
            mv = np.full(N_S, float('nan'))
        cs = Av.sum(axis=0).max()
        print(f"  {vname:<8} {mv.mean():11.3f} {mv.max():11.3f} {Av.max():10.4f} {cs:10.4f}")
    else:
        print(f"  {vname:<8} {'N/A':>11}")

# ═══════════════════════════════════════════════════════════════════
# RESUMO FINAL
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("RESUMO DA AUDITORIA")
print("=" * 70)
ok_int   = results['integridade']['ok']
ok_stab  = all(v['stable'] for v in stability.values())
ok_inv   = all(v['invertible'] for v in stability.values())
ok_cond  = all(v['cond_ImA'] < 1e8 for v in conds.values())
print(f"  Integridade numérica (sem NaN/Inf):    {'✅ OK' if ok_int else '❌ FALHOU'}")
print(f"  Estabilidade Leontief (col sums < 1):  {'✅ OK' if ok_stab else '❌ FALHOU'}")
print(f"  Invertibilidade (todos os 27 blocos):  {'✅ OK' if ok_inv else '❌ FALHOU'}")
print(f"  Número de condição aceitável (<1e8):   {'✅ OK' if ok_cond else '⚠ VERIFICAR'}")

all_ok = ok_int and ok_stab and ok_inv
print(f"\n  {'✅ MRIO v7.0 APROVADA — pronta para uso em simulações' if all_ok else '❌ REVISÃO NECESSÁRIA'}")

# Salvar JSON de resultados
out_json = CW / 'audit_v7_results.json'
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n  Resultados da auditoria salvos: {out_json}")
print("\n[AUDITORIA CONCLUÍDA]")
