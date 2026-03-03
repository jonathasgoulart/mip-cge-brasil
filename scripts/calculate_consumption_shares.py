
import pandas as pd
import numpy as np
import os

def calculate_consumption_shares():
    # 1. Get Sector Prefixes from Columns of 06.csv (Aggregated View)
    path_06 = r'C:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\06.csv'
    df_06 = pd.read_csv(path_06, nrows=3)
    
    # We know from inspection that sectors start at column index 3 and end at 69
    # (Sector 1 at index 3, Sector 67 at index 69)
    # The header row is row 2
    sector_headers = df_06.iloc[2, 3:70].tolist()
    
    prefix_to_idx = {}
    for i, header in enumerate(sector_headers):
        if str(header) != 'nan':
            prefix = str(header)[:4]
            prefix_to_idx[prefix] = i
            
    print(f"Mapped {len(prefix_to_idx)} prefixes to the 67 sectors.")

    # 2. Extract Consumption from 02.csv (127 products)
    path_02 = r'C:\Users\jonat\Documents\MIP e CGE\data\processed\mip_2015\02.csv'
    df_02 = pd.read_csv(path_02)
    
    def parse_smart(s):
        s = str(s).strip()
        if not s or s == 'nan': return 0.0
        if ',' in s and '.' in s: return float(s.replace('.', '').replace(',', '.'))
        if ',' in s: return float(s.replace(',', '.'))
        try:
            return float(s)
        except:
            return 0.0

    # Household consumption is column index 73
    # Product codes are in column index 0, rows 4 to 130
    
    cons_67 = np.zeros(67)
    unmapped_value = 0
    
    for i in range(4, 131):
        full_code = str(df_02.iloc[i, 0]).strip()
        if not full_code or full_code.lower() == 'total':
            break
            
        value = parse_smart(df_02.iloc[i, 73])
        prefix = full_code[:4]
        
        # Mapping logic: check 4-digit prefix
        if prefix in prefix_to_idx:
            idx = prefix_to_idx[prefix]
            cons_67[idx] += value
        else:
            # Fallback for prefixes that might be different (e.g. 01911 vs 0191)
            # Try 3 digits? No, 4 is usually the "Activity" level.
            unmapped_value += value
            # print(f"Warning: Unmapped product prefix {prefix} - {df_02.iloc[i, 1]}")

    total_cons = np.sum(cons_67)
    print(f"\nTotal Consumo Mapeado: {total_cons:,.2f}")
    print(f"Total Consumo Não Mapeado: {unmapped_value:,.2f}")
    
    # Calculate shares
    shares = cons_67 / total_cons
    
    output_path = r'C:\Users\jonat\Documents\MIP e CGE\output\intermediary\household_consumption_shares_67.npy'
    np.save(output_path, shares)
    print(f"Vetor de shares salvo em {output_path}")

    # 3. Validation
    # Let's see some top consuming sectors
    top_indices = np.argsort(shares)[-10:][::-1]
    print("\nTop 10 setores no consumo das famílias (Nacional):")
    for idx in top_indices:
        print(f"Setor {idx+1}: {shares[idx]:.4%}")

if __name__ == "__main__":
    calculate_consumption_shares()
