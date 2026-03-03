import pandas as pd
import os

def convert_xls_to_csv(file_path, output_dir):
    print(f"Reading {file_path}...")
    try:
        xl = pd.ExcelFile(file_path, engine='xlrd')
        print(f"Sheets found: {xl.sheet_names}")
        
        for sheet in xl.sheet_names:
            # Clean sheet name for filename
            clean_name = sheet.replace(" ", "_").replace("/", "-")
            output_file = os.path.join(output_dir, f"{clean_name}.csv")
            
            print(f"  Converting sheet '{sheet}' to {output_file}...")
            df = pd.read_excel(xl, sheet_name=sheet)
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"  Done: {output_file}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Process MIP 2015
mip_path = 'data/raw/mip_2015_67.xls'
mip_out = 'data/processed/mip_2015'
os.makedirs(mip_out, exist_ok=True)
convert_xls_to_csv(mip_path, mip_out)

# Process Contas Regionais Tabela 1 (Nacional)
cr1_path = 'data/raw/contas_regionais_2021/Tabela1.xls'
cr1_out = 'data/processed/contas_regionais_2021_t1'
os.makedirs(cr1_out, exist_ok=True)
convert_xls_to_csv(cr1_path, cr1_out)

# Process Contas Regionais Tabela 2 (Por UF)
cr2_path = 'data/raw/contas_regionais_2021/Tabela2.xls'
cr2_out = 'data/processed/contas_regionais_2021_t2'
os.makedirs(cr2_out, exist_ok=True)
convert_xls_to_csv(cr2_path, cr2_out)

print("All conversions finished!")
