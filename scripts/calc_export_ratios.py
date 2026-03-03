
import csv
import json
import numpy as np

def parse_float(x):
    try:
        if isinstance(x, str):
            return float(x.replace('.','').replace(',','.'))
        return float(x)
    except:
        return 0.0

def run():
    print("=== CALCULATING EXPORT RATIOS (MIP 2015) ===")
    
    # Paths
    # 01.csv: Production (We need Total Output by Product or Activity?)
    # 02.csv: Final Demand (Contains Exports column)
    # We work with 67 Sectors (Activities) or 128 Products?
    # MIP matrices are usually Product x Activity.
    # Exports are by PRODUCT.
    # We need to map Product Exports -> Activity Exports.
    # Method: Assume Product P is produced by Activity A (Main Diagonal assumption or use Market Share).
    # Simpler: Use Activity Total Output (VBP) from 01.csv and calculate Indirect Export Share?
    # NO. 
    # Let's simple sum Exports of Products typically produced by Sector S.
    
    # BETTER:
    # 02.csv (Demand) has columns for Consumption, Govt, Investment, Exports.
    # It is usually 128 Products x 6 Demand Components.
    
    # 01.csv (Make) is 128 Products x 67 Activities.
    
    # Algorithm:
    # 1. Get `Exp_P` (Exports by Product) from 02.csv.
    # 2. Get `Make_PA` (Make Matrix) from 01.csv.
    # 3. `Exp_A` (Exports by Activity) = `Make_PA.T` * `Exp_P` ?? 
    #    No. We assume the *share* of product P exported applies to the activity P?
    #    Actually, `Make` maps who makes what.
    #    Total Exports of Activity A = Sum_over_P ( Share of P made by A * Total Exports of P ).
    #    Yes. 
    
    # 1. Read 02.csv (Demand)
    # Finding Export Column. Usually col 3 or 4.
    path_02 = 'data/processed/mip_2015/02.csv'
    exports_by_product = np.zeros(128)
    
    with open(path_02, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        
    # Detect Data Start
    start_row = -1
    for i, row in enumerate(reader):
        if len(row) > 0 and row[0].strip().startswith("0191"):
            start_row = i
            break
            
    # Export Column? 
    # Header usually: Consumo Familias, Consumo Govt, ISFL, FBCF, Est., Exportacao
    # Let's assume Col Index 5 (6th column) is Exports. (Standard MIP: 301, 302, 303, 304, 305, 306).
    # Need to verify header.
    # Let's inspect headers first? No time. Standard MIP 2015 col 5 is Exports.
    # Let's try to detect header row "306" or "Exportação".
    
    # Locate header row (above start_row)
    # Scan first 20 rows
    header_row = []
    export_col_idx = -1
    
    for r in range(start_row):
        row = reader[r]
        row_str = " ".join(row).lower()
        if "xport" in row_str or "306" in row_str:
            header_row = row
            # Find column
            for idx, cell in enumerate(row):
                if "xport" in cell.lower() or "306" in cell:
                    export_col_idx = idx
                    print(f"Found Exports at Col {idx} ({cell})")
                    break
            break
            
    if export_col_idx == -1:
        print("WARNING: Could not identify Export column. Using -4 fallback.")
        export_col_idx = len(reader[start_row]) - 4 # Heuristic based on inspection
    
    print(f"Using Export Column Index: {export_col_idx}")
            
    # Read Exports
    for r in range(start_row, min(start_row+128, len(reader))):
        row = reader[r]
        if len(row) > export_col_idx:
            val = parse_float(row[export_col_idx])
            exports_by_product[r - start_row] = val
            
    # 2. Read 01.csv (Make Matrix)
    # We need to distribute these Product Exports to Activities.
    # or simplier: Total Output by Product (VBP_P).
    # Export_Ratio_P = Exp_P / VBP_P.
    # THEN map this ratio to sectors?
    
    # Let's calculate `Exp_A`.
    # Make Matrix (Products x Activities).
    # We need Share Matrix `D = Make / VBP_P_diag` ??
    # Let's just sum the Value.
    # Activity A exports P if it makes P.
    # If Product P has 100 Exports, and A makes 100% of P, A gets 100.
    # If A makes 50% of P, A gets 50.
    
    # Read Make Matrix (Product x Activity)
    path_01 = 'data/processed/mip_2015/01.csv'
    # Start row same logic
    # Cols 7 to 73 (67 cols) are Activities.
    
    activity_exports = np.zeros(67)
    activity_output = np.zeros(67) # To calc ratio
    
    with open(path_01, 'r', encoding='utf-8') as f:
        reader01 = list(csv.reader(f))
        
    start_row01 = -1
    for i, row in enumerate(reader01):
        if len(row) > 0 and row[0].strip().startswith("0191"):
            start_row01 = i
            break
            
    col_start = 7
    
    for r in range(start_row01, min(start_row01+128, len(reader01))):
        row = reader01[r]
        prod_idx = r - start_row01
        
        total_prod_output = 0.0
        row_vals = []
        
        # Read Activity productions for this product
        for c in range(67):
            if (col_start + c) < len(row):
                 val = parse_float(row[col_start + c])
                 row_vals.append(val)
                 total_prod_output += val
            else:
                 row_vals.append(0.0)
                 
        # If product produced > 0
        if total_prod_output > 0:
            exp_val = exports_by_product[prod_idx]
            
            # Distribute Export Value to Activities based on production share
            for c in range(67):
                share = row_vals[c] / total_prod_output
                activity_exports[c] += exp_val * share
                activity_output[c] += row_vals[c]
                
    # Calculate Ratios
    ratios = []
    for i in range(67):
        if activity_output[i] > 0:
            r = activity_exports[i] / activity_output[i]
        else:
            r = 0.0
        ratios.append(r)
        
    # Validation
    labels = []
    try:
        with open('output/intermediary/sector_labels.txt', 'r', encoding='latin1') as f:
            labels = [l.strip() for l in f if l.strip()]
    except:
        labels = [str(i) for i in range(67)]
        
    print("\n--- TOP EXPORTING SECTORS (RATIO) ---")
    sorted_d = sorted(enumerate(ratios), key=lambda x: x[1], reverse=True)
    for idx, r in sorted_d[:10]:
        safe_lbl = labels[idx][:30].encode('ascii', 'ignore').decode('ascii')
        print(f"{safe_lbl}: {r*100:.1f}%")
        
    # Save
    with open('data/processed/2021_final/export_ratios.json', 'w') as f:
        json.dump(ratios, f)
        
    print("\nSaved to data/processed/2021_final/export_ratios.json")

if __name__ == "__main__":
    run()
