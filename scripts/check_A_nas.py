import csv
import numpy as np

def check_11():
    path = 'data/processed/mip_2015/11.csv'
    Z = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        [next(reader) for _ in range(3)]
        for row in reader:
            if not row or not row[1].strip(): continue
            try:
                vals = [float(r.replace('.', '').replace(',', '.')) for r in row[3:70]]
                Z.append(vals)
            except:
                continue
            if len(Z) == 67: break
    
    Z = np.array(Z)
    col_sums = np.sum(Z, axis=0)
    print(f"Column sums (A_nas from 11.csv):")
    print(f"  Mean: {np.mean(col_sums):.4f}")
    print(f"  Max: {np.max(col_sums):.4f}")
    print(f"  Min: {np.min(col_sums):.4f}")

if __name__ == "__main__":
    check_11()
