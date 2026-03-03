
import pandas as pd
import numpy as np
import json
import os

def run():
    print("=== GERANDO MATRIZ DE INSUMO-PRODUTO V3 (OCES - RIO) ===")
    
    # 1. Carregar Dados Nacionais (Table 11: CI)
    path_ci = 'data/processed/mip_2015/11.csv'
    path_vbp = 'data/processed/mip_2015/01.csv' # Para pegar o VBP total
    
    df_ci = pd.read_csv(path_ci, skiprows=3)
    df_vbp = pd.read_csv(path_vbp, skiprows=1)
    
    # 2. Mapeamento de Atividades (Colunas 3 a 69)
    # 0-66 index inside the slice
    ACT_GROUPS = {
        "Audiovisual & Mídia": [47, 48], # IDs 48, 49
        "Artes & Espetáculos": [64],     # ID 65
        "Tecnologia & Software": [50],   # ID 51
        "Turismo & Lazer": [45, 46],     # IDs 46, 47
        "Indústria": list(range(3, 40)), 
        "Agropecuária": [0, 1, 2],
    }
    defined_act = []
    for v in ACT_GROUPS.values(): defined_act.extend(v)
    ACT_GROUPS["Demais Serviços"] = [i for i in range(67) if i not in defined_act]
    
    # 3. Mapeamento de Produtos (Linhas 1 a 110 aprox)
    # Vamos usar padrões de string nos labels da Col 1 para agrupar produtos
    # Isso é mais robusto que chutes de índices.
    PRODUCT_MAP = {} # row_index -> group_name
    
    group_keywords = {
        "Audiovisual & Mídia": ["cinematogr", "rdio", "televis", "edio", "livros", "jornais"],
        "Artes & Espetáculos": ["artes", "cultura", "esporte", "recrea"],
        "Tecnologia & Software": ["desenvolvimento de sistemas", "servios de informao"],
        "Turismo & Lazer": ["alojamento", "alimentao"],
        "Agropecuária": ["agricultura", "pecuria", "florestal", "pesca"],
        "Indústria": ["extrao", "fabricao", "produo de ferro", "eletricidade", "gua", "construo"]
    }
    
    for i in range(1, 128): # Olhar até a linha 128 para pegar Artes e Serviços Pessoais
        label = str(df_ci.iloc[i, 1]).lower()
        matched = False
        for g, keywords in group_keywords.items():
            if any(k in label for k in keywords):
                PRODUCT_MAP[i] = g
                matched = True
                break
        if not matched:
            PRODUCT_MAP[i] = "Demais Serviços"
            
    # 4. Regionalização (FLQ) usando VAB 2021
    vab_path = 'data/processed/2021_final/vab_regional.json'
    with open(vab_path, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    vab_rj = np.array(vab_regional['RJ'])
    vab_nas = np.zeros(67)
    for v in vab_regional.values(): vab_nas += np.array(v)
    
    delta = 0.3
    lambda_rj = (np.log2(1 + (np.sum(vab_rj) / np.sum(vab_nas)))) ** delta
    slq = (vab_rj / np.sum(vab_rj)) / (vab_nas / np.sum(vab_nas))
    
    # Matriz A_nas Nacional (P x A)
    # Activities start at index 2 in 11.csv (indices 2 to 68 = 67 cols)
    A_nas = df_ci.iloc[1:111, 2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values
    
    # X_nas (VBP Atividades)
    # Activities start at index 7 in 01.csv (indices 7 to 73 = 67 cols)
    mask = df_vbp.iloc[:, 0].astype(str).str.contains("Total", case=False, na=False)
    X_nas = df_vbp[mask].iloc[0, 7:74].apply(pd.to_numeric, errors='coerce').fillna(0).values
    
    # Regionalizar A_rj (P x A)
    A_rj = A_nas * lambda_rj # Simples ajuste regional (Ciso)
            
    # 5. Agregação Final (7x7)
    group_names = ["Audiovisual & Mídia", "Artes & Espetáculos", "Tecnologia & Software", "Turismo & Lazer", "Indústria", "Agropecuária", "Demais Serviços"]
    
    # Pesos VBP Rio
    vab_ratio = np.divide(vab_rj, vab_nas, out=np.zeros_like(vab_rj), where=vab_nas!=0)
    X_rj = X_nas * vab_ratio
    
    # Z_rj = A_rj * X_rj
    Z_rj = A_rj * X_rj[None, :]
    
    matrix_Z_7x7 = np.zeros((7, 7))
    for r_idx, r_name in enumerate(group_names):
        for c_idx, c_name in enumerate(group_names):
            # Filtrar linhas (Produtos) do grupo R
            row_indices = [i-1 for i, g in PRODUCT_MAP.items() if g == r_name and i-1 < Z_rj.shape[0]]
            # Filtrar colunas (Atividades) do grupo C
            col_indices = ACT_GROUPS[c_name]
            
            if row_indices and col_indices:
                matrix_Z_7x7[r_idx, c_idx] = Z_rj[np.ix_(row_indices, col_indices)].sum()

    # Matriz A_7x7
    matrix_A_7x7 = np.zeros((7, 7))
    for c_idx, c_name in enumerate(group_names):
        col_indices = ACT_GROUPS[c_name]
        vbp_macro = X_rj[col_indices].sum()
        if vbp_macro > 0:
            matrix_A_7x7[:, c_idx] = matrix_Z_7x7[:, c_idx] / vbp_macro

    # 6. Exportar
    df_A = pd.DataFrame(matrix_A_7x7, index=group_names, columns=group_names)
    df_Z = pd.DataFrame(matrix_Z_7x7, index=group_names, columns=group_names)
    
    path_out = 'output/Matriz_Insumo_Produto_Criativa_RJ_v3.xlsx'
    with pd.ExcelWriter(path_out) as writer:
        df_A.to_excel(writer, sheet_name='Coeficientes_A')
        df_Z.to_excel(writer, sheet_name='Fluxos_Z_M_RS')
        
    print(f"Sucesso! Gerada v3 em {path_out}")
    print("\n--- Visualização Tecnologia & Software (V3) ---")
    print(df_A.loc[["Tecnologia & Software"]])

if __name__ == "__main__":
    run()
