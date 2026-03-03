
import json
import numpy as np

def run():
    print("=== VAB POR ESTADO (MATRIZ AJUSTADA 2021) ===")
    
    # 1. Load Raw Regional Data
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
        
    # 2. Calculate Raw Sum
    raw_total = 0.0
    state_totals = {}
    
    for uf, values in vab_regional.items():
        s_sum = np.sum(values)
        state_totals[uf] = s_sum
        raw_total += s_sum
        
    print(f"Soma Bruta da Matriz Regional: R$ {raw_total/1e6:,.2f} Trilhões (Provável VP)")
    
    # 3. Target 2021 (Tabela 33 IBGE)
    TARGET_VAB_2021 = 7713999.0 # R$ 7.714 Bi
    
    print(f"Meta VAB Oficial 2021:       R$ {TARGET_VAB_2021/1e6:,.2f} Trilhões")
    
    # 4. Scale Factor
    scale = TARGET_VAB_2021 / raw_total
    print(f"Fator de Ajuste (Escala):    {scale:.4f}\n")
    
    # 5. List States
    print(f"{'Ranking':<3} | {'UF':<4} | {'VAB 2021 (R$ Bi)':<15} | {'Part. (%)':<10}")
    print("-" * 50)
    
    # Sort by VAB
    sorted_states = sorted(state_totals.items(), key=lambda x: x[1], reverse=True)
    
    check_sum = 0.0
    for i, (uf, raw_val) in enumerate(sorted_states):
        final_val = raw_val * scale
        share = (final_val / TARGET_VAB_2021) * 100
        check_sum += final_val
        
        print(f"{i+1:<3} | {uf:<4} | {final_val/1e3:,.1f}           | {share:<10.2f}")
        
    print("-" * 50)
    print(f"TOTAL BRASIL   | {check_sum/1e3:,.1f}           | 100.00%")

if __name__ == "__main__":
    run()
