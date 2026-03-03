
import pandas as pd
import json
import os

FILE_PATH = r"c:\Users\jonat\Documents\MIP e CGE\data\ctb_1990-2024_0.xlsx"
OUTPUT_PATH = r"c:\Users\jonat\Documents\MIP e CGE\output\ctb_2021_dump.json"

def dump_2021():
    print("Dumping all 2021 data...")
    try:
        df = pd.read_excel(FILE_PATH, sheet_name=0, header=None)
        
        # 1990 = Col 1
        # 2021 = 1 + (2021 - 1990) = 32
        data_col = 32
        name_col = 0
        
        c = 0
        result = {}
        for i, row in df.iterrows():
            if i < 4: continue
            
            try:
                name = str(row.iloc[name_col]).strip()
                val = row.iloc[data_col]
                try:
                    fval = float(val)
                    if fval > 0:
                        result[f"{i}_{name}"] = fval
                        c+=1
                except:
                    pass
            except:
                pass
                
        # Also grab GDP 2021 if available (check last rows)
        
        print(f"Extracted {c} rows for 2021.")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_2021()
