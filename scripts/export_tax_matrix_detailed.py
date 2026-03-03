
import json
import numpy as np
import pandas as pd
import os

def run():
    print("=== GERANDO MATRIZ TRIBUTÁRIA DETALHADA (SETOR x IMPOSTO) ===")
    
    # Paths
    tax_path = 'output/tax_data.json'
    vab_path = 'output/intermediary/VAB_nacional.npy'
    labels_path = 'output/intermediary/sector_labels.txt'
    output_csv = 'output/tabela_carga_tributaria_detalhada.csv'
    
    # Load Data
    with open(tax_path, 'r', encoding='utf-8') as f:
        tax_data = json.load(f)
        
    try:
        vab = np.load(vab_path)
    except:
        vab = np.zeros(67) # Should not happen based on context
        
    with open(labels_path, 'r', encoding='latin1') as f:
        sectors = [l.strip() for l in f if l.strip()]
        
    # Prepare DataFrame
    # Columns: Setor, VAB, ICMS, IPI, ISS, PIS, COFINS, II, IOF, CIDE, TOTAL, Carga%
    
    data = {
        "Setor": sectors,
        "VAB_2021": vab
    }
    
    taxes = tax_data['taxes_by_type']
    total_tax_calc = np.zeros(67)
    
    tax_cols = ['ICMS', 'IPI', 'ISS', 'PIS_PASEP', 'COFINS', 'II', 'IOF', 'CIDE']
    
    for tax_name in tax_cols:
        if tax_name in taxes:
            vals = np.array(taxes[tax_name])
            data[tax_name] = vals
            total_tax_calc += vals
        else:
            data[tax_name] = np.zeros(67)
            
    data['TOTAL_IMPOSTOS'] = total_tax_calc
    
    # Calculate Burden
    burden_pct = np.zeros(67)
    non_zero = vab > 0
    burden_pct[non_zero] = (total_tax_calc[non_zero] / vab[non_zero]) * 100
    
    data['CARGA_VAB_PCT'] = burden_pct
    
    df = pd.DataFrame(data)
    
    # Format for display/export
    # (Optional) Rounding
    df_export = df.round(2)
    
    df_export.to_csv(output_csv, index=False, sep=';', encoding='utf-8-sig', decimal=',')
    
    print(f"Arquivo salvo em: {output_csv}")
    print(f"Data Vintage (Ano Base): {tax_data.get('year', 'Unknown')}")
    
    # Preview Top 5 Burden
    print("\nTop 5 Setores por Carga Tributária (% VAB):")
    top5 = df.sort_values('CARGA_VAB_PCT', ascending=False).head(5)
    print(top5[['Setor', 'CARGA_VAB_PCT', 'TOTAL_IMPOSTOS']])

if __name__ == "__main__":
    run()
