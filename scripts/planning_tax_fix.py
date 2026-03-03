
import csv
import json
import numpy as np
import os

def run():
    print("=== REPROCESSANDO DISTRIBUIÇÃO DE IMPOSTOS (BASE ESTRUTURAL MIP 2015) ===")
    
    # 1. Load Data Paths
    MIP_DIR = 'data/processed/mip_2015'
    OUTPUT_DIR = 'output'
    
    # Targets 2021 (Nominal R$ Millions) - Same as used before
    TARGETS_2021 = {
        "ICMS": 537000,
        "IPI": 55000,
        "ISS": 74000,
        "II": 52000,
        "IOF": 47000,
        "CIDE": 4400,
        "PIS_PASEP": 71000,
        "COFINS": 270000
    }
    
    # 2. Read Total Columns from MIP Tables (05 and 06) to get Structural Weights
    def read_total_vector(filename):
        path = os.path.join(MIP_DIR, filename)
        vec = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip 4 header rows. Read 128 products (MIP 128) or 67 products (MIP 67)?
            # The file 05.csv likely has 128 products (rows).
            # We need to aggregate them to 67 Activities (Sectors).
            # Actually, our matrix is Product x Sector? No, usually Commodity x Activity.
            # Let's check the number of rows.
            rows = list(reader)
            
            # Start data at row 87 (0-based) ?
            # User saw line 88: "01911 Arroz..."
            
            start_row = 87
            # Let's verify if we have 128 products.
            # Assuming standard 128 products mapping to 67 activities.
            # We need a mapper [128] -> [67].
            
            # SIMPLIFICATION:
            # If we don't have the mapper handy, check if the file is already aggregated to 67?
            # Codes like "01911" imply 128.
            # Code "01" implies 67.
            
            # Let's assume we read 128 and aggregate.
            # Or use a heuristic: The first 67 rows are the main products? No.
            
            # Wait, 05.csv has 128 products.
            # We need to map Product -> Activity.
            # Usually diagonal, but some activities produce multiple products.
            # Let's assume 1-to-1 or N-to-1 aggregation based on the first 2 digits?
            
            data_rows = rows[start_row:]
            vals = []
            codes = []
            
            for r in data_rows:
                if len(r) < 2: continue
                code = r[0]
                # Total usually last column
                try:
                    # Finds last non-empty column
                    last_val = 0.0
                    for c in reversed(r):
                        if c.strip():
                            last_val = float(c.replace('.','').replace(',','.'))
                            break
                    vals.append(last_val)
                    codes.append(code)
                except:
                    pass
                    
            return codes, np.array(vals)

    codes_05, vec_05 = read_total_vector('05.csv') # Taxes on Dom Products
    codes_06, vec_06 = read_total_vector('06.csv') # Taxes on Imp Products (II)
    
    print(f"Lido vetor base 05.csv: {len(vec_05)} produtos. Soma (MIP): {np.sum(vec_05):,.0f}")
    
    # 3. Aggregate 128 Products -> 67 Activities
    # Mapper Logic: The IBGE 128 -> 67 mapping is standard.
    # Group by first 2 chars seems flaky (some are 5 digits).
    # Since we lack the explicit mapping file right now, let's look at the mapping logic in `step1_pre_process.py` or similar?
    # Or just distribute proportionally to X? No, that defeats the purpose.
    
    # Let's assume the 128 vector is what we distribute, and then we sum to 67 based on order?
    # Our `X_nacional` has 67.
    # We must aggregate.
    
    # Quick fix: Create a 67-element vector.
    # There are 67 activities and 128 products.
    # Actually, let's treat the existing 128 vector as the "Tax Profile".
    # Just need to know which products belong to which sector.
    # 01911 -> activity 01?
    # 01912 -> activity 01?
    
    # Since we urgently need to fix the "Nonsense" result, let's try to map by index if we can't map by code.
    # 128 is almost 2x 67.
    # Let's Try to look for `01.csv` (Supply) which maps Product to Activity? No too complex for now.
    
    # ALTERNATIVE: Use the previous `process_taxes.py` if it outputted `tax_data.json` correctly before we overwrote it with `2021` version.
    # `process_taxes.py` used `read_total_column` with n=67. 
    # Did it assume the first 67 rows were the sectors?
    # If 05.csv has 128 rows, reading only 67 is WRONG (cuts off half the economy).
    
    # CORRECT APPROACH:
    # 1. Read all 128 product taxes.
    # 2. Normalize to get share of total tax (Vector S, size 128).
    # 3. Use `Tabela 01` (Make Matrix) to map Products (rows) to Activities (cols)? 
    #    Or `Tabela 02` (Use)? 
    #    Actually, if we want "Tax by Sector (Activity)", we need to know who produced the taxed product.
    #    Make Matrix (01.csv) tells us which Activity makes which Product.
    #    Assumption: Principal Product.
    #    We can map Product -> Activity based on the Make Matrix structure.
    
    # SIMPLER HEURISTIC (Product Code Prefix):
    # MIP 67 codes are `01000` to `67000`.
    # MIP 128 codes are `01911`, etc.
    # Mapping usually aggregates sequential products.
    # I will attempt to confirm standard aggregation (approx 2 products per sector).
    # But to be safe, I will distribute the calculated tax targets using the **128-product weights** aggregated into 67 buckets.
    # How to aggregate? 
    # I'll create a binning: 128 items / 67 items ~ 1.9.
    # Actually, the file `sector_labels.txt` has 67 names.
    # Let's assume we can map by string similarity or just load the 128-product labels and the 67-sector labels.
    
    # Let's use `step1_pre_process.py` Aggregation Matrix logic if available.
    # It usually builds a P (128x67) matrix.
    # If not found, I will implement a basic "Sequential Sum" if codes are ordered.
    # Codes usually start with Activity Code? E.g. Activity 01 -> Prod 01xxx.
    
    # Let's inspect codes:
    # 01911 -> Sector 1 (Agro)
    # 02911 (Forestal) -> Sector 2 (Forestal) ?
    # Let's rely on the first 2 digits of the code?
    
    # Mapping:
    # 01xxx -> 01
    # ...
    # Any code starting with 'S' is Service?
    
    # Let's do this:
    # 1. Load the vector of 128 taxes.
    # 2. Use a "Smart Aggregator" that sums neighboring products into 67 bins trying to match relative size of X.
    # 3. Or simpler: The previous `process_taxes.py` script was importing `step1`.
    
    # Let's try to infer the mapping from `output/intermediary/mapping_128_67.json` if it exists?
    
    pass

if __name__ == "__main__":
    run()
