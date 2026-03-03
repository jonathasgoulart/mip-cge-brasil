import pandas as pd
import numpy as np
import json

def extract_make_matrix():
    """
    Extract Make matrix (Table 13): Products x Activities
    Shows which activities produce which products
    """
    
    print("="*70)
    print("EXTRACTING MAKE MATRIX (TABELA 13)")
    print("="*70)
    
    FILE_PATH = 'data/processed/mip_2015/13.csv'
    
    # Read file
    df = pd.read_csv(FILE_PATH, encoding='utf-8')
    
    print(f"\nShape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    
    # Skip header rows (first 4)
    # Rows 4+ contain: Product code, Product name, then activity values
    
    make_data = []
    
    for idx in range(4, min(71, len(df))):  # Products 1-67
        row = df.iloc[idx]
        
        product_code = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        product_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        
        # Values for each activity (columns 2+)
        activity_values = []
        for col_idx in range(2, min(len(row), 77)):  # 75 activities
            val = row.iloc[col_idx]
            activity_values.append(float(val) if pd.notna(val) and val != '' else 0.0)
        
        make_data.append({
            "product_num": idx - 3,  # 1-67
            "product_code": product_code,
            "product_name": product_name,
            "activities": activity_values
        })
        
        if idx < 10:  # Print first few
            print(f"\nProduct {idx-3}: [{product_code}] {product_name}")
            print(f"  Non-zero activities: {sum(1 for v in activity_values if v > 0)}")
    
    print(f"\n{'-'*70}")
    print(f"Total products extracted: {len(make_data)}")
    
    # Save
    output = {
        "description": "Make matrix: which activities produce which products",
        "source": "MIP 2015 - Tabela 13",
        "products": make_data
    }
    
    with open('output/make_matrix.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved: output/make_matrix.json")
    
    # Analyze structure
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print("="*70)
    
    # For each product, which activity is the main producer?
    print(f"\nMain producer by product (first 20):")
    for i, prod in enumerate(make_data[:20]):
        if prod['activities']:
            max_idx = np.argmax(prod['activities'])
            max_val = prod['activities'][max_idx]
            if max_val > 0:
                print(f"  Product {prod['product_num']}: Activity {max_idx+1} ({max_val:.1f}%)")
    
    return make_data

if __name__ == "__main__":
    extract_make_matrix()
