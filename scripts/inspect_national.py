import csv
import os

data_dir = 'data/processed/mip_2015'
for i in range(1, 16):
    filename = f'{i:02d}.csv'
    path = os.path.join(data_dir, filename)
    if not os.path.exists(path): continue
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        found = False
        for row_idx, row in enumerate(reader):
            if not row or len(row) < 2: continue
            label = str(row[1]).lower()
            if "produção total" in label or "producao total" in label or "valor adicionado bruto" in label:
                print(f"{filename} Row {row_idx}: {label}")
                found = True
        if not found:
            # Check headers
            f.seek(0)
            header = next(reader)
            if any("total" in str(h).lower() for h in header):
                 print(f"{filename} Header has total")
