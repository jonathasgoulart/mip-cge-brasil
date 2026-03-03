import csv

def check_mip_tables():
    """Check what each MIP table contains"""
    
    tables = {
        11: "data/processed/mip_2015/11.csv",
        12: "data/processed/mip_2015/12.csv",
        13: "data/processed/mip_2015/13.csv",
        14: "data/processed/mip_2015/14.csv",
        15: "data/processed/mip_2015/15.csv"
    }
    
    for num, path in tables.items():
        print(f"\n{'='*70}")
        print(f"TABELA {num}")
        print("="*70)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i >= 5:  # First 5 rows
                        break
                    if row and row[0]:
                        print(f"Row {i}: {row[0][:80]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_mip_tables()
