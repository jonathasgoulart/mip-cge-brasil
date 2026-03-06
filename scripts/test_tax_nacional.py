"""Teste final: demand_shock Nacional com A_nacional.py."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\jonat\Documents\MIP e CGE')
from api.simulators.demand_shock import run_demand_shock

SHOCKS = {'64': 1500, '45': 1000, '46': 800, '41': 400, '40': 300}

r = run_demand_shock(region='Nacional', shocks=SHOCKS, agg_level='detailed', require_spillover=False)
s = r['summary']

print('=== CARNAVAL NACIONAL - A_nacional.npy + Tax 2019 ===')
print(f'Injecao direta:    R$ {s["direct_injection"]:,.0f} Mi')
print(f'Producao total:    R$ {s["total_production"]:,.0f} Mi')
print(f'Multiplicador:     {s["multiplier"]:.3f}')
print(f'Empregos:          {s["total_jobs"]:,.0f} postos')
print(f'Receita fiscal:    R$ {s["total_tax"]:,.1f} Mi')
print()
print('Detalhe por tributo:')
for t, v in r['fiscal_detail'].items():
    print(f'  {t:<12}: R$ {v:,.1f} Mi')
