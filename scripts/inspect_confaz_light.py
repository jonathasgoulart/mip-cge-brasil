import xlrd
import os

FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\2026.01.08.xls"

def inspect_confaz_light():
    """Memory-efficient inspection - only first 20 rows"""
    
    print("="*70)
    print("CONFAZ ICMS FILE STRUCTURE (Light Inspection)")
    print("="*70)
    
    try:
        # Open with xlrd (lower memory than pandas)
        wb = xlrd.open_workbook(FILE_PATH, on_demand=True)
        
        print(f"\nSheets: {wb.sheet_names()}")
        
        # Read first sheet
        sheet = wb.sheet_by_index(0)
        
        print(f"\nDimensions: {sheet.nrows} rows x {sheet.ncols} cols")
        print(f"\n[First 20 rows, first 10 columns]:")
        print("-"*70)
        
        for row_idx in range(min(20, sheet.nrows)):
            row_data = []
            for col_idx in range(min(10, sheet.ncols)):
                try:
                    cell = sheet.cell_value(row_idx, col_idx)
                    if cell != '':
                        row_data.append(f"C{col_idx}={str(cell)[:30]}")
                except:
                    pass
            
            if row_data:
                print(f"Row {row_idx}: {' | '.join(row_data)}")
        
        # Check column D and E specifically (Year and Month per user)
        print(f"\n[Column D and E - First 20 rows]:")
        print("-"*70)
        for row_idx in range(min(20, sheet.nrows)):
            try:
                col_d = sheet.cell_value(row_idx, 3)  # Column D (0-indexed)
                col_e = sheet.cell_value(row_idx, 4)  # Column E
                if col_d != '' or col_e != '':
                    print(f"Row {row_idx}: D={col_d} | E={col_e}")
            except:
                pass
        
        wb.release_resources()
        del wb
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_confaz_light()
