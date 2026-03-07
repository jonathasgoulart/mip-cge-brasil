import numpy as np
import os
import json
import pandas as pd
from io import BytesIO

# Unicode Escapes: u00e0 = à, u00e1 = á, u00e2 = â, u00e3 = ã, u00e7 = ç, u00e9 = é, u00ea = ê, u00ed = í, u00f3 = ó, u00f4 = ô, u00fa = ú
AGGREGATION_LEVELS = {
    "macro": [
        (0, 3, "Agropecu\u00e1ria"),
        (3, 37, "Ind\u00fastria"),
        (37, 67, "Servi\u00e7os")
    ],
    "intermediate": [
        (0, 3, "Agropecu\u00e1ria e Extra\u00e7\u00e3o"),
        (3, 7, "Extra\u00e7\u00e3o e Minera\u00e7\u00e3o"),
        (7, 20, "Ind\u00fastria de Alimentos e Refino"),
        (20, 37, "Outras Ind\u00fastrias"),
        (37, 39, "Utilidades P\u00fablicas"),
        (39, 40, "Constru\u00e7\u00e3o Civil"),
        (40, 41, "Com\u00e9rcio"),
        (41, 45, "Transportes e Log\u00edstica"),
        (45, 47, "Alojamento e Alimenta\u00e7\u00e3o"),
        (47, 64, "Servi\u00e7os Profissionais e TI"),
        (64, 67, "Cultura, Lazer e Pessoais")
    ]
}

STATES_ORDER = ["RO", "AC", "AM", "RR", "PA", "AP", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA", "MG", "ES", "RJ", "SP", "PR", "SC", "RS", "MS", "MT", "GO", "DF"]

def run_demand_shock(region: str, shocks: dict, agg_level: str = "detailed", require_spillover: bool = False):
    # Determine project root relative to this file (api/simulators/demand_shock.py)
    base_proj = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    final_dir = os.path.join(base_proj, 'output', 'final')
    inter_dir = os.path.join(base_proj, 'output', 'intermediary')
    data_dir  = os.path.join(base_proj, 'data', 'processed', '2021_final')

    # X_nas fiscal: VBP MIP Nacional 2019 — denominador correto para coef. tributários
    # (separado do VBP_IIOAS que eh usado apenas para distribuir o choque y)
    path_X_nas_fiscal = os.path.join(inter_dir, 'X_nas.npy')
    X_nas_fiscal = np.load(path_X_nas_fiscal) if os.path.exists(path_X_nas_fiscal) else np.ones(67)
    
    # 1. Selection of Matrix (MRIO or Single Region)
    if require_spillover:
        # Fallback chain: v7.0 (IIOAS real 2019) → v6.1 → v6 → v5 → v4
        for v in ['A_mrio_official_v7_0.npy', 'A_mrio_official_v6_1.npy',
                  'A_mrio_official_v6.npy', 'A_mrio_official_v5.npy',
                  'A_mrio_official_v4.npy']:
            path_A = os.path.join(final_dir, v)
            if os.path.exists(path_A):
                break
        else:
            raise FileNotFoundError("No MRIO matrix found.")
        A = np.load(path_A)
        n_total = A.shape[0] # 1809
        n_sectors = 67
        n_regions = 27
    else:
        if region == 'Nacional':
            # Prioridade: A_nacional_v7_0.npy (NEREUS 2019) > A_nacional.npy > A_nas.npy
            path_A = os.path.join(final_dir, 'A_nacional_v7_0.npy')
            if not os.path.exists(path_A):
                path_A = os.path.join(final_dir, 'A_nacional.npy')
            if not os.path.exists(path_A):
                path_A = os.path.join(inter_dir, 'A_nas.npy')
            if not os.path.exists(path_A):
                raise FileNotFoundError("National Matrix not found.")
            A = np.load(path_A)
        else:
            # Dynamically extract local state 67x67 block from full MRIO
            # Priority: v7.0 (IIOAS real 2019) → v6.1 → v5 → v4
            path_mrio = None
            for v in ['A_mrio_official_v7_0.npy', 'A_mrio_official_v6_1.npy',
                      'A_mrio_official_v5.npy', 'A_mrio_official_v4.npy']:
                cand = os.path.join(final_dir, v)
                if os.path.exists(cand):
                    path_mrio = cand
                    break
            if path_mrio is None:
                raise FileNotFoundError("No MRIO matrix found.")
                
            A_full = np.load(path_mrio)
            
            if region in STATES_ORDER:
                idx = STATES_ORDER.index(region)
                start_idx = idx * 67
                end_idx = (idx + 1) * 67
                A = A_full[start_idx:end_idx, start_idx:end_idx]
            else:
                # Fallback for macro regions (e.g. 'Sul')
                path_A = os.path.join(final_dir, f'A_{region}.npy')
                if not os.path.exists(path_A):
                    path_A = os.path.join(inter_dir, f'A_{region}.npy')
                A = np.load(path_A)
                
        n_total = A.shape[0] # 67
        n_sectors = n_total
        n_regions = 1

    I = np.eye(n_total)
    L = np.linalg.inv(I - A)

    # 2. VBP weights — usa VBP real da IIOAS 2019 por UF quando disponível
    # Shape: (27 UFs, 68 setores IIOAS); agregamos para 67 setores MRIO
    path_vbp_iioas = os.path.join(os.path.dirname(final_dir), 'crosswalk', 'vbp_iioas_all_ufs.npy')
    path_X_nas = os.path.join(inter_dir, 'X_nas.npy')
    if os.path.exists(path_vbp_iioas):
        vbp_all = np.load(path_vbp_iioas)  # (27, 68)
        # Para a região de interesse (ou média nacional), agregar 68→67 setores
        # S41+S42 IIOAS → M41 MRIO (índice 40, 0-based)
        if region in STATES_ORDER:
            origin_uf_idx = STATES_ORDER.index(region)
            vbp_68 = vbp_all[origin_uf_idx]  # (68,)
        else:
            vbp_68 = vbp_all.sum(axis=0)     # (68,) Nacional ou fallback

        vbp_67 = np.zeros(n_sectors)
        for ii in range(68):
            mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
            if mi < n_sectors:
                vbp_67[mi] += vbp_68[ii]
        # Onde ainda for zero, usar média do nacional como fallback
        vbp_br = vbp_all.sum(axis=0)
        vbp_br_67 = np.zeros(n_sectors)
        for ii in range(68):
            mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
            if mi < n_sectors:
                vbp_br_67[mi] += vbp_br[ii]
        vbp_67 = np.where(vbp_67 > 0, vbp_67, vbp_br_67 / 27.0)
        X_nas = vbp_67
    elif os.path.exists(path_X_nas):
        X_nas = np.load(path_X_nas)
    else:
        X_nas = np.ones(n_sectors)
    RJ_IDX = 18  # índice do RJ na ordem das UFs

    # 3. Build Shock Vector (y)
    y = np.zeros(n_total)
    origin_idx = STATES_ORDER.index(region) if require_spillover and region in STATES_ORDER else 0
    offset = origin_idx * n_sectors if require_spillover else 0
    
    agg_level = agg_level.lower()
    if agg_level in AGGREGATION_LEVELS:
        agg_defs = AGGREGATION_LEVELS[agg_level]
        for name, value in shocks.items():
            for start, end, agg_name in agg_defs:
                if agg_name == name:
                    subset_X = X_nas[start:end]
                    total_subset_X = np.sum(subset_X)
                    if total_subset_X > 0:
                        y[offset+start : offset+end] += (subset_X / total_subset_X) * float(value)
                    else:
                        y[offset+start : offset+end] += float(value) / (end - start)
                    break
    else:
        for idx_str, val in shocks.items():
            try:
                i = int(idx_str)
                if 0 <= i < n_sectors: y[offset + i] = float(val)
            except: pass

    # 4. Calculate Impacts
    x_total = L @ y
    total_production = np.sum(x_total)
    direct_injection = np.sum(y)
    multiplier = total_production / direct_injection if direct_injection > 0 else 0

    # 5. Employment
    coeff_path = os.path.join(final_dir, 'emp_coefficients_67x27.npy')
    jobs_by_sector = np.zeros(n_total)
    if os.path.exists(coeff_path):
        emp_coeffs = np.load(coeff_path)
        if require_spillover:
            for r in range(n_regions):
                jobs_by_sector[r*n_sectors : (r+1)*n_sectors] = emp_coeffs[:, r] * x_total[r*n_sectors : (r+1)*n_sectors]
        else:
            if region == 'Nacional': 
                # Média Ponderada de Empregos: (Soma Ocupações UFs) / (VBP Nacional NEREUS)
                # emp_coeffs[:, r] = jobs/VBP_r -> jobs = emp_coeffs * VBP_r
                path_vbp = os.path.join(os.path.dirname(final_dir), 'crosswalk', 'vbp_iioas_all_ufs.npy')
                if os.path.exists(path_vbp):
                    vbp_68_all = np.load(path_vbp)
                    # Agregar pra 67 para todas UFs
                    vbp_67_ufs = np.zeros((27, n_sectors))
                    for uf in range(27):
                        for ii in range(68):
                            mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
                            if mi < n_sectors: vbp_67_ufs[uf, mi] += vbp_68_all[uf, ii]
                    total_jobs_nat = np.sum(emp_coeffs * vbp_67_ufs.T, axis=1)
                    total_prod_nat = np.sum(vbp_67_ufs, axis=0)
                    c = np.where(total_prod_nat > 0, total_jobs_nat / total_prod_nat, 0)
                else:
                    c = np.mean(emp_coeffs, axis=1) # Fallback para média simples
            else:
                 idx = STATES_ORDER.index(region) if region in STATES_ORDER else 18
                 c = emp_coeffs[:, idx]
            jobs_by_sector = c * x_total
    
    total_jobs = np.sum(jobs_by_sector)

    # 6. Fiscal Impact — coeficientes estado-específicos 2019
    # Prioridade 1: tax_matrix_by_state_2019.json (ICMS p/ UF + federais p/ VBP)
    # Prioridade 2: tax_matrix_2019.json (nacional, fallback)
    tax_results = {}
    total_tax = 0

    state_tax_path = os.path.join(data_dir, 'tax_matrix_by_state_2019.json')
    nat_tax_path   = os.path.join(data_dir, 'tax_matrix_2019.json')
    if not os.path.exists(nat_tax_path):
        nat_tax_path = os.path.join(data_dir, 'tax_matrix.json')

    # Escolher qual vetor de imposto usar (estado-específico ou nacional)
    region_key = region if region in STATES_ORDER else None
    use_state_tax = (os.path.exists(state_tax_path) and region_key is not None
                     and region != 'Nacional')

    if use_state_tax:
        with open(state_tax_path, 'r', encoding='utf-8') as f:
            state_tax_full = json.load(f).get('by_state', {})
        state_tax_data = state_tax_full.get(region_key, {})
    
    if os.path.exists(nat_tax_path):
        with open(nat_tax_path, 'r', encoding='utf-8') as f:
            nat_tax_data = json.load(f).get('taxes_by_type', {})

    tax_source = state_tax_data if use_state_tax else nat_tax_data

    # Denominador fiscal correto: VBP do estado (quando estado-específico) ou VBP nacional NEREUS
    # τ = imposto[setor] / VBP[setor]  — denominador deve corresponder ao numerador
    vbp_iioas_path = os.path.join(os.path.dirname(final_dir), 'crosswalk', 'vbp_iioas_all_ufs.npy')
    if use_state_tax and region_key in STATES_ORDER:
        if os.path.exists(vbp_iioas_path):
            vbp_all = np.load(vbp_iioas_path)   # (27, 68)
            uf_idx  = STATES_ORDER.index(region_key)
            vbp68   = vbp_all[uf_idx]
            X_fiscal = np.zeros(n_sectors)
            for ii in range(68):
                mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
                if mi < n_sectors:
                    X_fiscal[mi] += vbp68[ii]
        else:
            X_fiscal = X_nas_fiscal
    else:
        # Se Nacional ou Fallback, usar VBP agregado real das UFs 2019 da NEREUS
        if os.path.exists(vbp_iioas_path):
            vbp_all = np.load(vbp_iioas_path)
            vbp_nat_68 = vbp_all.sum(axis=0)
            X_fiscal = np.zeros(n_sectors)
            for ii in range(68):
                mi = ii if ii < 40 else (40 if ii == 41 else ii - 1)
                if mi < n_sectors: X_fiscal[mi] += vbp_nat_68[ii]
        else:
            X_fiscal = X_nas_fiscal

    for tax_type, values in tax_source.items():
        vals = list(values.values())[:n_sectors] if isinstance(values, dict) else values[:n_sectors]
        if len(vals) >= n_sectors:
            tax_values = np.array(vals[:n_sectors])
            coef = np.zeros(n_sectors)
            valid = X_fiscal > 0
            coef[valid] = tax_values[valid] / X_fiscal[valid]
            x_origin = x_total[offset : offset + n_sectors]
            revenue = np.sum(coef * x_origin)
            tax_results[tax_type] = float(revenue)
            total_tax += revenue

    # 7. Labels
    from ..main import DETAILED_SECTORS as labels
    
    # Origin results
    x_origin = x_total[offset : offset + n_sectors]
    jobs_origin = jobs_by_sector[offset : offset + n_sectors]
    
    sectoral_results = []
    for i in range(min(n_sectors, len(labels))):
        sectoral_results.append({
            "id": i, "name": labels[i],
            "production": float(x_origin[i]), "jobs": float(jobs_origin[i])
        })
    sectoral_results.sort(key=lambda x: x['production'], reverse=True)

    # 8. Spillover
    spillover_results = []
    if require_spillover:
        for r in range(n_regions):
            if r == origin_idx: continue
            state_prod = np.sum(x_total[r*n_sectors : (r+1)*n_sectors])
            if state_prod > 0.01:
                spillover_results.append({
                    "state": STATES_ORDER[r],
                    "production": float(state_prod),
                    "jobs": float(np.sum(jobs_by_sector[r*n_sectors : (r+1)*n_sectors]))
                })
        spillover_results.sort(key=lambda x: x['production'], reverse=True)

    return {
        "summary": {
            "region": region, "aggregation": agg_level,
            "direct_injection": float(direct_injection), "total_production": float(total_production),
            "multiplier": float(multiplier), "total_jobs": float(total_jobs),
            "total_tax": float(total_tax), "spillover_production": float(total_production - np.sum(x_origin))
        },
        "fiscal_detail": tax_results,
        "results": sectoral_results,
        "spillover": spillover_results
    }

def export_to_excel(result_data: dict):
    output = BytesIO()
    # Explicitly use XlsxWriter engine
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Summary
        df_sum = pd.DataFrame([result_data['summary']]).T.reset_index()
        df_sum.columns = ['M\u00e9trica', 'Valor']
        df_sum.to_excel(writer, sheet_name='Resumo', index=False)
        
        # Sectoral
        df_sect = pd.DataFrame(result_data['results'])
        df_sect.to_excel(writer, sheet_name='Setores', index=False)
        
        # Fiscal
        if result_data.get('fiscal_detail'):
            df_tax = pd.DataFrame(list(result_data['fiscal_detail'].items()), columns=['Imposto', 'Valor (Mi)'])
            df_tax.to_excel(writer, sheet_name='Fiscal', index=False)
        
        # Spillover
        if result_data.get('spillover'):
            df_spill = pd.DataFrame(result_data['spillover'])
            df_spill.to_excel(writer, sheet_name='Estados', index=False)
            
    output.seek(0)
    return output
