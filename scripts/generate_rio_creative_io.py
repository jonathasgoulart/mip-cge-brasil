
import json
import numpy as np
import pandas as pd
import os

def run():
    print("=== GERANDO MATRIZ DE INSUMO-PRODUTO (RIO - ECONOMIA CRIATIVA) ===")
    
    # 1. Carregar Matriz de Coeficientes Nacional (A_nas)
    # Usaremos os CSVs da MIP 2015 processados
    ci_path = 'data/processed/mip_2015/05.csv'
    vbp_path = 'data/processed/mip_2015/01.csv'
    
    ci_nacional = pd.read_csv(ci_path, skiprows=3)
    vbp_nacional = pd.read_csv(vbp_path, skiprows=3)
    
    # Z (Consumo Intermediário) e X (VBP)
    Z_nas = ci_nacional.iloc[:67, 3:70].apply(pd.to_numeric, errors='coerce').fillna(0).values
    
    # Extract VBP from footer correctly
    mask = vbp_nacional.iloc[:, 0].astype(str).str.contains("Total", case=False, na=False)
    vbp_footer = vbp_nacional[mask].iloc[0]
    X_nas = vbp_footer.iloc[3:70].apply(pd.to_numeric, errors='coerce').fillna(0).values
    
    A_nas = np.divide(Z_nas, X_nas, out=np.zeros_like(Z_nas, dtype=float), where=X_nas!=0)

    # 2. Carregar VAB Regional (2021 Final)
    vab_path = 'data/processed/2021_final/vab_regional.json'
    with open(vab_path, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
        
    # Calcular VAB Total Nacional (pela soma das UFs)
    vab_rj = np.array(vab_regional['RJ'])
    vab_nas_total = np.zeros(67)
    for uf, vec in vab_regional.items():
        vab_nas_total += np.array(vec)

    # 3. Regionalização para Rio de Janeiro via FLQ
    delta = 0.3
    sum_rj = np.sum(vab_rj)
    sum_nas = np.sum(vab_nas_total)
    
    # Lambda (Fator de escala regional)
    lambda_rj = (np.log2(1 + (sum_rj / sum_nas))) ** delta
    
    # SLQ (Quocientes de Localização)
    slq = (vab_rj / sum_rj) / (vab_nas_total / sum_nas)
    slq[np.isnan(slq)] = 0.0
    slq[np.isinf(slq)] = 1.0

    # Gerar A_rj (Coeficientes Regionais)
    A_rj = np.zeros_like(A_nas)
    for i in range(67):
        for j in range(67):
            if slq[j] == 0:
                flq = 0
            else:
                flq = (slq[i] / slq[j]) * lambda_rj
            # O coeficiente regional é o nacional ajustado por FLQ (limite de 1)
            A_rj[i, j] = A_nas[i, j] * min(1, flq)

    # 4. Agregação Setorial (7 Grupos Criativos)
    groups = {
        "Audiovisual & Mídia": [47, 48], # IDs 48, 49
        "Artes & Espetáculos": [64],     # ID 65
        "Tecnologia & Software": [50],   # ID 51
        "Turismo & Lazer": [45, 46],     # IDs 46, 47
        "Indústria": list(range(3, 40)), 
        "Agropecuária": [0, 1, 2],
        "Demais Serviços": [i for i in range(67) if i not in [47,48,64,50,45,46,0,1,2] and i not in range(3, 40)]
    }
    
    group_names = list(groups.keys())
    matrix_A_7x7 = np.zeros((7, 7))
    
    # Estimar o VBP Regional (X_rj)
    vab_ratio = np.divide(vab_rj, vab_nas_total, out=np.zeros_like(vab_rj), where=vab_nas_total!=0)
    X_rj = X_nas * vab_ratio
    
    # Fluxos Intermediários Estimados (Z_rj)
    Z_rj = A_rj * X_rj[None, :] 
    
    for row_idx, row_name in enumerate(group_names):
        for col_idx, col_name in enumerate(group_names):
            rows = groups[row_name]
            cols = groups[col_name]
            
            # Soma dos fluxos (Consumo do setor J proveniente do setor I)
            flow = Z_rj[np.ix_(rows, cols)].sum()
            # VBP total do macro-setor comprador (coluna)
            vbp_sum = X_rj[cols].sum()
            
            if vbp_sum > 0:
                matrix_A_7x7[row_idx, col_idx] = flow / vbp_sum
            else:
                matrix_A_7x7[row_idx, col_idx] = 0

    # 5. Exportar Matriz A (Coeficientes Técnicos)
    df_A = pd.DataFrame(matrix_A_7x7, index=group_names, columns=group_names)
    
    # Também exportar a Matriz Z (Fluxos em Milhões de R$) para clareza
    matrix_Z_7x7 = np.zeros((7, 7))
    for row_idx, row_name in enumerate(group_names):
        for col_idx, col_name in enumerate(group_names):
            rows = groups[row_name]
            cols = groups[col_name]
            matrix_Z_7x7[row_idx, col_idx] = Z_rj[np.ix_(rows, cols)].sum()
            
    df_Z = pd.DataFrame(matrix_Z_7x7, index=group_names, columns=group_names)

    output_path = 'output/Matriz_Insumo_Produto_Criativa_RJ_v2.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        df_A.to_excel(writer, sheet_name='Coeficientes_Tecnicos_A')
        df_Z.to_excel(writer, sheet_name='Fluxos_Z_Milhoes_RS')
        
    print(f"Sucesso! Matriz salva em: {output_path}")
    print("\n--- Visualização da Matriz de Coeficientes Técnicos (A) ---")
    print(df_A.round(4))

if __name__ == "__main__":
    run()
