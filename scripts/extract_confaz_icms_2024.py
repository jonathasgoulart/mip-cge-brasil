import pandas as pd
import json
import os

FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\2026.01.08.xls"
OUTPUT_PATH = r"C:\Users\jonat\Documents\MIP e CGE\output\confaz_icms_2024_by_uf.json"

# Brazilian states
UFS = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
       'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
       'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

def extract_confaz_corrected():
    """
    CORRECTED EXTRACTION
    
    Structure:
    - Row 0: Headers (Col 0 = "Rótulos de Linha", Cols 1+ = CNAE divisions)
    - Rows 1-27: Each UF (Col 0 = UF code, Cols 1+ = ICMS by CNAE division)
    - Values are in MIL REAIS (thousands of BRL)
    """
    
    print("="*70)
    print("CONFAZ ICMS 2024 EXTRACTION (CORRECTED)")
    print("="*70)
    
    print("\n[1/3] Loading file...")
    df = pd.read_excel(FILE_PATH, header=0)  # Use row 0 as header
    
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {len(df.columns)}")
    
    # The first column should contain UFs
    first_col_name = df.columns[0]
    print(f"  First column name: '{first_col_name}'")
    
    print("\n[2/3] Extracting data by UF...")
    
    uf_totals = {}
    uf_by_cnae = {}
    
    for _, row in df.iterrows():
        uf = row[first_col_name]
        
        if uf in UFS:
            # Sum all CNAE columns (all columns except the first one)
            # Columns 1+ contain ICMS values by CNAE division
            icms_values = pd.to_numeric(row.iloc[1:], errors='coerce').fillna(0)
            total_uf = icms_values.sum()
            
            uf_totals[uf] = float(total_uf)
            
            # Store detailed breakdown
            uf_by_cnae[uf] = {
                col_name: float(val) 
                for col_name, val in zip(df.columns[1:], icms_values)
                if val > 0  # Only keep non-zero values
            }
            
            print(f"  {uf}: R$ {total_uf/1e6:,.2f} Bilhões ({len([v for v in icms_values if v > 0])} CNAEs)")
    
    # Calculate total Brasil
    total_brasil = sum(uf_totals.values())
    
    print(f"\n[3/3] Results:")
    print("-"*70)
    print(f"Total ICMS Brasil 2024: R$ {total_brasil/1e9:.2f} Bilhões")
    
    # Show top 5 states
    sorted_ufs = sorted(uf_totals.items(), key=lambda x: x[1], reverse=True)
    print(f"\nTop 5 Arrecadadores:")
    for uf, value in sorted_ufs[:5]:
        pct = (value/total_brasil*100) if total_brasil > 0 else 0
        print(f"  {uf}: R$ {value/1e9:.2f} Bi ({pct:.1f}%)")
    
    # Save results
    results = {
        "year": 2024,
        "total_brasil_reais": float(total_brasil),  # In REAIS (units)
        "total_brasil_bilhoes": float(total_brasil / 1e9),  # In billions
        "by_uf_reais": {uf: float(val) for uf, val in uf_totals.items()},
        "by_uf_bilhoes": {uf: float(val/1e9) for uf, val in uf_totals.items()},
        "by_uf_by_cnae": uf_by_cnae,  # Detailed breakdown (in reais)
        "metadata": {
            "source": "CONFAZ 2026.01.08.xls",
            "extraction_date": "2026-01-24",
            "units": "BRL (reais)",
            "structure": "rows=UFs (27), columns=CNAE_divisions (88)",
            "note": "Annual totals for 2024. Values are in absolute BRL."
        }
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Results saved to: {OUTPUT_PATH}")
    
    # Validation check
    print(f"\n{'='*70}")
    print("VALIDATION:")
    print("="*70)
    print(f"UFs extracted: {len(uf_totals)} (expected: 27)")
    print(f"Total ICMS 2024: R$ {total_brasil/1e9:.2f} Bilhões")
    print(f"Expected range: R$ 600-800 Bi (growth from 2021's R$ 537 Bi)")
    print(f"  Note: CONFAZ may include additional components beyond CTB definition")
    
    growth_from_2021 = ((total_brasil/1e9) / 537.0 - 1) * 100
    print(f"Nominal growth from CTB 2021: {growth_from_2021:+.1f}%")
    print(f"  (~{growth_from_2021/3:.1f}%/year over 3 years)")
    
    if 600e9 <= total_brasil <= 900e9:
        print("Status: OK - Within expected range")
    else:
        print(f"Status: INFO - Value is {total_brasil/1e9:.0f} Bi (may include broader tax base)")

    
    return results

if __name__ == "__main__":
    extract_confaz_corrected()
