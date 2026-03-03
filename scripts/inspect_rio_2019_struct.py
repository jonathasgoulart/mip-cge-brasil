
import pandas as pd
import json
import os

def run_inspection():
    print("=== INSPECTING RIO 2019 OFFICIAL FILES ===")
    
    file_mip = 'data/Cópia de MIP_RJ_2019_102X56.xlsx'
    file_tru = 'data/Cópia de TRU_RJ_2019_104X56.xlsx'
    
    # 1. Extract Labels from Sheet 9 (MIP)
    print("\nReading Sheet 9 (MIP)...")
    df9 = pd.read_excel(file_mip, sheet_name='9', skiprows=3)
    
    # Activity labels are in headers (starting from Col 2 usually)
    # The header names often contain the code and name separated by \n
    activities = [c for c in df9.columns if isinstance(c, str) and '\n' in c]
    
    # Product labels are in the second column (Index 1)
    products = df9.iloc[:, 1].dropna().tolist()
    
    # Filter products - usually there are totals at the bottom
    # Typically 102 products
    products_clean = [p for p in products if 'Total' not in str(p)]
    
    print(f"Total Activities: {len(activities)}")
    print(f"Total Products: {len(products_clean)}")
    
    # 2. Extract Labels from TRU
    print("\nReading TRU Sheet...")
    df_tru = pd.read_excel(file_tru, sheet_name='TRU_RJ 104', skiprows=3)
    # Check shape and content
    print(f"TRU columns: {df_tru.shape[1]}")
    
    # 3. Save to JSON
    results = {
        "mip_activities": activities,
        "mip_products": products_clean,
        "raw_headers": [str(c) for c in df9.columns]
    }
    
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/rio_2019_labels.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("\nLabels saved to data/processed/rio_2019_labels.json")

if __name__ == "__main__":
    run_inspection()
