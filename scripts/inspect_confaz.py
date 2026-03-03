import pandas as pd
import os

FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\2026.01.08.xls"

def inspect_confaz():
    """Inspect CONFAZ ICMS file structure"""
    
    print("="*70)
    print("CONFAZ ICMS FILE INSPECTION")
    print("="*70)
    
    try:
        # Read with header=None to see raw structure
        df = pd.read_excel(FILE_PATH, sheet_name=0, header=None, nrows=30)
        
        print("\n[1] First 30 rows (raw):")
        print("-"*70)
        print(df.to_string())
        
        # Try to identify header row
        print("\n[2] Attempting to identify structure:")
        print("-"*70)
        
        # Look for year/month columns
        for i, row in df.iterrows():
            row_str = ' | '.join([str(x) for x in row.iloc[:10] if pd.notna(x)])
            if len(row_str) > 0:
                print(f"Row {i}: {row_str[:100]}")
            if i > 15:
                break
        
        # Read all sheets
        xls = pd.ExcelFile(FILE_PATH)
        print(f"\n[3] Available sheets: {xls.sheet_names}")
        
        # Get file info
        print(f"\n[4] File size: {os.path.getsize(FILE_PATH) / 1024:.1f} KB")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_confaz()
