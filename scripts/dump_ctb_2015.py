
import pandas as pd
import json
import os

FILE_PATH = r"c:\Users\jonat\Documents\MIP e CGE\data\ctb_1990-2024_0.xlsx"
OUTPUT_PATH = r"c:\Users\jonat\Documents\MIP e CGE\output\ctb_2015_dump.json"

def dump_all():
    print("Dumping all 2015 data (Col Index 26)...")
    try:
        # Load headerless to access by index safely
        df = pd.read_excel(FILE_PATH, sheet_name=0, header=None)
        
        # Col 26 is 2015 (verified previously: 0=1989/Names, 1=1990... 26=2015)
        # Actually in previous step: 1990 was Col 1.
        # Let's verify: Col 1 = 1990.
        # 1990 -> 1
        # 2015 -> 1 + (2015 - 1990) = 26. Correct.
        
        data_col = 26
        name_col = 0
        
        c = 0
        result = {}
        for i, row in df.iterrows():
            if i < 4: continue # Skip metadata
            
            try:
                name = str(row.iloc[name_col]).strip()
                val = row.iloc[data_col]
                
                # Try convert to float
                try:
                    fval = float(val)
                    if fval > 0:
                        result[f"{i}_{name}"] = fval
                        c+=1
                except:
                    pass
            except Exception as e:
                pass
                
        print(f"Extracted {c} rows.")
        # Save to JSON
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"Dump saved to {OUTPUT_PATH}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_all()
