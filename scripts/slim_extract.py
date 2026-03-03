import xlrd
import numpy as np
import os

def extract_vab_2021():
    data_dir = 'data/raw/contas_regionais_2021'
    output_dir = 'output/intermediary'
    os.makedirs(output_dir, exist_ok=True)
    
    # Mapping UF indices (1-indexed based on file names)
    # Ex: Tabela2.xls is RO
    uf_indices = list(range(2, 9)) + list(range(10, 19)) + list(range(20, 24)) + list(range(25, 28)) + list(range(29, 33))
    
    # Each UF has ~19 activities (sheets 1 to 19)
    # We want Sheet X, Row that matches Year 2021, Column "VALOR A PREÇO CORRENTE" (index 5)
    
    # We will save a matrix of (27 UFs x 19 activities)
    vab_matrix = np.zeros((33, 20)) # Buffer for all potential indices
    
    print("Starting Slim Extraction (VAB 2021)...")
    
    for i in range(1, 34):
        filename = f'Tabela{i}.xls'
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            continue
            
        try:
            wb = xlrd.open_workbook(path, on_demand=True)
            # Iterate through sheets (1.1, 1.2, ..., 1.19)
            # Tabela X.1 is Total, so we usually want X.2 to X.19
            for sheet_idx in range(1, 20):
                sheet_name = f'Tabela{i}.{sheet_idx}'
                try:
                    sheet = wb.sheet_by_name(sheet_name)
                except:
                    continue
                
                # Find row for 2021
                # The data usually starts after header on line 6 (index 5)
                # But let's search for "2021" in the first column
                vab_2021 = 0.0
                for row_idx in range(sheet.nrows):
                    cell_val = str(sheet.cell_value(row_idx, 0)).strip()
                    if cell_val == "2021" or cell_val == "2021.0":
                        # Column 5 is "VALOR A PREÇO CORRENTE"
                        raw_val = sheet.cell_value(row_idx, 5)
                        try:
                            vab_2021 = float(raw_val)
                        except:
                            vab_2021 = 0.0
                        break
                
                vab_matrix[i, sheet_idx] = vab_2021
            print(f"  Extracted: {filename}")
        except Exception as e:
            print(f"  Error in {filename}: {e}")

    # Save the full matrix
    np.save(os.path.join(output_dir, 'vab_matrix_raw.npy'), vab_matrix)
    print(f"Done! Raw VAB matrix saved to {output_dir}/vab_matrix_raw.npy")

if __name__ == "__main__":
    extract_vab_2021()
