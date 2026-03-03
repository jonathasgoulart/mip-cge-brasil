import xlrd
import sys

def list_sheets(path):
    print(f"--- Scanning {path} ---")
    try:
        # on_demand=True é crucial para memória, carrega apenas estrutura
        book = xlrd.open_workbook(path, on_demand=True)
        print(f"Total Sheets: {book.nsheets}")
        print("Sheet Names:")
        for name in book.sheet_names():
            print(f"  {name}")
    except Exception as e:
        print(f"Error: {e}")
    sys.stdout.flush()

if __name__ == "__main__":
    list_sheets('data/raw/contas_regionais_2021/Tabela1.xls')
    list_sheets('data/raw/contas_regionais_2021/Tabela2.xls')
