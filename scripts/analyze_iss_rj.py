
import json
import numpy as np
import os
import csv

def analyze_iss():
    # Load Tax Data
    try:
        with open('output/tax_data.json', 'r') as f:
            tax_data = json.load(f)
            
        coefs = np.array(tax_data['coef_tax_domestic'])
        X = np.array(tax_data['production_X'])
        taxes = np.array(tax_data['taxes_domestic_abs']) # Calibrated Absolute Taxes
        
    except Exception as e:
        print(f"Error loading tax data: {e}")
        return

    # Load Sector Names to filter Services
    # Assuming standard MIP 67 arrangement
    path_names = 'data/processed/mip_2015/05.csv'
    names = []
    with open(path_names, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 4: continue
            if i >= 4+67: break
            names.append(row[1])

    print("\n--- ANALISE DE ISS (SERVIÇOS) ---")
    
    service_indices = []
    service_taxes = 0.0
    service_output = 0.0
    
    # Heuristic: Services usually start after Construction (Sector ~35-40?)
    # Let's looking for keywords "Serviço", "Comércio", "Transporte", "Educação", "Saúde"
    # Or usually sector 41+ in MIP 67?
    
    print("\nDetalhamento Setores de Serviços (Top 10 Carga):")
    
    sector_data = []
    
    for i, name in enumerate(names):
        is_service = False
        n_u = name.upper()
        # Common service keywords excluding Utilities/Construction if needed.
        # ISS applies to Services list. 
        # Excludes: Agriculture, Industry, Construction (ISS? sometimes), Utilities (ICMS mostly? Water/Energy is ICMS).
        # We will scan for typical service sectors.
        
        if any(x in n_u for x in ["SERVIÇO", "COMÉRCIO", "TRANSPORTE", "ALIMENTAÇÃO", "FINANCEIRO", "IMOBILIÁRIO", "ALUGUEL", "ADMINISTRAÇÃO", "EDUCAÇÃO", "SAÚDE", "ARTES", "DOMÉSTICO", "INFORMÁTICA", "P&D"]):
             is_service = True
             
        # Manual adjustment for MIP 67
        # 01-03 Agro
        # 04-05 Extractive
        # 06-34 Transformation Ind
        # 35-39 Utilities/Construction (Energy, Water, Waste, Constr) -> Eletricidade (ICMS). Construction (ISS).
        # 40+ Trade/Transport/Services
        
        # Checking index logic (Approximate)
        if i >= 39: # Trade starts around 40
            is_service = True
            
        # Refine: Energy (35) is ICMS. Water (36) is mixed. Construction (39) is ISS.
        if i == 39: is_service = True 
        
        if is_service:
            service_indices.append(i)
            service_taxes += taxes[i]
            service_output += X[i]
            
            rate = (taxes[i]/X[i])*100 if X[i]>0 else 0
            sector_data.append((name, taxes[i], X[i], rate))

    # Sort by Rate
    sector_data.sort(key=lambda x: x[3], reverse=True)
    
    for s in sector_data[:10]:
         print(f"{s[0][:40]}... | Tax: {s[1]:,.0f} | Rate: {s[3]:.2f}%")
         
    avg_rate = (service_taxes / service_output)*100 if service_output > 0 else 0
    
    print(f"\nTotal Serviço Taxes (Proxy ISS): {service_taxes:,.2f}")
    print(f"Total Serviço Output: {service_output:,.2f}")
    print(f"Média Ponderada (Carga Tributária de Serviços): {avg_rate:.2f}%")
    
    print("\nNOTE: O modelo aplica esta taxa média nacionalmente.")
    print("Para o Rio de Janeiro, a base de cálculo é o VAB de Serviços do estado.")

if __name__ == "__main__":
    analyze_iss()
