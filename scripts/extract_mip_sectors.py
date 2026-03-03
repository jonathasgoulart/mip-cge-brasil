import csv
import json

def extract_mip_sectors():
    """
    Extract MIP 67 sector names from 05.csv
    """
    
    print("="*70)
    print("EXTRACTING MIP 67 SECTOR NAMES")
    print("="*70)
    
    FILE_PATH = 'data/processed/mip_2015/05.csv'
    
    sectors = {}
    
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Skip header rows
        for _ in range(4):
            next(reader)
        
        # Read 67 sectors
        for i, row in enumerate(reader):
            if i >= 67:
                break
            
            if len(row) >= 2:
                code = row[0].strip()
                description = row[1].strip()
                
                sectors[i + 1] = {  # 1-indexed
                    "code": code,
                    "description": description
                }
    
    print(f"\nExtracted {len(sectors)} MIP sectors\n")
    
    # Display all
    print("MIP 67 SECTORS:")
    print("-"*70)
    for sector_num in sorted(sectors.keys()):
        info = sectors[sector_num]
        print(f"{sector_num:2d} - {info['description']}")
    
    # Save to JSON
    output = {
        "total_sectors": len(sectors),
        "sectors": sectors,
        "source": "MIP 2015 - Tabela 05.csv"
    }
    
    with open('output/mip_67_sectors.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved to: output/mip_67_sectors.json\n")
    
    return sectors

if __name__ == "__main__":
    extract_mip_sectors()
