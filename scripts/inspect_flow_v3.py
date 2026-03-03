
import pandas as pd
import numpy as np

def run():
    print("=== INSPECTING V3 FLOW MATRIX (Z) ===")
    df = pd.read_excel('output/Matriz_Insumo_Produto_Criativa_RJ_v3.xlsx', sheet_name='Fluxos_Z_M_RS', index_col=0)
    print(df)
    
    print("\nRow Sums (Output of sector in R$ M):")
    print(df.sum(axis=1))
    
    print("\nCol Sums (Input into sector in R$ M):")
    print(df.sum(axis=0))

if __name__ == "__main__":
    run()
