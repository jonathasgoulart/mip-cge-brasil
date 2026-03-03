"""
CORREÇÃO: Extração MIP 2015 com linhas CORRETAS

ERRO IDENTIFICADO:
- Estava usando iloc[1:68] = Linhas 5-71 do Excel
- Correto é iloc[2:69] = Linhas 6-72 do Excel

VERIFICAÇÃO:
- [0] deve ser "Agricultura..." não "Pecuária..."
- [39] deve ser "Construção" não "Energia elétrica..."
- [45] deve ser "Alojamento" não "Transporte aéreo"
"""

import pandas as pd
import numpy as np
import json
import os

def run_extraction():
    print("=== EXTRAÇÃO CORRIGIDA: MIP IBGE 2015 (67 SETORES) ===")
    path = 'data/raw/mip_2015_67.xls'
    
    # 1. MATRIZ A (TABELA 14 - SIMÉTRICA D.BN)
    print("Carregando Tabela 14 (Coeficientes Simétricos)...")
    df_14 = pd.read_excel(path, sheet_name='14', skiprows=3)
    
    # CORREÇÃO: Linhas 6-72 do Excel = iloc[2:69] após skiprows=3
    # Colunas C-BQ (67 colunas) = iloc[2:69] 
    A_nas = df_14.iloc[2:69, 2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values
    labels = df_14.iloc[2:69, 1].astype(str).values  # Coluna B
    
    print(f"Setores carregados: {len(labels)}")
    print(f"\nVerificação de labels corretos:")
    print(f"  [0] {labels[0]}")  # Deve ser Agricultura
    print(f"  [1] {labels[1]}")  # Deve ser Pecuária  
    print(f"  [39] {labels[39]}")  # Deve ser Construção
    print(f"  [45] {labels[45]}")  # Deve ser Alojamento

    # 2. VBP NACIONAL 2015 (TABELA 01 - RECURSOS)
    print("\nCarregando Tabela 01 (VBP e Impostos)...")
    df_01 = pd.read_excel(path, sheet_name='01', skiprows=3)
    total_row_mask = df_01.iloc[:, 0].astype(str).str.contains('Total', case=False, na=False)
    vbp_row = df_01[total_row_mask].iloc[0]
    # IMPORTANTE: Verificar se colunas também precisam ajuste
    X_2015 = vbp_row.iloc[7:74].apply(pd.to_numeric, errors='coerce').fillna(0).values

    # 3. CONSUMO INTERMEDIÁRIO TOTAL (TABELA 02 - USOS)
    print("Carregando Tabela 02 (Consumo Intermediário)...")
    df_02 = pd.read_excel(path, sheet_name='02', skiprows=3)
    ci_total_row_mask = df_02.iloc[:, 0].astype(str).str.contains('Total', case=False, na=False)
    ci_total_row = df_02[ci_total_row_mask].iloc[0]
    CI_total_2015 = ci_total_row.iloc[2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values

    # 4. MATRIZ DE IMPORTADOS (TABELA 12)
    print("Carregando Tabela 12 (Coeficientes Importados)...")
    df_12 = pd.read_excel(path, sheet_name='12', skiprows=3)
    A_imp_raw = df_12.iloc[1:111, 2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values
    A_imp = A_imp_raw[:67, :]  # Proxy de agregação 1:1

    # 5. CALCULAR VAB + IMP PRODUÇÃO 2015
    VAB_plus_2015 = X_2015 - CI_total_2015

    # 6. SALVAR COMPONENTES BASE
    os.makedirs('output/intermediary', exist_ok=True)
    base_data = {
        "labels": labels.tolist(),
        "X_2015": X_2015.tolist(),
        "CI_total_2015": CI_total_2015.tolist(),
        "VAB_plus_2015": VAB_plus_2015.tolist(),
        "A_matrix": A_nas.tolist(),
        "A_imp_matrix": A_imp.tolist()
    }
    
    with open('output/intermediary/perfectionist_base_2015.json', 'w', encoding='utf-8') as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
    
    print("\nSucesso! Componentes extraídos para output/intermediary/perfectionist_base_2015.json")
    print(f"\nVerificação final:")
    print(f"  Labels: {len(labels)}")
    print(f"  Matriz A: {A_nas.shape}")
    print(f"  X_2015: {len(X_2015)}")

if __name__ == "__main__":
    run_extraction()
