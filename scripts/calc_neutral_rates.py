
import json
import numpy as np
import os

def run():
    print("=== CÁLCULO DE ALÍQUOTAS NEUTRAS (REFORMA TRIBUTÁRIA - IBS/CBS) ===")
    
    # --- 1. SETTINGS & CONSTANTS (2015 REFERENCE) ---
    # Valores de referência para "Revenue Neutrality" (Neutralidade de Arrecadação)
    # Fonte: Carga Tributária Receita Federal 2015 (R$ Milhões)
    
    # TARGET FEDERAL (CBS): PIS (57k) + COFINS (202k) + IPI (48k)
    # Total ~ 307 Bi. Vamos usar 300 Bi para ser conservador/arredondado ou exato.
    # Exato: 57432 + 201708 + 48048 = 307188.
    TARGET_CBS_REVENUE = 307188.0 
    
    # TARGET SUBNATIONAL (IBS): ICMS (396k) + ISS (54k)
    # ICMS: 396428 (Process Taxes Script Reference)
    # ISS: 54454 (Process Taxes Script Reference)
    TARGET_ICMS_NATIONAL = 396428.0
    TARGET_ISS_NATIONAL = 54454.0
    TARGET_IBS_REVENUE = TARGET_ICMS_NATIONAL + TARGET_ISS_NATIONAL
    
    # TOTAL REVENUE TARGET
    TOTAL_TARGET = TARGET_CBS_REVENUE + TARGET_IBS_REVENUE
    
    print(f"Target Receita CBS (Federal): R$ {TARGET_CBS_REVENUE/1e3:,.1f} Bi")
    print(f"Target Receita IBS (Subnac): R$ {TARGET_IBS_REVENUE/1e3:,.1f} Bi")
    print(f"Target TOTAL (Consumo):      R$ {TOTAL_TARGET/1e3:,.1f} Bi")
    
    # --- 2. LOAD DATA ---
    print("\n--- Carregando Dados Econômicos (MIP/VAB) ---")
    
    # Load Regional VAB
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f) # {UF: [67 values]}
        
    # Load Regional ICMS (Existing)
    with open('output/icms_regional_v3_final.json', 'r', encoding='utf-8') as f:
        icms_data = json.load(f)
        
    # --- 3. DEFINE TAX BASE (BASE DE CÁLCULO) ---
    # A base do IVA (IBS/CBS) é o Valor Adicionado em toda a cadeia (~ PIB)
    # Ajustes finos: PIB - Exportações - Investimentos + Importações (Consumo Final)
    # Como proxy robusto para alíquota de referência, usaremos o VAB Total.
    # Nota: O Governo estima alíquota de 26.5% sobre uma base ampla de consumo.
    # Se usarmos VAB puro, a base é um pouco maior que o Consumo (pois inclui Investimento).
    # Se ajustarmos VAB * 0.85 (Proxy Consumo), a alíquota sobe.
    # Vamos calcular ambos os cenários.
    
    # --- 3. DEFINE TAX BASE (BASE DE CÁLCULO) ---
    # A base do IVA (IBS/CBS) é o Valor Adicionado em toda a cadeia (~ PIB)
    # DIAGNOSTICO: A soma do vab_regional está dando ~15.8 Trillion, o que é muito alto para 2015 (~6T GDP, ~5.5T VAB).
    # Provavelmente os dados regionais estão em Produção (X) ou inflacionados.
    # CORREÇÃO: Vamos normalizar o Total para um VAB Nacional Realista de 2015.
    
    # Referência IBGE 2021: VAB ~ 7.7 Trilhões (Tabela 33).
    # Como nossos Impostos (Targets) são de 2021, o Denominador (VAB) PRECISA ser de 2021.
    OFFICIAL_VAB_2021 = 7713999.0 # R$ 7.71 Trillion (Millions)
    # OFFICIAL_VAB_2015 = 5500000.0 # OLD
    
    # Calcular VAB Nacional (Sum of Regional)
    vab_sum_raw = 0.0
    for values in vab_regional.values():
        vab_sum_raw += np.sum(values)
        
    print(f"VAB Regional Raw Sum: R$ {vab_sum_raw/1e3:,.1f} Bi (Inflated/Production?)")
    print(f"Adjusting to Official VAB 2021: R$ {OFFICIAL_VAB_2021/1e3:,.1f} Bi")
    
    SCALE_FACTOR = OFFICIAL_VAB_2021 / vab_sum_raw if vab_sum_raw > 0 else 1.0
    print(f"Applied Scale Factor: {SCALE_FACTOR:.4f}")
    
    # Recalculate Adjusted VABs
    vab_states_total = {}
    vab_national_sectoral = np.zeros(67)
    
    for uf, values in vab_regional.items():
        vab_arr = np.array(values) * SCALE_FACTOR
        total_uf = np.sum(vab_arr)
        vab_states_total[uf] = total_uf
        vab_national_sectoral += vab_arr

    BASE_VAB_TOTAL = np.sum(vab_national_sectoral)
    
    print(f"Base de Cálculo (VAB Total Ajustado): R$ {BASE_VAB_TOTAL/1e3:,.1f} Bi")
    
    # --- 4. CÁLCULO DE ALÍQUOTAS NACIONAIS (MÉDIAS) ---
    
    # Cenário 1: Base = VAB (Otimista/Base cheia)
    rate_cbs_vab = (TARGET_CBS_REVENUE / BASE_VAB_TOTAL) * 100
    rate_ibs_vab = (TARGET_IBS_REVENUE / BASE_VAB_TOTAL) * 100
    
    # Cenário 2: Base = Consumo Efectivo (~85% do VAB... ou ~65% do PIB?)
    # Se Consumo das Familias + Governo ~ 80% do PIB -> ~85% do VAB.
    # Vamos manter 0.85 como estimativa de base ampla.
    CONSUMPTION_FACTOR = 0.85
    BASE_CONSUMPTION = BASE_VAB_TOTAL * CONSUMPTION_FACTOR
    
    rate_cbs_cons = (TARGET_CBS_REVENUE / BASE_CONSUMPTION) * 100
    rate_ibs_cons = (TARGET_IBS_REVENUE / BASE_CONSUMPTION) * 100
    
    print("\n[RESULTADOS NACIONAIS PRELIMINARES]")
    print(f"Alíquota CBS (Federal): {rate_cbs_vab:.2f}% (Base VAB) | {rate_cbs_cons:.2f}% (Base Consumo)")
    print(f"Alíquota IBS (Média):   {rate_ibs_vab:.2f}% (Base VAB) | {rate_ibs_cons:.2f}% (Base Consumo)")
    print(f"Aliq. PADRÃO (TOTAL):   {rate_cbs_vab+rate_ibs_vab:.2f}% (Base VAB) | {rate_cbs_cons+rate_ibs_cons:.2f}% (Base Consumo)")
    
    print(f"\nNota: A estimativa oficial Governo é ~26.5%. Nossos dados 2015 indicam {(rate_cbs_cons+rate_ibs_cons):.1f}% se base for Consumo Ajustado.")
    
    # --- 5. CÁLCULO ESTADUAL (RJ, MG, SP) ---
    print("\n--- Detalhamento Estadual (RJ, MG, SP) ---")
    
    # Para calcular a alíquota neutra ESTADUAL do IBS:
    # Receita Alvo UF = ICMS_Atual_UF + (ISS_Nacional * Share_Servicos_UF)
    # Base UF = VAB_UF (ajustado pelo fator consumo)
    
    # Definir setores de Serviço para rateio do ISS
    # Indices 0-based: Construção (39) até Doméstico (66), exceto talvez Comércio (40)?
    # ISS incide forte em: 51 dev 66.
    # Vamos usar VAB dos setores 49 a 66 como proxy de "Serviços ISS".
    # (Sector labels indicam indices. Vamos assumir range fim da lista).
    
    # Heurística: Isolar setores 1-67.
    # ISS Sectors indices (aprox): 39 (Constr), 45-46 (Aloj/Alim?), 49-66 (Serviços Puro).
    # Vamos usar peso geral de serviços.
    
    target_states = ['RJ', 'SP', 'MG']
    
    # Calcular Total Service VAB Nacional ACORRIGIDO para normalizar ISS
    # Slice 49:67 (últimos 18 setores) - Ajustar conforme labels se necessario
    # Usando indices 40 a 67 como "Terciário"
    SERVICES_SLICE = slice(40, 67) 
    
    vab_serv_national = np.sum(vab_national_sectoral[SERVICES_SLICE])
    
    print(f"VAB Serviços Nacional (Proxy ISS Base): R$ {vab_serv_national/1e3:,.1f} Bi")
    
    results = []
    
    for uf in target_states:
        # 1. Receita ICMS Atual (Target)
        # Buscar do JSON de ICMS Regional
        current_icms = icms_data['by_uf'].get(uf, {}).get('total_icms_milhoes', 0.0)
        
        # 2. Receita ISS estimada
        # Usar VAB ajustado
        vab_uf_all = np.array(vab_regional[uf]) * SCALE_FACTOR
        vab_serv_uf = np.sum(vab_uf_all[SERVICES_SLICE])
        
        share_serv = vab_serv_uf / vab_serv_national if vab_serv_national > 0 else 0
        est_iss = TARGET_ISS_NATIONAL * share_serv
        
        # 3. Target IBS UF
        target_ibs_uf = current_icms + est_iss
        
        # 4. Base IBS UF (Consumo Residente + Governo Local)
        # Proxy: VAB UF * CONSUMPTION_FACTOR
        base_uf = np.sum(vab_uf_all) * CONSUMPTION_FACTOR
        
        # 5. Alíquota Neutra
        rate_ibs_uf = (target_ibs_uf / base_uf) * 100
        
        results.append({
            "uf": uf,
            "icms": current_icms,
            "iss_est": est_iss,
            "target_ibs": target_ibs_uf,
            "base": base_uf,
            "rate": rate_ibs_uf
        })

        
    print(f"{'UF':<4} | {'ICMS(Bi)':<10} | {'ISS(Bi)':<10} | {'Meta IBS':<10} | {'Base(Bi)':<10} | {'Aliq. IBS(%)':<12}")
    print("-" * 75)
    for r in results:
        print(f"{r['uf']:<4} | {r['icms']/1e3:<10.2f} | {r['iss_est']/1e3:<10.2f} | {r['target_ibs']/1e3:<10.2f} | {r['base']/1e3:<10.2f} | {r['rate']:<12.2f}")
        
    print("-" * 75)
    print("Nota: 'Aliq. IBS(%)' é a alíquota necessária para manter a arrecadação atual (ICMS+ISS).")
    print(f"Considerando Alíquota CBS Federal fixa de {rate_cbs_cons:.2f}%.")
    print("Carga Total Estimada (IBS+CBS) nos Estados:")
    for r in results:
        total_rate = r['rate'] + rate_cbs_cons
        print(f"  {r['uf']}: {total_rate:.2f}%")

    # Save Results
    out_path = 'output/ibs_neutral_rates_simulation.json'
    with open(out_path, 'w') as f:
        json.dump({
            "national": {
                "base_vab": BASE_VAB_TOTAL,
                "target_cbs": TARGET_CBS_REVENUE,
                "target_ibs": TARGET_IBS_REVENUE,
                "rate_cbs_cons": rate_cbs_cons,
                "rate_ibs_avg_cons": rate_ibs_cons
            },
            "states": results
        }, f, indent=2)
    print(f"\nResultados detalhados salvos em {out_path}")

if __name__ == "__main__":
    run()
