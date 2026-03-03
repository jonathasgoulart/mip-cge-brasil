import csv

def debug_sectors():
    path = 'data/processed/mip_2015/11.csv'
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        [next(reader) for _ in range(5)]
        sectors = []
        for row in reader:
            if not row or not row[1].strip(): continue
            label = row[1].strip()
            # If it has numbers, it's likely a data row
            sectors.append(label)
        
        print(f"Total rows found: {len(sectors)}")
        for i, s in enumerate(sectors):
            print(f"{i:03d}: {s}")

if __name__ == "__main__":
    debug_sectors()
