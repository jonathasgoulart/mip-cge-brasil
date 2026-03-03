import csv
import os

def check_headers():
    data_dir = 'data/processed/mip_2015'
    for i in range(1, 16):
        path = os.path.join(data_dir, f"{i:02d}.csv")
        if not os.path.exists(path): continue
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Try to find the first non-empty row that looks like a header
            print(f"\n--- File {i:02d}.csv ---")
            for row_idx in range(10):
                try:
                    row = next(reader)
                    if any(len(str(h)) > 5 for h in row):
                        cols = [f"{idx}:{str(h)[:30]}" for idx, h in enumerate(row) if h]
                        print(f"Row {row_idx} Headers (sample): {cols[:10]}")
                        if len(row) > 70:
                            print(f"End Headers: {cols[-5:]}")
                except StopIteration:
                    break

if __name__ == "__main__":
    check_headers()
