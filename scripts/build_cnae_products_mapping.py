"""
V3 FINAL: Complete ICMS Regionalization using Make Matrix

Chain: CNAE divisions -> MIP activities -> MIP products

Uses:
1. IBGE correspondence file: CNAE -> Activities
2. Make matrix (Table 13): Activities -> Products
3. CONFAZ data: ICMS by UF x CNAE
"""

import pandas as pd
import numpy as np
import json

def build_cnae_to_product_mapping():
    """
    Build complete mapping CNAE -> Products using official matrices
    """
    
    print("="*70)
    print("BUILDING CNAE -> PRODUCTS MAPPING")
    print("="*70)
    
    # Step 1: Load CNAE -> Activity correspondence
    print("\n[1/3] Loading CNAE -> Activity correspondence...")
    
    ibge_file = r"C:\Users\jonat\Documents\MIP e CGE\data\Atividade -contas de divulgação x Cnae 2.0 - Resumo.xls"
    df_corresp = pd.read_excel(ibge_file)
    
    # Skip header rows, extract correspondence
    cnae_to_activity = {}
    
    for idx in range(3, len(df_corresp)):
        row = df_corresp.iloc[idx]
        
        activity_code = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        cnae_list = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
        
        if activity_code and cnae_list and activity_code != 'Ativ_Divulg.':
            # Parse CNAE list like "05 + 08" or "011 + 012 + 013"
            cnae_divisions = []
            for part in cnae_list.split('+'):
                part = part.strip()
                if part:
                    # Extract first 2 digits (division)
                    div_num = int(part[:2]) if len(part) >= 2 and part[:2].isdigit() else None
                    if div_num and div_num not in cnae_divisions:
                        cnae_divisions.append(div_num)
            
            if cnae_divisions:
                cnae_to_activity[activity_code] = cnae_divisions
    
    print(f"  Activities mapped: {len(cnae_to_activity)}")
    
    # Step 2: Load Make matrix (Activity -> Product)
    print("\n[2/3] Loading Make matrix...")
    
    with open('output/make_matrix.json', 'r', encoding='utf-8') as f:
        make_data = json.load(f)
    
    # Convert to lookup: for each product, which activities produce it
    make_matrix = {}  # {product_num: {activity_idx: share}}
    
    for prod in make_data['products']:
        prod_num = prod['product_num']
        activities = prod['activities']
        
        # Get non-zero activities
        activity_shares = {}
        total = sum(activities)
        
        if total > 0:
            for act_idx, val in enumerate(activities):
                if val > 0:
                    activity_shares[act_idx + 1] = val / total  # Normalize to shares
        
        if activity_shares:
            make_matrix[prod_num] = activity_shares
    
    print(f"  Products in Make matrix: {len(make_matrix)}")
    
    # Step 3: Build CNAE -> Product mapping
    print("\n[3/3] Building CNAE -> Product mapping...")
    
    cnae_to_products = {}
    
    # Reverse mapping: Activity code -> Activity index
    activity_codes = sorted(cnae_to_activity.keys())
    
    for cnae_div in range(1, 100):  # All CNAE divisions
        # Find which activities include this CNAE
        relevant_activities = []
        
        for act_code, cnae_list in cnae_to_activity.items():
            if cnae_div in cnae_list:
                # Find activity index
                act_idx = activity_codes.index(act_code) + 1 if act_code in activity_codes else None
                if act_idx:
                    relevant_activities.append((act_code, act_idx))
        
        if relevant_activities:
            # For this CNAE, distribute across products based on Make matrix
            product_distribution = {}
            
            for act_code, act_idx in relevant_activities:
                # Which products does this activity produce?
                for prod_num, act_shares in make_matrix.items():
                    if act_idx in act_shares:
                        share = act_shares[act_idx]
                        product_distribution[prod_num] = product_distribution.get(prod_num, 0) + share
            
            # Normalize
            total_share = sum(product_distribution.values())
            if total_share > 0:
                product_distribution = {p: s/total_share for p, s in product_distribution.items()}
                cnae_to_products[cnae_div] = product_distribution
    
    print(f"  CNAE divisions mapped: {len(cnae_to_products)}")
    
    # Save
    output = {
        "description": "CNAE divisions to MIP products using Make matrix",
        "methodology": "CNAE -> Activities (IBGE) -> Products (Make matrix)",
        "mapping": cnae_to_products
    }
    
    with open('output/cnae_to_products_final.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved: output/cnae_to_products_final.json")
    
    # Show examples
    print(f"\n{'='*70}")
    print("EXAMPLES")
    print("="*70)
    
    for cnae_div in [1, 10, 19, 35, 45]:
        if cnae_div in cnae_to_products:
            products = cnae_to_products[cnae_div]
            print(f"\nCNAE {cnae_div}:")
            top_products = sorted(products.items(), key=lambda x: x[1], reverse=True)[:5]
            for prod, share in top_products:
                print(f"  Product {prod}: {share*100:.1f}%")
    
    print(f"\n{'='*70}\n")
    
    return cnae_to_products

if __name__ == "__main__":
    build_cnae_to_product_mapping()
