
import json
import numpy as np
import re

def run():
    print("=== ANÁLISE DE INTEGRAÇÃO HÍBRIDA (CONFAZ vs MIP) ===")
    
    path_confaz = 'output/confaz_icms_2024_by_uf.json'
    path_tax_mip = 'data/processed/2021_final/tax_matrix.json'
    
    with open(path_confaz, 'r', encoding='utf-8') as f:
        confaz_data = json.load(f)
    with open(path_tax_mip, 'r') as f:
        tax_mip = json.load(f)
        
    tax_source = tax_mip.get('taxes_by_type', tax_mip)
    mip_icms_vec = np.array(tax_source['ICMS'])
    total_mip_icms = np.sum(mip_icms_vec)
    print(f"Total MIP ICMS: {total_mip_icms/1000:,.1f} Bi")

    # Load Labels to find indices dynamically
    labels = []
    try:
        with open('output/intermediary/sector_labels.txt', 'r', encoding='latin1') as f:
            labels = [l.strip() for l in f if l.strip()]
    except: pass
    
    # helper
    def find_idx(keyword):
        for i, l in enumerate(labels):
            if keyword.lower() in l.lower():
                return i
        return -1
        
    # Hardcode best guess indices for standard MIP 67
    mip_indices = {
        "Energia": 37,
        "Telecom": 49,
        "Refino": 18,
        "Comercio": 44
    }
    
    groups = {
        "Energia": r"35 -",
        "Telecom": r"61 -",
        "Refino": r"19 -",
        "Comercio": r"4[567] -"
    }
    
    # 3. Sum CONFAZ
    confaz_sums = {k: 0.0 for k in groups}
    total_confaz = 0.0
    
    # Correct Data Source
    data_source = confaz_data.get('by_uf_by_cnae', confaz_data)
    
    print(f"Available States: {list(data_source.keys())[:10]}")
    for uf, content in data_source.items():
        if not isinstance(content, dict): continue 
        
        # Debug Keys for first UF
        # Calculate State Total carefully
        uf_total = 0.0
        for k_sec, v_val in content.items():
            if isinstance(v_val, (int, float)):
                 uf_total += v_val
                 
                 for g_name, pattern in groups.items():
                     if re.search(pattern, k_sec):
                         confaz_sums[g_name] += v_val
                         
        total_confaz += uf_total

    print("\n--- Comparativo Big 4 (R$ Bi) ---")
    sum_mip = 0
    sum_confaz = 0
    
    for k in groups:
        idx = mip_indices[k]
        if idx == -1: continue
        
        m_val = mip_icms_vec[idx] / 1000.0
        c_val = confaz_sums[k] / 1e9
        
        print(f"{k}: MIP={m_val:.1f} | CONFAZ={c_val:.1f} | ShareReal={c_val/(total_confaz/1e9):.1%}")
        sum_mip += m_val
        sum_confaz += c_val
        
    total_confaz_bi = total_confaz/1e9
    share_mip = sum_mip / (total_mip_icms/1000.0)
    share_confaz = sum_confaz / total_confaz_bi
    
    print("-" * 30)
    print(f"Total Big 4: MIP={sum_mip:.1f} | CONFAZ={sum_confaz:.1f}")
    print(f"Share Big 4: MIP={share_mip:.1%} | CONFAZ={share_confaz:.1%}")
    
    diff = share_confaz - share_mip
    print(f"REBALANCEAMENTO: Aumentar Big 4 em {diff*100:+.1f} pp.")
    
if __name__ == "__main__":
    run()
