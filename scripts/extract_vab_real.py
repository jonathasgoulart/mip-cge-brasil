import xlrd
import numpy as np
import os

RAW_DIR = 'data/raw/contas_regionais_2021'
OUTPUT_DIR = 'output/intermediary'
INTER_DIR = 'output/intermediary'

# Map File Index (based on our discovery) to UF (Standard IBGE Order)
# Regions are skipped (1, 9, 19, 24, 28, 33)
FILE_MAP = {
    2: 'RO', 3: 'AC', 4: 'AM', 5: 'RR', 6: 'PA', 7: 'AP', 8: 'TO',
    10: 'MA', 11: 'PI', 12: 'CE', 13: 'RN', 14: 'PB', 15: 'PE', 16: 'AL', 17: 'SE', 18: 'BA',
    20: 'MG', 21: 'ES', 22: 'RJ', 23: 'SP',
    25: 'PR', 26: 'SC', 27: 'RS',
    29: 'MS', 30: 'MT', 31: 'GO', 32: 'DF'
}

# Map 67 Sectors (0-indexed) to 18 Regional Aggregates (1-indexed based on sheet idx usually)
# However, usually sheet indices are 1.1, 1.2... 
# Tabela 1.1 is Total. Tabela 1.2 is Agro.
# Let's map 0..66 to Aggregate Index 0..17 (where 0 is Agro)
# Regional List (approx):
# 0: Agro (1.2)
# 1: Pecuaria (1.3)
# 2: Florestal/Pesca (1.4)
# 3: Extrativas (1.5)
# 4: Transformacao (1.6)
# 5: Eletricidade/Gas/Agua (1.7) -> Wait, 1.7 covers both.
# 6: Construcao (1.8)
# 7: Comercio (1.9)
# 8: Transporte (1.10)
# 9: Alojamento/Alim (1.11)
# 10: Info/Com (1.12)
# 11: Finac (1.13)
# 12: Imob (1.14)
# 13: Prof/Adm (1.15)
# 14: Pub/Edu/Saude (1.16)
# 15: Priv Edu/Saude (1.17)
# 16: Artes (1.18)
# 17: Domesticos (1.19)

# 67 Sectors (1-based in text file, 0-based here)
SECTOR_MAP = {
    0: 0, # Agro
    1: 1, # Pecuaria
    2: 2, # Florestal
    3: 3, 4: 3, 5: 3, 6: 3, # Extrativas (4 sectors)
    # Transformacao (8 to 37 -> 30 sectors). Indices 7..36
    **{i: 4 for i in range(7, 37)},
    37: 5, 38: 5, # Eletricidade (38) + Agua (39). Indices 37, 38
    39: 6, # Construcao (40 -> 39)
    40: 7, # Comercio
    41: 8, 42: 8, 43: 8, 44: 8, # Transporte
    45: 9, 46: 9, # Alojamento
    47: 10, 48: 10, 49: 10, 50: 10, # Info
    51: 11, # Financeiras
    52: 12, # Imob
    53: 13, 54: 13, 55: 13, 56: 13, 57: 13, 58: 13, # Prof
    59: 14, 60: 14, 62: 14, # Pub (60, 61, 63 -> 59, 60, 62)
    61: 15, 63: 15, # Priv (62, 64 -> 61, 63)
    64: 16, 65: 16, # Artes
    66: 17 # Domesticos
}

def load_national_vab_structure():
    # Load X (Total Output) as proxy for VAB distribution within aggregates
    x_path = os.path.join(INTER_DIR, 'X_nacional.npy')
    try:
        if os.path.exists(x_path):
            X = np.load(x_path)
            # Ensure 1D array
            if X.ndim > 1: X = X.flatten()
            
            if X.size == 67 and np.sum(X) > 0:
                print(f"Loaded X_nacional.npy (Sum={np.sum(X)})")
                return X
            else:
                print(f"X_nacional.npy is invalid (Size={X.size}, Sum={np.sum(X)}). Trying CSV.")
                
        # Fallback to 03.csv
        import csv
        path_03 = os.path.join('data/processed/mip_2015', '03.csv')
        data = []
        if os.path.exists(path_03):
            with open(path_03, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i < 4: continue # Skip header
                    if i >= 4 + 67: break
                    try:
                        val = float(row[2].replace('.', '').replace(',', '.')) if row[2] else 0.0
                    except:
                        val = 0.0
                    data.append(val)
        
        arr = np.array(data)
        if arr.size == 67:
            print(f"Loaded X from 03.csv (Sum={np.sum(arr)})")
            return arr
            
        print("Fallback to Uniform weights.")
        return np.ones(67)
    except Exception as e:
        print(f"Error loading national structure: {e}. Using uniform.")
        return np.ones(67)

def run():
    print("--- EXTRACTING REAL REGIONAL VAB (27 UFs) ---")
    
    # National Weights
    X_nas = load_national_vab_structure()
    
    # Verify we have mapping for all 67
    for i in range(67):
        if i not in SECTOR_MAP:
            print(f"Warning: Sector {i} not mapped. Defaulting to 17 (Domestico).")
            SECTOR_MAP[i] = 17
            
    # Calculate share of each sector within its aggregate
    # norm_weights[sec_idx] = X_nas[sec_idx] / Sum(X_nas of all sectors in same aggregate)
    agg_totals = np.zeros(18)
    for i in range(67):
        agg_idx = SECTOR_MAP[i]
        agg_totals[agg_idx] += X_nas[i]
        
    weights = np.zeros(67)
    for i in range(67):
        agg_idx = SECTOR_MAP[i]
        total = agg_totals[agg_idx]
        if total > 0:
            weights[i] = X_nas[i] / total
        else:
            weights[i] = 0.0 # Should not happen if X > 0

    # Extract
    extracted_count = 0
    for file_idx, uf_sigla in FILE_MAP.items():
        filename = f'Tabela{file_idx}.xls'
        path = os.path.join(RAW_DIR, filename)
        
        if not os.path.exists(path):
            print(f"Missing: {filename} ({uf_sigla})")
            continue
            
        print(f"Processing {uf_sigla} ({filename})...")
        try:
            wb = xlrd.open_workbook(path, on_demand=True)
            
            # Semantic Extraction map to Aggregates (0-17)
            # Init with zeros
            reg_vab_agg = np.zeros(18)
            
            def clean_text(text):
                return str(text).lower().strip().replace('ç', 'c').replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                
            found_count = 0
            
            for s_idx in range(wb.nsheets):
                try:
                    sheet = wb.sheet_by_index(s_idx)
                    # Read Header (first 20 lines) to identify sector
                    header_text = ""
                    for r in range(min(20, sheet.nrows)):
                         row_vals = sheet.row_values(r)
                         txt = " ".join([str(x) for x in row_vals if isinstance(x, str)])
                         header_text += " " + clean_text(txt)
                    
                    sector_id = -1
                    # Semantic Matching Logic (Matches SECTOR_MAP structure 0-17)
                    if "gricultura" in header_text: sector_id = 0
                    elif "pecu" in header_text and "ria" in header_text: sector_id = 1
                    elif "florestal" in header_text or "silvicultura" in header_text: sector_id = 2
                    elif "pesca" in header_text or "aquicultura" in header_text: sector_id = 2 # Merge Pesca into Forestal (Index 2) to match MIP structure if usually combined? 
                    # Wait, MIP Sector 2 is "Forestal, Pesca". 
                    
                    elif "xtrativa" in header_text: sector_id = 3
                    elif "transforma" in header_text: sector_id = 4
                    elif "eletricidade" in header_text and "s" in header_text: sector_id = 5
                    elif "constru" in header_text: sector_id = 6
                    elif "com" in header_text and "rcio" in header_text: sector_id = 7
                    elif "transporte" in header_text: sector_id = 8
                    elif "alojamento" in header_text: sector_id = 9
                    elif "informa" in header_text and "comunica" in header_text: sector_id = 10
                    elif "financeira" in header_text: sector_id = 11
                    elif "imobili" in header_text: sector_id = 12
                    elif "profissionai" in header_text: sector_id = 13
                    elif "publica" in header_text and "administra" in header_text: sector_id = 14
                    elif "privada" in header_text: sector_id = 15
                    elif "artes" in header_text: sector_id = 16
                    elif "dom" in header_text and "stico" in header_text: sector_id = 17
                    
                    if sector_id != -1:
                        # Find 2021 Value
                        val_2021 = 0.0
                        for r in range(sheet.nrows):
                            c0 = str(sheet.cell_value(r, 0)).strip()
                            if c0 == '2021' or c0 == '2021.0':
                                try:
                                    val = sheet.cell_value(r, 5)
                                    if isinstance(val, (int, float)):
                                        val_2021 = val
                                    elif isinstance(val, str) and val.replace('.','').replace(',','').isdigit():
                                         val_2021 = float(val)
                                except:
                                    pass
                                break
                        
                        if val_2021 > 0:
                            # Accumulate because Pesca + Forestal both map to 2
                            reg_vab_agg[sector_id] += val_2021 
                            found_count += 1
                            
                except:
                    pass
            
            if found_count < 5:
                print(f"  Warning: Only {found_count} sectors found for {uf_sigla}. Check file.")
            
            # Distribute to 67 sectors
            reg_vab_67 = np.zeros(67)
            for i in range(67):
                agg = SECTOR_MAP[i]
                reg_vab_67[i] = reg_vab_agg[agg] * weights[i]
                
            # Save
            np.save(os.path.join(OUTPUT_DIR, f'VAB_{uf_sigla}.npy'), reg_vab_67)
            extracted_count += 1
            
        except Exception as e:
            print(f"  Error extracting {uf_sigla}: {e}")

    print(f"Extraction Complete. {extracted_count}/27 UFs processed.")
    
if __name__ == "__main__":
    run()
