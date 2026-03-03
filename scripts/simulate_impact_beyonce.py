import numpy as np
import os

def simulate_show():
    print("--- SIMULAÇÃO DE IMPACTO: SHOW DA BEYONCÉ NO RIO ---")
    final_dir = 'output/final'
    
    # 1. Carregar Matriz de Coeficientes do Rio de Janeiro
    path_A = os.path.join(final_dir, 'A_Rio_de_Janeiro.npy')
    if not os.path.exists(path_A):
        print("Erro: Matriz do Rio de Janeiro não encontrada.")
        return
    
    A_rio = np.load(path_A)
    n = A_rio.shape[0] # Deve ser 67
    
    # 2. Calcular Inversa de Leontief: L = (I - A)^-1
    print("Calculando Inversa de Leontief para o Rio...")
    I = np.eye(n)
    L_rio = np.linalg.inv(I - A_rio)
    
    # 3. Definir o Choque Econômico (Demanda Final Adicional y)
    # Estimativas conservadoras (em Milhões de Reais):
    # - Ingressos/Produção (Setor 64): R$ 60M
    # - Hotéis/Alojamento (Setor 45): R$ 40M
    # - Restaurantes/Alimentação (Setor 46): R$ 30M
    # - Transporte Terrestre (Setor 41): R$ 20M
    
    y = np.zeros(n)
    y[64] = 60  # Atividades artísticas
    y[45] = 40  # Alojamento
    y[46] = 30  # Alimentação
    y[41] = 20  # Transporte terrestre
    
    # 4. Calcular o Impacto Total na Produção: x = L * y
    x_total = L_rio @ y
    
    # 5. Resultados
    impacto_direto = np.sum(y)
    impacto_total = np.sum(x_total)
    multiplicador_medio = impacto_total / impacto_direto
    
    print(f"\nDEMANDA INICIAL (Choque): R$ {impacto_direto:.1f} Milhões")
    print(f"IMPACTO TOTAL NA PRODUÇÃO: R$ {impacto_total:.1f} Milhões")
    print(f"MULTIPLICADOR DE PRODUÇÃO: {multiplicador_medio:.3f}")
    
    # Detalhar principais setores beneficiados Indiretamente
    print("\nPrincipais setores beneficiados (Direto + Indireto):")
    top_indices = np.argsort(x_total)[-8:][::-1]
    
    # Nomes simplificados para os setores
    setores_map = {
        64: "Cultura e Espetáculos",
        45: "Alojamento",
        46: "Alimentação",
        41: "Transporte Terrestre",
        37: "Energia Elétrica",
        42: "Comércio",
        51: "Serviços Financeiros",
        52: "Atividades Imobiliárias" # Aluguel efetivo e imputado
    }
    
    for idx in top_indices:
        nome = setores_map.get(idx, f"Setor {idx}")
        print(f"  - {nome:25}: R$ {x_total[idx]:.2f} M")

if __name__ == "__main__":
    simulate_show()
