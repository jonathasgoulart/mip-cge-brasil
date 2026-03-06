"""
Gera tax_matrix_by_state_2019.json com todos os tributos por UF × setor.

Metodologia (sharing factors):
  - ICMS: usa participação regional do tax_matrix_hybrid_by_state.json (2021)
    como proxy estrutural, normalizada pelo total nacional 2019 do tax_matrix_2019.json
  - Tributos federais (IPI, PIS, COFINS, IOF, CIDE, II):
    distribui pelo VBP real de cada UF (vbp_iioas_all_ufs.npy) como proxy
    → mais correto: produção maior = mais tributo federal
  - ISS: usa a mesma participação setorial do ICMS por UF como proxy
    → ISS é municipal, mas a distribuição setorial (serviços) é correlacionada

Pressuposto documentado: a estrutura regional de 2021 é usada como proxy de 2019
(mudança estrutural em 2 anos é pequena; risco COVID documentado).
"""
import numpy as np, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
HYBRID = BASE / 'data' / 'processed' / '2021_final' / 'tax_matrix_hybrid_by_state.json'
TAX19  = BASE / 'data' / 'processed' / '2021_final' / 'tax_matrix_2019.json'
VBP_UF = BASE / 'output' / 'crosswalk' / 'vbp_iioas_all_ufs.npy'
X_NAS  = BASE / 'output' / 'intermediary' / 'X_nas.npy'
OUT    = BASE / 'data' / 'processed' / '2021_final' / 'tax_matrix_by_state_2019.json'

UFS = ['RO','AC','AM','RR','PA','AP','TO','MA','PI','CE','RN','PB',
       'PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF']
N_S = 67; N_UF = 27

# ── Carregar dados ──────────────────────────────────────────────────────────
with open(HYBRID, encoding='utf-8') as f:
    hybrid = json.load(f)

with open(TAX19, encoding='utf-8') as f:
    tax19 = json.load(f)['taxes_by_type']

# VBP IIOAS por UF (27×68) → agregar para 67 setores
vbp_all68 = np.load(VBP_UF)   # (27, 68)
vbp_uf67  = np.zeros((N_UF, N_S))
for ii in range(68):
    mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
    if mi < N_S:
        vbp_uf67[:, mi] += vbp_all68[:, ii]

# VBP total por UF (escalar)
vbp_total_uf = vbp_uf67.sum(axis=1)

# ── 1. ICMS: sharing factors a partir do hybrid 2021 ────────────────────────
print("Calculando sharing factors ICMS (via hybrid 2021)...")
icms_2021 = np.zeros((N_UF, N_S))
for u, uf in enumerate(UFS):
    arr = hybrid.get(uf, [0]*N_S)
    icms_2021[u] = np.array(arr[:N_S])

# Share de cada UF em cada setor (soma = 1 por setor)
# share[u, s] = icms_2021[u,s] / Σ_u icms_2021[u,s]
total_icms_br_21 = icms_2021.sum(axis=0)  # (67,)
sharing_icms = np.where(total_icms_br_21 > 0,
                         icms_2021 / total_icms_br_21,
                         1.0 / N_UF)  # fallback: igual entre UFs

# Total ICMS por setor em 2019
icms_2019_br = np.array(tax19['ICMS'][:N_S])  # (67,)

# Distribuir ICMS 2019 para cada UF
icms_2019_uf = sharing_icms * icms_2019_br  # (27, 67)

print(f"  Total ICMS 2019 BR: R$ {icms_2019_br.sum():,.0f} Mi")
print(f"  Verificação (soma UFs): R$ {icms_2019_uf.sum():,.0f} Mi")

# ── 2. VBP sharing: compartilhar tributos federais pelo VBP regional ─────────
print("\nCalculando sharing factors federais (via VBP IIOAS 2019)...")
# Share de cada UF em cada setor por VBP
total_vbp_br = vbp_uf67.sum(axis=0)  # (67,)
sharing_vbp = np.where(total_vbp_br > 0,
                        vbp_uf67 / total_vbp_br,
                        1.0 / N_UF)

# ── 3. ISS: usar sharing ICMS (proxy razoável — correlacionado com serviços) ─
sharing_iss = sharing_icms.copy()

# ── 4. Construir result final ─────────────────────────────────────────────────
result = {}

TAX_SHARING = {
    'ICMS':     sharing_icms,
    'ISS':      sharing_iss,      # proxy: mesmo perfil regional que ICMS
    'IPI':      sharing_vbp,      # federal: proporcional ao VBP
    'PIS_PASEP':sharing_vbp,
    'COFINS':   sharing_vbp,
    'IOF':      sharing_vbp,
    'CIDE':     sharing_vbp,
    'II':       sharing_vbp,
}

for u, uf in enumerate(UFS):
    result[uf] = {}
    for tname, sharing in TAX_SHARING.items():
        national_total = np.array(tax19[tname][:N_S])
        uf_vals = sharing[u] * national_total
        result[uf][tname] = [round(v, 4) for v in uf_vals.tolist()]

# ── 5. Validação ──────────────────────────────────────────────────────────────
print("\n=== VALIDAÇÃO: totais por UF e tributo ===")
print(f"  {'UF':<5} {'ICMS':>10} {'ISS':>8} {'PIS':>8} {'COFINS':>10} {'Total':>12}")
print("  " + "-" * 55)
grand_total = 0
for u, uf in enumerate(UFS):
    icms_t = sum(result[uf]['ICMS'])
    iss_t  = sum(result[uf]['ISS'])
    pis_t  = sum(result[uf]['PIS_PASEP'])
    cof_t  = sum(result[uf]['COFINS'])
    total  = icms_t + iss_t + pis_t + cof_t + \
             sum(result[uf]['IPI']) + sum(result[uf]['IOF']) + \
             sum(result[uf]['CIDE']) + sum(result[uf]['II'])
    grand_total += total
    print(f"  {uf:<5} {icms_t:10,.0f} {iss_t:8,.0f} {pis_t:8,.0f} {cof_t:10,.0f} {total:12,.0f}")
print("  " + "-" * 55)
print(f"  {'BR':5} {'Total geral:':>30}  R$ {grand_total:,.0f} Mi")

# ── 6. Metadados e salvar ───────────────────────────────────────────────────
output_data = {
    "metadata": (
        "Matriz fiscal 2019 por UF e setor. "
        "ICMS: sharing factors da tax_matrix_hybrid 2021 (IBGE/CONFAZ), normalizado pelo total 2019. "
        "ISS: proxy via sharing ICMS (correlação setorial serviços). "
        "Tributos federais (IPI, PIS, COFINS, IOF, CIDE, II): proporcional ao VBP regional IIOAS 2019. "
        "Pressuposto: estrutura regional 2021 como proxy de 2019 (mudança < 2 anos). "
        "ATENÇÃO: anos COVID (2020-2021) podem subestimar turismo/cultura."
    ),
    "year": 2019,
    "sharing_source_icms": "tax_matrix_hybrid_by_state.json (2021)",
    "sharing_source_federal": "vbp_iioas_all_ufs.npy (2019)",
    "national_totals_source": "tax_matrix_2019.json (CTB IBGE)",
    "by_state": result
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
print(f"\nSalvo: {OUT}")
print(f"Tamanho: {OUT.stat().st_size/1024:.0f} KB")
