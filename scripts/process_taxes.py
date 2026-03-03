import csv
import numpy as np
import os
import json

# --- CONFIGS ---
DATA_DIR = 'data/processed/mip_2015'
OUTPUT_DIR = 'output'
INTER_DIR = 'output/intermediary'

def parse_val(s):
    try:
        # IBGE CSVs: 1.234,56 ou 1234,56
        if isinstance(s, str):
            val = s.replace('.', '').replace(',', '.')
            return float(val)
        return float(s)
    except:
        return 0.0

def read_total_column(path, skip_rows, n_rows=67):
    """Lê a última coluna (Total) de um arquivo CSV padrão do IBGE."""
    if not os.path.exists(path):
        print(f"ERRO: Arquivo não encontrado: {path}")
        return np.zeros(n_rows)
    
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < skip_rows: continue
            if i >= skip_rows + n_rows: break
            
            # Assumindo que a última coluna com dados é a de totais.
            # Nos arquivos 05/06 visualizados, a última coluna (index -1) parece vazia ou sujeira em algumas linhas?
            # O header "Total da Demanda" ou "Total do Produto" geralmente é a última coluna numérica.
            # Vamos pegar a última coluna não vazia ou um índice fixo se soubermos.
            # Visualizei 05.csv: Col 86 "Demanda total" (índice 85 0-based? headers indicam isso).
            # Mas vamos ser robustos e pegar a última coluna (-1) e se for vazio, a penúltima.
            
            val = 0.0
            # Tenta de trás pra frente achar um número
            for col in reversed(row):
                if col.strip():
                    val = parse_val(col)
                    break
            data.append(val)
            
    return np.array(data)

def run():
    print(">>> Processando Matriz de Impostos...")
    
    # 1. Carregar Valor da Produção (X)
    # Preferimos ler do arquivo X_nacional.npy gerado pelo step1 para consistência?
    # Sim, mas vamos garantir carregando o CSV raw se o npy não existir.
    x_path = os.path.join(INTER_DIR, 'X_nacional.npy')
    x_path = os.path.join(INTER_DIR, 'X_nacional.npy')
    loaded_ok = False
    if os.path.exists(x_path):
        X = np.load(x_path)
        if np.sum(X) > 0:
            loaded_ok = True
            print(f"Loaded X from npy (Sum: {np.sum(X)})")
            



    if not loaded_ok:
        print("X_nacional.npy is invalid (or zeros). Fallback to raw 03.csv...")
        path_03 = os.path.join(DATA_DIR, '03.csv')
        SKIP_ROWS_X = 4 
        # Read X distribution (likely relative structure is correct)
        X = read_total_column(path_03, SKIP_ROWS_X)
        print(f"Loaded X (Raw Sum): {np.sum(X):.2f}")
        
    # --- OUTPUT MAGNITUDE CORRECTION ---
    # Retrieve authoritative Total Supply from 01.csv Total Row
    try:
        path_01 = os.path.join(DATA_DIR, '01.csv')
        with open(path_01, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        target_output = 11909669.0 # Default fallback (11.9T)
        for line in reversed(lines):
            if line.startswith("Total,"):
                parts = list(csv.reader([line]))[0]
                try:
                    # Col 2 is Total Supply
                    val = float(parts[2].replace('.', '').replace(',', '.'))
                    if val > 5000000: # Sanity check (>5T)
                        target_output = val
                except:
                    pass
                break
        
        current_sum = np.sum(X)
        if current_sum > 0:
            scale_factor = target_output / current_sum
            # If discrepancy is large (>20%), apply correction
            if scale_factor > 1.2 or scale_factor < 0.8:
                print(f"Detected X Magnitude Mismatch (Loaded: {current_sum/1e6:.2f}T, Target: {target_output/1e6:.2f}T)")
                print(f"Applying Output Scale Factor: {scale_factor:.4f}")
                X = X * scale_factor
                
    except Exception as e:
        print(f"Output Magnitude Correction Warning: {e}")
    # -----------------------------------




    # 2. Ler Impostos
    # 05.csv: Impostos sobre Produtos Nacionais
    # Linha 88 start. 67 setores.
    # Coluna Total é a última?
    # No preview do 05.csv:
    # 216: Total,,684832...

    # ...
    
    SKIP_ROWS = 4
    
    taxes_dom = read_total_column(os.path.join(DATA_DIR, '05.csv'), SKIP_ROWS)
    taxes_imp = read_total_column(os.path.join(DATA_DIR, '06.csv'), SKIP_ROWS)

    
    # --- CALIBRATION STEP (NEW) ---
    print("\n>>> Calibrating with Receita Federal Data (CTB 2015)...")
    try:
        ctb_path = os.path.join(OUTPUT_DIR, 'ctb_dump_2015.json') # Used specific dump file or recreate mapping
        # Let's use hardcoded values from checks or reload robustly
        # Based on current audit:
        # MIP Raw Total = 297,150
        # Target (ICMS+IPI+ISS+PIS/COFINS_Products)
        # ICMS: 396,428
        # IPI: 48,048
        # ISS: 54,454
        # PIS/COFINS (Subset roughly 50% of total 250k? Or full?)
        # Let's take a conservative "Product Tax" target = ICMS + IPI + ISS + portion of PIS/COFINS
        # For now, let's match the "Broad Product Tax" usually around 14-15% of GDP.
        # GDP 2015 ~ 6 Trillion. 15% = 900 Billion.
        # Our MIP is ~360Bn (incl imports).
        # Let's calibrate to match ICMS + IPI + ISS + II + IOF + CIDE.
        
        # Values from CTB 2015 (Million R$):
        TARGET_ICMS = 396428.0
        TARGET_IPI = 48048.0
        TARGET_ISS = 54454.0
        TARGET_II = 38969.0 # From dump "12_Impostos sobre o Comércio Exterior"
        TARGET_IOF = 34681.0
        TARGET_CIDE = 3271.0
        
        # PIS/COFINS is tricky because it's largely Value Added, but often computed on products.
        # Let's assume a factor to cover the gap.
        
        TARGET_CORE = TARGET_ICMS + TARGET_IPI + TARGET_ISS + TARGET_II + TARGET_IOF + TARGET_CIDE
        
        initial_total = np.sum(taxes_dom) + np.sum(taxes_imp)
        print(f"Initial MIP Total: {initial_total:,.2f}")
        print(f"Target Core (ICMS+IPI+ISS+II+IOF+CIDE): {TARGET_CORE:,.2f}")
        
        CALIBRATION_FACTOR = TARGET_CORE / initial_total if initial_total > 0 else 1.0
        
        if CALIBRATION_FACTOR < 1.0: CALIBRATION_FACTOR = 1.0 # Never reduce
        
        print(f"Applying Calibration Factor: {CALIBRATION_FACTOR:.4f}")
        
        taxes_dom *= CALIBRATION_FACTOR
        taxes_imp *= CALIBRATION_FACTOR
        
    except Exception as e:
        print(f"Calibration Warning: {e}")
    # ------------------------------

    # 3. Calcular Coeficientes
    # tau = Tax / X
    # Evitar divisão por zero
    
    tax_coeff_dom = np.zeros_like(X)
    tax_coeff_imp = np.zeros_like(X)
    tax_coeff_total = np.zeros_like(X)
    
    non_zero = X > 0
    
    tax_coeff_dom[non_zero] = taxes_dom[non_zero] / X[non_zero]
    # Para importados, tecnicamente seria sobre importações, mas para o modelo de choque de demanda (Input-Output),
    # queremos saber quanto de imposto é gerado dado um aumento de produção doméstica TOTAL.
    # Mas imposto de importação só acontece se houver importação.
    # O modelo L * f gera X (produção doméstica).
    # Se usarmos coeff = Tax_Imp / X_Dom, estamos assumindo que para cada unidade produzida aqui,
    # importa-se X proporcionalmente e paga-se Y de imposto. É uma aproximação válida para conta satélite.
    tax_coeff_imp[non_zero] = taxes_imp[non_zero] / X[non_zero]
    
    tax_coeff_total = tax_coeff_dom + tax_coeff_imp
    
    print(f"X Total (Soma): {np.sum(X):.2f}")
    print(f"Impostos Domésticos (CALIBRADO): {np.sum(taxes_dom):.2f}")
    print(f"Impostos Importados (CALIBRADO): {np.sum(taxes_imp):.2f}")
    print(f"Carga Tributária Produtiva (%): {np.sum(taxes_dom+taxes_imp)/np.sum(X)*100:.2f}%")

    # 4. Salvar
    output_data = {
        "production_X": X.tolist(),
        "taxes_domestic_abs": taxes_dom.tolist(),
        "taxes_import_abs": taxes_imp.tolist(),
        "coef_tax_domestic": tax_coeff_dom.tolist(),
        "coef_tax_import": tax_coeff_imp.tolist(),
        "coef_tax_total": tax_coeff_total.tolist(),
        "metadata": {
            "calibration_factor": float(CALIBRATION_FACTOR),
            "source_ctb": "ctb_1990-2024_0.xlsx"
        }
    }
    
    with open(os.path.join(OUTPUT_DIR, 'tax_data.json'), 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Dados salvos em {os.path.join(OUTPUT_DIR, 'tax_data.json')}")

if __name__ == "__main__":
    run()
