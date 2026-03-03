
import pandas as pd
import numpy as np
import os

def extract_consumption_shares_v2():
    csv_path = r'C:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\06.csv'
    df = pd.read_csv(csv_path)
    
    def parse_smart(s):
        s = str(s).strip()
        if not s or s == 'nan': return 0.0
        if ',' in s and '.' in s: return float(s.replace('.', '').replace(',', '.'))
        if ',' in s: return float(s.replace(',', '.'))
        try:
            return float(s)
        except:
            return 0.0

    # Consumo das famílias is at index 74 in 06.csv
    # Rows for sectors: checking first where they end
    # Based on previous check, rows 4 to 70 should be the 67 sectors.
    
    cons = []
    labels = []
    for i in range(4, 71):
        labels.append(df.iloc[i, 1])
        val = parse_smart(df.iloc[i, 74])
        cons.append(val)
        
    cons = np.array(cons)
    total_cons = np.sum(cons)
    
    if total_cons == 0:
        print("Erro: Total de consumo extraído é zero!")
        return
        
    shares = cons / total_cons
    
    output_path = r'C:\Users\jonat\Documents\MIP e CGE\output\intermediary\household_consumption_shares_67.npy'
    np.save(output_path, shares)
    
    print(f"Total Consumo Extraído: {total_cons:,.2f}")
    print(f"Vetor de shares salvo em {output_path}")
    
    # Print top 10
    top_idx = np.argsort(shares)[-10:][::-1]
    print("\nTop 10 setores em consumo das famílias:")
    for idx in top_idx:
        print(f"{labels[idx]}: {shares[idx]:.4%}")

if __name__ == "__main__":
    extract_consumption_shares_v2()
