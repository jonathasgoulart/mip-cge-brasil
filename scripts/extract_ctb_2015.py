

import pandas as pd
import os
import json

FILE_PATH = r"c:\Users\jonat\Documents\MIP e CGE\data\ctb_1990-2024_0.xlsx"
OUTPUT_PATH = r"c:\Users\jonat\Documents\MIP e CGE\output\federal_taxes_2015.json"

def extract():
    print("Loading simplified Excel...")
    try:
        # Load Sheet 0 (Values), header=None to handle pure data extraction by index
        df = pd.read_excel(FILE_PATH, sheet_name=0, header=None)
        
        # Column 0: Names
        # Column 26: 2015 data (Assuming 1990 is Col 1. 2015 = 1 + (2015-1990) = 26)
        
        data_col_idx = 26
        
        extracted = {}
        print(f"Extracting from Column Index: {data_col_idx}")
        
        # Iterate rows starting from row 5 (skip headers)
        for index, row in df.iterrows():
            if index < 5: continue
            
            name = str(row.iloc[0]).strip()
            try:
                val = float(row.iloc[data_col_idx])
            except:
                val = 0.0

            # Map to standard keys
            if name == "IPI": extracted["IPI"] = val
            elif "IPI" in name and "Total" in name: extracted["IPI"] = val # Fallback
            
            if "Importação" in name and "Imposto" in name: extracted["II"] = val
            
            # Income
            if "Imposto de Renda" in name and "Total" in name: extracted["IR_Total"] = val # Catch specific total row
            if name == "Imposto de Renda": extracted["IR_Total"] = val # Exact match often used as group header
            
            if "Pessoas Jurídicas" in name: extracted["IRPJ"] = val
            if "Pessoas Físicas" in name: extracted["IRPF"] = val
            if "Retido na Fonte" in name: extracted["IRRF"] = val
            
            # Social Contributions
            if "COFINS" in name and ("Total" in name or len(name) < 10): extracted["COFINS"] = val
            if "PIS" in name and "PASEP" in name: extracted["PIS_PASEP"] = val
            if "CSLL" in name: extracted["CSLL"] = val
            if "IOF" in name: extracted["IOF"] = val
            if "CIDE" in name and "Combustíveis" in name: extracted["CIDE"] = val
            
            if "Receita Administrada pela RFB" in name: extracted["Total_Administrada"] = val
            if "Receita Total" in name: extracted["Total_Geral"] = val

        print("Extracted Data (2015):")
        print(json.dumps(extracted, indent=2))
        
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(extracted, f, indent=2)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract()
