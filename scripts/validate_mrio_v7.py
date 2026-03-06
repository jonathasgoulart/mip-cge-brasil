"""
Validação completa da MRIO v7.0: multiplicadores por UF e por setor RJ.
"""
import numpy as np, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE  = Path(r'C:\Users\jonat\Documents\MIP e CGE')
OUT   = BASE / 'output' / 'final'
CW    = BASE / 'output' / 'crosswalk'

A_v7  = np.load(OUT / 'A_mrio_official_v7_0.npy').astype(np.float64)
A_v6  = np.load(OUT / 'A_mrio_official_v6_1.npy').astype(np.float64)

labels_path = BASE / 'output' / 'intermediary' / 'sector_labels.txt'
with open(labels_path, encoding='utf-8') as f:
    labels = [l.strip() for l in f if l.strip()]

UFS = ['RO','AC','AM','RR','PA','AP','TO','MA','PI','CE','RN','PB',
       'PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF']

N_S  = 67
N_UF = 27

# ── Validação global ─────────────────────────────────────────────────────────
print('=== VALIDACAO GLOBAL ===')
print(f'v7.0 shape: {A_v7.shape}')
print(f'v7.0 max coef: {A_v7.max():.4f}')
cs = A_v7.sum(axis=0)
print(f'v7.0 max soma de coluna: {cs.max():.4f}  |  colunas >= 1: {(cs>=1).sum()}')

# ── Multiplicadores por UF ───────────────────────────────────────────────────
print()
print(f"{'UF':<5} {'v6.1':>9} {'v7.0':>9} {'Var%':>7}")
print('-' * 33)
I = np.eye(N_S)
mv7_list, mv6_list = [], []
for u in range(N_UF):
    s0, s1 = u*N_S, (u+1)*N_S
    B7 = A_v7[s0:s1, s0:s1]
    B6 = A_v6[s0:s1, s0:s1]
    det7 = np.linalg.det(I - B7)
    det6 = np.linalg.det(I - B6)
    m7 = np.linalg.inv(I - B7).sum(axis=0).mean() if det7 > 1e-10 else float('nan')
    m6 = np.linalg.inv(I - B6).sum(axis=0).mean() if det6 > 1e-10 else float('nan')
    var = (m7-m6)/m6*100 if m6 > 0 else 0
    mv7_list.append(m7); mv6_list.append(m6)
    print(f"{UFS[u]:<5} {m6:9.3f} {m7:9.3f} {var:7.1f}%")

mv7_arr = np.array(mv7_list); mv6_arr = np.array(mv6_list)
var_br = (mv7_arr.mean() - mv6_arr.mean()) / mv6_arr.mean() * 100
print('-' * 33)
print(f"{'MEDIA':<5} {mv6_arr.mean():9.3f} {mv7_arr.mean():9.3f} {var_br:7.1f}%")

# ── Detalhe por setor para RJ ────────────────────────────────────────────────
rj = 18
s0, s1 = rj*N_S, (rj+1)*N_S
L7 = np.linalg.inv(I - A_v7[s0:s1, s0:s1])
L6 = np.linalg.inv(I - A_v6[s0:s1, s0:s1])
m7 = L7.sum(axis=0)
m6 = L6.sum(axis=0)
dp = (m7 - m6) / m6 * 100

print()
print('=== DETALHE RJ: Multiplicadores por setor ===')
print(f"{'M#':>3} {'Setor':<45} {'v6.1':>7} {'v7.0':>7} {'Var%':>7}")
print('-' * 67)
for i in range(N_S):
    lbl = labels[i][:43] if i < len(labels) else f'Setor {i+1}'
    flag = ' ***' if abs(dp[i]) > 30 else (' **' if abs(dp[i]) > 15 else '')
    print(f"M{i+1:02d} {lbl:<45} {m6[i]:7.3f} {m7[i]:7.3f} {dp[i]:7.1f}%{flag}")
print('-' * 67)
print(f"{'Média RJ':<49} {m6.mean():7.3f} {m7.mean():7.3f} {dp.mean():7.1f}%")

# Salvar para uso em simulações
result = {
    "mrio_version": "v7.0",
    "source": "IIOAS_BRUF_2019 MIIP SS",
    "mult_rj_mean_v6": float(m6.mean()),
    "mult_rj_mean_v7": float(m7.mean()),
    "change_pct": float(dp.mean()),
}
with open(CW / 'validation_v7.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print('\n[OK] Validacao completa.')
