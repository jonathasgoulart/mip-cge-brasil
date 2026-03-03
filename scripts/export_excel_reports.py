
import pandas as pd
import os

def run():
    print("=== EXPORTANDO RELATÓRIOS PARA EXCEL ===")
    
    files_to_sheets = {
        'output/carga_setorial_2021.csv': 'Carga_Setorial',
        'output/simulacao_reforma_setorial.csv': 'Simulacao_Reforma',
        'output/impacto_regional_hibrido.csv': 'Impacto_Regional_Hibrido',
        'output/impacto_regional.csv': 'Impacto_Regional_Estimado_V1'
    }
    
    # Read DataFrames
    dfs = {}
    for path, sheet in files_to_sheets.items():
        if os.path.exists(path):
            try:
                dfs[sheet] = pd.read_csv(path, encoding='utf-8')
            except UnicodeDecodeError:
                 dfs[sheet] = pd.read_csv(path, encoding='latin1')
            print(f"Loaded {sheet} from {path}")
        else:
            print(f"Skipping {sheet} (File not found: {path})")

    # Function to save
    def save_excel(filename):
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet, index=False)
        print(f"Success! Saved to {filename}")

    # Try Save
    default_out = 'output/Resultados_MIP_CGE_2021.xlsx'
    fallback_out = 'output/Resultados_MIP_CGE_2021_v2.xlsx'
    
    try:
        save_excel(default_out)
    except PermissionError:
        print(f"Permission Denied for {default_out}. Trying {fallback_out}...")
        try:
            save_excel(fallback_out)
        except Exception as e:
            print(f"Failed to save fallback: {e}")
    except Exception as e:
         print(f"Error saving Excel: {e}")

if __name__ == "__main__":
    run()
