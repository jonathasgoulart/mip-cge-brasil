import numpy as np
import os

def simulate_spillover():
    print("--- ANÁLISE DE TRANSBORDAMENTO (SPILLOVER): CARNAVAL DO RIO ---")
    final_dir = 'output/final'
    inter_dir = 'output/intermediary'
    
    # 1. Carregar Matrizes
    A_rio = np.load(os.path.join(final_dir, 'A_Rio_de_Janeiro.npy'))
    A_nas = np.load(os.path.join(final_dir, 'A_nacional.npy'))
    n = 67
    
    # 2. Calcular Inversas de Leontief
    print("Calculando multiplicadores locais e nacionais...")
    L_rio = np.linalg.inv(np.eye(n) - A_rio)
    L_nas = np.linalg.inv(np.eye(n) - A_nas)
    
    # 3. Definir o Choque (R$ 4 Bilhões no Rio)
    y = np.zeros(n)
    y[64] = 1500; y[45] = 1000; y[46] = 800; y[41] = 400; y[40] = 300
    
    # 4. Calcular Impactos
    x_local = L_rio @ y
    x_nacional = L_nas @ y
    
    # O transbordamento é a diferença entre o que o Brasil produz e o que o Rio retém
    x_spillover = x_nacional - x_local
    
    # 5. Empregos
    e = np.load(os.path.join(os.path.dirname(inter_dir), 'final', 'emp_coefficients_67x27.npy'))[:, 18]  # RJ
    vagas_rj = np.sum(e * x_local)
    vagas_br = np.sum(e * x_nacional)
    vagas_spillover = vagas_br - vagas_rj
    
    # 6. Resultados
    print(f"\n--- IMPACTO COMPARATIVO ---")
    print(f"Impacto na PRODUÇÃO (Total BR): R$ {np.sum(x_nacional):,.0f} Milhões")
    print(f"Impacto RETIDO no Rio de Jan: R$ {np.sum(x_local):,.0f} Milhões")
    print(f"Efeito TRANSBORDAMENTO (Outros): R$ {np.sum(x_spillover):,.0f} Milhões")
    
    print(f"\n--- IMPACTO EM EMPREGOS ---")
    print(f"Vagas totais no Brasil       : {vagas_br:,.0f}")
    print(f"Vagas retidas no Rio         : {vagas_rj:,.0f}")
    print(f"Vagas geradas nos DEMAIS ESTADOS: {vagas_spillover:,.0f}")
    
    print("\n--- PRINCIPAIS SETORES BENEFICIADOS NOS DEMAIS ESTADOS ---")
    # Onde o Rio mais "vaza" demanda?
    top_spillover = np.argsort(x_spillover)[-8:][::-1]
    
    setores_map = {
        0: "Arroz/Cereais (Alimentação)",
        4: "Soja",
        18: "Refino de Petróleo",
        40: "Comércio (Atacado nacional)",
        51: "Serviços Financeiros",
        32: "Rações/Produtos Alimentares",
        22: "Produtos Químicos",
        37: "Energia Elétrica"
    }

    for idx in top_spillover:
        nome = setores_map.get(idx, f"Setor {idx}")
        valor = x_spillover[idx]
        print(f"  - {nome:30}: R$ {valor:7.1f} M")

if __name__ == "__main__":
    simulate_spillover()
