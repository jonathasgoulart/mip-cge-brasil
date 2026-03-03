
import pandas as pd
import numpy as np
import os
import json

def run_carnaval_simulation_v2():
    print("=== SIMULAÇÃO V2: IMPACTO ECONÔMICO CARNAVAL (Modelos Tipo I e II) ===")
    
    # 1. LOAD DATA
    path_nas = r'C:\Users\jonat\Documents\MIP e CGE\output\Matriz_Nacional_2021_PERFEITA_v3.xlsx'
    path_official_local = r'C:\Users\jonat\Documents\MIP e CGE\output\regional_matrices\A_RIO_LOCAIS_67x67.xlsx'
    path_emp_coeffs = r'C:\Users\jonat\Documents\MIP e CGE\output\final\emp_coefficients_67x27.npy'
    path_inc_coeffs = r'C:\Users\jonat\Documents\MIP e CGE\output\final\inc_coefficients_67x27.npy'
    path_cons_shares = r'C:\Users\jonat\Documents\MIP e CGE\output\intermediary\household_consumption_shares_67.npy'
    path_tax_matrix = r'C:\Users\jonat\Documents\MIP e CGE\data\processed\2021_final\tax_matrix.json'

    # Matrizes Básicas
    A_local = pd.read_excel(path_official_local, index_col=0).values
    n = 67
    I = np.eye(n)
    
    # Coeficientes
    e_coeffs = np.load(path_emp_coeffs)
    y_coeffs_raw = np.load(path_inc_coeffs)
    y_coeffs = y_coeffs_raw / 1e6 # Converter R$ p/ Mi R$ -> Adimensional
    h_shares = np.load(path_cons_shares).reshape(-1, 1) # Column vector
    
    # Impostos
    with open(path_tax_matrix, 'r') as f:
        tax_data = json.load(f)['taxes_by_type']
    
    df_sintese_nas = pd.read_excel(path_nas, sheet_name='Sintese_Setorial')
    X_nas = df_sintese_nas['VBP_MM'].values
    
    def get_rates(tax_values, vbp):
        return np.divide(tax_values, vbp, out=np.zeros_like(vbp), where=vbp!=0)
    
    iss_rates = get_rates(np.array(tax_data['ISS']), X_nas)
    icms_rates = get_rates(np.array(tax_data['ICMS']), X_nas)
    pis_rates = get_rates(np.array(tax_data['PIS_PASEP']), X_nas)
    cofins_rates = get_rates(np.array(tax_data['COFINS']), X_nas)
    total_tax_rates = iss_rates + icms_rates + pis_rates + cofins_rates # Simplified total for sum check

    # 2. DEFINIR CHOQUE
    shock_total = 5000.0
    F = np.zeros(n)
    F[45] = 1500.0 # Alojamento
    F[46] = 1200.0 # Alimentação
    F[64] = 1000.0 # Artes/Cultura
    F[40] = 500.0  # Comércio
    F[41] = 400.0  # Transp Terrestre
    F[43] = 400.0  # Transp Aéreo

    # 3. CALCULOS TIPO I (Direto + Indireto)
    L_type1 = np.linalg.inv(I - A_local)
    X_type1 = L_type1 @ F
    
    # 4. CALCULOS TIPO II (Direto + Indireto + Induzido)
    # Propensão a consumir renda laborial localmente (Estimativa: 0.7)
    # Isso desconta: impostos sobre renda, poupança e importação final direta.
    MPC_local = 0.7 
    
    # Matriz Aumentada (Rank-1 update)
    # X = (I - A - mpc * c * v)^-1 * F
    M_induced = MPC_local * (h_shares @ y_coeffs.reshape(1, -1))
    L_type2 = np.linalg.inv(I - A_local - M_induced)
    X_type2 = L_type2 @ F
    
    # 5. RESULTADOS
    def get_metrics(X):
        return {
            "Producao": np.sum(X),
            "Empregos": np.sum(X * e_coeffs),
            "Renda_Mi": np.sum(X * y_coeffs), # Já está em Mi R$
            "Impostos_Mi": np.sum(X * total_tax_rates)
        }
    
    res_t1 = get_metrics(X_type1)
    res_t2 = get_metrics(X_type2)
    
    # 6. EXIBIÇÃO
    print("\n" + "="*60)
    print(f"{'MÉTRICA':<25} | {'TIPO I (S/ Renda)':<15} | {'TIPO II (C/ Renda)':<15}")
    print("-"*60)
    print(f"{'Produção Total (Mi R$)':<25} | {res_t1['Producao']:>15,.2f} | {res_t2['Producao']:>15,.2f}")
    print(f"{'Empregos Sustentados':<25} | {res_t1['Empregos']:>15,.0f} | {res_t2['Empregos']:>15,.0f}")
    print(f"{'Renda Salarial (Mi R$)':<25} | {res_t1['Renda_Mi']:>15,.2f} | {res_t2['Renda_Mi']:>15,.2f}")
    print(f"{'Arrecadação Est. (Mi R$)':<25} | {res_t1['Impostos_Mi']:>15,.2f} | {res_t2['Impostos_Mi']:>15,.2f}")
    print("-" * 60)
    print(f"Multiplicador Efetivo:    | {res_t1['Producao']/shock_total:>15.2f} | {res_t2['Producao']/shock_total:>15.2f}")
    print("="*60)
    
    # Delta (Efeito Renda)
    print(f"\nEfeito Renda Puro (Induzido):")
    print(f"- Geração Extra de Empregos: {res_t2['Empregos'] - res_t1['Empregos']:,.0f}")
    print(f"- Geração Extra de Renda: R$ {res_t2['Renda_Mi'] - res_t1['Renda_Mi']:,.2f} Mi")

if __name__ == "__main__":
    run_carnaval_simulation_v2()
