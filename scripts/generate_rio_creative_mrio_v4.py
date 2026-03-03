
import pandas as pd
import numpy as np

def run_aggregation():
    print("=== AGREGANDO MATRIZ CRIATIVA RJ (V4 - BASE SIMÉTRICA) ===")
    
    path_rj = 'output/regional_matrices/MIP_2021_RJ.xlsx'
    df_z = pd.read_excel(path_rj, sheet_name='Fluxos_Z', index_col=0)
    df_summary = pd.read_excel(path_rj, sheet_name='Sintese')
    
    sectors = df_z.columns.tolist()
    
    # Mapping for 7x7 Aggregation
    mapping = {
        "Audiovisual & Mídia": [47, 48],
        "Artes & Espetáculos": [64],
        "Tecnologia & Software": [50],
        "Turismo & Lazer": [45, 46],
        "Agropecuária": list(range(0, 3)),
        "Indústria": list(range(3, 40)),
        "Demais Serviços": [40, 41, 42, 43, 44, 49, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 65, 66]
    }
    
    # Verify all sectors are mapped
    all_mapped = []
    for s in mapping.values(): all_mapped.extend(s)
    print(f"Setores mapeados: {len(all_mapped)} / 67")

    # Aggregate Flow Matrix Z (7x7)
    group_names = list(mapping.keys())
    Z_agg = np.zeros((7, 7))
    
    for i, row_group in enumerate(group_names):
        for j, col_group in enumerate(group_names):
            row_idxs = mapping[row_group]
            col_idxs = mapping[col_group]
            # Sum sub-matrix
            val = df_z.iloc[row_idxs, col_idxs].values.sum()
            Z_agg[i, j] = val
            
    # Aggregate Production X (7)
    X_nas = df_summary['VBP_MM'].values
    X_agg = np.array([X_nas[idxs].sum() for idxs in mapping.values()])
    
    # Calculate Coeffs A (7x7)
    with np.errstate(divide='ignore', invalid='ignore'):
        A_agg = Z_agg / X_agg[None, :]
        A_agg = np.nan_to_num(A_agg, nan=0.0)
        
    # Save to Excel
    output_file = 'output/Matriz_Insumo_Produto_Criativa_RJ_v4.xlsx'
    df_Z_agg = pd.DataFrame(Z_agg, index=group_names, columns=group_names)
    df_A_agg = pd.DataFrame(A_agg, index=group_names, columns=group_names)
    
    with pd.ExcelWriter(output_file) as writer:
        df_Z_agg.to_excel(writer, sheet_name='Fluxos_Z_Milhoes_RS')
        df_A_agg.to_excel(writer, sheet_name='Coeficientes_Tecnicos_A')
        
    print(f"Sucesso! Matriz Criativa RJ v4 salva em {output_file}")

if __name__ == "__main__":
    run_aggregation()
