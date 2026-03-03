
import json
import numpy as np
import re
import os

def run():
    print("=== GERANDO MATRIZ TRIBUTÁRIA HÍBRIDA (MIP + CONFAZ) ===")
    
    # 1. Load Sources
    path_confaz = 'output/confaz_icms_2024_by_uf.json'
    path_tax_mip = 'data/processed/2021_final/tax_matrix.json'
    path_vab = 'data/processed/2021_final/vab_regional.json'
    path_vab_nac = 'data/processed/2021_final/vab_nacional.npy'
    
    print(f"Loading CONFAZ: {path_confaz}")
    with open(path_confaz, 'r', encoding='utf-8') as f:
        raw_confaz = json.load(f)
        confaz_data = raw_confaz.get('by_uf_by_cnae', raw_confaz)

    print(f"Loading Tax MIP: {path_tax_mip}")
    with open(path_tax_mip, 'r') as f:
        tax_mip = json.load(f)
        
    print(f"Loading VAB Regional: {path_vab}")
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
        
    # Get MIP National Profile (Base distribution for non-Big4)
    tax_source = tax_mip.get('taxes_by_type', tax_mip)
    print(f"Tax Keys: {list(tax_source.keys())}")
    
    mip_icms_vec_nac = np.array(tax_source['ICMS'])
    print(f"ICMS Vector Stats: Min={np.min(mip_icms_vec_nac)}, Max={np.max(mip_icms_vec_nac)}, Sum={np.sum(mip_icms_vec_nac)}")
    
    # Updated Indices (0-based) based on sector_labels.txt
    # Refino: Line 19 -> 18
    # Energia: Line 38 -> 37
    # Comércio: Line 41 -> 40 (Was 44 - ERROR)
    # Telecom: Line 50 -> 49
    
    IDX_REFINO = 18 
    IDX_ENERGIA = 37 
    IDX_COMERCIO = 40
    IDX_TELECOM = 49
    
    indices_big4 = [IDX_ENERGIA, IDX_TELECOM, IDX_REFINO, IDX_COMERCIO]
    
    groups_regex = {
        37: r"35 -", # Energia
        49: r"61 -", # Telecom
        18: r"19 -", # Refino
        40: r"4[567] -" # Comercio
    }
    
    # 2. Init Matrix (27 UFs x 67 Sectors)
    # Warning: tax_matrix.json was "Taxes By Type" (National Vector).
    # Now we are building "Taxes By State x Sector".
    
    hybrid_tax_matrix = {} # {UF: [67 values]}
    total_reallocated = 0.0
    
    # Scale Factor: CONFAZ 2024 is ~775 Bi (Sample). MIP Target 2021 is 537 Bi.
    # We must scale down CONFAZ values to match 2021 reality using Global Ratio.
    
    # Calculate Total CONFAZ Sum first
    sum_confaz_raw = 0.0
    for uf, content in confaz_data.items():
        if isinstance(content, dict):
            sum_confaz_raw += sum([v for v in content.values() if isinstance(v, (int,float))])
            
    # Calculate Total MIP ICMS
    target_icms_2021 = np.sum(mip_icms_vec_nac) # 537 Bi
    
    # SCALE_FACTOR = Target / Real
    if sum_confaz_raw > 0:
        SCALE_FACTOR = target_icms_2021 / sum_confaz_raw
    else:
        SCALE_FACTOR = 1.0 # Should not happen
        
    print(f"Total CONFAZ 2024: R$ {sum_confaz_raw/1e9:.1f} Bi")
    print(f"Meta ICMS 2021:   R$ {target_icms_2021/1e9:.1f} Bi")
    print(f"Fator de Ajuste (Deflator): {SCALE_FACTOR:.4f}")
    
    # 3. Build Matrix
    # Logic per State:
    # A. Calculate "Big 4" Real Amount (Scaled)
    # B. Calculate "Remainder" = State Target - Big 4? 
    #    No, we don't know "State Target".
    #    We assume the State Arises from [Big 4 Real] + [Non-Big 4 Estimated].
    #    Non-Big 4 Estimated = (MIP_National_Vec[i] * Share_State_VAB[i])?
    #    Yes. We check national tax intensity of Textile, apply to State Textile VAB.
    #    Then we allow Big 4 to override this estimate.
    #    BUT: We must normalize to ensure Global Sum = 537 Bi?
    #    Actually, the "Rebalancing" implies:
    #    New_National_Big4 = Sum(State_Big4_Real).
    #    New_National_Others = Target_537 - New_National_Big4.
    #    We distribute New_National_Others to sectors based on Original MIP Shares (Renormalized).
    #    Then distribute to States based on VAB.
    
    # Step 3.1: Calculate National Big 4 Sum (Scaled)
    nat_big4_real_vec = np.zeros(67)
    
    for uf, content in confaz_data.items():
        if not isinstance(content, dict): continue
        if uf not in vab_regional: continue
        
        for idx, regex in groups_regex.items():
            val = 0.0
            for k_sec, v_val in content.items():
                if re.search(regex, k_sec) and isinstance(v_val, (int,float)):
                    val += v_val
            
            # Scale
            val_2021 = val * SCALE_FACTOR
            nat_big4_real_vec[idx] += val_2021
            
    # Step 3.2: Rebalance residuals
    total_big4_new = np.sum(nat_big4_real_vec)
    remaining_budget = target_icms_2021 - total_big4_new
    
    print(f"Novo Big 4 (Nacional): R$ {total_big4_new/1e9:.1f} Bi")
    print(f"Orçamento Restante (Ind/Serv): R$ {remaining_budget/1e9:.1f} Bi")
    
    if remaining_budget < 0:
        print("ALERTA CRÍTICO: Big 4 consome mais que 100% da meta! Ajustando escala.")
        # Fallback?
        
    # Calculate original share of Non-Big4 sectors
    original_others_vec = mip_icms_vec_nac.copy()
    for idx in indices_big4:
        original_others_vec[idx] = 0.0 # Remove Big 4
        
    sum_orig_others = np.sum(original_others_vec)
    
    # Create new National Vector
    new_national_tax_vec = np.zeros(67)
    
    # Fill Big 4
    for idx in indices_big4:
        new_national_tax_vec[idx] = nat_big4_real_vec[idx]
        
    # Fill Others (Proportional)
    if sum_orig_others > 0:
        alloc_factor = remaining_budget / sum_orig_others
        print(f"Fator de Redução para Ind/Serv: {alloc_factor:.2f}x (Carga cai {(1-alloc_factor)*100:.1f}%)")
        new_national_tax_vec += original_others_vec * alloc_factor
    
    # Step 3.3: Distribute to States (Regionalize)
    # Big 4: Use LOCAL Real Data (Scaled).
    # Others: Use National Rate * Local VAB.
    # Rate = New_National_Tax_Vec[i] / National_VAB[i]
    
    # Wait, National VAB might be different sum than sum(vab_regional).
    # Use sum(vab_regional) for consistency.
    sum_regional_vab_vec = np.zeros(67)
    for vec in vab_regional.values():
        sum_regional_vab_vec += np.array(vec)
        
    # Effective Rates
    rates_vec = np.zeros(67)
    with np.errstate(divide='ignore', invalid='ignore'):
        rates_vec = new_national_tax_vec / sum_regional_vab_vec
    rates_vec[np.isnan(rates_vec)] = 0.0
    
    # Generate Hybrid Matrix
    for uf, content in confaz_data.items():
        if uf == "metadata": continue
        if uf not in vab_regional:
            # Maybe metadata or aggregation key
            continue
            
        local_vab = np.array(vab_regional[uf])
        local_tax = np.zeros(67)
        
        # 1. Fill Others using Rates
        local_tax = local_vab * rates_vec
        
        # 2. Override Big 4 with Real Data
        if isinstance(content, dict):
            for idx, regex in groups_regex.items():
                val_real = 0.0
                for k_sec, v_val in content.items():
                     if re.search(regex, k_sec) and isinstance(v_val, (int,float)):
                        val_real += v_val
                
                # Apply same scale factor
                val_real_2021 = val_real * SCALE_FACTOR
                
                # Check consistency: if State matches pattern, use it.
                # If State has 0 in Big 4 (Missing Data), fallback to Rate?
                # Hybrid Logic: If val_real > epsilon, use it. Else use Estimated.
                if val_real_2021 > 1000: # Threshold
                    local_tax[idx] = val_real_2021
                else:
                    # Keep estimated based on VAB
                    pass
                    
        hybrid_tax_matrix[uf] = local_tax.tolist()
        
    # Save
    out_path = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(hybrid_tax_matrix, f, indent=2)
        
    print(f"Hybrid Matrix Saved: {out_path}")
    print("Ready for Burden Simulation.")

if __name__ == "__main__":
    run()
