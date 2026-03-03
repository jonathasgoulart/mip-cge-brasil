
import xlrd
import os
import glob
import re

def run():
    print("=== AUDITORIA DE VAB REGIONAL 2021 (CÉLULA F54) ===")
    
    FOLDER = 'data/raw/contas_regionais_2021'
    # Pattern to find all Tabela*.xls
    files = glob.glob(os.path.join(FOLDER, '*.xls'))
    
    results = []
    
    # Map File Number to State Name (Approximate, based on usual order or extracting from B4/B40)
    # Tabela 2 is usually RO. Tabela 33 is BR?
    # Let's read the State Name from the file itself (usually Row 40 or 5?)
    
    for path in sorted(files, key=lambda x: int(re.search(r'Tabela(\d+)', x).group(1)) if re.search(r'Tabela(\d+)', x) else 999):
        fname = os.path.basename(path)
        try:
            wb = xlrd.open_workbook(path, on_demand=True)
            # Typically Sheet 1 (Index 1) has the Summary Table if similar to Tabela33.
            # But let's check Index 0 first if it looks right, or Index 1. 
            # User said "segunda aba" (Index 1).
            
            if wb.nsheets > 1:
                sh = wb.sheet_by_index(1) 
            else:
                sh = wb.sheet_by_index(0)
                
            # Target: Line 54 (Index 53), Col F (Index 5)
            target_row = 53
            target_col = 5
            
            val_2021 = 0.0
            state_name = "Unknown"
            
            if sh.nrows > target_row:
                cell_val = sh.cell_value(target_row, target_col)
                # State name usually in Row 39 or 40, Col A (Index 0)
                try:
                    state_name = sh.cell_value(39, 0) # Line 40
                except:
                    pass
                
                # If cell_val is empty, try looking around
                if isinstance(cell_val, str):
                    val_2021 = cell_val # Parse later
                else:
                    val_2021 = float(cell_val)
            
            results.append((fname, state_name, val_2021))
            
        except Exception as e:
            results.append((fname, "Error", str(e)))
            
    # Print content
    total_extracted = 0.0
    
    print(f"{'Arquivo':<15} | {'Estado (A40)':<20} | {'VAB 2021 (F54)':<20} | {'Valor'}")
    print("-" * 75)
    
    for fname, st, val in results:
        v_float = 0.0
        try:
             v_float = float(val)
        except:
             pass
        total_extracted += v_float
        print(f"{fname:<15} | {st:<20} | {val:<20} | {v_float:,.0f}")
        
    print("-" * 75)
    print(f"SOMA TOTAL EXTRAÍDA: {total_extracted/1e6:,.2f} Trilhões")

if __name__ == "__main__":
    run()
