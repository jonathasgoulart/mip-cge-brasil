import csv
import numpy as np
import os
import json

# --- CONFIGS ---
DATA_DIR = 'data/processed/mip_2015'
OUTPUT_DIR = 'output'
INTER_DIR = 'output/intermediary'

# 2021 TAX TARGETS (Million R$)
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

def parse_val(s):
    try:
        if isinstance(s, str):
            val = s.replace('.', '').replace(',', '.')
            return float(val)
        return float(s)
    except:
        return 0.0

def read_total_column(path, skip_rows, n_rows=67):
    """Lê a última coluna (Total) de um arquivo CSV padrão do IBGE."""
    if not os.path.exists(path):
        print(f"ERRO: Arquivo não encontrado: {path}")
        return np.zeros(n_rows)
    
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < skip_rows: continue
            if i >= skip_rows + n_rows: break
            
            val = 0.0
            for col in reversed(row):
                if col.strip():
                    val = parse_val(col)
                    break
            data.append(val)
            
    return np.array(data)

def load_sector_names():
    """Load sector names for classification"""
    names = []
    path = os.path.join(DATA_DIR, '05.csv')
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 4: continue
            if i >= 4 + 67: break
            names.append(row[1].upper() if len(row) > 1 else "UNKNOWN")
    return names

def classify_sector(name, index):
    """Classify sector for tax distribution"""
    # Returns dict with weights for each tax type
    classification = {
        "ICMS": 0.0,
        "IPI": 0.0,
        "ISS": 0.0,
        "II": 0.0,
        "IOF": 0.0,
        "CIDE": 0.0,
        "PIS_PASEP": 1.0,  # Apply to all
        "COFINS": 1.0      # Apply to all
    }
    
    # AGRICULTURE (0-3): ICMS + PIS/COFINS
    if index <= 3:
        classification["ICMS"] = 1.0
        
    # EXTRACTIVE (4-5): ICMS + PIS/COFINS + CIDE (fuels)
    elif index <= 5:
        classification["ICMS"] = 1.0
        if "PETRÓLEO" in name or "GÁS" in name:
            classification["CIDE"] = 1.0
            
    # MANUFACTURING (6-38): IPI + ICMS + PIS/COFINS + II
    elif index <=38:
        classification["IPI"] = 1.0
        classification["ICMS"] = 1.0
        classification["II"] = 0.3  # Partial (imported inputs)
        
        # Special: Fuels
        if "COMBUSTÍVEL" in name or "PETRÓLEO" in name or "ETANOL" in name:
            classification["CIDE"] = 1.0
            
    # UTILITIES (39-42): ICMS (energy/water)
    elif index <= 42:
        classification["ICMS"] = 1.0
        
    # SERVICES (43+): ISS + PIS/COFINS
    else:
        classification["ISS"] = 1.0
        
        # Financial services: IOF (broader classification)
        if any(x in name for x in ["FINANCEIRO", "SEGURO", "BANCO", "PREVIDÊNCIA", "CRÉDITO", "CAPITAL"]):
            classification["IOF"] = 1.0
        # Apply IOF proportionally to all service sectors if no financial identified
        elif index >= 50:  # Mid-to-high service indices
            classification["IOF"] = 0.1  # Partial weighting
            
        # Trade margins: ICMS
        if "COMÉRCIO" in name:
            classification["ICMS"] = 0.3
            
    return classification

def run():
    print(">>> Processando Matriz de Impostos (2021 Disaggregated)...")
    
    # 1. Load X (Total Output)
    x_path = os.path.join(INTER_DIR, 'X_nacional.npy')
    loaded_ok = False
    if os.path.exists(x_path):
        X = np.load(x_path)
        if np.sum(X) > 0:
            loaded_ok = True
            print(f"Loaded X from npy (Sum: {np.sum(X)/1e6:.2f} Trillion)")
            
    if not loaded_ok:
        print("X_nacional.npy is invalid. Fallback to raw 03.csv...")
        path_03 = os.path.join(DATA_DIR, '03.csv')
        SKIP_ROWS_X = 4 
        X = read_total_column(path_03, SKIP_ROWS_X)
        print(f"Loaded X (Raw Sum): {np.sum(X)/1e6:.2f} Trillion")
        
    # Output Magnitude Correction
    try:
        path_01 = os.path.join(DATA_DIR, '01.csv')
        with open(path_01, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        target_output = 11909669.0
        for line in reversed(lines):
            if line.startswith("Total,"):
                parts = list(csv.reader([line]))[0]
                try:
                    val = float(parts[2].replace('.', '').replace(',', '.'))
                    if val > 5000000:
                        target_output = val
                except:
                    pass
                break
        
        current_sum = np.sum(X)
        if current_sum > 0:
            scale_factor = target_output / current_sum
            if scale_factor > 1.2 or scale_factor < 0.8:
                print(f"Applying Output Scale Factor: {scale_factor:.4f}")
                X = X * scale_factor
                
    except Exception as e:
        print(f"Output Magnitude Warning: {e}")

    # 2. Load MIP tax structure (for distribution weights)
    SKIP_ROWS = 4
    taxes_mip_dom = read_total_column(os.path.join(DATA_DIR, '05.csv'), SKIP_ROWS)
    taxes_mip_imp = read_total_column(os.path.join(DATA_DIR, '06.csv'), SKIP_ROWS)
    
    # 3. Load sector names and classifications
    sector_names = load_sector_names()
    
    # 4. Initialize disaggregated tax vectors
    tax_vectors = {}
    for tax_type in TARGETS_2021.keys():
        tax_vectors[tax_type] = np.zeros(67)
    
    # 5. Distribute taxes by sector classification
    print("\n>>> Distributing taxes by sector...")
    
    for tax_type, target_total in TARGETS_2021.items():
        # Calculate weights based on X and sector classification
        weights = np.zeros(67)
        
        for i in range(67):
            classification = classify_sector(sector_names[i], i)
            weights[i] = X[i] * classification.get(tax_type, 0.0)
        
        # Normalize and apply target
        total_weight = np.sum(weights)
        if total_weight > 0:
            tax_vectors[tax_type] = (weights / total_weight) * target_total
            
        print(f"{tax_type:12s}: R$ {np.sum(tax_vectors[tax_type]):,.0f} M (Target: {target_total:,.0f})")
    
    # 6. Calculate total and coefficients
    taxes_total_abs = sum(tax_vectors.values())
    
    # Coefficients (tau = Tax / X)
    tax_coeff_total = np.zeros(67)
    tax_coeff_by_type = {}
    
    non_zero = X > 0
    tax_coeff_total[non_zero] = taxes_total_abs[non_zero] / X[non_zero]
    
    for tax_type in TARGETS_2021.keys():
        coef = np.zeros(67)
        coef[non_zero] = tax_vectors[tax_type][non_zero] / X[non_zero]
        tax_coeff_by_type[tax_type] = coef
    
    print(f"\nX Total: {np.sum(X)/1e6:.2f} Trillion")
    print(f"Total Taxes (2021): {np.sum(taxes_total_abs)/1e3:.2f} Billion")
    print(f"Effective Tax Rate: {np.sum(taxes_total_abs)/np.sum(X)*100:.2f}%")
    
    # 7. Save disaggregated data
    output_data = {
        "year": 2021,
        "production_X": X.tolist(),
        "taxes_total_abs": taxes_total_abs.tolist(),
        "coef_tax_total": tax_coeff_total.tolist(),
        "taxes_by_type": {k: v.tolist() for k, v in tax_vectors.items()},
        "coef_by_type": {k: v.tolist() for k, v in tax_coeff_by_type.items()},
        "metadata": {
            "calibration_year": 2021,
            "source_ctb": "ctb_1990-2024_0.xlsx",
            "targets": TARGETS_2021
        }
    }
    
    output_path = os.path.join(OUTPUT_DIR, 'tax_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\nDados salvos em {output_path}")
    return output_data

if __name__ == "__main__":
    run()
