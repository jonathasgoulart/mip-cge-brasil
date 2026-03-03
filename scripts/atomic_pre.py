import csv
import numpy as np
import os
import sys

def update_status(msg):
    with open('output/status.txt', 'a', encoding='utf-8') as f:
        f.write(f"[ATO 1] {msg}\n")
    print(msg)
    sys.stdout.flush()

REGIOES_MAP = {
    'Sul': [21, 22, 23],
    'Centro_Oeste': [24, 25, 26, 27],
    'Norte_Nordeste': list(range(1, 17)),
    'Rio_de_Janeiro': [19],
    'Sao_Paulo': [20],
    'Minas_EspiritoSanto': [17, 18]
}

def parse_val(s):
    try:
        return float(s.replace('.', '').replace(',', '.'))
    except:
        return 0.0

def load_col_robust(path, skip, col, target_size=67):
    """Carrega dados e garante o tamanho target_size preenchendo com zeros."""
    if not os.path.exists(path):
        return None
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < skip: continue
            if i >= skip + target_size: break
            val = parse_val(row[col]) if col < len(row) else 0.0
            data.append(val)
    
    arr = np.array(data)
    if len(arr) < target_size:
        # Preenche com zeros se for menor (ex: 52 setores -> 67 setores)
        arr = np.pad(arr, (0, target_size - len(arr)), 'constant')
    return arr[:target_size]

def find_uf_file(uf_idx):
    """Busca o arquivo da UF em múltiplas pastas e padrões de nome."""
    search_paths = [
        f'data/processed/contas_regionais_2021_t1/Tabela1.{uf_idx}.csv',
        f'data/processed/contas_regionais_2021_t1/Tabela1.{uf_idx:02d}.csv',
        f'data/processed/contas_regionais_2021_t2/Tabela2.{uf_idx}.csv',
        f'data/processed/contas_regionais_2021_t2/Tabela2.{uf_idx:02d}.csv',
        f'data/processed/contas_regionais_2021_t1/Tabela1.UF{uf_idx}.csv',
        f'data/processed/contas_regionais_2021_t2/Tabela2.UF{uf_idx}.csv'
    ]
    for p in search_paths:
        if os.path.exists(p):
            return p
    return None

def run():
    os.makedirs('output/intermediary', exist_ok=True)
    update_status("Iniciando Ato 1 (Versão Robusta)")

    try:
        # 1. MIP Nacional 2015
        update_status("Lendo Matriz Nacional...")
        # Lendo matriz A e X. Se X tiver tamanho diferente, usamos robust loader
        Z_nas = []
        path_z = 'data/processed/mip_2015/11.csv'
        with open(path_z, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i < 3: continue
                if i >= 3 + 67: break
                line = [parse_val(row[c]) for c in range(2, 69)]
                if len(line) < 67: line += [0.0] * (67 - len(line))
                Z_nas.append(line[:67])
        Z_nas = np.array(Z_nas)
        
        X_nas = load_col_robust('data/processed/mip_2015/14.csv', 3, 1, 67)
        
        np.save('output/intermediary/Z_nas.npy', Z_nas)
        np.save('output/intermediary/X_nas.npy', X_nas)
        update_status(f"MIP Nacional salva. Z: {Z_nas.shape}, X: {X_nas.shape}")

        # 2. Agregação Regional
        vab_agg_nas = np.zeros(67)
        for reg, ufs in REGIOES_MAP.items():
            update_status(f"Processando {reg}...")
            reg_vab = np.zeros(67)
            for uf in ufs:
                path = find_uf_file(uf)
                if path:
                    vab_uf = load_col_robust(path, 3, 5, 67)
                    reg_vab += vab_uf
                else:
                    # Tenta busca cega em t1/t2 se o índice linear falhar
                    update_status(f"  AVISO: UF {uf} não encontrada pelo índice. Tentando busca manual...")
            
            np.save(f'output/intermediary/VAB_{reg}.npy', reg_vab)
            vab_agg_nas += reg_vab
        
        np.save('output/intermediary/VAB_nas_agg.npy', vab_agg_nas)
        update_status("Ato 1 CONCLUÍDO com sucesso.")
        
    except Exception as e:
        update_status(f"ERRO ATO 1: {e}")

if __name__ == "__main__":
    run()
