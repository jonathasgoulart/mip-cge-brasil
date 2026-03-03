
import os
import xlrd
import collections
import json

def run():
    print("=== DEBUGGING REGIONAL ACCOUNTS BUCKETS (SP) ===")
    
    RAW_DIR = 'data/raw/contas_regionais_2021'
    # Find SP file
    # Filenames are Tabela1, Tabela2... we don't know which is SP.
    # We loop and check cell A4.
    
    sp_file = None
    all_files = [f for f in os.listdir(RAW_DIR) if f.startswith('Tabela') and f.endswith('xls')]
    
    for fname in all_files:
        path = os.path.join(RAW_DIR, fname)
        try:
            wb = xlrd.open_workbook(path, on_demand=True)
            if wb.nsheets < 3: continue
            
            # Check Sheet 2 (Index 2)
            sheet = wb.sheet_by_index(2)
            state_name = sheet.cell_value(3, 0)
            
            if "Paulo" in str(state_name):
                print(f"Found SP File: {fname} ({state_name})")
                sp_file = path
                break
        except: pass
        
    if not sp_file:
        print("SP File not found!")
        return

    # Read Buckets for SP
    wb = xlrd.open_workbook(sp_file, on_demand=True)
    # Iterate sheets? No, one sheet per state normally?
    # Wait, previous script iterated sheets AND files.
    # Maybe multiple states per file?
    # Let's inspect the found file's sheets.
    
    print(f"Sheets in {os.path.basename(sp_file)}: {wb.nsheets}")
    
    # We found SP in the loop above. Let's start from there.
    # We assume the layout:
    # Row 5 (Index 4) -> Sector Name
    # Row 54 (Index 53) -> VAB 2021 (Col F)
    
    # Let's iterate rows 4 to 25 (sectors usually listed there or one per sheet?)
    # Previous script: `sheet = wb.sheet_by_index(i)`. "Header Extraction... Row 4 -> State, Row 5 -> Sector".
    # This implies ONE SECTOR PER SHEET?
    # If so, iterating sheets gives us the sectors.
    
    print(f"{'Sheet':<5} | {'Sector Name':<60} | {'VAB 2021 (Scale?)'}")
    
    total_vab = 0.0
    
    # Manufacturing Bucket?
    manuf_vab = 0.0
    
    for i in range(2, wb.nsheets):
        sheet = wb.sheet_by_index(i)
        try:
            sector = str(sheet.cell_value(4, 0)).strip()
            val = sheet.cell_value(53, 5) # F54
            if not isinstance(val, (int, float)): val = 0.0
            
            # Print
            # Scale? Previous script summed raw values.
            # Usually Million Reais.
            
            print(f"{i:<5} | {sector:<60} | {val:,.2f}")
            
            total_vab += val
            
            if "transforma" in sector.lower():
                manuf_vab += val
                
        except: pass
        
    print("-" * 50)
    print(f"Total SP VAB: {total_vab:,.2f}")
    print(f"Manufacturing VAB: {manuf_vab:,.2f}")
    
    # Inspect Telecom Tax Composition
    print("\n=== TELECOM (ID 50) TAX COMPOSITION ===")
    path_tax = 'data/processed/2021_final/tax_matrix.json'
    try:
        with open(path_tax, 'r') as f:
            full_tax = json.load(f).get('taxes_by_type', {})
            
        # Telecom is Index 49 (Subscript 50-1)?
        # Let's verify labels, but standard is 49.
        idx = 49
        
        total_tax_structure = 0.0
        for k, vec in full_tax.items():
            if len(vec) > idx:
                val = vec[idx]
                total_tax_structure += val
                print(f"{k:<10}: {val:,.1f} Mi")
                
        print(f"Total Structural: {total_tax_structure:,.1f} Mi")
        
    except Exception as e:
        print(f"Tax Check Failed: {e}")

if __name__ == "__main__":
    run()
