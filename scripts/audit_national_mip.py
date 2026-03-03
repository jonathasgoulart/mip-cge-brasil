
import pandas as pd
import numpy as np

def run_audit():
    print("=== AUDITORIA DE INTEGRIDADE: MIP NACIONAL 2021 ===")
    
    file_path = 'output/Matriz_Nacional_2021_COMPLETA.xlsx'
    
    # 1. Load Summary
    df = pd.read_excel(file_path, sheet_name='Sintese_Setorial_2021')
    
    # Check for Negatives
    neg_vab = df[df['VAB_MM'] < 0]
    if not neg_vab.empty:
        print(f"ALERTA: Setores com VAB negativo: {neg_vab['Setor'].tolist()}")
    else:
        print("OK: Nenhum VAB negativo encontrado.")
        
    # Check for impossible margins (VAB > VBP)
    impossible_margin = df[df['VAB_MM'] > df['VBP_MM']]
    if not impossible_margin.empty:
        print(f"ALERTA: Setores com VAB > VBP (Impossvel): {impossible_margin['Setor'].tolist()}")
    else:
        print("OK: Todas as margens VAB/VBP esto dentro do limite inferior.")

    # Check for Tax Burdens > 100%
    high_burden = df[df['Carga_Tributaria_Pct'] > 100]
    if not high_burden.empty:
        print("\nSetores com Carga Tributria > 100%:")
        print(high_burden[['Setor', 'Carga_Tributaria_Pct']])
    
    # 2. Check Technical Coefficients (Matriz A)
    df_a = pd.read_excel(file_path, sheet_name='Matriz_Coeficientes_A', index_col=0)
    col_sums = df_a.sum(axis=0)
    
    impossible_coeffs = col_sums[col_sums > 1.0]
    if not impossible_coeffs.empty:
        print(f"\nALERTA CRTICO: Soma da coluna de A > 1.0 (Consome mais que gera):")
        print(impossible_coeffs)
    else:
        print("OK: Todas as colunas de Coeficientes Tcnicos somam < 1.0.")
        print(f"Consumo Intermedirio Mdio: {col_sums.mean()*100:.1f}% da produo.")

    # 3. Check Account Balance
    # VBP should be approx Sum(Z_row) + Final Demand, but here we can check if 
    # VAB + Taxes + Sum(Z_col) == VBP
    df_z = pd.read_excel(file_path, sheet_name='Matriz_Fluxos_Z', index_col=0)
    z_col_sums = df_z.sum(axis=0)
    
    # Identity: VBP_j = Z_sum_col_j + VAB_j + Taxes_j (roughly, depending on import treatment)
    calculated_vbp = z_col_sums.values + df['VAB_MM'].values + df['Total_Impostos_MM'].values
    diff_pct = np.abs(calculated_vbp - df['VBP_MM'].values) / df['VBP_MM'].values * 100
    
    outliers_id = df.loc[diff_pct > 1, 'Setor'].tolist()
    if outliers_id:
        print(f"\nALERTA: Desvio na identidade contbil (VBP != Z_col + VAB + Tax) em {len(outliers_id)} setores.")
        print(f"Exemplos: {outliers_id[:3]}")
    else:
        print("OK: Identidade contbil balanceada (VBP = Fluxos + VAB + Impostos).")

if __name__ == "__main__":
    run_audit()
