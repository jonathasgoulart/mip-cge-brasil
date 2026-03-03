import numpy as np
import pandas as pd
import os
import gc

def validate_linkages():
    """
    Calcula os índices de Rasmussen-Hirschman de forma otimizada.
    Processa uma região por vez para evitar uso excessivo de memória.
    """
    print("--- VALIDAÇÃO: ÍNDICES DE ENCADEAMENTO (Otimizado) ---")
    final_dir = 'output/final'
    output_dir = 'output/validation'
    os.makedirs(output_dir, exist_ok=True)
    
    # Apenas primeiros 15 setores para reduzir carga
    setor_names = [
        "Arroz/Cereais", "Milho", "Algodão", "Cana", "Soja",
        "Outras Lavouras", "Laranja", "Café", "Lavoura Perm.", "Pecuária",
        "Leite", "Suínos", "Aves", "Silvicultura", "Pesca"
    ]
    
    regioes = ['Rio_de_Janeiro', 'Sao_Paulo', 'Sul']  # Processar 3 principais primeiro
    
    results = []
    
    for reg in regioes:
        print(f"\nProcessando {reg}...", flush=True)
        
        # Carregar matriz (liberando memória após uso)
        A = np.load(os.path.join(final_dir, f'A_{reg}.npy'))
        n = A.shape[0]
        
        # Inversa de Leontief
        I = np.eye(n)
        L = np.linalg.inv(I - A)
        
        # Cálculos simplificados
        col_sums = np.sum(L, axis=0)
        row_sums = np.sum(L, axis=1)
        total_mean = np.mean(L)
        
        BL = col_sums / (n * total_mean)
        FL = row_sums / (n * total_mean)
        
        # Salvar apenas top 15 setores
        for i in range(min(15, n)):
            is_key = (BL[i] > 1.0) and (FL[i] > 1.0)
            
            results.append({
                'Região': reg.replace('_', ' '),
                'Setor': setor_names[i] if i < len(setor_names) else f"Setor {i}",
                'BL': round(BL[i], 3),
                'FL': round(FL[i], 3),
                'Chave': 'Sim' if is_key else 'Não'
            })
        
        # Liberar memória
        del A, L, I, col_sums, row_sums
        gc.collect()
        print(f"  ✓ {reg} concluído")
    
    # Salvar resultados
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(output_dir, 'validation_linkages.csv'), index=False)
    
    # Resumo
    print("\n--- SETORES-CHAVE IDENTIFICADOS ---")
    for reg in regioes:
        df_reg = df[df['Região'] == reg.replace('_', ' ')]
        key_count = df_reg[df_reg['Chave'] == 'Sim'].shape[0]
        print(f"{reg.replace('_', ' ')}: {key_count} setores-chave de 15 analisados")
    
    print(f"\n✓ Resultados salvos: {output_dir}/validation_linkages.csv")
    
if __name__ == "__main__":
    validate_linkages()
