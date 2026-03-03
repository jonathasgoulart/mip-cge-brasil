
import pandas as pd

FILE_PATH = r"c:\Users\jonat\Documents\MIP e CGE\data\ctb_1990-2024_0.xlsx"

def debug():
    try:
        df = pd.read_excel(FILE_PATH, sheet_name=0, header=None)
        print("--- Row Names (Col 0) ---")
        for i, row in df.iterrows():
            if pd.notna(row[0]):
                val = str(row[0]).strip()
                if len(val) > 1:
                    print(f"{i}: {val}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    debug()
