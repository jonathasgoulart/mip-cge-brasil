import pandas as pd

FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\2026.01.08.xls"

def deep_inspect():
    """
    Deep inspection - now that we know Col 0 = UFs
    """
    
    print("="*70)
    print("CONFAZ DEEP STRUCTURE ANALYSIS")
    print("="*70)
    
    # Read more rows now
    df = pd.read_excel(FILE_PATH, header=None, nrows=200)
    
    print(f"\nTotal shape: {df.shape}")
    
    # Count occurrences of each UF in column 0
    print(f"\n[UF FREQUENCY IN COL 0]:")
    print("-"*70)
    
    UFS = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
           'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
           'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    
    uf_counts = {}
    for uf in UFS:
        count = (df[0] == uf).sum()
        if count > 0:
            uf_counts[uf] = count
    
    print(f"UF appearances in first 200 rows:")
    for uf, count in sorted(uf_counts.items()):
        print(f"  {uf}: {count} times")
    
    # Check if there's a month/year pattern
    print(f"\n[LOOKING FOR MONTH/YEAR COLUMNS]:")
    print("-"*70)
    
    # Sample rows for each UF
    print(f"\n[SAMPLE: First 3 occurrences of 'SP']:")
    sp_rows = df[df[0] == 'SP'].head(3)
    print(sp_rows.iloc[:, :10].to_string())  # First 10 columns
    
    # Check column 1-5 for potential month/year
    print(f"\n[COLUMNS 1-5 for SP rows]:")
    if len(sp_rows) > 0:
        for idx, row in sp_rows.iterrows():
            print(f"Row {idx}: {row[1:6].tolist()}")
    
    # See if we can find total row
    print(f"\n[LOOKING FOR 'TOTAL' OR 'BRASIL' ROWS]:")
    print("-"*70)
    total_rows = df[df[0].astype(str).str.contains('Total|TOTAL|Brasil|BRASIL', na=False, case=False)]
    if len(total_rows) > 0:
        print(f"Found {len(total_rows)} total rows")
        print(total_rows.iloc[:, :10].to_string())
    
    # Check the header row (row 0)
    print(f"\n[ROW 0 - LIKELY HEADER]:")
    print("-"*70)
    header_row = df.iloc[0, :30].tolist()
    print(f"First 30 values: {header_row}")
    
    return df

if __name__ == "__main__":
    deep_inspect()
