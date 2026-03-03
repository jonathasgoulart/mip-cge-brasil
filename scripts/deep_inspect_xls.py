
import pandas as pd
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def deep_inspect():
    path = 'data/raw/mip_2015_67.xls'
    xl = pd.ExcelFile(path)
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, nrows=50) # Read enough for headers
        print(f"\n--- SHEET {sheet} ---")
        print(f"Shape: {pd.read_excel(path, sheet_name=sheet).shape}")
        print(f"Sample Rows (First 5):")
        print(df.iloc[:5, :5])

if __name__ == "__main__":
    deep_inspect()
