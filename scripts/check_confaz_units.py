import pandas as pd

FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\2026.01.08.xls"

def manual_check():
    """Check actual raw values from the file"""
    
    df = pd.read_excel(FILE_PATH, header=0)
    
    print("="*70)
    print("MANUAL RAW VALUE CHECK")
    print("="*70)
    
    # Get SP row
    sp_row = df[df.iloc[:, 0] == 'SP']
    
    if len(sp_row) > 0:
        print("\nSP Row (first 10 CNAE columns):")
        print("-"*70)
        
        for i in range(1, min(11, len(df.columns))):
            col_name = df.columns[i]
            value = sp_row.iloc[0, i]
            
            print(f"\nColumn {i}: {col_name[:50]}...")
            print(f"  Raw value: {value}")
            print(f"  As millions: R$ {value/1e6:.2f} Mi")
            print(f"  As thousands: R$ {value/1e3:.2f} Mil")
            print(f"  As units: R$ {value:.2f}")
        
        # Sum all CNAE columns for SP
        sp_total_raw = sp_row.iloc[0, 1:].sum()
        
        print(f"\n{'='*70}")
        print("SP TOTAL (all CNAEs):")
        print("="*70)
        print(f"Raw sum: {sp_total_raw:,.2f}")
        print(f"\nInterpretations:")
        print(f"  If in REAIS: R$ {sp_total_raw/1e9:.2f} Bilhões")
        print(f"  If in THOUSANDS: R$ {sp_total_raw/1e6:.2f} Bilhões")
        print(f"  If in MILLIONS: R$ {sp_total_raw/1e3:.2f} Bilhões")
        
        # Expected SP ICMS ~28-30% of national
        # If Brazil = R$ 640 Bi in 2024, SP should be ~R$ 180-200 Bi
        print(f"\n{'='*70}")
        print("EXPECTED VALUES:")
        print("="*70)
        print("SP ICMS 2024 (expected): ~R$ 180-200 Bilhões (28-30% of R$ 640 Bi national)")
        
        if 180e9 <= sp_total_raw <= 200e9:
            print("\nCONCLUSION: Values are in REAIS (units)")
        elif 180e6 <= sp_total_raw/1e3 <= 200e6:
            print("\nCONCLUSION: Values are in THOUSANDS")
        elif 180e3 <= sp_total_raw/1e6 <= 200e3:
            print("\nCONCLUSION: Values are in MILLIONS")
        else:
            print(f"\nCONCLUSION: UNCLEAR - raw value {sp_total_raw/1e9:.2f} Bi doesn't match expected")

if __name__ == "__main__":
    manual_check()
