import numpy as np
import os

def calculate_employment_impact():
    print("--- SIMULAÇÃO DE IMPACTO: EMPREGO (ESTIMATIVA) ---")
    final_dir = 'output/final'
    inter_dir = 'output/intermediary'
    
    # 1. Carregar X_nas (Produção Nacional) para escala
    X_nas = np.load(os.path.join(inter_dir, 'X_nas.npy'))
    n = len(X_nas) # 67 setores
    
    # 2. DEFINIÇÃO DOS COEFICIENTES DE EMPREGO (E)
    # e_j = Pessoal Ocupado / Produção Total (em pessoas por R$ 1 Milhão)
    # Carregando dos benchmarks gerados
    coeff_path = os.path.join(os.path.dirname(inter_dir), 'final', 'emp_coefficients_67x27.npy')
    if os.path.exists(coeff_path):
        e = np.load(coeff_path)
        print("Coeficientes de Emprego carregados com sucesso.")
    else:
        print("Erro: Coeficientes não encontrados. Usando fallback.")
        e = np.zeros(n)
        e.fill(2.5) 
    
    # 3. Rodar a simulação de impacto novamente (como no script anterior)
    A_rio = np.load(os.path.join(final_dir, 'A_Rio_de_Janeiro.npy'))
    I = np.eye(n)
    L_rio = np.linalg.inv(I - A_rio)
    
    # Choque de R$ 150M
    y = np.zeros(n)
    y[64] = 60; y[45] = 40; y[46] = 30; y[41] = 20
    
    # Impacto total na produção (Direto + Indireto)
    x_total = L_rio @ y
    
    # 4. Impacto no Emprego (Delta E = e * Delta x)
    empregos_por_setor = e * x_total
    total_empregos = np.sum(empregos_por_setor)
    
    # 5. Resultados
    print(f"\nIMPACTO TOTAL EM EMPREGOS: {total_empregos:.0f} postos de trabalho")
    print(f"Multiplicador de Emprego Total: {total_empregos / np.sum(y):.3f} empregos / R$ 1M")
    
    print("\nDistribuição do Emprego Gerado (Top Setores):")
    top_indices = np.argsort(empregos_por_setor)[-8:][::-1]
    
    setores_map = {
        64: "Cultura e Espetáculos", # Atividades artísticas
        45: "Alojamento",
        46: "Alimentação",
        41: "Transporte Terrestre",
        57: "Serviços Administrativos",
        40: "Comércio",
        18: "Refino de Petróleo"
    }

    for idx in top_indices:
        nome = setores_map.get(idx, f"Setor {idx}")
        print(f"  - {nome:25}: {empregos_por_setor[idx]:5.1f} vagas")

if __name__ == "__main__":
    calculate_employment_impact()
