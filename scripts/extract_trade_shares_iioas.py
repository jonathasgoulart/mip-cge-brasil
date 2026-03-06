"""
Extrai os Trade Shares reais (probabilidades de comércio inter-regional)
a partir da MRIO v7.0 observada e do VBP da IIOAS.

trade_share[r_orig, r_dest, setor] =
    Fluxo do setor de r_orig para r_dest / Total consumido do setor em r_dest

Calculado sobre a demanda intermediária (Z = A * X), que é a proxy canônica
para padrões de comércio no modelo.

Output:
  - trade_shares_iioas_2019.npy: shape (27, 27, 67)
"""
import numpy as np, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
A_MRIO = BASE / 'output' / 'final' / 'A_mrio_official_v7_0.npy'
VBP_UF = BASE / 'output' / 'crosswalk' / 'vbp_iioas_all_ufs.npy'
OUT    = BASE / 'output' / 'final' / 'trade_shares_iioas_2019.npy'
OUT_TXT= BASE / 'output' / 'final' / 'trade_shares_analysis.txt'

N_UFS, N_SEC = 27, 67

print("1. Carregando dados base...")
A_full = np.load(A_MRIO)          # (1809, 1809)
vbp_all68 = np.load(VBP_UF)       # (27, 68)

# Agregar VBP para 67 setores (fusão 40+41 → 40)
vbp_uf67 = np.zeros((N_UFS, N_SEC))
for ii in range(68):
    mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
    if mi < N_SEC:
        vbp_uf67[:, mi] += vbp_all68[:, ii]

# Reconstruir o vetor VBP completo (1809)
X_full = vbp_uf67.flatten()

print("2. Reconstruindo matriz de fluxos intermediários Z (1809x1809)...")
# Z = A * X
# Broadcasting: mult de cada coluna j por X[j]
Z_full = A_full * X_full[np.newaxis, :]

print("3. Consolidando fluxos por par UF-UF e Setor...")
# Z_agg[r_orig, r_dest, setor_i] = sum_j Z[r_orig, i, r_dest, j]
Z_agg = np.zeros((N_UFS, N_UFS, N_SEC))

for r in range(N_UFS):
    for s in range(N_UFS):
        # Bloco Z de r para s: (67x67)
        r0, r1 = r*N_SEC, (r+1)*N_SEC
        s0, s1 = s*N_SEC, (s+1)*N_SEC
        bloco = Z_full[r0:r1, s0:s1]
        
        # O fluxo total do produto i saindo de r para s
        # = soma da linha i dentro do bloco r->s
        Z_agg[r, s, :] = bloco.sum(axis=1)

print("4. Calculando Trade Shares setoriais...")
# Demanda total intermediária no estado s para o produto i 
# (independente de onde veio)
total_demand = Z_agg.sum(axis=0)  # shape (27, 67) --> axis=0 soma sobre 'r'

# trade_shares[r, s, i]
trade_shares = np.zeros((N_UFS, N_UFS, N_SEC))
for r in range(N_UFS):
    # Tratar divisão por zero: se a demanda for 0, share = 0 (ou autarquico local)
    mask = total_demand > 0
    trade_shares[r][mask] = Z_agg[r][mask] / total_demand[mask]
    
    # Se total_demand=0, assumir todo abastecimento local (r=s)
    mask_zero = total_demand == 0
    if r > 0:
        pass # para origens r!=s fica 0
        
# Fix: forced self-sufficiency (r=s) if demand=0
for s in range(N_UFS):
    for i in range(N_SEC):
        if total_demand[s, i] == 0:
            trade_shares[s, s, i] = 1.0

# Validação: a soma sobre 'r' deve dar 1.0 para todo (s, i)
sums = trade_shares.sum(axis=0)
assert np.allclose(sums, 1.0), "Falha na normalização das trade shares"

np.save(OUT, trade_shares)
print(f"\nSalvo: {OUT} (Shape: {trade_shares.shape})")

# --- ANÁLISE BÁSICA ---
labels_path = BASE / 'output' / 'intermediary' / 'sector_labels.txt'
with open(labels_path, encoding='utf-8') as f:
     labels = [l.strip()[:40] for l in f if l.strip()]

UF_NAMES = ['RO','AC','AM','RR','PA','AP','TO','MA','PI','CE','RN','PB',
            'PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF']
RJ_IDX = 18

rep = ["=== ANÁLISE DE DEPENDÊNCIA (TRADE SHARES) - RJ ==="]
rep.append(f"Auto-suficiência Média RJ (diagonal): {trade_shares[RJ_IDX, RJ_IDX, :].mean()*100:.1f}%")
rep.append("\nTop 5 Setores Mais Auto-suficientes do RJ:")
asc = np.argsort(trade_shares[RJ_IDX, RJ_IDX, :])[::-1]
for idx in asc[:5]:
    rep.append(f"  {labels[idx]:40s} : {trade_shares[RJ_IDX, RJ_IDX, idx]*100:5.1f}%")

rep.append("\nTop 5 Setores Mais Dependentes (Mais importados de outras UFs):")
asc2 = np.argsort(trade_shares[RJ_IDX, RJ_IDX, :])
for idx in asc2[:5]:
    share_rj = trade_shares[RJ_IDX, RJ_IDX, idx]
    # Encontrar principal fornecedor
    shares_for_i = trade_shares[:, RJ_IDX, idx]
    best_sup = np.argmax(shares_for_i)
    if best_sup == RJ_IDX:
        # Pega o segundo
        shares_for_i[RJ_IDX] = -1
        best_sup = np.argmax(shares_for_i)
    rep.append(f"  {labels[idx]:40s} : RJ produz {share_rj*100:4.1f}%, Principal: {UF_NAMES[best_sup]} ({trade_shares[best_sup, RJ_IDX, idx]*100:4.1f}%)")

txt = "\n".join(rep)
print(f"\n{txt}")
with open(OUT_TXT, 'w', encoding='utf-8') as f:
    f.write(txt)
