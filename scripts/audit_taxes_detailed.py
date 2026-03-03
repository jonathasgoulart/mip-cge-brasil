
import numpy as np
import pandas as pd
import json
import os
import csv

DATA_DIR = 'data/processed/mip_2015'
OUTPUT_DIR = 'output'

def audit_mip_taxes():
    print("--- AUDIT MIP 2015 TAXES ---")
    
    # Load Sector Names
    names = []
    with open(os.path.join(DATA_DIR, '05.csv'), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 4: continue
            if i >= 4 + 67: break
            names.append(row[1]) # Descricao is Col 1
            
    # Load Tax Data (Domestic)
    # Re-using logic from process_taxes but reading specifically to debug
    # We want the values for each sector to see who is paying.
    
    path_05 = os.path.join(DATA_DIR, '05.csv')
    
    taxes_dom = []
    
    with open(path_05, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 4: continue
            if i >= 4 + 67: break
            
            # Find the value in the last column (Total)
            # Inspecting row structure again:
            # Col 0: Code, Col 1: Name, Col 2: Resources... Col N: Total
            # We will grab the last non-empty numeric value
            val = 0.0
            for col in reversed(row):
                if col.strip():
                    try:
                        val = float(col.replace('.', '').replace(',', '.'))
                        break
                    except:
                        continue
            taxes_dom.append(val)
            
    # Top 10 Tax Payers
    df = pd.DataFrame({'Sector': names, 'Tax_Dom': taxes_dom})
    df = df.sort_values('Tax_Dom', ascending=False)
    
    print("\n--- TOP 10 SECTORS PAYING TAXES (05.csv) ---")
    print(df.head(10).to_string())
    
    total_mip = df['Tax_Dom'].sum()
    print(f"\nTotal MIP (05.csv) Taxes: {total_mip:,.2f} Million R$")
    
    # Load CTB Targets
    try:
        with open('output/ctb_2015_dump.json', 'r', encoding='utf-8') as f:
            ctb = json.load(f)
            
        print("\n--- CTB 2015 TARGETS (Million R$) ---")
        print(f"ICMS: {ctb.get('30_ICMS', 0):,.2f}")
        print(f"IPI: {ctb.get('10_Imposto sobre Produtos Industrializados', 0):,.2f}")
        print(f"ISS: {ctb.get('36_ISS', 0):,.2f}")
        print(f"PIS/PASEP: {ctb.get('18_Contribuição para o PIS/Pasep', 0) if '18_Contribuição para o PIS/Pasep' in ctb else ctb.get('18_Contribuiǜo para o PIS/Pasep', 0):,.2f}")
        # Note: keys in dump might have messy encoding characters, printed output will help guide.
        # Let's just print the relevant ones based on previous output.
        
        icms = 396428.49
        ipi = 48048.71
        iss = 54454.89
        pis_cofins = 52589.86 + 199876.0 # Approx 250k
        
        print(f"Target ICMS+IPI+ISS: {icms+ipi+iss:,.2f}")
        print(f"Target Broad Indirect (incl PIS/COFINS): {icms+ipi+iss+pis_cofins:,.2f}")
        
        diff = total_mip - (icms+ipi+iss)
        print(f"\nDifference (MIP - Target Core): {diff:,.2f}")
        
    except Exception as e:
        print(f"Could not load CTB dump: {e}")

if __name__ == "__main__":
    audit_mip_taxes()
