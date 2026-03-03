
import json
import numpy as np

def run():
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('--- CARGA TRIBUTÁRIA ATUAL (MATRIZ) ---')
    
    taxes = data['taxes_by_type']
    target_keys = ['ICMS', 'IPI', 'ISS', 'PIS_PASEP', 'COFINS', 'II', 'IOF', 'CIDE']
    
    total_x = sum(data['production_X'])
    total_tax_all = sum(data['taxes_total_abs']) # Sum of all domestic taxes calibrated
    
    # Load VAB to calculate GDP
    try:
        vab = np.load('output/intermediary/VAB_nacional.npy')
        total_vab = np.sum(vab)
    except:
        # Fallback if NPY missing (Official IBGE 2015 VAB ~ 5.03T)
        print("Warning: VAB_nacional.npy not found using fallback.")
        total_vab = 5036000.0 # R$ 5.0T
        
    # GDP (Market Prices) = VAB (Basic) + Taxes on Products
    total_gdp = total_vab + total_tax_all
    
    print(f'Total Output (X):  R$ {total_x/1e6:,.2f} Trillion')
    print(f'Total VAB:         R$ {total_vab/1e6:,.2f} Trillion')
    print(f'Total Tax (Prod):  R$ {total_tax_all/1e3:,.2f} Billion')
    print(f'Total GDP (Est):   R$ {total_gdp/1e6:,.2f} Trillion')
    print(f'Overall Burden (Tax/GDP): {(total_tax_all/total_gdp)*100:.2f}%')
    
    print('\n--- DETALHAMENTO POR TRIBUTO ---')
    print(f"{'Tributo':<10} | {'Valor (R$ Bi)':<15} | {'Part. (%)':<10} | {'% do PIB':<15}")
    print("-" * 60)
    
    check_sum = 0.0
    
    for k in target_keys:
        if k in taxes:
            val = sum(taxes[k])
            share = (val / total_tax_all) * 100
            burden = (val / total_gdp) * 100
            check_sum += val
            
            print(f"{k:<10} | {val/1e3:<15.2f} | {share:<10.1f} | {burden:<15.2f}")
    
    print("-" * 60)
    print(f"Check Sum: R$ {check_sum/1e3:,.2f} Bi ({(check_sum/total_tax_all)*100:.1f}%)")

if __name__ == "__main__":
    run()
