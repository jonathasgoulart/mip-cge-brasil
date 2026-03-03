import xlrd
import os

DATA_DIR = 'data/raw/contas_regionais_2021'

def inspect_file(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"{filename} not found.")
        return

    try:
        wb = xlrd.open_workbook(path, on_demand=True)
        sheet = wb.sheet_by_index(0) # First sheet
        
        print(f"\n--- Checking {filename} ---")
        # Print first 10 rows of column 0
        for i in range(min(10, sheet.nrows)):
            val = sheet.cell_value(i, 0)
            print(f"Row {i}: {val}")
            
    except Exception as e:
        print(f"Error reading {filename}: {e}")

def run():
    # Check potential candidates
    inspect_file('Tabela1.xls')
    inspect_file('Tabela11.xls')
    inspect_file('Tabela20.xls')
    inspect_file('Tabela33.xls')

if __name__ == "__main__":
    run()
