
import pandas as pd
import numpy as np
import sys

# Set encoding to utf-8 for console output to avoid character errors
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
        print(f"ALERTA: Setores com VAB > VBP: {impossible_margin['Setor'].tolist()}")
    else:
        print("OK: Margens VAB/VBP consistentes.")

    # High Burdens
    high_burden = df[df['Carga_Tributaria_Pct'] > 50].sort_values('Carga_Tributaria_Pct', ascending=False)
    print("\nSetores com Carga Tributária > 50%:")
    for _, row in high_burden.iterrows():
        print(f"  - {row['Setor']}: {row['Carga_Tributaria_Pct']:.1f}%")

    # 2. Activity Balance
    # We used A_2015 coefficients. We scaled X_2021 = VAB_2021 / (1 - CI_ratio)
    # So by definition VAB + CI = VBP.
    # We just need to check if CI_ratio was correctly handled.
    df_a = pd.read_excel(file_path, sheet_name='Matriz_Coeficientes_A', index_col=0)
    col_sums = df_a.sum(axis=0)
    
    # Check if sum(A) > 1 (impossible)
    if any(col_sums >= 1.0):
        print("\nERRO: Existem colunas em A que somam >= 1.0!")
        print(col_sums[col_sums >= 1.0])
    else:
        print("\nOK: Matriz A técnica está dentro dos limites (Soma col < 1.0).")

    # 3. Check for Anomalous Employment (Zero jobs)
    zero_jobs = df[df['Empregos_Total'] <= 0]
    if not zero_jobs.empty:
        print(f"\nAVISO: Setores sem empregos reportados: {zero_jobs['Setor'].tolist()}")
    
    print("\n--- RESUMO DOS TOTAIS ---")
    print(f"PIB (VAB Total): R$ {df['VAB_MM'].sum()/1000:.1f} Bi")
    print(f"Tributos Totais: R$ {df['Total_Impostos_MM'].sum()/1000:.1f} Bi")
    print(f"VBP Total: R$ {df['VBP_MM'].sum()/1000:.1f} Bi")
    print(f"Empregos Totais: {df['Empregos_Total'].sum():,.0f}")

if __name__ == "__main__":
    run_audit()
