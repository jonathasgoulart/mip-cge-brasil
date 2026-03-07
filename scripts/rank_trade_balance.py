import numpy as np, sys
from pathlib import Path

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
A_MRIO = BASE / 'output' / 'final' / 'A_mrio_official_v7_0.npy'
VBP_UF = BASE / 'output' / 'crosswalk' / 'vbp_iioas_all_ufs.npy'

N_UFS, N_SEC = 27, 67
UF_NAMES = ['RO','AC','AM','RR','PA','AP','TO','MA','PI','CE','RN','PB',
            'PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF']

A_full = np.load(A_MRIO)
vbp_all68 = np.load(VBP_UF)

# Rebuild VBP 67
vbp_uf67 = np.zeros((N_UFS, N_SEC))
for ii in range(68):
    mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
    if mi < N_SEC:
        vbp_uf67[:, mi] += vbp_all68[:, ii]

X_full = vbp_uf67.flatten()
Z_full = A_full * X_full[np.newaxis, :]

# Z_agg[orig, dest] = fluxo intermediario total (mi R$)
Z_agg = np.zeros((N_UFS, N_UFS))
for r in range(N_UFS):
    for s in range(N_UFS):
        r0, r1 = r*N_SEC, (r+1)*N_SEC
        s0, s1 = s*N_SEC, (s+1)*N_SEC
        Z_agg[r, s] = Z_full[r0:r1, s0:s1].sum()

results = []
for i in range(N_UFS):
    exports = Z_agg[i, :].sum() - Z_agg[i, i]
    imports = Z_agg[:, i].sum() - Z_agg[i, i]
    saldo = exports - imports  # Exportações Líquidas (Positivo = Exportador Líquido, Negativo = Importador Líquido)
    results.append({
        'uf': UF_NAMES[i],
        'exports': exports,
        'imports': imports,
        'saldo': saldo
    })

# Ordenar por Saldo crescente (Maiores importadores líquidos primeiro - saldo mais negativo)
results.sort(key=lambda x: x['saldo'])

print('--- RANKING DE DEPENDÊNCIA (Maiores Importadores Líquidos Interestaduais) ---')
print('Considera apenas a Demanda Intermediária Produtiva em R$ Milhões Correntes (2019)')
print(f'| Posição | UF |     Importa de outras UFs |     Exporta p/ outras UFs   |  Saldo Líquido  | Perfil')
print('|---------|----|---------------------------|-----------------------------|-----------------|--------')
for idx, r in enumerate(results, 1):
    sinal = '-' if r['saldo'] < 0 else '+'
    saldo_formatado = f"{sinal} R$ {abs(r['saldo']):8,.0f}"
    perfil = 'Importador Líquido' if r['saldo'] < 0 else 'Exportador Líquido'
    print(f"| {idx:7d} | {r['uf']:2s} | R$ {r['imports']:10,.0f} | R$ {r['exports']:10,.0f} | {saldo_formatado:>13s} | {perfil}")
