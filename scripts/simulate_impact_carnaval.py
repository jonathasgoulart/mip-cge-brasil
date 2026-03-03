import numpy as np
import os

def simulate_carnaval():
    print("--- SIMULAÇÃO DE IMPACTO: CARNAVAL DO RIO DE JANEIRO ---")
    final_dir = 'output/final'
    inter_dir = 'output/intermediary'
    
    # 1. Carregar Matriz de Coeficientes do Rio de Janeiro
    path_A = os.path.join(final_dir, 'A_Rio_de_Janeiro.npy')
    if not os.path.exists(path_A):
        print("Erro: Matriz do Rio de Janeiro não encontrada.")
        return
    
    A_rio = np.load(path_A)
    n = A_rio.shape[0] # 67
    
    # 2. Calcular Inversa de Leontief: L = (I - A)^-1
    print("Calculando Inversa de Leontief...")
    I = np.eye(n)
    L_rio = np.linalg.inv(I - A_rio)
    
    # 3. Definir o Choque Econômico (Demanda Final Adicional y em Milhões de R$)
    # Estimativa de R$ 4.0 Bilhões de impacto direto circulando nos setores
    y = np.zeros(n)
    
    # Setores impactados:
    y[64] = 1500  # Atividades artísticas, criativas e espetáculos (Desfiles, Blocos)
    y[45] = 1000  # Alojamento (Hotéis com lotação máxima)
    y[46] = 800   # Alimentação (Restaurantes, bares, ambulantes)
    y[41] = 400   # Transporte Terrestre (Ônibus, táxis, aplicativos)
    y[40] = 300   # Comércio (Fantasias, adereços, bebidas em mercados)
    
    # 4. Calcular Impacto na Produção (x = L * y)
    x_total = L_rio @ y
    
    # 5. Calcular Impacto no Emprego (Delta E = e * Delta x)
    coeff_path = os.path.join(os.path.dirname(inter_dir), 'final', 'emp_coefficients_67x27.npy')
    if os.path.exists(coeff_path):
        e = np.load(coeff_path)
    else:
        e = np.zeros(n)
        e.fill(5.0) # Fallback
    
    vagas_por_setor = e * x_total
    total_vagas = np.sum(vagas_por_setor)
    
    # 6. Resultados
    print(f"\n--- RESULTADOS GLOBAIS ---")
    print(f"Investimento/Gasto Direto: R$ {np.sum(y):,.0f} Milhões")
    print(f"Impacto Total na Produção: R$ {np.sum(x_total):,.0f} Milhões")
    print(f"Total de Empregos Gerados: {total_vagas:,.0f} postos")
    print(f"Multiplicador de Produção: {np.sum(x_total)/np.sum(y):.3f}")
    
    print("\n--- DISTRIBUIÇÃO SETORIAL (Top 10 Vagas) ---")
    top_indices = np.argsort(vagas_por_setor)[-10:][::-1]
    
    setores_map = {
        64: "Arte e Cultura",
        45: "Alojamento",
        46: "Alimentação",
        41: "Transporte Terrestre",
        40: "Comércio",
        57: "Serviços Adm. (Segurança/Limpeza)",
        53: "Financeiro",
        52: "Imobiliário",
        37: "Energia Elétrica",
        18: "Refino de Petróleo"
    }

    for idx in top_indices:
        nome = setores_map.get(idx, f"Setor {idx}")
        producao = x_total[idx]
        vagas = vagas_por_setor[idx]
        print(f"  - {nome:35}: R$ {producao:7.1f} M | {vagas:7.0f} vagas")

if __name__ == "__main__":
    simulate_carnaval()
