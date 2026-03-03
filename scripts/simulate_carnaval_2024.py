import numpy as np
import os
import json

def simulate_carnaval():
    print("="*70)
    print("SIMULAÇÃO: IMPACTO ECONÔMICO DO CARNAVAL 2024 - RIO DE JANEIRO")
    print("="*70)
    
    final_dir = 'output/final'
    inter_dir = 'output/intermediary'
    output_dir = 'output'
    
    # 1. Load Rio de Janeiro MRIO Matrix
    path_A = os.path.join(final_dir, 'A_Rio_de_Janeiro.npy')
    if not os.path.exists(path_A):
        print("ERROR: Rio MRIO matrix not found.")
        print("Run: python scripts/integrated_pipeline.py first")
        return
    
    A_rio = np.load(path_A)
    n = A_rio.shape[0]  # 67 sectors
    
    # 2. Calculate Leontief Inverse
    print("\n[1/5] Calculating Leontief Inverse...")
    I = np.eye(n)
    L_rio = np.linalg.inv(I - A_rio)
    print(f"      Matrix dimension: {n}x{n}")
    
    # 3. Define Economic Shock (Final Demand in Million R$)
    # Carnival 2024 estimates: ~R$ 6 Billion direct injection
    print("\n[2/5] Defining Carnival Economic Shock...")
    y = np.zeros(n)
    
    # Directly impacted sectors (based on Riotur/Sebrae estimates)
    y[64] = 2000  # Arts, Culture, Entertainment (Parades, Blocos)
    y[45] = 1500  # Accommodation (Hotels 95% occupancy)
    y[46] = 1200  # Food Services (Bars, restaurants, street vendors)
    y[41] = 600   # Land Transport (Buses, taxis, ride-sharing)
    y[40] = 500   # Retail Trade (Costumes, accessories, beverages)
    y[42] = 200   # Air Transport (Domestic tourism flights)
    
    direct_injection = np.sum(y)
    print(f"      Direct spending: R$ {direct_injection:,.0f} Million")
    
    # 4. Calculate Production Impact
    print("\n[3/5] Computing Production Multipliers...")
    x_total = L_rio @ y
    total_production = np.sum(x_total)
    multiplier = total_production / direct_injection
    
    print(f"      Total production impact: R$ {total_production:,.0f} Million")
    print(f"      Production multiplier: {multiplier:.3f}x")
    
    # 5. Calculate Employment Impact
    print("\n[4/5] Estimating Employment Generation...")
    coeff_path = os.path.join(os.path.dirname(inter_dir), 'final', 'emp_coefficients_67x27.npy')
    if os.path.exists(coeff_path):
        e = np.load(coeff_path)
    else:
        # Fallback coefficients (jobs per million R$ of output)
        e = np.full(n, 8.0)  # Conservative avg: 8 jobs/M R$
        print("      [WARNING] Using fallback employment coefficients")
    
    jobs_by_sector = e * x_total
    total_jobs = np.sum(jobs_by_sector)
    
    print(f"      Total jobs created: {total_jobs:,.0f} positions")
    print(f"      Jobs per R$ 1M invested: {total_jobs/direct_injection:.1f}")
    
    # 6. Calculate Tax Revenue (Disaggregated)
    print("\n[5/5] Computing Tax Revenue (Disaggregated by Type)...")
    tax_path = os.path.join(output_dir, 'tax_data.json')
    
    if os.path.exists(tax_path):
        with open(tax_path, 'r') as f:
            tax_data = json.load(f)
        
        # Calculate taxes by type
        tax_revenue = {}
        tax_totals = 0
        
        for tax_type, coef_list in tax_data['coef_by_type'].items():
            coef = np.array(coef_list)
            revenue = np.sum(coef * x_total)
            tax_revenue[tax_type] = revenue
            tax_totals += revenue
        
        print(f"      Total tax revenue: R$ {tax_totals:,.2f} Million")
        print(f"      Effective tax rate: {tax_totals/total_production*100:.2f}%")
        
    else:
        print("      [WARNING] Tax data not found. Run process_taxes_2021.py")
        tax_revenue = {}
        tax_totals = 0
    
    # === RESULTS SUMMARY ===
    print("\n" + "="*70)
    print("RESULTADOS - IMPACTO TOTAL DO CARNAVAL 2024 NO RIO")
    print("="*70)
    
    print(f"\n💰 IMPACTO ECONÔMICO (PIB)")
    print(f"   Gasto Direto (Turistas + Produção):  R$ {direct_injection:>10,.0f} Milhões")
    print(f"   Impacto Total na Produção:           R$ {total_production:>10,.0f} Milhões")
    print(f"   Multiplicador de Produção:           {multiplier:>10.2f}x")
    
    print(f"\n👷 EMPREGO")
    print(f"   Total de Postos Gerados:             {total_jobs:>10,.0f} vagas")
    print(f"   Empregos por R$ 1M investido:        {total_jobs/direct_injection:>10.1f} vagas")
    
    if tax_totals > 0:
        print(f"\n💵 ARRECADAÇÃO TRIBUTÁRIA (Desagregada)")
        print(f"   Total Arrecadado:                    R$ {tax_totals:>10,.2f} Milhões")
        print(f"\n   Detalhamento por Tipo:")
        
        # Sort by revenue
        sorted_taxes = sorted(tax_revenue.items(), key=lambda x: x[1], reverse=True)
        for tax_type, revenue in sorted_taxes:
            pct = (revenue/tax_totals*100) if tax_totals > 0 else 0
            print(f"      {tax_type:12s}: R$ {revenue:>8,.2f} M ({pct:>5.1f}%)")
    
    # Top 10 Sectors by Output
    print(f"\n📊 TOP 10 SETORES BENEFICIADOS (Produção)")
    print("-" * 70)
    top_indices = np.argsort(x_total)[-10:][::-1]
    
    sector_names = {
        64: "Artes, Cultura e Entretenimento",
        45: "Alojamento (Hotéis)",
        46: "Alimentação (Bares/Restaurantes)",
        41: "Transporte Terrestre",
        40: "Comércio Varejista",
        42: "Transporte Aéreo",
        57: "Serviços Adm. (Segurança/Limpeza)",
        53: "Serviços Financeiros",
        52: "Atividades Imobiliárias",
        37: "Energia Elétrica",
        18: "Refino de Petróleo (Combustíveis)",
        35: "Bebidas"
    }
    
    for idx in top_indices:
        nome = sector_names.get(idx, f"Setor {idx}")
        producao = x_total[idx]
        vagas = jobs_by_sector[idx]
        print(f"  {nome:42s}: R$ {producao:>8,.1f} M | {vagas:>7,.0f} vagas")
    
    print("\n" + "="*70)
    print("FONTE: Modelo MRIO 27 UFs (2021) calibrado com CTB/Receita Federal")
    print("="*70)
    
    # Save results
    results = {
        "event": "Carnaval Rio 2024",
        "direct_injection_M": float(direct_injection),
        "total_production_M": float(total_production),
        "multiplier": float(multiplier),
        "total_jobs": float(total_jobs),
        "total_taxes_M": float(tax_totals),
        "taxes_by_type": {k: float(v) for k, v in tax_revenue.items()},
        "top_sectors": {
            sector_names.get(idx, f"Sector {idx}"): {
                "production_M": float(x_total[idx]),
                "jobs": float(jobs_by_sector[idx])
            } for idx in top_indices
        }
    }
    
    results_path = os.path.join(output_dir, 'carnaval_impact_results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em: {results_path}")

if __name__ == "__main__":
    simulate_carnaval()
