import csv
import numpy as np

def parse_smart(s):
    s = str(s).strip()
    if not s: return 0.0
    if ',' in s and '.' in s: return float(s.replace('.', '').replace(',', '.'))
    if ',' in s: return float(s.replace(',', '.'))
    try: return float(s)
    except: return 0.0

def check_14():
    path = 'data/processed/mip_2015/14.csv'
    Z = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        [next(reader) for _ in range(5)]
        for row in reader:
            if not row or not row[1].strip(): continue
            vals = [parse_smart(r) for r in row[2:69]]
            if len(vals) == 67: Z.append(vals)
            if len(Z) == 67: break
    
    Z = np.array(Z)
    col_sum = np.sum(Z, axis=0)[0]
    print(f"Column 0 sum (A_total from 14.csv): {col_sum:.4f}")

if __name__ == "__main__":
    check_14()
