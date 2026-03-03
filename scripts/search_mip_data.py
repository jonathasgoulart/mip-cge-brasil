import csv
import os

def search_keywords():
    data_dir = 'data/processed/mip_2015'
    keywords = ["valor adicionado", "pessoal ocupado", "ocupados", "empregos", "trabalho", "salários", "rendimento"]
    
    for i in range(1, 16):
        path = os.path.join(data_dir, f"{i:02d}.csv")
        if not os.path.exists(path): continue
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                if not row: continue
                line_content = " ".join(str(item) for item in row).lower()
                for kw in keywords:
                    if kw in line_content:
                        print(f"File {i:02d}, Row {row_idx}: Keyword '{kw}' found.")
                        # Print first few items of the row
                        print(f"  Content: {row[:2]}... (len {len(row)})")
                        break

if __name__ == "__main__":
    search_keywords()
