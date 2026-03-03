
import pandas as pd
import numpy as np
import os

def extract_consumption_shares():
    csv_path = r'C:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\02.csv'
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

    # Household consumption is at index 73 (based on previous inspection)
    # 67 sectors are in rows 4 to 70
    cons = []
    for i in range(4, 71):
        val = parse_smart(df.iloc[i, 73])
        cons.append(val)
        
    cons = np.array(cons)
    total_cons = np.sum(cons)
    
    if total_cons == 0:
        print("Erro: Total de consumo extraído é zero!")
        return
        
    shares = cons / total_cons
    
    output_path = r'C:\Users\jonat\Documents\MIP e CGE\output\intermediary\household_consumption_shares.npy'
    np.save(output_path, shares)
    
    print(f"Total Consumo Extraído: {total_cons:,.2f}")
    print(f"Vetor de shares salvo em {output_path}")
    print(f"Top 3 setores em consumo: {np.argsort(shares)[-3:][::-1]}")

if __name__ == "__main__":
    extract_consumption_shares()
