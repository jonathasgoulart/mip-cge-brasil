
import xlrd
import os

def check_structure():
    path = 'data/raw/contas_regionais_2021/Tabela1.xls'
    print(f"Checking {path}...")
    
    wb = xlrd.open_workbook(path, on_demand=True)
    print(f"Number of sheets: {wb.nsheets}")
    print(f"Sheet Names: {wb.sheet_names()}")
    
    # Iterate from sheet 2 (3rd sheet) onwards
    for i in range(2, wb.nsheets):
        sheet = wb.sheet_by_index(i)
        print(f"\n--- Sheet {i}: {sheet.name} ---")
        
        # State: Line 4 (Index 3)
        try:
            state_val = sheet.cell_value(3, 0) # Col A
            print(f"Line 4 (State Candidate): {state_val}")
        except Exception as e:
            print(f"Error reading Line 4: {e}")

        # Sector: Line 5 (Index 4)
        try:
            sector_val = sheet.cell_value(4, 0) # Col A
            print(f"Line 5 (Sector Candidate): {sector_val}")
        except Exception as e:
            print(f"Error reading Line 5: {e}")
            
        # VAB: Line 54 (Index 53), Col F (Index 5)
        try:
            vab_val = sheet.cell_value(53, 5)
            print(f"Line 54, Col F (VAB 2021 Candidate): {vab_val}")
        except Exception as e:
            print(f"Error reading VAB: {e}")
            
        # Stop after 3 sheets to separate log
        if i >= 4: break

if __name__ == "__main__":
    check_structure()
