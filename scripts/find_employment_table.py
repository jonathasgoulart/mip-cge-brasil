import xlrd
import os

def find_employment_table():
    data_dir = 'data/raw/contas_regionais_2021'
    for i in range(1, 34):
        path = os.path.join(data_dir, f'Tabela{i}.xls')
        if not os.path.exists(path): continue
        
        try:
            wb = xlrd.open_workbook(path, on_demand=True)
            sheet = wb.sheet_by_index(0)
            # Check first few rows for title
            title = ""
            for r in range(5):
                val = str(sheet.cell_value(r, 0)).strip()
                if val and len(val) > 10:
                    title = val
                    break
            print(f"Tabela {i:02d}: {title[:80]}")
        except Exception as e:
            print(f"Error Tabela {i}: {e}")

if __name__ == "__main__":
    find_employment_table()
