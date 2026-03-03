
import csv
import os
import numpy as np

def parse_val(s):
    try:
        return float(s.replace('.', '').replace(',', '.'))
    except:
        return 0.0

def check_total_row():
    path = 'data/processed/mip_2015/01.csv'
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find "Total" row
    total_row = None
    for line in reversed(lines):
        if line.startswith("Total,"):
            total_row = line
            break
            
    if not total_row:
        print("Total row not found.")
        return

    # Parse CSV line
    reader = csv.reader([total_row])
    row = next(reader)
    
    print(f"Total Row Length: {len(row)}")
    
    # Try slice 6 to 6+67 (Supply matrix usually Col 0-5 are summaries)
    start_col = 6
    end_col = 6 + 67
    
    x_vec = []
    for val in row[start_col:end_col]:
        x_vec.append(parse_val(val))
        
    x_vec = np.array(x_vec)
    total_x = np.sum(x_vec)
    
    print(f"Slice [{start_col}:{end_col}] Sum: {total_x:,.2f}")
    
    # Try next block (maybe Uses?)
    # Just to be sure
    slice2 = []
    for val in row[end_col:]:
        slice2.append(parse_val(val))
    print(f"Remaining Columns Sum: {np.sum(slice2):,.2f}")
    
    # Check Col 2 (Total Supply)
    print(f"Col 2 (Total Supply): {parse_val(row[2]):,.2f}")

if __name__ == "__main__":
    check_total_row()
