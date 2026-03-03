import numpy as np
import os
import json

def export_data():
    print("--- EXPORTANDO DADOS PARA DASHBOARD ---")
    final_dir = 'output/final'
    inter_dir = 'output/intermediary'
    dashboard_dir = 'dashboard'
    os.makedirs(dashboard_dir, exist_ok=True)
    
    n = 67
    e = np.load(os.path.join(os.path.dirname(inter_dir), 'final', 'emp_coefficients_67x27.npy'))[:, 18]  # RJ
    
    # 1. Estatísticas da Matriz
    stats = {
        "regioes": ["Sul", "Centro_Oeste", "Norte_Nordeste", "Rio_de_Janeiro", "Sao_Paulo", "Minas_EspiritoSanto"],
        "setores_count": 67,
        "ano_base_mip": 2015,
        "ano_base_cr": 2021,
        "multiplicadores": {}
    }
    
    # Calcular multiplicadores por região para comparação
    multiplicadores_regiões = []
    for reg in stats["regioes"]:
        A = np.load(os.path.join(final_dir, f'A_{reg}.npy'))
        L = np.linalg.inv(np.eye(n) - A)
        mult_prod = np.sum(L, axis=0)
        
        region_stats = {
            "nome": reg.replace('_', ' '),
            "valor": float(np.mean(mult_prod)),
            "max": float(np.max(mult_prod))
        }
        multiplicadores_regiões.append(region_stats)
        stats["multiplicadores"][reg] = region_stats

    stats["rank_multiplicadores"] = sorted(multiplicadores_regiões, key=lambda x: x['valor'], reverse=True)

    # 2. Simulação Beyoncé
    A_rio = np.load(os.path.join(final_dir, 'A_Rio_de_Janeiro.npy'))
    L_rio = np.linalg.inv(np.eye(n) - A_rio)
    y_beyonce = np.zeros(n)
    y_beyonce[64] = 60; y_beyonce[45] = 40; y_beyonce[46] = 30; y_beyonce[41] = 20
    x_beyonce = L_rio @ y_beyonce
    emp_beyonce = e * x_beyonce
    
    beyonce_data = {
        "titulo": "Impacto Show Beyoncé (RJ)",
        "choque_direto": float(np.sum(y_beyonce)),
        "impacto_producao": float(np.sum(x_beyonce)),
        "total_empregos": float(np.sum(emp_beyonce)),
        "top_setores_prod": [
            {"nome": "Cultura", "valor": x_beyonce[64]},
            {"nome": "Alojamento", "valor": x_beyonce[45]},
            {"nome": "Alimentação", "valor": x_beyonce[46]},
            {"nome": "Transporte", "valor": x_beyonce[41]},
            {"nome": "Refino", "valor": x_beyonce[18]}
        ]
    }

    # 3. Simulação Carnaval
    y_carnaval = np.zeros(n)
    y_carnaval[64] = 1500; y_carnaval[45] = 1000; y_carnaval[46] = 800; y_carnaval[41] = 400; y_carnaval[40] = 300
    x_carn_local = L_rio @ y_carnaval
    A_nas = np.load(os.path.join(final_dir, 'A_nacional.npy'))
    L_nas = np.linalg.inv(np.eye(n) - A_nas)
    x_carn_nas = L_nas @ y_carnaval
    emp_carn = e * x_carn_local
    
    carnaval_data = {
        "titulo": "Impacto Carnaval (RJ)",
        "choque_direto": float(np.sum(y_carnaval)),
        "impacto_producao_rj": float(np.sum(x_carn_local)),
        "impacto_spillover": float(np.sum(x_carn_nas - x_carn_local)),
        "total_empregos_rj": float(np.sum(emp_carn)),
        "vagas_fora_rj": float(np.sum(e * (x_carn_nas - x_carn_local)))
    }

    # 4. Carregar Linkages
    linkages = {}
    linkages_path = os.path.join(inter_dir, 'linkages.json')
    if os.path.exists(linkages_path):
        with open(linkages_path, 'r', encoding='utf-8') as f:
            linkages = json.load(f)

    # 5. [NEW] Dados para Simulador Dinamico
    print("Gerando matrizes para simulador...")
    l_matrices = {}
    
    # Carregar labels oficiais
    labels_path = os.path.join(inter_dir, 'sector_labels.txt')
    sector_labels = []
    if os.path.exists(labels_path):
        with open(labels_path, 'r', encoding='utf-8') as f:
            sector_labels = [l.strip() for l in f.readlines()]
            
    # 1. Carregar Matriz MRIO Global (V4 Official)
    gravity_path = os.path.join(final_dir, 'A_mrio_official_v4.npy')
    region_order_path = os.path.join(final_dir, 'region_order_v4.txt')
    
    if os.path.exists(gravity_path) and os.path.exists(region_order_path):
        print("Calculando Inversa de Leontief (Global MRIO V4: 1809x1809)...")
        A_mrio = np.load(gravity_path)
        n_total = A_mrio.shape[0]
        
        # Calcular L = (I - A)^-1
        I = np.eye(n_total)
        L_mrio = np.linalg.inv(I - A_mrio)
        
        # Carregar Lista de Regiões
        with open(region_order_path, 'r') as f:
            regioes_mrio = [l.strip() for l in f.readlines()]
            
        print(f"L Global calculada. Shape: {L_mrio.shape}")
        
        # Serializar L Global (Pode ser grande, round 5 casas)
        # Estratégia: Salvar flat ou lista de listas? Lista de listas pro JSON.
        # ~3M floats.
        l_matrices = {
             "GLOBAL": np.round(L_mrio, 5).tolist()
        }
        
        # Atualizar stats
        stats["regioes"] = regioes_mrio
        stats["model_type"] = "MRIO_GRAVITY_27UF"
    else:
        # Fallback LEGACY (6 Regiões)
        print("MRIO Gravity não encontrado. Usando modo legado (6 Regiões).")
        for reg in stats["regioes"]:
            p = os.path.join(final_dir, f'A_{reg}.npy')
            if os.path.exists(p):
                A = np.load(p)
                L = np.linalg.inv(np.eye(n) - A)
                l_matrices[reg] = np.round(L, 6).tolist()
    
    # Carregar dados de impostos e expandir para 27 UFs
    tax_data_path = os.path.join('output', 'tax_data.json')
    tax_vector_full = []
    
    if os.path.exists(tax_data_path):
        with open(tax_data_path, 'r', encoding='utf-8') as f:
            tdata = json.load(f)
            # O coef_tax_total tem 67 setores (Nacional constant assumption)
            base_tax = tdata.get('coef_tax_total', [])
            
            if "global" in (k.upper() for k in l_matrices.keys()):
                 # Replicar o vetor base 27 vezes
                 num_regs = len(stats["regioes"])
                 tax_vector_full = base_tax * num_regs # List repetition [a,b] * 2 = [a,b,a,b]
            else:
                tax_vector_full = base_tax # Legado (assume vetor curto se for single region sim)
    else:
        tax_vector_full = [0.0] * (67 * 27)

    simulator_data = {
        "l_matrices": l_matrices,
        "employment_vector": list(e) * 27 if "GLOBAL" in l_matrices else list(e), # Expandido também (Assumption: Employ coeff constant)
        "tax_vector": tax_vector_full,
        "sector_labels": sector_labels,
        "regions": stats["regioes"]
    }

    # Salvar everything
    final_output = {
        "stats": stats,
        "beyonce": beyonce_data,
        "carnaval": carnaval_data,
        "linkages": linkages,
        "simulator": simulator_data
    }
    
    with open(os.path.join(dashboard_dir, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    print(f"Dados exportados para {dashboard_dir}/data.json")

if __name__ == "__main__":
    export_data()
