
import pandas as pd
import os

FILE_PATH = r"c:\Users\jonat\Documents\MIP e CGE\data\ctb_1990-2024_0.xlsx"

def inspect():
    if not os.path.exists(FILE_PATH):
        print("File not found.")
        return

    try:
        # Load all sheets to see names
        xls = pd.ExcelFile(FILE_PATH)
        print("Sheets:", xls.sheet_names)
        
        # Read Sheet 1 (Values)
        df1 = pd.read_excel(xls, sheet_name=0, header=None, nrows=10)
        print("\n--- Sheet 1 Head ---")
        print(df1.to_string())

        # Read Sheet 2 (% GDP)
        df2 = pd.read_excel(xls, sheet_name=1, header=None, nrows=10)
        print("\n--- Sheet 2 Head ---")
        print(df2.to_string())
        
        # Try to find 2015 year in Sheet 1
        # Re-read with better header guess if needed later
        
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    inspect()
