"""
Recalcula multiplicadores IIOAS × MRIO v6.1 com VBP real.
Valores na MIIP SS sao fluxos em R$ Mi — confirma pelo VBP extraido da Producao.
"""
import numpy as np, json, sys, openpyxl
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
IIOAS_FILE = BASE / 'data' / 'IIOAS_BRUF_2019.xlsx'
MRIO_FILE  = BASE / 'output' / 'final' / 'A_mrio_official_v6_1.npy'
CW_FILE    = BASE / 'output' / 'crosswalk' / 'crosswalk_iioas_mrio67.json'
VBP_FILE   = BASE / 'output' / 'crosswalk' / 'vbp_iioas_rj.npy'
OUT_DIR    = BASE / 'output' / 'crosswalk'

N_S   = 68
N_S67 = 67
RJ_IDX = 18   # 0-indexed

# ── 1. Crosswalk ─────────────────────────────────────────────────────────────
with open(CW_FILE, encoding='utf-8') as f:
    cw = json.load(f)
iioas_to_mrio = {}
for row in cw['crosswalk']:
    ii = row['iioas_idx'] - 1
    mi = row['mrio67_idx'] - 1
    if ii not in iioas_to_mrio:
        iioas_to_mrio[ii] = mi

# ── 2. VBP do RJ da aba Produção ─────────────────────────────────────────────
vbp_rj = np.load(VBP_FILE)
print(f"VBP RJ carregado: {N_S} setores, total R$ {vbp_rj.sum():,.0f} Mi")
print(f"Agro (S01): R$ {vbp_rj[0]:,.1f} Mi | Petróleo (S05): R$ {vbp_rj[4]:,.1f} Mi")

# ── 3. Extrair bloco RJ×RJ da MIIP SS ────────────────────────────────────────
print("\nLendo bloco RJ (68×68) da MIIP SS...")
wb = openpyxl.load_workbook(IIOAS_FILE, read_only=True, data_only=True)
ws = wb[wb.sheetnames[6]]

rj_r_s = 6 + 18 * N_S + 1
rj_r_e = rj_r_s + N_S - 1
rj_c_s = 4 + 18 * N_S + 1
rj_c_e = rj_c_s + N_S - 1

Z_rj = np.zeros((N_S, N_S), dtype=np.float64)
for i, row in enumerate(ws.iter_rows(min_row=rj_r_s, max_row=rj_r_e,
                                      min_col=rj_c_s, max_col=rj_c_e,
                                      values_only=True)):
    for j, v in enumerate(row):
        try:
            Z_rj[i, j] = float(v)
        except:
            pass
wb.close()

print(f"Bloco RJ lido. Z sum={Z_rj.sum():.2f} | max={Z_rj.max():.4f}")
print(f"  → Valores muito pequenos = já são coeficientes? min={Z_rj[Z_rj>0].min():.6f}")

# Verificação: se max < 2 provavelmente são coeficientes; se > 100 são fluxos
IS_COEFF = Z_rj.max() < 2.0
print(f"  → Interpretação: {'COEFICIENTES (A direta)' if IS_COEFF else 'FLUXOS em R$ Mi (Z)'}")

if IS_COEFF:
    # Os valores já são coeficientes técnicos — usar diretamente como A
    A_rj_iioas = Z_rj.copy()
    print("  → Usando Z_rj diretamente como matriz A (coeficientes)")
else:
    # São fluxos — dividir pelo VBP
    print("  → Convertendo para coeficientes usando VBP real")
    with np.errstate(divide='ignore', invalid='ignore'):
        A_rj_iioas = np.where(vbp_rj > 0, Z_rj / vbp_rj, 0.0)

# Verificar estabilidade: máximo de colunas
col_sums = A_rj_iioas.sum(axis=0)
print(f"  Soma de colunas de A: min={col_sums.min():.3f} max={col_sums.max():.3f}")
print(f"  Colunas com soma >= 1 (instável): {(col_sums >= 1).sum()}")

# ── 4. Calcular multiplicadores IIOAS (68×68) ──────────────────────────────
I68 = np.eye(N_S)
IminA = I68 - A_rj_iioas
det = np.linalg.det(IminA)
print(f"\ndet(I-A) IIOAS RJ = {det:.4f} {'(OK)' if det > 0 else '(SINGULAR!)'}")

if det > 1e-10:
    L_rj_iioas = np.linalg.inv(IminA)
    mult_iioas = L_rj_iioas.sum(axis=0)
    print(f"Multiplicadores IIOAS68: min={mult_iioas.min():.3f} max={mult_iioas.max():.3f}")
else:
    print("ERRO: Matriz singular. Usando pseudoinversa.")
    L_rj_iioas = np.linalg.pinv(IminA)
    mult_iioas = L_rj_iioas.sum(axis=0)

# ── 5. Agregar para 67 setores via crosswalk ────────────────────────────────
mult_iioas_67 = np.zeros(N_S67)
counts = np.zeros(N_S67, dtype=int)
for ii, mi in iioas_to_mrio.items():
    mult_iioas_67[mi] += mult_iioas[ii]
    counts[mi] += 1
for mi in range(N_S67):
    if counts[mi] > 1:
        mult_iioas_67[mi] /= counts[mi]

# ── 6. Multiplicadores MRIO v6.1 (bloco RJ) ──────────────────────────────
A_mrio = np.load(MRIO_FILE)
s0, s1 = RJ_IDX * N_S67, (RJ_IDX + 1) * N_S67
A_rj_mrio = A_mrio[s0:s1, s0:s1].astype(np.float64)
I67 = np.eye(N_S67)
L_rj_mrio = np.linalg.inv(I67 - A_rj_mrio)
mult_mrio  = L_rj_mrio.sum(axis=0)
print(f"\nMultiplicadores MRIO67: min={mult_mrio.min():.3f} max={mult_mrio.max():.3f}")

# ── 7. Comparação ─────────────────────────────────────────────────────────
diff     = mult_mrio - mult_iioas_67
diff_pct = np.where(mult_iioas_67 > 0, diff / mult_iioas_67 * 100, 0.0)

labels_path = BASE / 'output' / 'intermediary' / 'sector_labels.txt'
with open(labels_path, encoding='utf-8') as f:
    labels = [l.strip() for l in f if l.strip()]

print()
print(f"{'M#':>3} {'Setor':<45} {'IIOAS':>8} {'MRIOv6':>8} {'Diff%':>7}")
print("-" * 75)
for i in range(N_S67):
    lbl = labels[i][:43] if i < len(labels) else f"Setor {i+1}"
    flag = " ***" if abs(diff_pct[i]) > 30 else (" **" if abs(diff_pct[i]) > 15 else ("  !" if abs(diff_pct[i]) > 5 else ""))
    print(f"M{i+1:02d} {lbl:<45} {mult_iioas_67[i]:8.3f} {mult_mrio[i]:8.3f} {diff_pct[i]:7.1f}%{flag}")
print("-" * 75)

# Estatísticas
print(f"\n=== RESUMO ===")
print(f"  Média multiplicador IIOAS: {mult_iioas_67.mean():.3f}")
print(f"  Média multiplicador MRIO:  {mult_mrio.mean():.3f}")
print(f"  |Diff%| média:            {np.abs(diff_pct).mean():.1f}%")
print(f"  Setores |diff| > 30%:     {(np.abs(diff_pct) > 30).sum()}")
print(f"  Setores |diff| 15-30%:    {((np.abs(diff_pct) > 15) & (np.abs(diff_pct) <= 30)).sum()}")
print(f"  Setores |diff| 5-15%:     {((np.abs(diff_pct) > 5) & (np.abs(diff_pct) <= 15)).sum()}")
print(f"  Setores |diff| < 5%:      {(np.abs(diff_pct) < 5).sum()}")

# Salvar resultados
results = []
for i in range(N_S67):
    lbl = labels[i] if i < len(labels) else f"Setor {i+1}"
    results.append({
        "mrio67_idx": i + 1,
        "label": lbl,
        "mult_iioas": round(float(mult_iioas_67[i]), 4),
        "mult_mrio_v61": round(float(mult_mrio[i]), 4),
        "diff_abs": round(float(diff[i]), 4),
        "diff_pct": round(float(diff_pct[i]), 2),
        "divergence": "alta" if abs(diff_pct[i]) > 30 else ("media" if abs(diff_pct[i]) > 15 else ("baixa" if abs(diff_pct[i]) > 5 else "ok")),
    })

out = OUT_DIR / 'mult_comparison_rj_final.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump({"is_coeff": bool(IS_COEFF), "results": results}, f, ensure_ascii=False, indent=2)
print(f"\nResultados salvos: {out}")
