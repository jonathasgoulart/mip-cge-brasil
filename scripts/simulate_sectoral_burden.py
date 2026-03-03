
import json
import numpy as np

def run():
    print("=== SIMULAÇÃO DE CARGA TRIBUTÁRIA SETORIAL (ATUAL vs REFORMA) ===")
    
    # --- 1. CARREGAR DADOS ---
    try:
        # VAB (Agora já corrigido para 2021 no arquivo .npy)
        vab = np.load('output/intermediary/VAB_nacional.npy')
        print(f"VAB Nacional Carregado: R$ {np.sum(vab)/1e3:,.1f} Bi")
        
        # Impostos Atuais (Calibrados)
        with open('output/tax_data.json', 'r') as f:
            tax_data = json.load(f)
            
        # Nomes dos Setores
        with open('output/intermediary/sector_labels.txt', 'r', encoding='latin1') as f:
            labels = [line.strip() for line in f if line.strip()]
            
    except Exception as e:
        print(f"Erro carregando dados: {e}")
        return

    # Dados
    # CORREÇÃO: Usar apenas impostos DOMÉSTICOS para cálculo de carga setorial.
    # Excluir II (Imposto de Importação) pois ele onera o produto estrangeiro, não o VAB doméstico.
    
    taxes_types = tax_data['taxes_by_type']
    dom_keys = ['ICMS', 'IPI', 'ISS', 'PIS_PASEP', 'COFINS', 'IOF', 'CIDE'] # Excludes 'II'
    
    current_taxes = np.zeros(67)
    for k in dom_keys:
        if k in taxes_types:
            current_taxes += np.array(taxes_types[k])
            
    imp_taxes = np.array(taxes_types.get('II', np.zeros(67)))
    
    print(f"Total Domestic Taxes: R$ {np.sum(current_taxes)/1e3:,.1f} Bi")
    print(f"Excluded Import Taxes (II): R$ {np.sum(imp_taxes)/1e3:,.1f} Bi")
    
    # --- 2. DEFINIR GRUPOS E PARÂMETROS ---
    
    # Indices 0-based
    # Agro: 0, 1, 2
    # Extrativa: 3, 4, 5, 6
    # Ind. Transformação: 7 a 36
    # Utilidades (Energia/Agua): 37, 38
    # Construção: 39
    # Comércio: 40
    # Serviços: 41 a 66
    
    groups = {
        "Agropecuária": list(range(0, 3)),
        "Ind. Extrativa": list(range(3, 7)),
        "Ind. Transformação": list(range(7, 37)),
        "Utilidades (Energia)": [37, 38],
        "Construção Civil": [39],
        "Comércio": [40],
        "Serviços (Geral)": list(range(41, 67))
    }
    
    # Fatores da Reforma (Redutores de Alíquota)
    # Padrão = 1.0. Reduções incidem sobre a alíquota cheia.
    reform_factors = np.ones(67)
    
    # Regras (PEC Reforma Tributária - Estimativa)
    reform_factors[0:3] = 0.4   # Agro: -60%
    reform_factors[39] = 0.6    # Construção: -40% (Regime Específico)
    reform_factors[61] = 0.4    # Educação Privada: -60%
    reform_factors[63] = 0.4    # Saúde Privada: -60%
    # Public Admin/Saude/Educação (59, 60, 62): Assumindo isenção (Output não comercial).
    reform_factors[59] = 0.0
    reform_factors[60] = 0.0
    reform_factors[62] = 0.0
    # Transporte Público (41, 42?): Alguns têm redução. Vamos manter 1.0 para Transp Carga (maioria) por prudência.
    
    # --- 3. CÁLCULO CARGA ATUAL ---
    print("\n[CENÁRIO ATUAL]")
    
    results = {}
    
    total_tax_current = 0.0
    total_vab_base = 0.0
    
    print(f"{'Grupo':<20} | {'VAB (Bi)':<10} | {'Tax Atual':<10} | {'Carga/VAB %':<12}")
    print("-" * 60)
    
    for gname, indices in groups.items():
        g_vab = np.sum(vab[indices])
        g_tax = np.sum(current_taxes[indices])
        
        burden = (g_tax / g_vab) * 100 if g_vab > 0 else 0
        
        results[gname] = {
            "vab": g_vab,
            "tax_current": g_tax,
            "burden_current": burden,
            "indices": indices
        }
        
        total_tax_current += g_tax
        if gname != "Serviços (Geral)": # Add all to base initially?
             pass 
        
        print(f"{gname:<20} | {g_vab/1e3:<10.1f} | {g_tax/1e3:<10.1f} | {burden:<12.2f}")
    
    print("-" * 60)
    print(f"TOTAL GERAL          | {np.sum(vab)/1e3:<10.1f} | {total_tax_current/1e3:<10.1f} | {(total_tax_current/np.sum(vab))*100:<12.2f}")

    # --- 4. CÁLCULO CENÁRIO REFORMA ---
    print("\n[CENÁRIO REFORMA TRIBUTÁRIA]")
    
    # Calcular Nova Base Ponderada
    # Base = Sum(VAB_setor * Factor_setor)
    # A Alíquota Padrão 'R' deve satisfazer: R * Base = Revenue_Target
    
    # Revenue Target = Arrecadação Atual (Neutralidade Global)
    # Target = R$ 1.11 Tri (do passo anterior)
    
    TARGET_REVENUE = total_tax_current
    
    weighted_base = 0.0
    for i in range(67):
        weighted_base += vab[i] * reform_factors[i]
        
    print(f"Receita Alvo (Neutralidade): R$ {TARGET_REVENUE/1e3:,.1f} Bi")
    print(f"Base de Cálculo Ponderada:   R$ {weighted_base/1e3:,.1f} Bi")
    
    # Alíquota Padrão Necessária
    STANDARD_RATE = (TARGET_REVENUE / weighted_base) 
    STANDARD_RATE_PCT = STANDARD_RATE * 100
    
    print(f"-> ALÍQUOTA PADRÃO CALCULADA: {STANDARD_RATE_PCT:.2f}%")
    
    # Calcular Carga por Grupo na Reforma
    print("\nCOMPARATIVO CARGA EFETIVA (Tax/VAB)")
    print(f"{'Grupo':<20} | {'Atual %':<10} | {'Reforma %':<10} | {'Variação':<10}")
    print("-" * 60)
    
    for gname, info in results.items():
        indices = info['indices']
        
        # Tax Reform = Sum(VAB_i * Rate_Std * Factor_i)
        # Burden = Tax_Reform / VAB_Total_Group
        
        g_tax_reform = 0.0
        for i in indices:
            g_tax_reform += vab[i] * STANDARD_RATE * reform_factors[i]
            
        burden_reform = (g_tax_reform / info['vab']) * 100 if info['vab'] > 0 else 0
        diff = burden_reform - info['burden_current']
        
        print(f"{gname:<20} | {info['burden_current']:<10.2f} | {burden_reform:<10.2f} | {diff:+10.2f}")
        
    print("-" * 60)
    
    # Detalhe Serviços Especiais
    print("\n[DETALHE: SERVIÇOS ESPECÍFICOS]")
    specials = [
        (61, "Educação Privada"),
        (63, "Saúde Privada"), 
        (54, "Jurídico/Contábil"), # Geralmente Prof Liberais tem -30%. Aqui tá 1.0 (Full). Teste de sensibilidade?
        (50, "Desenv. Sistemas")
    ]
    
    for idx, name in specials:
        v = vab[idx]
        t_curr = current_taxes[idx]
        b_curr = (t_curr/v)*100 if v>0 else 0
        
        t_ref = v * STANDARD_RATE * reform_factors[idx]
        b_ref = (t_ref/v)*100 if v>0 else 0
        
        print(f"{name:<20} | Atual: {b_curr:.2f}% -> Reforma: {b_ref:.2f}% (Fator: {reform_factors[idx]})")

if __name__ == "__main__":
    run()
