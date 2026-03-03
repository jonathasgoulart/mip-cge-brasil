import pandas as pd
import json

def extract_ibge_cnae_mapping():
    """
    Extract official IBGE mapping between activities and CNAE 2.0
    """
    
    print("="*70)
    print("EXTRACTING OFFICIAL IBGE CNAE MAPPING")
    print("="*70)
    
    FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\Atividade -contas de divulgação x Cnae 2.0 - Resumo.xls"
    
    try:
        # Read Excel file
        df = pd.read_excel(FILE_PATH)
        
        print(f"\nFile loaded successfully")
        print(f"Shape: {df.shape}")
        print(f"\nColumn names:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")
        
        print(f"\nFirst 20 rows:")
        print(df.head(20))
        
        # Save to JSON for inspection
        sample_data = df.head(50).to_dict(orient='records')
        
        with open('output/ibge_cnae_mapping_sample.json', 'w', encoding='utf-8') as f:
            json.dump({
                "columns": list(df.columns),
                "shape": df.shape,
                "sample_rows": sample_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Sample saved to: output/ibge_cnae_mapping_sample.json")
        
        return df
        
    except Exception as e:
        print(f"\nError: {e}")
        return None

if __name__ == "__main__":
    extract_ibge_cnae_mapping()
