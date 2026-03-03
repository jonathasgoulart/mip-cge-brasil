import numpy as np
import os
import sys

def log(msg):
    with open('output/status.txt', 'a', encoding='utf-8') as f:
        f.write(f"[ATO 2] {msg}\n")
    print(msg)
    sys.stdout.flush()

INTER_DIR = 'output/intermediary'
OUTPUT_DIR = 'output/final'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_math():
    log("Iniciando Ato 2: Cálculos Matemáticos (FLQ)")
    
    try:
        # 1. Carregar dados binários
        Z_nas = np.load(os.path.join(INTER_DIR, 'Z_nas.npy'))
        X_nas = np.load(os.path.join(INTER_DIR, 'X_nas.npy'))
        VAB_nas_agg = np.load(os.path.join(INTER_DIR, 'VAB_nas_agg.npy'))
        
        # Coeficientes Técnicos Nacionais A = Z / X (divisão por colunas)
        A_nas = np.divide(Z_nas, X_nas[None, :], out=np.zeros_like(Z_nas), where=X_nas[None, :]!=0)
        
        # 2. Processar cada região
        regioes = [f.replace('VAB_', '').replace('.npy', '') for f in os.listdir(INTER_DIR) if f.startswith('VAB_') and f != 'VAB_nas_agg.npy']
        
        delta = 0.3 # Coeficiente Flegg
        nas_vab_total = np.sum(VAB_nas_agg)
        
        for reg in regioes:
            log(f"  Calculando regionalização para: {reg}")
            vab_reg = np.load(os.path.join(INTER_DIR, f'VAB_{reg}.npy'))
            
            reg_vab_total = np.sum(vab_reg)
            if reg_vab_total == 0:
                log(f"    AVISO: VAB total da região {reg} é zero. Pulando.")
                continue
                
            # Lambda de Flegg: [log2(1 + VAB_reg/VAB_nas)]^delta
            lambda_reg = (np.log2(1 + (reg_vab_total / nas_vab_total))) ** delta
            
            # SLQ (Simple Location Quotient)
            # SLQ_i = (VAB_i_reg / VAB_total_reg) / (VAB_i_nas / VAB_total_nas)
            slq = np.divide(vab_reg / reg_vab_total, VAB_nas_agg / nas_vab_total, 
                             out=np.zeros_like(vab_reg), where=(VAB_nas_agg != 0))
            
            # CILQ_ij = SLQ_i / SLQ_j
            # FLQ_ij = CILQ_ij * lambda_reg
            # cilq[i,j] = slq[i] / slq[j]
            cilq = np.divide(slq[:, None], slq[None, :], out=np.ones((67,67)), where=(slq[None, :] != 0))
            flq = cilq * lambda_reg
            flq = np.clip(flq, 0, 1.0) 
            
            # Matriz de Coeficientes Regionais A_reg
            A_reg = A_nas * flq
            
            # Salvar como binário
            np.save(os.path.join(OUTPUT_DIR, f'A_{reg}.npy'), A_reg)
            log(f"    Matriz A_{reg} salva.")
            
        log("FIM DO ATO 2: Cálculos concluídos.")
        
    except Exception as e:
        log(f"ERRO ATO 2: {e}")

if __name__ == "__main__":
    run_math()
