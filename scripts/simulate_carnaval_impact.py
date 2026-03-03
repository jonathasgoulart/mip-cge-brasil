
import pandas as pd
import numpy as np
import os
import json

def run_carnaval_simulation():
    print("=== SIMULAÇÃO: IMPACTO ECONÔMICO CARNAVAL RIO DE JANEIRO (BASE 2021) ===")
    
    # 1. PATHS
    path_nas = r'C:\Users\jonat\Documents\MIP e CGE\output\Matriz_Nacional_2021_PERFEITA_v3.xlsx'
    path_rj_sintese = r'C:\Users\jonat\Documents\MIP e CGE\output\regional_matrices\MIP_2021_RJ.xlsx'
    path_official_local = r'C:\Users\jonat\Documents\MIP e CGE\output\regional_matrices\A_RIO_LOCAIS_67x67.xlsx'
    path_official_inter = r'C:\Users\jonat\Documents\MIP e CGE\output\regional_matrices\A_RIO_INTER_67x67.xlsx'
    path_emp_coeffs = r'C:\Users\jonat\Documents\MIP e CGE\output\final\emp_coefficients_67x27.npy'
    path_inc_coeffs = r'C:\Users\jonat\Documents\MIP e CGE\output\final\inc_coefficients_67x27.npy'
    path_tax_matrix = r'C:\Users\jonat\Documents\MIP e CGE\data\processed\2021_final\tax_matrix.json'

    # 2. LOAD DATA
    print("Carregando bases e matrizes...")
    # Labels e VBP Nacional (para rates de impostos federais)
    df_sintese_nas = pd.read_excel(path_nas, sheet_name='Sintese_Setorial')
    X_nas = df_sintese_nas['VBP_MM'].values
    
    # VBP RJ (para rates de ICMS)
    df_sintese_rj = pd.read_excel(path_rj_sintese, sheet_name='Sintese')
    X_rj_base = df_sintese_rj['VBP_MM'].values
    
    # Matrizes de Coeficientes Técnicos
    A_local = pd.read_excel(path_official_local, index_col=0).values
    A_inter = pd.read_excel(path_official_inter, index_col=0).values
    
    # Leontief (I - A_local)^-1
    n = 67
    I = np.eye(n)
    L_local = np.linalg.inv(I - A_local)
    
    # Coeficientes Sociais (Emprego e Renda Anualizada)
    e_coeffs = np.load(path_emp_coeffs)
    y_coeffs = np.load(path_inc_coeffs)
    
    # Impostos
    with open(path_tax_matrix, 'r') as f:
        tax_data = json.load(f)['taxes_by_type']
    
    # 3. CALCULAR TAX RATES (Alíquotas Efetivas por Setor)
    def get_rates(tax_values, vbp):
        return np.divide(tax_values, vbp, out=np.zeros_like(vbp), where=vbp!=0)
    
    # Municipais
    iss_rates = get_rates(np.array(tax_data['ISS']), X_nas)
    
    # Estaduais (ICMS) - Usamos o VBP do RJ para refletir melhor a economia local
    icms_rates = get_rates(np.array(tax_data['ICMS']), X_nas) # Proxy nacional se o RJ nao estiver separado no json
    
    # Federais
    pis_rates = get_rates(np.array(tax_data['PIS_PASEP']), X_nas)
    cofins_rates = get_rates(np.array(tax_data['COFINS']), X_nas)
    ipi_rates = get_rates(np.array(tax_data['IPI']), X_nas)
    iof_rates = get_rates(np.array(tax_data['IOF']), X_nas)
    cide_rates = get_rates(np.array(tax_data['CIDE']), X_nas)
    ii_rates = get_rates(np.array(tax_data['II']), X_nas) if 'II' in tax_data else np.zeros(n)
    
    fed_rates_total = pis_rates + cofins_rates + ipi_rates + iof_rates + cide_rates + ii_rates

    # 4. DEFINIR CHOQUE (Gasto Direto do Carnaval)
    # Total: R$ 5.0 Bilhões
    shock_total = 5000.0
    F = np.zeros(n)
    F[45] = 1500.0 # Alojamento (Setor 46 index 45)
    F[46] = 1200.0 # Alimentação (Setor 47 index 46)
    F[64] = 1000.0 # Artes/Cultura (Setor 65 index 64)
    F[40] = 500.0  # Comércio (Setor 41 index 40)
    F[41] = 400.0  # Transp Terrestre (Setor 42 index 41)
    F[43] = 400.0  # Transp Aéreo (Setor 44 index 43)
    
    # 5. CALCULAR IMPACTOS NO RJ
    print("Calculando impactos diretos, indiretos e induzidos (RJ)...")
    X_impact = L_local @ F
    
    jobs_impact = X_impact * e_coeffs
    income_impact = X_impact * y_coeffs
    
    # Impostos
    tax_mun = X_impact * iss_rates
    tax_est = X_impact * icms_rates
    tax_fed = X_impact * fed_rates_total
    
    # Vazamento (Importação de outros estados)
    leakage = A_inter @ X_impact
    
    # 6. AGREGAR RESULTADOS (Setores Simples para o Usuário)
    agg_mapping = [
        (0, 40, "Indústria e Agro"),
        (40, 41, "Comércio"),
        (41, 45, "Transportes e Logística"),
        (45, 47, "Alojamento e Alimentação"),
        (47, 64, "Outros Serviços"),
        (64, 67, "Cultura, Lazer e Pessoal")
    ]
    
    summary_data = []
    for start, end, name in agg_mapping:
        summary_data.append({
            "Setor": name,
            "Producao_MM": np.sum(X_impact[start:end]),
            "Empregos": np.sum(jobs_impact[start:end]),
            "Renda_Anual_MM": np.sum(income_impact[start:end]),
            "Imposto_Fed_MM": np.sum(tax_fed[start:end]),
            "Imposto_Est_MM": np.sum(tax_est[start:end]),
            "Imposto_Mun_MM": np.sum(tax_mun[start:end])
        })
    
    df_summary = pd.DataFrame(summary_data)
    
    # 7. EXIBIÇÃO
    print("\n" + "="*50)
    print("RESULTADOS TOTAIS - CARNAVAL RIO")
    print("="*50)
    print(f"Gasto Direto (Choque): R$ {shock_total:,.2f} Mi")
    print(f"Produção Total Gerada (RJ): R$ {np.sum(X_impact):,.2f} Mi")
    print(f"Multiplicador de Produção: {np.sum(X_impact)/shock_total:.2f}")
    print("-" * 30)
    print(f"Empregos Sustentados: {np.sum(jobs_impact):,.0f}")
    print(f"Massa Salarial Gerada (Ano): R$ {np.sum(income_impact)/1e6:,.2f} Mi")
    print("-" * 30)
    print(f"Arrecadação Federal: R$ {np.sum(tax_fed):,.2f} Mi")
    print(f"Arrecadação Estadual (ICMS): R$ {np.sum(tax_est):,.2f} Mi")
    print(f"Arrecadação Municipal (ISS): R$ {np.sum(tax_mun):,.2f} Mi")
    print(f"Total Impostos Gerados: R$ {np.sum(tax_fed + tax_est + tax_mun):,.2f} Mi")
    print("-" * 30)
    print(f"Vazamento para outros estados: R$ {np.sum(leakage):,.2f} Mi")
    print("="*50)

    # 8. SALVAR
    results = {
        "resumo_setorial": summary_data,
        "totais": {
            "pib_gerado": float(np.sum(X_impact)),
            "empregos": float(np.sum(jobs_impact)),
            "renda_anual_mi": float(np.sum(income_impact)/1e6),
            "tax_fed": float(np.sum(tax_fed)),
            "tax_est": float(np.sum(tax_est)),
            "tax_mun": float(np.sum(tax_mun))
        }
    }
    
    with open('output/impacto_carnaval_rj_2021.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    df_summary.to_csv('output/impacto_carnaval_rj_detalhado.csv', index=False, sep=';', decimal=',')
    print(f"\nArquivos salvos no diretório 'output/'.")

if __name__ == "__main__":
    run_carnaval_simulation()
