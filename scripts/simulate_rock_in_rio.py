
import pandas as pd
import numpy as np
import os
import json

def run_rock_in_rio_simulation():
    print("=== SIMULAÇÃO: IMPACTO ECONÔMICO ROCK IN RIO (BASE 2021/2019) ===")
    
    # 1. LOAD MATRICES
    path_nas = 'output/Matriz_Nacional_2021_PERFEITA_v3.xlsx'
    path_rj = 'output/regional_matrices/MIP_2021_RJ.xlsx'
    path_official_local = 'output/regional_matrices/A_RIO_LOCAIS_67x67.xlsx'
    path_official_inter = 'output/regional_matrices/A_RIO_INTER_67x67.xlsx'
    path_coeffs = 'output/final/emp_coefficients_67x27.npy'
    
    # 3. LOAD DATA
    df_labels = pd.read_excel(path_nas, sheet_name='Sintese_Setorial')
    labels = df_labels['Setor'].tolist()
    VBP_nas = df_labels['VBP_MM'].values
    
    # Load Tax Components
    with open('data/processed/2021_final/tax_matrix.json', 'r') as f:
        tax_types = json.load(f)['taxes_by_type']
    
    iss_nas = np.array(tax_types['ISS'])
    # ISS rate per VBP (national proxy)
    iss_rates = np.divide(iss_nas, VBP_nas, out=np.zeros_like(iss_nas), where=VBP_nas!=0)
    
    # Load RJ VBP and Hybrid ICMS
    df_rj = pd.read_excel(path_rj, sheet_name='Sintese')
    X_rj_base = df_rj['VBP_MM'].values
    
    with open('data/processed/2021_final/tax_matrix_hybrid_by_state.json', 'r') as f:
        icms_rj_abs = np.array(json.load(f)['RJ'])
    
    icms_rates_rj = np.divide(icms_rj_abs, X_rj_base, out=np.zeros_like(icms_rj_abs), where=X_rj_base!=0)
    
    A_local = pd.read_excel(path_official_local, index_col=0).values
    A_inter = pd.read_excel(path_official_inter, index_col=0).values
    e_coeffs = np.load(path_coeffs)
    
    n = 67
    I = np.eye(n)
    Leontief_local = np.linalg.inv(I - A_local)
    
    # 4. DEFINE SHOCK (F) - R$ 2.0 Billion
    shock_total = 2000.0 
    F = np.zeros(n)
    F[64], F[45], F[46], F[40], F[41], F[50] = shock_total*0.4, shock_total*0.2, shock_total*0.15, shock_total*0.1, shock_total*0.1, shock_total*0.05
    
    # 5. CALCULATE IMPACTS
    X_impact_rj = Leontief_local @ F
    
    # Jobs
    jobs_rj = X_impact_rj * e_coeffs
    
    # Taxes Breakdown
    icms_impact = X_impact_rj * icms_rates_rj
    iss_impact = X_impact_rj * iss_rates
    total_tax = np.sum(icms_impact) + np.sum(iss_impact)
    
    # 6. AGGREGATE TO 10 SECTORS
    # 1: Agro, 2: Ind Alim, 3: Ind Transf, 4: Utilidades, 5: Const, 6: Com, 7: Transp, 8: Aloj/Alim, 9: Serv Pro/Fin/TI, 10: Artes/Outros
    agg_mapping = [
        (0,3, "Agropecuária e Extração"),
        (3,7, "Extração e Mineração"),
        (7,20, "Indústria de Alimentos e Refino"),
        (20,37, "Outras Indústrias"),
        (37,39, "Utilidades Públicas"),
        (39,40, "Construção Civil"),
        (40,41, "Comércio"),
        (41,45, "Transportes e Logística"),
        (45,47, "Alojamento e Alimentação"),
        (47,64, "Serviços Profissionais e TI"),
        (64,67, "Cultura, Lazer e Pessoais")
    ]
    
    summary = []
    for start, end, name in agg_mapping:
        summary.append({
            "Setor": name,
            "Impacto_Producao_MM": np.sum(X_impact_rj[start:end]),
            "Empregos_Gerados": np.sum(jobs_rj[start:end]),
            "ICMS_MM": np.sum(icms_impact[start:end]),
            "ISS_MM": np.sum(iss_impact[start:end]),
            "Vazamento_Outros_Estados_MM": np.sum((A_inter @ X_impact_rj)[start:end])
        })
        
    df_summary = pd.DataFrame(summary)
    
    # 7. RESULTS
    print(f"\nChoque Inicial: R$ {shock_total:,.0f} Mi")
    print(f"Impacto Total Produção RJ: R$ {np.sum(X_impact_rj):,.2f} Mi")
    print(f"Total Empregos Sustentados: {np.sum(jobs_rj):,.0f}")
    print(f"\n--- IMPACTO FISCAL ROCK IN RIO ---")
    print(f"ICMS Gerado (Estado): R$ {np.sum(icms_impact):,.2f} Mi")
    print(f"ISS Gerado (Municípios): R$ {np.sum(iss_impact):,.2f} Mi")
    print(f"Arrecadação Total: R$ {total_tax:,.2f} Mi")

    # Save to JSON for report
    results = {
        "resumo_setorial": summary,
        "totais": {
            "choque": shock_total,
            "producao_total_rj": float(np.sum(X_impact_rj)),
            "icms_rj": float(np.sum(icms_impact)),
            "iss_rj": float(np.sum(iss_impact)),
            "arrecadacao_total_rj": float(total_tax),
            "multiplicador": float(np.sum(X_impact_rj)/shock_total),
            "empregos": float(np.sum(jobs_rj)),
            "vazamento_brasil": float(np.sum(A_inter @ X_impact_rj))
        }
    }
    
    with open('output/impacto_rock_in_rio_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    df_summary.to_excel('output/impacto_rock_in_rio_detalhado.xlsx', index=False)
    print("\nResultados salvos em 'output/impacto_rock_in_rio_results.json'")

if __name__ == "__main__":
    run_rock_in_rio_simulation()
