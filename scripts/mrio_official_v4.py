"""
MRIO Oficial V4 - Modelo Interregional Unificado
Integra: Modelo Gravitacional + Beta Setorial + Matrizes Específicas RJ
"""

import numpy as np
import pandas as pd
import json
import os
from pathlib import Path
from gravity_params import get_distance_matrix, UF_LIST

# ========== CONFIGURAÇÕES ==========
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output' / 'final'
INTER_DIR = BASE_DIR / 'output' / 'intermediary'
REGIONAL_DIR = BASE_DIR / 'output' / 'regional_matrices'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Calibração de Beta por Tipo de Setor
BETA_SECTORAL = {
    # Commodities (Agricultura + Extrativismo): Setores 1-21
    'commodities': {'range': range(1, 22), 'beta': 0.8},
    
    # Manufaturados (Indústria): Setores 22-52
    'manufacturing': {'range': range(22, 53), 'beta': 1.5},
    
    # Serviços: Setores 53-67
    'services': {'range': range(53, 68), 'beta': 3.0}
}

# FLQ Delta
DELTA_FLQ = 0.3

N_SECTORS = 67
N_UFS = 27

def get_beta_vector():
    """Retorna vetor de 67 betas calibrados por setor."""
    beta_vec = np.ones(N_SECTORS) * 1.5  # Default
    
    for category, params in BETA_SECTORAL.items():
        for idx in params['range']:
            beta_vec[idx - 1] = params['beta']  # Convert 1-indexed to 0-indexed
    
    return beta_vec

def load_national_data():
    """Carrega matriz nacional e vetores de produção."""
    print("[1/6] Carregando dados nacionais...")
    
    # Tentar carregar do intermediário
    z_path = INTER_DIR / 'Z_nas.npy'
    x_path = INTER_DIR / 'X_nas.npy'
    
    if z_path.exists() and x_path.exists():
        Z_nas = np.load(z_path)
        X_nas = np.load(x_path)
        print(f"  [OK] Matriz nacional carregada. VBP Total: R$ {np.sum(X_nas):,.0f} Mi")
    else:
        raise FileNotFoundError("Arquivos nacionais não encontrados em output/intermediary/")
    
    # Calcular coeficientes técnicos
    with np.errstate(divide='ignore', invalid='ignore'):
        A_nas = np.divide(Z_nas, X_nas, out=np.zeros_like(Z_nas), where=X_nas!=0)
        A_nas = np.nan_to_num(A_nas)
    
    return A_nas, X_nas

def load_regional_vab():
    """Carrega VAB regional para todos os estados."""
    print("[2/6] Carregando VAB regional...")
    
    vab_per_uf = {}
    gdp_vec = []
    
    for uf in UF_LIST:
        path = INTER_DIR / f'VAB_{uf}.npy'
        if path.exists():
            vab = np.load(path)
            if vab.shape[0] != N_SECTORS:
                vab = np.zeros(N_SECTORS)
        else:
            vab = np.zeros(N_SECTORS)
        
        vab_per_uf[uf] = vab
        gdp_vec.append(np.sum(vab))
    
    total_gdp = np.sum(gdp_vec)
    print(f"  [OK] VAB regional carregado. PIB Total: R$ {total_gdp/1e6:,.2f} Bi")
    
    return vab_per_uf, np.array(gdp_vec)

def calculate_gravity_probabilities_sectoral(gdp_vec, dist_matrix, beta_vec):
    """
    Calcula probabilidades de comércio com beta diferenciado por setor.
    Retorna: array (27 UFs, 27 UFs, 67 setores)
    """
    print("[3/6] Calculando probabilidades gravitacionais setoriais...")
    
    n_regions = len(UF_LIST)
    trade_prob = np.zeros((n_regions, n_regions, N_SECTORS))
    
    for s in range(N_SECTORS):
        beta_s = beta_vec[s]
        
        # Atração da região j para o setor s: GDP_j / d_ij^beta_s
        attraction = gdp_vec[np.newaxis, :] / (dist_matrix ** beta_s)
        
        # Normalizar por linha (probabilidade de i comprar de j)
        total_attraction = np.sum(attraction, axis=1, keepdims=True)
        trade_prob[:, :, s] = attraction / total_attraction
    
    print(f"  [OK] Probabilidades calculadas com beta setorial (0.8 - 3.0)")
    return trade_prob

def load_rio_matrices():
    """Carrega matrizes oficiais do Rio de Janeiro."""
    print("  [RJ] Carregando matrizes oficiais UFRJ/CEPERJ...")
    
    path_local = REGIONAL_DIR / 'A_RIO_LOCAIS_67x67.xlsx'
    path_inter = REGIONAL_DIR / 'A_RIO_INTER_67x67.xlsx'
    
    if not path_local.exists() or not path_inter.exists():
        print("  ⚠ Matrizes oficiais RJ não encontradas. Usando FLQ padrão.")
        return None, None
    
    A_local = pd.read_excel(path_local, index_col=0).values
    A_inter = pd.read_excel(path_inter, index_col=0).values
    
    print(f"  [OK] RJ: Matriz Local {A_local.shape}, Vazamento {A_inter.shape}")
    return A_local, A_inter

def build_mrio_official(A_nas, X_nas, vab_per_uf, gdp_vec, trade_prob):
    """Constrói matriz MRIO unificada com RJ especial e FLQ para demais."""
    print("[4/6] Construindo MRIO Oficial (1809×1809)...")
    
    n_total = N_UFS * N_SECTORS
    A_mrio = np.zeros((n_total, n_total), dtype=np.float32)
    
    # Carregar VAB nacional para FLQ
    vab_nas_path = INTER_DIR / 'VAB_nacional.npy'
    if vab_nas_path.exists():
        VAB_nas = np.load(vab_nas_path)
    else:
        # Aproximação: VAB ≈ 40% do VBP
        VAB_nas = X_nas * 0.4
    
    total_vab_nas = np.sum(VAB_nas)
    
    # Carregar matrizes RJ
    A_rio_local, A_rio_inter = load_rio_matrices()
    rj_idx = UF_LIST.index('RJ')
    
    for r_idx, uf_r in enumerate(UF_LIST):
        vab_r = vab_per_uf[uf_r]
        total_vab_r = np.sum(vab_r)
        
        # ========== CASO ESPECIAL: RIO DE JANEIRO ==========
        if uf_r == 'RJ' and A_rio_local is not None:
            A_r_local = A_rio_local
            A_r_inter_total = A_rio_inter
            
        # ========== OUTROS ESTADOS: FLQ ==========
        else:
            # Calibração FLQ
            with np.errstate(divide='ignore', invalid='ignore'):
                slq = (vab_r / total_vab_r) / (VAB_nas / total_vab_nas)
                slq = np.nan_to_num(slq, nan=0.0)
            
            lambda_r = (np.log2(1 + (total_vab_r / total_vab_nas))) ** DELTA_FLQ
            flq_factor = slq * lambda_r
            flq_factor = np.clip(flq_factor, 0, 1)
            
            A_r_local = A_nas * flq_factor[:, None]
            A_r_inter_total = A_nas - A_r_local
        
        # ========== DISTRIBUIR NO MRIO ==========
        for s_idx, uf_s in enumerate(UF_LIST):
            row_start = r_idx * N_SECTORS
            row_end = row_start + N_SECTORS
            col_start = s_idx * N_SECTORS
            col_end = col_start + N_SECTORS
            
            if r_idx == s_idx:
                # Diagonal: Coeficientes locais
                A_mrio[row_start:row_end, col_start:col_end] = A_r_local
            else:
                # Off-diagonal: Vazamento distribuído por gravidade
                # Para cada setor, usar a probabilidade específica
                for sec in range(N_SECTORS):
                    prob_sec = trade_prob[s_idx, r_idx, sec]  # Prob de s comprar de r
                    
                    # Coeficiente de importação do setor 'sec' de r para s
                    A_mrio[row_start:row_end, col_start + sec] += A_r_inter_total[:, sec] * prob_sec
    
    print(f"  [OK] MRIO construido. Tamanho: {A_mrio.nbytes / 1024**2:.2f} MB")
    return A_mrio

def save_outputs(A_mrio, trade_prob, beta_vec):
    """Salva outputs finais."""
    print("[5/6] Salvando arquivos...")
    
    # Matriz MRIO principal
    np.save(OUTPUT_DIR / 'A_mrio_official_v4.npy', A_mrio)
    print(f"  [OK] A_mrio_official_v4.npy")
    
    # Probabilidades de comércio
    np.save(OUTPUT_DIR / 'trade_prob_sectoral_v4.npy', trade_prob)
    print(f"  [OK] trade_prob_sectoral_v4.npy")
    
    # Calibração Beta
    beta_dict = {
        'beta_vector': beta_vec.tolist(),
        'parameters': {k: {'range': list(v['range']), 'beta': v['beta']} 
                      for k, v in BETA_SECTORAL.items()}
    }
    with open(OUTPUT_DIR / 'beta_sectoral_calibration.json', 'w') as f:
        json.dump(beta_dict, f, indent=2)
    print(f"  [OK] beta_sectoral_calibration.json")
    
    # Ordem das regiões
    with open(OUTPUT_DIR / 'region_order_v4.txt', 'w') as f:
        f.write('\n'.join(UF_LIST))
    print(f"  [OK] region_order_v4.txt")

def main():
    print("="*60)
    print("MRIO OFICIAL V4 - MODELO CONSOLIDADO")
    print("="*60)
    
    # Pipeline
    A_nas, X_nas = load_national_data()
    vab_per_uf, gdp_vec = load_regional_vab()
    
    # Distâncias
    dist_matrix, ordered_ufs = get_distance_matrix()
    assert ordered_ufs == UF_LIST, "Ordem das UFs não coincide!"
    
    # Beta setorial
    beta_vec = get_beta_vector()
    
    # Gravidade setorial
    trade_prob = calculate_gravity_probabilities_sectoral(gdp_vec, dist_matrix, beta_vec)
    
    # Construir MRIO
    A_mrio = build_mrio_official(A_nas, X_nas, vab_per_uf, gdp_vec, trade_prob)
    
    # Salvar
    save_outputs(A_mrio, trade_prob, beta_vec)
    
    print("\n" + "="*60)
    print("[OK] MRIO OFICIAL V4 GERADO COM SUCESSO")
    print("="*60)
    print(f"Arquivo principal: output/final/A_mrio_official_v4.npy")
    print(f"Dimensões: {A_mrio.shape} ({N_UFS} UFs × {N_SECTORS} setores)")
    print(f"Tecnologia RJ: Matrizes UFRJ/CEPERJ")
    print(f"Outros estados: FLQ (delta={DELTA_FLQ})")
    print(f"Beta setorial: 0.8 (commodities) a 3.0 (serviços)")

if __name__ == "__main__":
    main()
