
import json
import numpy as np
import pandas as pd
import os

def run():
    print("=== GERANDO MATRIZ NACIONAL COMPLETA (67 SETORES - 2021) ===")
    
    # 1. LOAD BASE DATA
    path_vab = 'data/processed/2021_final/vab_regional.json'
    path_tax_hybrid = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    path_tax_struct = 'data/processed/2021_final/tax_matrix.json'
    path_labels = 'output/intermediary/sector_labels.txt'
    path_emp_coeff = 'output/final/emp_coefficients_67x27.npy'
    path_ci_2015 = 'data/processed/mip_2015/11.csv'
    path_vbp_2015 = 'data/processed/mip_2015/01.csv'

    # Load Labels
    with open(path_labels, 'r', encoding='latin1') as f:
        labels = [line.strip().split(':')[-1].strip() for line in f if line.strip()]
    if len(labels) > 67: labels = labels[:67]

    # Load VAB 2021
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    vab_2021 = np.zeros(67)
    for vec in vab_regional.values():
        vab_2021 += np.array(vec)

    # Load Hybrid ICMS 2021
    with open(path_tax_hybrid, 'r') as f:
        icms_data = json.load(f)
    icms_2021 = np.zeros(67)
    for vec in icms_data.values():
        icms_2021 += np.array(vec)

    # Load Structural Taxes 2021
    with open(path_tax_struct, 'r') as f:
        struct_data = json.load(f).get('taxes_by_type', {})
    
    iss_2021 = np.array(struct_data.get('ISS', np.zeros(67)))
    ipi_2021 = np.array(struct_data.get('IPI', np.zeros(67)))
    pis_cofins_2021 = np.array(struct_data.get('PIS_PASEP', np.zeros(67))) + np.array(struct_data.get('COFINS', np.zeros(67)))
    others_2021 = np.array(struct_data.get('CIDE', np.zeros(67))) + np.array(struct_data.get('IOF', np.zeros(67))) + np.array(struct_data.get('II', np.zeros(67)))
    
    total_tax_2021 = icms_2021 + iss_2021 + ipi_2021 + pis_cofins_2021 + others_2021

    # 2. CALIBRATE VBP AND Z
    # We need 2015 ratios to estimate 2021 VBP
    df_ci_2015 = pd.read_csv(path_ci_2015, skiprows=3)
    A_2015 = df_ci_2015.iloc[1:111, 2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values # Product x Activity
    # Aggregate A_2015 to Activity x Activity (67x67) - Approximation: use first 67 rows or map.
    # To be precise, 11th table rows 1-67 match activities 1-67 in standard MIP.
    A_67x67_2015 = A_2015[:67, :]
    
    # VBP 2015
    df_vbp_2015 = pd.read_csv(path_vbp_2015, skiprows=1)
    mask = df_vbp_2015.iloc[:, 0].astype(str).str.contains("Total", case=False, na=False)
    X_2015 = df_vbp_2015[mask].iloc[0, 7:74].apply(pd.to_numeric, errors='coerce').fillna(0).values

    # VAB 2015 (derived from TRU or same source)
    # Since we have vab_2021 and we want ratio, let's use the assumption VBP = VAB / (1 - CI_ratio)
    # CI_ratio = Sum of columns of A
    ci_reduction = np.sum(A_67x67_2015, axis=0) # Sum of technical coefficients (intermediate cons / total production)
    # VAB_ratio = 1 - ci_reduction
    vab_ratio_2015 = 1 - ci_reduction
    vab_ratio_2015[vab_ratio_2015 <= 0.1] = 0.5 # Safety floor
    
    X_2021 = vab_2021 / vab_ratio_2015
    
    # Flow Matrix Z 2021
    Z_2021 = A_67x67_2015 * X_2021[None, :]

    # 3. EMPLOYMENT (Jobs)
    if os.path.exists(path_emp_coeff):
        e_coeff = np.load(path_emp_coeff)
        
        # Patch zeros with benchmarks (per R$ 1MM)
        # Index 13 (Clothing): 15.0
        # Index 14 (Shoes): 15.0
        # Index 62/63 (Health): 12.0
        # Index 65 (Associative): 10.0
        # Index 66 (Service Domest): 15.0 (already handled usually but let's check)
        
        if e_coeff[13] == 0: e_coeff[13] = 15.0
        if e_coeff[14] == 0: e_coeff[14] = 15.0
        if e_coeff[62] == 0: e_coeff[62] = 12.0
        if e_coeff[63] == 0: e_coeff[63] = 12.0
        if e_coeff[65] == 0: e_coeff[65] = 10.0
        
        jobs_2021 = e_coeff * X_2021
    else:
        jobs_2021 = np.zeros(67)

    # 4. CONSOLIDATE REPORT
    df_summary = pd.DataFrame({
        "Setor": labels,
        "VAB_MM": vab_2021,
        "VBP_MM": X_2021,
        "ICMS_MM": icms_2021,
        "ISS_MM": iss_2021,
        "IPI_MM": ipi_2021,
        "PIS_COFINS_MM": pis_cofins_2021,
        "Demais_Impostos_MM": others_2021,
        "Total_Impostos_MM": total_tax_2021,
        "Carga_Tributaria_Pct": (total_tax_2021 / vab_2021 * 100),
        "Empregos_Total": jobs_2021
    })
    
    df_Z = pd.DataFrame(Z_2021, index=labels, columns=labels)
    df_A = pd.DataFrame(A_67x67_2015, index=labels, columns=labels)

    output_file = 'output/Matriz_Nacional_2021_COMPLETA_v2.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        df_summary.to_excel(writer, sheet_name='Sintese_Setorial_2021', index=False)
        df_Z.to_excel(writer, sheet_name='Matriz_Fluxos_Z')
        df_A.to_excel(writer, sheet_name='Matriz_Coeficientes_A')

    print(f"Sucesso! Matriz Nacional 2021 salva em {output_file}")
    
    # Print Totals for Verification
    print(f"Total VAB: R$ {np.sum(vab_2021)/1000:.1f} Bi")
    print(f"Total Tributos: R$ {np.sum(total_tax_2021)/1000:.1f} Bi")
    print(f"Total Empregos: {np.sum(jobs_2021):,.0f}")

if __name__ == "__main__":
    run()
