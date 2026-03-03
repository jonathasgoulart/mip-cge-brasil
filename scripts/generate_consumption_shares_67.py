
import pandas as pd
import numpy as np
import json
import os

def generate_consumption_shares_67():
    # 1. Load Sector Info
    with open('output/mip_67_sectors.json', 'r', encoding='utf-8') as f:
        sectors_data = json.load(f)['sectors']
    
    # Map prefix -> Sector Index (0-based)
    prefix_to_idx = {}
    for i_str, info in sectors_data.items():
        prefix = info['code'][:4] # Take first 4 chars
        prefix_to_idx[prefix] = int(i_str) - 1
        
    print(f"Mapped {len(prefix_to_idx)} prefixes to 67 sectors.")

    # 2. Load 02.csv (127 products)
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

    # Household consumption: index 73
    # Product Code: index 0
    # Process rows 4 to 130 (approx, until "Total")
    
    cons_67 = np.zeros(67)
    
    for i in range(4, 131):
        full_code = str(df.iloc[i, 0]).strip()
        if not full_code or full_code.lower() == 'total':
            break
            
        prefix = full_code[:4]
        value = parse_smart(df.iloc[i, 73])
        
        if prefix in prefix_to_idx:
            idx = prefix_to_idx[prefix]
            cons_67[idx] += value
        else:
            # Special logic for prefixes that might be different or missed
            print(f"Warning: Prefix {prefix} from product {df.iloc[i, 1]} not in mapping.")

    # 3. Finalize
    total_cons = np.sum(cons_67)
    if total_cons == 0:
        print("Error: Total consumption integrated is zero!")
        return
        
    shares = cons_67 / total_cons
    
    output_path = r'C:\Users\jonat\Documents\MIP e CGE\output\intermediary\household_consumption_shares_67_v3.npy'
    np.save(output_path, shares)
    
    print(f"\nTotal Consumo Integrado: {total_cons:,.2f}")
    print(f"Shares saved to {output_path}")
    
    # Display top 10 sectors for validation
    top_idx = np.argsort(shares)[-10:][::-1]
    print("\nTop 10 Setores no Consumo das Famílias:")
    for idx in top_idx:
        desc = sectors_data[str(idx+1)]['description']
        print(f"Setor {idx+1} - {desc}: {shares[idx]:.4%}")

if __name__ == "__main__":
    generate_consumption_shares_67()
