import pandas as pd
import os

file_path = r'c:\Users\jonat\Documents\MIP e CGE\output\regional_matrices\MIP_2021_RJ.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    print(f"Sheets: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(file_path, sheet_name=sheet, index_col=0)
        print("Shape:", df.shape)
        print("Columns (Head):", df.columns[:10].tolist())
        print("Index (Tail):", df.index[-15:].tolist()) # Look at the bottom entries for Value Added components
        
        # Check for ICMS specific rows
        icms_rows = [i for i in df.index if 'ICMS' in str(i).upper() or 'IMPOSTO' in str(i).upper()]
        if icms_rows:
            print("Found Potential Tax Rows:", icms_rows)
            # Print values for first few sectors
            print(df.loc[icms_rows, df.columns[:5]])

except Exception as e:
    print(f"Error: {e}")
