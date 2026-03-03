
import json
import numpy as np
import pandas as pd
import os

def run():
    print("=== GERANDO MATRIZ ECONOMIA CRIATIVA (FOCO RJ) ===")
    
    # 1. Load Data
    path_vab = 'data/processed/2021_final/vab_regional.json'
    path_tax = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    path_struct = 'data/processed/2021_final/tax_matrix.json'
    
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
        
    with open(path_tax, 'r') as f:
        icms_data = json.load(f)
        
    with open(path_struct, 'r') as f:
        struct_data = json.load(f).get('taxes_by_type', {})
        
    # Prepare Structural Tax Vector (National)
    struct_taxes = ["PIS_PASEP", "COFINS", "IPI", "ISS"]
    struct_vec_nac = np.zeros(67)
    for k in struct_taxes:
        if k in struct_data:
            struct_vec_nac += np.array(struct_data[k])
            
    # We need to distribute Structural Tax to Regions to aggregate correctly.
    # Assumption: Proportional to VAB (Standard Model Rule).
    # Calc National VAB per sector
    vab_nac = np.zeros(67)
    for vec in vab_data.values():
        vab_nac += np.array(vec)
        
    # Struct Rates
    struct_rates = np.divide(struct_vec_nac, vab_nac, out=np.zeros_like(struct_vec_nac), where=vab_nac!=0)
    
    # 2. Define Groups
    # Indices are 0-based. ID 1 -> Index 0.
    
    SECTOR_GROUPS = {
        "Audiovisual & Mídia": [47, 48], # IDs 48, 49
        "Artes & Espetáculos": [64],     # ID 65
        "Tecnologia & Software": [50],   # ID 51
        "Turismo & Lazer": [45, 46],     # IDs 46, 47 (Alojamento, Alimentacao)
        "Agropecuária": [0, 1, 2],       # IDs 1, 2, 3
        # Industry: 4 to 40 (Indices 3 to 39)
        "Indústria & Construção": list(range(3, 40)), 
        # All others go to Services
    }
    
    # Flatten defined indices to find "Others"
    defined_indices = []
    for idxs in SECTOR_GROUPS.values():
        defined_indices.extend(idxs)
    defined_indices = set(defined_indices)
    
    others = [i for i in range(67) if i not in defined_indices]
    SECTOR_GROUPS["Demais Serviços"] = others
    
    REGIONS = {
        "Rio de Janeiro": ["RJ"],
        "Resto do Brasil": [uf for uf in vab_data.keys() if uf != "RJ"]
    }
    
    # 3. Aggregate
    results = []
    
    for reg_name, ufs in REGIONS.items():
        for sec_name, indices in SECTOR_GROUPS.items():
            
            val_vab = 0.0
            val_tax = 0.0
            
            for uf in ufs:
                if uf not in vab_data: continue
                
                # Get vectors
                v_vec = np.array(vab_data[uf])
                i_vec = np.array(icms_data.get(uf, np.zeros(67)))
                
                # Struct Tax = VAB * Rate
                s_vec = v_vec * struct_rates
                
                t_vec = i_vec + s_vec
                
                # Sum for specific indices
                val_vab += np.sum(v_vec[indices])
                val_tax += np.sum(t_vec[indices])
                
            results.append({
                "Região": reg_name,
                "Macro-Setor": sec_name,
                "VAB (Bi)": val_vab / 1000,
                "Tax (Bi)": val_tax / 1000,
                "Carga (%)": (val_tax / val_vab * 100) if val_vab > 0 else 0
            })
            
    # 4. Export
    df = pd.DataFrame(results)
    
    # Pivot for better view? 
    # Let's keep flat list for now, user can pivot in Excel.
    
    outfile = 'output/Matriz_Economia_Criativa_RJ.xlsx'
    df.to_excel(outfile, index=False)
    print(f"Saved to {outfile}")
    
    # Preview
    print(df[df['Região'] == 'Rio de Janeiro'])

if __name__ == "__main__":
    run()
