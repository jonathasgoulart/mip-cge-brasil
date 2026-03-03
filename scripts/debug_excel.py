import xlrd
import os

def inspect():
    path = 'data/raw/contas_regionais_2021/Tabela11.xls' # PI
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0) # Sheet 0 (check summary)
    
    # Print rows 10 to 30
    for i in range(10, min(50, sheet.nrows)):
        print(f"Row {i}: {sheet.row_values(i)}")

    # Check Sheet 1 (Agro)
    if wb.nsheets > 1:
        print("\n--- Sheet 1 (Agro?) ---")
        sheet1 = wb.sheet_by_index(1)
        for i in range(10, min(30, sheet1.nrows)):
            print(f"S1 Row {i}: {sheet1.row_values(i)}")

if __name__ == "__main__":
    inspect()
