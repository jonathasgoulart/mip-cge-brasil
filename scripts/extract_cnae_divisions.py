import pandas as pd
import json

def extract_cnae_divisions():
    """
    Extract actual CNAE division names from CONFAZ file
    """
    
    print("="*70)
    print("EXTRACTING CNAE DIVISIONS FROM CONFAZ")
    print("="*70)
    
    FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\2026.01.08.xls"
    
    # Read header row
    df = pd.read_excel(FILE_PATH, header=0, nrows=1)
    
    print(f"\nTotal columns: {len(df.columns)}")
    print(f"\nFirst column: {df.columns[0]}")
    
    # Extract CNAE division names (columns 1 onwards)
    cnae_divisions = {}
    
    for i, col_name in enumerate(df.columns[1:], start=1):
        # Column names should be like "Soma de Divisão: X - Nome"
        if "Divisão:" in str(col_name):
            # Extract division number and name
            parts = str(col_name).split("Divisão:")[1].strip()
            
            # Split on " - " to get number and description
            if " - " in parts:
                div_num_str, description = parts.split(" - ", 1)
                try:
                    div_num = int(div_num_str.strip())
                    cnae_divisions[div_num] = {
                        "column_index": i,
                        "description": description.strip(),
                        "full_name": col_name
                    }
                except:
                    pass
    
    print(f"\nExtracted {len(cnae_divisions)} CNAE divisions\n")
    
    # Display all
    print("CNAE DIVISIONS IN CONFAZ:")
    print("-"*70)
    for div_num in sorted(cnae_divisions.keys()):
        info = cnae_divisions[div_num]
        print(f"{div_num:2d} - {info['description']}")
    
    # Save to JSON
    output = {
        "total_divisions": len(cnae_divisions),
        "divisions": cnae_divisions,
        "source": "CONFAZ 2026.01.08.xls"
    }
    
    with open('output/cnae_divisions_confaz.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved to: output/cnae_divisions_confaz.json\n")
    
    return cnae_divisions

if __name__ == "__main__":
    extract_cnae_divisions()
