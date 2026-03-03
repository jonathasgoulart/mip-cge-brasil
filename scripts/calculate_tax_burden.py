import numpy as np
import json
import os

def run():
    print("--- CÁLCULO DA CARGA TRIBUTÁRIA (IMPOSTOS SOBRE PRODUTOS) ---")
    
    # 1. Carregar Impostos Totais
    tax_path = 'output/tax_data.json'
    taxes_total_abs = 0.0
    if os.path.exists(tax_path):
        with open(tax_path, 'r') as f:
            tdata = json.load(f)
            t_dom = sum(tdata.get('taxes_domestic_abs', []))
            t_imp = sum(tdata.get('taxes_import_abs', []))
            taxes_total_abs = t_dom + t_imp
            print(f"Total Impostos s/ Produtos: R$ {taxes_total_abs:,.2f} M")
    else:
        print("tax_data.json not found.")
        return

    try:
        # 2. Carregar VAB (Prefer direct load)
        vab_path = 'output/intermediary/VAB_nacional.npy'
        total_vab_2015 = 0.0
        
        if os.path.exists(vab_path):
             vab_nas = np.load(vab_path)
             if vab_nas.ndim > 1: vab_nas = vab_nas.flatten()
             total_vab_2015 = np.sum(vab_nas)
             print(f"VAB Total 2015 (Loaded direct): R$ {total_vab_2015:,.2f} M")
        else:
             print("VAB_nacional.npy not found. Trying calculation from X...")
             X_nas = np.load('output/intermediary/X_nacional.npy')
             # Fallback approx: VAB is usually ~50% of X? NO.
             # Let's assume VAB = X - Z.
             # If Z is missing, we are stuck.
             return

        # GDP 2015 = VAB + Impostos (Produtos)
        gdp_2015 = total_vab_2015 + taxes_total_abs
        print(f"PIB 2015 (Preços de Mercado): R$ {gdp_2015:,.2f} M")
        
        if gdp_2015 > 0:
            burden_pct = (taxes_total_abs / gdp_2015) * 100
            print(f"Carga Tributária (Produtos) / PIB: {burden_pct:.2f}%")
        
        print("\n Nota: A carga tributária BRUTA total do Brasil é ~33%, pois inclui Renda e Salários (INSS).")
        print("       Esta matriz calcula apenas a tributação sobre o CONSUMO/PRODUÇÃO.")
        
    except Exception as e:
        print(f"Error calculating VAB: {e}")

if __name__ == "__main__":
    run()
