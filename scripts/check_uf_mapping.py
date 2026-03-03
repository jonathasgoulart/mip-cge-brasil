import xlrd
import os

def check_titles():
    data_dir = 'data/raw/contas_regionais_2021'
    for i in range(1, 34):
        filename = f'Tabela{i}.xls'
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            continue
        
        try:
            wb = xlrd.open_workbook(path, on_demand=True)
            sheet = wb.sheet_by_index(0)
            # Find the first row that is not empty and seems like a title
            title = "Unknown"
            for row in range(5):
                val = str(sheet.cell_value(row, 0)).strip()
                if val and len(val) > 10:
                    title = val
                    break
            print(f"{i:02d}: {title}")
        except Exception as e:
            print(f"{i:02d}: Error {e}")

if __name__ == "__main__":
    check_titles()
