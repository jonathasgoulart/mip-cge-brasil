import xlrd
import os

def debug_ro():
    path = 'data/raw/contas_regionais_2021/Tabela2.xls'
    print(f"Opening {path}...")
    wb = xlrd.open_workbook(path)
    
    # Check Sheet 2 (usually Agro?)
    # Print clean text for rows 0-20
    s_idx = 2
    try:
        sheet = wb.sheet_by_index(s_idx)
        print(f"--- Sheet {s_idx} Raw Content ---")
        for r in range(min(20, sheet.nrows)):
            row = sheet.row_values(r)
            txt = " ".join([str(x) for x in row if str(x).strip()])
            print(f"Row {r}: {txt}")
            
    except Exception as e:
        print(e)

if __name__ == "__main__":
    debug_ro()
