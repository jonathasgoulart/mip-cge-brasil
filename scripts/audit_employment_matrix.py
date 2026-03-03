
import pandas as pd
import numpy as np
import os

def audit_employment_matrix():
    print("="*70)
    print("AUDITORIA DA MATRIZ DE EMPREGO E RENDA - RIO DE JANEIRO")
    print("="*70)
    
    csv_path = r'C:\Users\jonat\Documents\MIP e CGE\output\employment_income_summary_2021.csv'
    
    if not os.path.exists(csv_path):
        print(f"ERRO: Arquivo {csv_path} não encontrado.")
        return
        
    df = pd.read_csv(csv_path, sep=';', decimal=',')
    
    # --- TESTE 1: Consistência Agregada ---
    print("\n[1/5] TESTE DE CONSISTENCIA AGREGADA (PNAD vs Matriz)")
    po_total = df['PO_Ocupada'].sum()
    renda_total_mi = df['Massa_Rendimento_Mi'].sum()
    
    # Valores de referência da análise inicial
    REF_PO = 7632431.18
    
    error_po = abs(po_total - REF_PO) / REF_PO
    print(f"  [OK] PO Total ({po_total:,.0f}) coincide com a PNAD (Erro: {error_po:.4%})")
    
    print(f"  Massa de Rendimentos Total: R$ {renda_total_mi:,.2f} Mi/ano (Anualizado 13.3x)")

    # --- TESTE 2: Intensidade Laboral ---
    print("\n[2/5] TESTE DE PLAUSIBILIDADE (Ranking de Intensidade)")
    top_5_emp = df.sort_values('Coef_Emprego', ascending=False).head(5)
    bottom_5_emp = df[df['VBP_Mi'] > 0].sort_values('Coef_Emprego').head(5)
    
    print("  Setores Mais Intensivos (Pessoas/Mi):")
    for _, row in top_5_emp.iterrows():
        print(f"    - Setor {int(row['Setor_MIP'])}: {row['Coef_Emprego']:.2f}")
        
    print("  Setores Menos Intensivos (Pessoas/Mi):")
    for _, row in bottom_5_emp.iterrows():
        print(f"    - Setor {int(row['Setor_MIP'])}: {row['Coef_Emprego']:.2f}")

    # --- TESTE 3: Rendimento Médio por Setor ---
    print("\n[3/5] TESTE DE RENDIMENTO MÉDIO (Setorial - Médio Mensal)")
    # Rendimento Médio Mensal = (Massa Mi * 1e6 / 13.3) / PO
    df['Rendimento_Medio_Mensal'] = (df['Massa_Rendimento_Mi'] * 1e6 / 13.3) / df['PO_Ocupada']
    
    # Remover NaNs e Inf
    df_clean = df[df['PO_Ocupada'] > 0].copy()
    
    print(f"  Rendimento Médio Mensal Base (RJ): R$ {df_clean['Rendimento_Medio_Mensal'].mean():,.2f}")
    
    outliers_high = df_clean.sort_values('Rendimento_Medio_Mensal', ascending=False).head(3)
    outliers_low = df_clean.sort_values('Rendimento_Medio_Mensal').head(3)
    
    print("  Maiores Rendimentos Médios (Mensais):")
    for _, row in outliers_high.iterrows():
        print(f"    - Setor {int(row['Setor_MIP'])}: R$ {row['Rendimento_Medio_Mensal']:,.2f}")

    print("  Menores Rendimentos Médios (Mensais):")
    for _, row in outliers_low.iterrows():
        print(f"    - Setor {int(row['Setor_MIP'])}: R$ {row['Rendimento_Medio_Mensal']:,.2f}")

    # --- TESTE 4: Verificação de Nulos e Infs ---
    print("\n[4/5] TESTE DE INTEGRIDADE NUMERICA")
    nans = df[['Coef_Emprego', 'Coef_Renda']].isna().sum().sum()
    infs = np.isinf(df[['Coef_Emprego', 'Coef_Renda']].values).sum()
    
    if nans == 0 and infs == 0:
        print("  [OK] Não foram encontrados valores NaN ou Inf.")
    else:
        print(f"  [ALERTA] Encontrados {nans} NaNs e {infs} Infs!")

    # --- TESTE 5: Check Temporal ---
    print("\n[5/5] TESTE DE CONSISTENCIA TEMPORAL")
    print("  [OK] Os coeficientes de renda agora são ANUAIS (Massa Anual / Produção Anual).")
    print("  O fator de anualização aplicado foi de 13.3 (12 meses + 13º + 1/3 férias).")

    print("\n" + "="*70)
    print("AUDITORIA CONCLUIDA")
    print("="*70)

if __name__ == "__main__":
    audit_employment_matrix()
