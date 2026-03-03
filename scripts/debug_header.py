
import csv
import os

path = 'data/processed/mip_2015/01.csv'
with open(path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i > 15: break
        for col_idx, val in enumerate(row):
            if "Agricultura" in val or "01" == val.strip():
                print(f"FOUND 'Agricultura' (or 01) at Row {i+1} Col {col_idx}: {val}")
        
    print("Done")
