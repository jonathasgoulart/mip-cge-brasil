"""
Teste rápido do demand_shock.py atualizado (v7.0 + VBP IIOAS 2019).
Simula Carnaval do RJ e compara: com spillover e sem spillover.
"""
import sys, os
sys.path.insert(0, r'C:\Users\jonat\Documents\MIP e CGE')
sys.stdout.reconfigure(encoding='utf-8')

from api.simulators.demand_shock import run_demand_shock

# Choque Carnaval RJ
SHOCKS_CARNAVAL = {
    "64": 1500,  # Artes/Cultura/Espetáculos
    "45": 1000,  # Alojamento
    "46": 800,   # Alimentação
    "41": 400,   # Transporte terrestre
    "40": 300,   # Comércio
}

print("=" * 60)
print("TESTE 1: Simulação RJ sem spillover (bloco regional v7.0)")
print("=" * 60)
r1 = run_demand_shock(region='RJ', shocks=SHOCKS_CARNAVAL,
                      agg_level='detailed', require_spillover=False)
s1 = r1['summary']
print(f"  Injeção direta:        R$ {s1['direct_injection']:,.0f} Mi")
print(f"  Produção total:        R$ {s1['total_production']:,.0f} Mi")
print(f"  Multiplicador:         {s1['multiplier']:.3f}")
print(f"  Empregos gerados:      {s1['total_jobs']:,.0f} postos")

print()
print("=" * 60)
print("TESTE 2: Simulação RJ COM spillover (MRIO v7.0 completa)")
print("=" * 60)
r2 = run_demand_shock(region='RJ', shocks=SHOCKS_CARNAVAL,
                      agg_level='detailed', require_spillover=True)
s2 = r2['summary']
print(f"  Injeção direta:        R$ {s2['direct_injection']:,.0f} Mi")
print(f"  Produção total:        R$ {s2['total_production']:,.0f} Mi")
print(f"  Multiplicador:         {s2['multiplier']:.3f}")
print(f"  Empregos gerados:      {s2['total_jobs']:,.0f} postos")
print(f"  Spillover p/ outros:   R$ {s2['spillover_production']:,.0f} Mi")
print()
print("  Top 5 estados que recebem spillover:")
for sp in r2['spillover'][:5]:
    print(f"    {sp['state']}: R$ {sp['production']:,.1f} Mi | {sp['jobs']:,.0f} empregos")

print()
print("=" * 60)
print("COMPARATIVO v6.1 vs v7.0 (multiplicador de produção RJ)")
print("=" * 60)
# Forçar v6.1 temporariamente
import numpy as np
from pathlib import Path
BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
UFS = ['RO','AC','AM','RR','PA','AP','TO','MA','PI','CE','RN','PB',
       'PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF']
N_S = 67; RJ = 18
for ver, fname in [('v6.1', 'A_mrio_official_v6_1.npy'), ('v7.0', 'A_mrio_official_v7_0.npy')]:
    A = np.load(BASE / 'output' / 'final' / fname)
    B = A[RJ*N_S:(RJ+1)*N_S, RJ*N_S:(RJ+1)*N_S].astype(np.float64)
    L = np.linalg.inv(np.eye(N_S) - B)
    # Choque igual ao usado acima
    y = np.zeros(N_S)
    idx_map = {64: 1500, 45: 1000, 46: 800, 41: 400, 40: 300}
    for i, v in idx_map.items():
        y[i] = v
    x = L @ y
    print(f"  {ver}: mult={x.sum()/y.sum():.3f}  |  prod total R$ {x.sum():,.0f} Mi  |  "
          f"dif vs v7: {(x.sum()-0)/1:.0f}")
