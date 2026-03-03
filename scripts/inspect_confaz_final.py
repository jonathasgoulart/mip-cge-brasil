import pandas as pd

FILE_PATH = r"C:\Users\jonat\Documents\MIP e CGE\data\2026.01.08.xls"

def inspect_confaz_final():
    """Read only first 30 rows to understand structure"""
    
    print("="*70)
    print("CONFAZ ICMS STRUCTURE (First 30 rows only)")
    print("="*70)
    
    try:
        # Read ONLY first 30 rows (memory safe)
        dfsmall = pd.read_excel(FILE_PATH, nrows=30, header=None)
        
        print(f"\nDimensions: {dfsmall.shape[0]} rows x {dfsmall.shape[1]} cols")
        
        print("\n[All columns, first 30 rows]:")
        print("-"*70)
        print(dfsmall.to_string())
        
        # Free memory
        del dfsmall
        
        print("\n[SUCCESS] Inspection complete")
        print("Agora posso criar o processador baseado nessa estrutura")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_confaz_final()
