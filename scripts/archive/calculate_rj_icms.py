import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

# Config
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output' / 'final'
INTER_DIR = BASE_DIR / 'output' / 'intermediary'
REGIONAL_DIR = BASE_DIR / 'output' / 'regional_matrices'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed' / '2021_final'

def run():
    print("=== CÁLCULO DE CARGA TRIBUTÁRIA DE ICMS - RJ (OFICIAL) ===")
    
    # 1. Load Data
    path_vab = PROCESSED_DIR / 'vab_regional.json'
    path_icms = PROCESSED_DIR / 'tax_matrix_hybrid_by_state.json'
    path_a_local = REGIONAL_DIR / 'A_RIO_LOCAIS_67x67.xlsx'
    path_a_inter = REGIONAL_DIR / 'A_RIO_INTER_67x67.xlsx'
    path_labels = INTER_DIR / 'sector_labels.txt'
    
    print(f"Loading VAB: {path_vab}")
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
        vab_rj = np.array(vab_data['RJ'])
        
    print(f"Loading ICMS: {path_icms}")
    with open(path_icms, 'r', encoding='utf-8') as f:
        icms_data = json.load(f)
        icms_rj = np.array(icms_data['RJ'])
        
    print(f"Loading Matrices using Pandas...")
    df_local = pd.read_excel(path_a_local, index_col=0)
    df_inter = pd.read_excel(path_a_inter, index_col=0)
    
    # 2. Derive VBP
    # VBP = VAB / (1 - sum(A_col))
    # where A_col = A_local_col + A_inter_col
    
    A_local = df_local.values
    A_inter = df_inter.values
    
    # Check shapes
    if A_local.shape != (67, 67) or A_inter.shape != (67, 67):
        raise ValueError(f"Matrix shapes invalid: Local {A_local.shape}, Inter {A_inter.shape}")
        
    # Column Sums (Total Intermediate Consumption Coefficients)
    A_col_sum = np.sum(A_local, axis=0) + np.sum(A_inter, axis=0) # Sum over rows (dim 0) for each col
    
    # Calculate VBP
    # Handle division by zero or negative denominator (should not happen in stable IO)
    denominator = 1 - A_col_sum
    
    # Check for anomalies
    invalid_indices = np.where(denominator <= 0)[0]
    if len(invalid_indices) > 0:
        print(f"WARNING: Sectors {invalid_indices} have denominator <= 0. VBP calculation might be wrong.")
        
    # VBP Calculation
    vbp_rj = np.zeros(67)
    with np.errstate(divide='ignore', invalid='ignore'):
        vbp_rj = vab_rj / denominator
    
    # 3. Calculate Ratio ICMS/VBP
    ratios = np.zeros(67)
    with np.errstate(divide='ignore', invalid='ignore'):
        ratios = icms_rj / vbp_rj
        
    # 4. Export
    # Load Labels
    labels = [f"Setor {i+1}" for i in range(67)]
    if path_labels.exists():
        with open(path_labels, 'r', encoding='latin1') as f:
            labels = [l.strip() for l in f if l.strip()]
            
    results = []
    print(f"\n{'ID':<3} | {'Setor':<40} | {'VBP (Mi)':<12} | {'ICMS (Mi)':<12} | {'Carga %':<10}")
    print("-" * 90)
    
    for i in range(67):
        vbp = vbp_rj[i]
        icms = icms_rj[i]
        ratio = ratios[i]
        label = labels[i][:40] if i < len(labels) else f"Setor {i+1}"
        
        # Handle NaN/Inf
        if not np.isfinite(ratio): ratio = 0.0
        if not np.isfinite(vbp): vbp = 0.0
        
        results.append({
            "id": i+1,
            "label": labels[i], # Full label
            "vbp": vbp,
            "icms": icms,
            "ratio": ratio
        })
        
        # Print only significant ones or first 10 + last 5
        # Print top 20 by ratio
    
    # Sort by ratio
    results_sorted = sorted(results, key=lambda x: x['ratio'], reverse=True)
    
    for r in results_sorted:
        lbl = r['label'][:40]
        # Basic ASCII safe print
        try:
            lbl_safe = lbl.encode('ascii', 'ignore').decode('ascii')
        except:
            lbl_safe = "Label Error"
            
        print(f"{r['id']:<3} | {lbl_safe:<40} | {r['vbp']:<12.1f} | {r['icms']:<12.1f} | {r['ratio']*100:<10.2f}%")
        
    # CSV Export
    out_csv = OUTPUT_DIR / 'ICMS_Burden_RJ_Official.csv'
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"\n[OK] Results saved to CSV: {out_csv}")
    
    # Excel Export
    out_xlsx = OUTPUT_DIR / 'ICMS_Burden_RJ_Official.xlsx'
    pd.DataFrame(results).to_excel(out_xlsx, index=False, sheet_name='Carga_ICMS_RJ')
    print(f"[OK] Results saved to Excel: {out_xlsx}")
    
    # Calculate Total Effective Rate
    total_icms = np.sum(icms_rj)
    total_vbp = np.sum(vbp_rj)
    print(f"\nTOTAL ICMS (RJ): R$ {total_icms:,.2f} Mi")
    print(f"TOTAL VBP (RJ):  R$ {total_vbp:,.2f} Mi")
    print(f"CARGA MÉDIA:     {(total_icms/total_vbp)*100:.2f}%")
    
    # Auto-open (Windows)
    try:
        os.startfile(out_xlsx)
        print("[OK] Opening Excel file...")
    except Exception as e:
        print(f"[NOTE] Could not auto-open file: {e}")

if __name__ == "__main__":
    run()
