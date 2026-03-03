
import pandas as pd
import numpy as np

def run():
    print("=== INSPECTING FLOW MATRIX (Z) FOR CREATIVE ECONOMY ===")
    df = pd.read_excel('output/Matriz_Insumo_Produto_Criativa_RJ_v2.xlsx', sheet_name='Fluxos_Z_Milhoes_RS', index_col=0)
    print(df)
    
    print("\nRow Sums (Output of the sector in R$ M):")
    print(df.sum(axis=1))
    
    print("\nCol Sums (Inputs of the sector in R$ M):")
    print(df.sum(axis=0))

if __name__ == "__main__":
    run()
