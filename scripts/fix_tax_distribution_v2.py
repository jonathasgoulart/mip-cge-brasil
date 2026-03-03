
import csv
import json
import numpy as np
import os

def run():
    print("=== REPROCESSANDO DISTRIBUIÇÃO DE IMPOSTOS (MÉTODO ESTRUTURAL MIP) ===")
    
    DATA_DIR = 'data/processed/mip_2015'
    OUTPUT_DIR = 'output'
    
    # 1. 2021 Tax Targets (R$ Millions)
    TARGETS_2021 = {
        "ICMS": 537000,
        "IPI": 55000,
        "ISS": 74000,
        "PIS_PASEP": 71000,
        "COFINS": 270000,
        "II": 52000,
        "IOF": 47000,
        "CIDE": 4400
    }
    
    def parse_float(s):
        try:
            return float(s.replace('.','').replace(',','.'))
        except:
            return 0.0

    # 2. Read Make Matrix (01.csv) -> Fraction of Product P made by Sector S
    print("Lendo Matriz de Produção (01.csv)...")
    path_01 = os.path.join(DATA_DIR, '01.csv')
    
    # Rows: 128 Products. Cols: 67 Activities (Indices 3 to 69 in CSV)
    # Skip headers (approx 4 rows, verify start of data)
    # Data starts at row index ~87? No, 01.csv usually starts data earlier?
    # Let's inspect line count or content.
    # Previous inspection of 05.csv showed data at line 88. 
    # Let's assume uniform structure for MIP tables.
    
    START_ROW_DATA = 87 # 0-based index for line 88
    
    make_matrix = [] # List of [67 values]
    prod_codes = []
    
    # --- ROBUST READER FUNCTION ---
    def read_csv_block(filename, start_row, num_cols_to_read=None, is_vector=False):
        path = os.path.join(DATA_DIR, filename)
        data = []
        codes = []
        
        # Read entire file to memory to find start
        with open(path, 'r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            
        # Detect Start Row: Look for "01911" or first numeric code > 1000
        detected_start = -1
        for i, row in enumerate(reader):
            if len(row) > 0 and row[0].strip().startswith("0191"):
                detected_start = i
                break
                
        if detected_start == -1:
             # Fallback to hardcoded or try finding "019"
             for i, row in enumerate(reader):
                if len(row) > 0 and row[0].strip().startswith("019"):
                    detected_start = i
                    break
        
        if detected_start != -1:
            print(f"[{filename}] Auto-detected start at line {detected_start+1} (Code: {reader[detected_start][0]})")
            current_row = detected_start
        else:
            print(f"[{filename}] WARNING: Could not detect start. Using {start_row}")
            current_row = start_row

        while current_row < len(reader):
            row = reader[current_row]
            
            # Stop if row is empty or "Total"
            if not row or (len(row)>0 and "Total" in row[0]):
                break
                
            code = row[0]
            
            if is_vector:
                # Read last non-empty column
                val = 0.0
                for col in reversed(row):
                    if col.strip():
                        try:
                            val = parse_float(col)
                        except:
                            pass
                        break
                data.append(val)
                
            else:
                # Read specific matrix columns (e.g. 3 to 70 for Make Matrix)
                # Ensure we have enough columns
                if num_cols_to_read:
                    row_vals = []
                if num_cols_to_read:
                    row_vals = []
                    # Cols 7 to 7+67 = 74? (Indices 7...73 is 67 cols)
                    # Make Matrix 01.csv: Cols 7 to 73 are the 67 sectors.
                    slice_start = 7
                    slice_end = slice_start + 67
                    
                    segment = row[slice_start:slice_end]
                    # Pad if short
                    while len(segment) < 67: segment.append("0")
                    
                    row_vals = [parse_float(x) for x in segment]
                    data.append(row_vals)
                else:
                    data.append(row)
                    
            codes.append(code)
            current_row += 1
            
        return codes, np.array(data)

    # 2. Read Make Matrix (01.csv)
    print("Lendo Matriz de Produção (01.csv)...")
    codes_01, make_matrix = read_csv_block('01.csv', START_ROW_DATA, num_cols_to_read=67)
    print(f"Make Matrix Loaded: {make_matrix.shape}")
    
    # 3. Read Product Taxes (05.csv)
    print("Lendo Impostos sobre Produtos (05.csv)...")
    codes_05, tax_05_vec = read_csv_block('05.csv', START_ROW_DATA, is_vector=True)
    print(f"Tax Vector (05) Loaded: {tax_05_vec.shape}")
    
    # 4. ALIGNMENT LOGIC (BY CODE)
    print("\n--- CHECKING ALIGNMENT ---")
    print(f"01.csv Codes (First 5): {codes_01[:5]}")
    print(f"05.csv Codes (First 5): {codes_05[:5]}")
    
    # Create Dicts for 05 and 06
    tax_05_map = {c: v for c, v in zip(codes_05, tax_05_vec)}
    
    # Rebuild tax vector aligned to codes_01 (Make Matrix Base)
    aligned_tax_05 = []
    
    for code in codes_01:
        # Fuzzy match or exact? Codes in csv might be clean or have quotes.
        # My reader keeps raw string (checking cleaning).
        val = tax_05_map.get(code, 0.0)
        aligned_tax_05.append(val)
        
    tax_05_vec = np.array(aligned_tax_05)
    
    print(f"Aligned Tax Vector (05): sum = {np.sum(tax_05_vec):,.0f} (Should be close to original sum)")
    
    # Calculate Shares: Share[P, S] = Production[P, S] / TotalProd[P]
    # Make Matrix is already aligned to codes_01 by definition
    total_prod_per_p = np.sum(make_matrix, axis=1, keepdims=True)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        share_matrix = make_matrix / total_prod_per_p
    share_matrix[np.isnan(share_matrix)] = 0.0
    
    # 4a. Map Domestic Tax
    sector_tax_profile = np.dot(tax_05_vec, share_matrix) # Shape (67,)
    
    # Normalize
    total_profile = np.sum(sector_tax_profile)
    if total_profile > 0:
        norm_profile_dom = sector_tax_profile / total_profile
    else:
        norm_profile_dom = np.zeros(67)
        
    print("Perfil Setorial DOMÉSTICO Recalculado com Alinhamento por Código.")
    
    # 5. Read Import Taxes (06.csv) for II
    # 5. Read Import Taxes (06.csv)
    print("Lendo Impostos Importação (06.csv)...")
    codes_06, tax_06_vec = read_csv_block('06.csv', START_ROW_DATA, is_vector=True)
    
    # Align (Dictionary Map)
    tax_06_map = {c: v for c, v in zip(codes_06, tax_06_vec)}
    
    aligned_tax_06 = []
    for code in codes_01:
        val = tax_06_map.get(code, 0.0)
        aligned_tax_06.append(val)
        
    tax_06_vec = np.array(aligned_tax_06)
    
    sector_imp_tax_profile = np.dot(tax_06_vec, share_matrix) # Mapping II to producers (Proxy)
    
    total_profile_imp = np.sum(sector_imp_tax_profile)
    if total_profile_imp > 0:
        norm_profile_imp = sector_imp_tax_profile / total_profile_imp
    else:
        norm_profile_imp = np.zeros(67)

    # 6. Generate New tax_data.json
    # Distribute 2021 Targets using the profiles
    
    # Groups
    # Domestic Broad Taxes: ICMS, IPI, PIS, COFINS, CIDE, IOF
    # We use 'norm_profile_dom' for all these.
    # Refinement: ISS should be allocated to Services only?
    # Actually, 05.csv INCLUDES ISS.
    # So 'norm_profile_dom' ALREADY captures the Service vs Industry split correctly from MIP 2015 data.
    # (Since Service products have high ISS and low ICMS/IPI, the sum in 05.csv reflects that).
    
    taxes_by_type = {}
    
    # Domestic Keys
    for key in ["ICMS", "IPI", "ISS", "PIS_PASEP", "COFINS", "IOF", "CIDE"]:
        target = TARGETS_2021[key]
        dist = norm_profile_dom * target
        taxes_by_type[key] = dist.tolist()
        
    # Import Tax (II)
    target_ii = TARGETS_2021["II"]
    dist_ii = norm_profile_imp * target_ii
    taxes_by_type["II"] = dist_ii.tolist()
    
    # Save
    output_data = {
        "metadata": "Reprocessed with MIP 2015 Structural Distribution (Make Matrix Mapping)",
        "taxes_by_type": taxes_by_type
    }
    
    out_path = os.path.join(OUTPUT_DIR, 'tax_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"FULL SUCCESS. Taxes redistributed structurally. Saved to {out_path}.")
    
    # Debug: Show Top Products contributing to Tax
    print("\n--- TOP 10 PRODUTOS COM MAIOR IMPOSTO (05.csv) ---")
    top_prod_indices = np.argsort(tax_05_vec)[-10:][::-1]
    
    # Load Sector Labels
    s_labels = [f"Sector {i+1}" for i in range(67)]
    try:
        with open('output/intermediary/sector_labels.txt', 'r', encoding='latin1') as f:
            s_labels = [l.strip() for l in f if l.strip()]
    except: pass
    
    for idx in top_prod_indices:
        code = codes_01[idx]
        val = tax_05_vec[idx]
        
        # Find who produces this
        # share_matrix[idx, :] is vector of producers
        producer_idx = np.argmax(share_matrix[idx, :])
        producer_share = share_matrix[idx, producer_idx]
        producer_name = s_labels[producer_idx] if producer_idx < len(s_labels) else str(producer_idx)
        
        safe_prod_name = producer_name.encode('ascii', 'ignore').decode('ascii')
        print(f"Prod Code {code}: Tax = {val:,.0f} | Main Producer: {safe_prod_name} (Index {producer_idx}) ({producer_share*100:.1f}%)")
        
    print("\n--- TOP 5 SECTORS (TAX ARRECADAÇÃO 2021) ---")
    for v in taxes_by_type.values():
        total_tax_vec += np.array(v)
        
    print("\n--- TOP 5 SECTORS (TAX ARRECADAÇÃO 2021) ---")
    indices = np.argsort(total_tax_vec)[-5:][::-1]
    
    # Load Labels
    try:
        with open('output/intermediary/sector_labels.txt', 'r', encoding='latin1') as f:
            labels = [l.strip() for l in f if l.strip()]
            
        for idx in indices:
            print(f"{idx+1} - {labels[idx]}: R$ {total_tax_vec[idx]/1e3:,.1f} Bi")
    except:
        pass

if __name__ == "__main__":
    run()
