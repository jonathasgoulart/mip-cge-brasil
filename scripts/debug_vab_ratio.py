
import json
import numpy as np
import csv

def parse_float(x):
    try:
        if isinstance(x, str):
            return float(x.replace('.','').replace(',','.'))
        return float(x)
    except:
        return 0.0

def run():
    print("=== DIAGNOSTICO DE CARGA TRIBUTARIA ===")
    
    # 1. Load VAB (Denominator 1)
    vab_vec = np.load('output/intermediary/VAB_nacional.npy')
    
    # 2. Load Taxes (Numerator)
    with open('output/tax_data.json', 'r') as f:
        tax_data = json.load(f)
        
    tax_vec = np.zeros(67)
    tax_source = tax_data.get('taxes_by_type', tax_data) # Support both
    for k, v in tax_source.items():
        if k == 'metadata': continue
        if not isinstance(v, list): continue
        tax_vec += np.array(v, dtype=float)
        
    print(f"Total Tax Loaded: {np.sum(tax_vec):,.2f}")
        
    # 3. Load VP (Valor da Producao) - Denominator 2
    # From 01.csv (Make Matrix) -> Total Output per Activity (Column ??)
    # Wait, 01.csv is Products x Activities.
    # Sum of columns is Total Production of the Activity (VP).
    # We need to sum the columns of 01.csv corresponding to each sector.
    
    # Re-read 01.csv with correct offset (Col 7 to A)
    path_01 = 'data/processed/mip_2015/01.csv'
    vp_vec_2015 = np.zeros(67)
    
    with open(path_01, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        
    # Find start row (from previous knowledge, row 6 for data)
    start_row = 0
    for i, row in enumerate(reader):
        if len(row) > 0 and row[0].strip().startswith("0191"):
             start_row = i
             break
             
    # Sum columns 7 to 73 (67 cols)
    col_start = 7
    
    # Iterate rows (Products)
    # Actually, VP (Valor da Producao) of the SECTOR is the sum of everything it produces.
    # So we sum the COLUMNS.
    
    for c in range(67):
        col_idx = col_start + c
        col_sum = 0.0
        row_count = 0
        for r in range(start_row, len(reader)):
            row = reader[r]
            if len(row) > col_idx:
                 val = parse_float(row[col_idx])
                 col_sum += val
            else:
                 break
            row_count += 1
            if row_count >= 128: break # 128 products
            
        vp_vec_2015[c] = col_sum
        
    # Scale VP 2015 to 2021 Estimate?
    # We assume VP scales with VAB? Or just check ratios.
    # We can calculate the 2015 VP/VAB ratio and apply to 2021 VAB.
    # But simpler: calculate Tax/VP using 2015 VP scaled by (VAB2021/VAB2015).
    # Let's just output the implied "Markup" (VAB/VP).
    
    # Labels
    labels = [f"Setor {i+1}" for i in range(67)]
    try:
        with open('output/intermediary/sector_labels.txt', 'r', encoding='latin1') as f:
            labels = [l.strip() for l in f if l.strip()]
    except: pass
    
    print(f"{'ID':<3} | {'Setor':<40} | {'Tax/VAB (%)':<12} | {'Tax/Sales Est (%)':<15} | {'Margin (VAB/VP)':<15}")
    print("-" * 100)
    
    anomalies = [7, 12, 16, 18, 49, 37] # Indexes of Meat(8), Textile(13), Paper(17), OilRef(19), Telecom(50), Energy(38)
    # Python Index = ID - 1
    
    for idx in range(67):
        tax = tax_vec[idx]
        vab = vab_vec[idx]
        vp_2015 = vp_vec_2015[idx]
        
        # Estimate VP 2021 based on VAB growth?
        # Better: Calculate "Technical Coefficient" of VAB: (VAB/VP)_2015
        # We don't have VAB_2015 readily loaded here (it's in OLD json but I can infer).
        # Let's just use VP_2015 as a relative weight.
        
        # Actually, let's just look at Tax/VAB.
        # And check if the sector is known for high Turnover.
        
        burden = (tax/vab)*100 if vab > 0 else 0
        
        # Heuristic: Implied Sales Tax Rate considering a standard economy
        # If Burden is 300% and Margin is 5%, then Sales Tax is 15%.
        # Let's SOLVE for Margin assuming Sales Tax ~ 15-20%.
        # Margin = Tax_Rate_Sales / Burden_VAB
        implied_margin = (18.0 / burden) if burden > 0 else 1.0 # Assuming 18% avg sales tax
        
        # If I print this, and it says "Implied Margin 2%", it confirms the theory.
        
        if burden > 50 or idx in [5, 49, 37]: # Filter high ones
             safe_label = labels[idx][:40].encode('ascii', 'ignore').decode('ascii')
             print(f"{idx+1:<3} | {safe_label:<40} | {burden:6.1f}%      | {'~15-25%?':<15} | Implied: {implied_margin*100:.1f}%")

if __name__ == "__main__":
    run()
