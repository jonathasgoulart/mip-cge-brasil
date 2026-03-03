import csv

def extract_mip_products_correct():
    """
    Extract 67 MIP PRODUCTS from rows of table 05.csv
    (not activities/columns)
    """
    
    print("="*70)
    print("EXTRACTING 67 MIP PRODUCTS (TABLE ROWS)")
    print("="*70)
    
    FILE_PATH = 'data/processed/mip_2015/05.csv'
    
    products = {}
    
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Skip header rows (4 rows)
        for _ in range(4):
            next(reader)
        
        # Read products (rows)
        for i, row in enumerate(reader, start=1):
            if i > 67:  # Only 67 products
                break
            
            if len(row) >= 2:
                code = row[0].strip()
                description = row[1].strip()
                
                products[i] = {
                    "code": code,
                    "description": description
                }
                
                print(f"{i:2d}. [{code:5s}] {description}")
    
    print(f"\n{'='*70}")
    print(f"Total products extracted: {len(products)}")
    print(f"{'='*70}\n")
    
    # Save
    import json
    output = {
        "total_products": len(products),
        "products": products,
        "source": "MIP 2015 - Tabela 05.csv (ROWS = products)"
    }
    
    with open('output/mip_67_products_correct.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Saved: output/mip_67_products_correct.json\n")
    
    return products

if __name__ == "__main__":
    extract_mip_products_correct()
