
import csv
import os

def parse_val(s):
    try:
        return float(s.replace('.', '').replace(',', '.'))
    except:
        return 0.0

def debug_cols():
    path = 'data/processed/mip_2015/01.csv'
    if not os.path.exists(path):
        print("01.csv not found")
        return

    col_sums = {}
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 4: continue
            if i >= 4 + 67: break # Limit to sectors
            
            for c_idx, val in enumerate(row):
                if c_idx not in col_sums: col_sums[c_idx] = 0.0
                col_sums[c_idx] += parse_val(val)
                
    print("--- Column Sums (01.csv 67 sectors) ---")
    for c_idx in sorted(col_sums.keys()):
        s = col_sums[c_idx]
        if s > 1000: # Filter empty/small
            print(f"Col {c_idx}: {s:,.2f}")

if __name__ == "__main__":
    debug_cols()
