import csv
import numpy as np
import os
import sys

def log(msg):
    print(f"[STEP 1] {msg}")
    sys.stdout.flush()

# --- CONFIGS ---
REGIOES_CONFIG = {
    'Sul': [21, 22, 23],
    'Centro_Oeste': [24, 25, 26, 27],
    'Norte_Nordeste': list(range(1, 17)),
    'Rio_de_Janeiro': [19],
    'Sao_Paulo': [20],
    'Minas_EspiritoSanto': [17, 18]
}

DATA_DIR = 'data/processed'
OUTPUT_DIR = 'output/intermediary'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_val(s):
    try:
        # IBGE CSVs: 1.234,56 ou 1234,56
        return float(s.replace('.', '').replace(',', '.'))
    except:
        return 0.0

def read_column(path, skip_rows, col_idx, n_rows=67):
    if not os.path.exists(path):
        return None
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < skip_rows: continue
            if i >= skip_rows + n_rows: break
            data.append(parse_val(row[col_idx]))
    return np.array(data)

def read_mat(path, skip_rows, col_range, n_rows=67):
    mat = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < skip_rows: continue
            if i >= skip_rows + n_rows: break
            line = [parse_val(row[c]) for c in col_range]
            mat.append(line)
    return np.array(mat)

def run():
    log("Iniciando pré-processamento...")
    
    # 1. Dados Nacionais (MIP 2015)
    log("Carrregando MIP Nacional 2015 (67 setores)...")
    # Tabela 11: Consumo Intermediário (skip 3 rows, cols 3-69)
    try:
        Z_nas = read_mat(os.path.join(DATA_DIR, 'mip_2015', '11.csv'), 3, range(3, 70))
        # Tabela 14: Produção Total (skip 3 rows, col 70)
        X_nas = read_column(os.path.join(DATA_DIR, 'mip_2015', '14.csv'), 3, 70)
        
        np.save(os.path.join(OUTPUT_DIR, 'Z_nacional.npy'), Z_nas)
        np.save(os.path.join(OUTPUT_DIR, 'X_nacional.npy'), X_nas)
        log("Dados Nacionais salvos com sucesso.")
    except Exception as e:
        log(f"ERRO nos dados nacionais: {e}")
        return

    # 2. Dados Regionais (Contas Regionais 2021)
    log("Agregando VAB Regional 2021...")
    vab_total_reg = {}
    vab_nas_agg = np.zeros(67)
    
    try:
        for reg, ufs in REGIOES_CONFIG.items():
            log(f"  Somando região: {reg}")
            agg = np.zeros(67)
            for uf_idx in ufs:
                path = os.path.join(DATA_DIR, 'contas_regionais_2021_t1', f'Tabela1.{uf_idx}.csv')
                # VAB por setor está na coluna 5 (índice 5) nos CSVs gerados
                vab_uf = read_column(path, 3, 5)
                if vab_uf is not None:
                    agg += vab_uf
            vab_total_reg[reg] = agg
            vab_nas_agg += agg
        
        # Salvar dicionário de regiões (como objeto ou múltiplos npy)
        for reg, arr in vab_total_reg.items():
            np.save(os.path.join(OUTPUT_DIR, f'VAB_{reg}.npy'), arr)
        np.save(os.path.join(OUTPUT_DIR, 'VAB_nacional_agg.npy'), vab_nas_agg)
        log("Dados Regionais agregados e salvos.")
    except Exception as e:
        log(f"ERRO nos dados regionais: {e}")
        return

    log("Fase 1 CONCLUÍDA. Arquivos .npy gerados em output/intermediary.")

if __name__ == "__main__":
    run()
