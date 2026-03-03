
import json
import numpy as np
import pandas as pd
import os

def run():
    print("=== GERANDO RELATÓRIO COMPLETO: CARGA POR SETOR (2021) ===")
    
    # Paths
    vab_path = 'output/intermediary/VAB_nacional.npy'
    tax_path = 'output/tax_data.json'
    labels_path = 'output/intermediary/sector_labels.txt'
    
    # 1. Load Data
    try:
        vab = np.load(vab_path)
        print(f"VAB Carregado (Total): R$ {np.sum(vab)/1e3:,.1f} Bi")
    except Exception as e:
        print(f"Erro VAB: {e}")
        return

    with open(tax_path, 'r', encoding='utf-8') as f:
        tax_data = json.load(f)
        
    with open(labels_path, 'r', encoding='latin1') as f:
        sectors = [l.strip() for l in f if l.strip()]
        
    # 2. Calculate Domestic Tax per Sector
    taxes_types = tax_data['taxes_by_type']
    dom_keys = ['ICMS', 'IPI', 'ISS', 'PIS_PASEP', 'COFINS', 'IOF', 'CIDE']
    
    tax_matrix = np.zeros(67)
    
    for k in dom_keys:
        if k in taxes_types:
            tax_matrix += np.array(taxes_types[k])
            
    print(f"Impostos Domésticos (Total): R$ {np.sum(tax_matrix)/1e3:,.1f} Bi")
    
    # 3. Build DataFrame
    data = []
    for i in range(67):
        s_name = sectors[i] if i < len(sectors) else f"Setor {i}"
        v = vab[i]
        t = tax_matrix[i]
        burden = (t / v) * 100 if v > 0 else 0.0
        
        data.append({
            "ID": i+1,
            "Setor": s_name,
            "VAB (R$ Mi)": v,
            "Impostos (R$ Mi)": t,
            "Carga (%)": burden
        })
        
    df = pd.DataFrame(data)
    
    # 4. Export to CSV
    csv_path = 'output/carga_setorial_completa_2021_v2.csv'
    df.to_csv(csv_path, index=False, sep=';', decimal=',')
    print(f"CSV salvo em: {csv_path}")
    
    # 5. Export to Markdown (for Report)
    md_path = 'output/relatorio_carga_setorial_completo_v2.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Relatório Detalhado: Carga Tributária por Setor (Base 2021)\n\n")
        f.write(f"**VAB Total:** R$ {np.sum(vab)/1e6:,.2f} Tri\n")
        f.write(f"**Arrecadação Doméstica:** R$ {np.sum(tax_matrix)/1e6:,.2f} Tri\n")
        f.write(f"**Carga Média Global:** {(np.sum(tax_matrix)/np.sum(vab))*100:.2f}%\n\n")
        f.write("| ID | Setor | VAB (R$ Mi) | Impostos (R$ Mi) | Carga (%) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: |\n")
        
        for row in data:
            f.write(f"| {row['ID']} | {row['Setor']} | {row['VAB (R$ Mi)']:,.0f} | {row['Impostos (R$ Mi)']:,.0f} | **{row['Carga (%)']:.2f}%** |\n")
            
    print(f"Relatório Markdown salvo em: {md_path}")
    
    # Print Top 10 and Bottom 10 to Console
    print("\n--- TOP 10 MAIORES CARGAS ---")
    print(df.sort_values('Carga (%)', ascending=False).head(10)[['Setor', 'Carga (%)']].to_string(index=False))
    
    print("\n--- TOP 10 MENORES CARGAS ---")
    print(df.sort_values('Carga (%)', ascending=True).head(10)[['Setor', 'Carga (%)']].to_string(index=False))

if __name__ == "__main__":
    run()
