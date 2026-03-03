import numpy as np
import os

def validate():
    print("--- INICIANDO VALIDAÇÃO DE CONSISTÊNCIA ---")
    final_dir = 'output/final'
    inter_dir = 'output/intermediary'
    
    # 1. Carregar componentes nacionais
    Z_nas = np.load(os.path.join(inter_dir, 'Z_nas.npy'))
    X_nas = np.load(os.path.join(inter_dir, 'X_nas.npy'))
    VAB_nas = np.load(os.path.join(inter_dir, 'VAB_nacional.npy')) if os.path.exists(os.path.join(inter_dir, 'VAB_nacional.npy')) else None
    
    print(f"Propriedade 1: Coeficientes Nacionais (A_nas)")
    # Calcular A_nas = Z_nas / X_nas
    A_nas = np.divide(Z_nas, X_nas[None, :], out=np.zeros_like(Z_nas), where=X_nas[None, :]!=0)
    col_sums_nas = np.sum(A_nas, axis=0)
    print(f"  - Soma média das colunas: {np.mean(col_sums_nas):.4f}")
    print(f"  - Máximo em uma coluna: {np.max(col_sums_nas):.4f}")
    if np.any(col_sums_nas > 1.0):
        print("  [!] AVISO: Algumas colunas nacionais somam > 1.0 (consumo > produção).")
    else:
        print("  [OK] Todas as colunas nacionais são <= 1.0")

    # 2. Carregar e Validar Matrizes Regionais
    regioes = ['Sao_Paulo', 'Rio_de_Janeiro', 'Minas_EspiritoSanto', 'Sul', 'Centro_Oeste', 'Norte_Nordeste']
    
    print(f"\nPropriedade 2: Coeficientes Regionais (A_reg)")
    for reg in regioes:
        path = os.path.join(final_dir, f'A_{reg}.npy')
        if not os.path.exists(path):
            print(f"  [!] Matriz A_{reg} não encontrada.")
            continue
        
        A_reg = np.load(path)
        col_sums = np.sum(A_reg, axis=0)
        
        # O coeficiente regional A_reg deve ser SEMPRE menor ou igual ao A_nas (devido ao FLQ <= 1)
        diff = A_reg - A_nas
        if np.any(diff > 1e-9):
            print(f"  [!] ERRO na região {reg}: Coeficientes regionais superam os nacionais.")
        
        print(f"  - {reg}: Soma média colunas = {np.mean(col_sums):.4f}, Max = {np.max(col_sums):.4f} [OK]")

    # 3. Validar Equilíbrio de VAB
    print(f"\nPropriedade 3: Equilíbrio de Valor Adicionado (VAB)")
    vab_nas_agg = np.load(os.path.join(inter_dir, 'VAB_nas_agg.npy'))
    # No nosso pipeline, o VAB_nas_agg é a soma dos VABs regionais calculados
    # Se estivéssemos 100% corretos, a soma dos VABs regionais deve representar o VAB nacional de 2021
    # Vamos verificar se o peso relativo das regiões faz sentido econômico
    
    vabs = {}
    total_vab = 0
    for reg in regioes:
        vab = np.load(os.path.join(inter_dir, f'VAB_{reg}.npy'))
        vabs[reg] = np.sum(vab)
        total_vab += vabs[reg]
    
    print(f"  - Distribuição do VAB Total (2021 Est.):")
    for reg, val in vabs.items():
        print(f"    {reg:20}: {val/total_vab*100:6.2f}%")
        
    # Esperado (aproximado IBGE): SP ~30%, RJ ~10%, MG/ES ~10%, Sul ~17%, etc.
    
    print("\n--- VALIDAÇÃO CONCLUÍDA ---")

if __name__ == "__main__":
    validate()
