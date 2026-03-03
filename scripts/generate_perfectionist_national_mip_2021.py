
import json
import numpy as np
import pandas as pd
import os

def run_synthesis():
    print("=== SÍNTESE FINAL: MIP NACIONAL 2021 (PERFECCIONISTA) ===")
    
    # 1. LOAD DATA
    with open('output/intermediary/perfectionist_base_2015.json', 'r', encoding='utf-8') as f:
        base_2015 = json.load(f)
    
    with open('data/processed/2021_final/vab_regional.json', 'r', encoding='utf-8') as f:
        vab_mapping = json.load(f)
    
    path_tax_hybrid = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    path_tax_struct = 'data/processed/2021_final/tax_matrix.json'
    path_emp_coeff = 'output/final/emp_coefficients_67x27.npy'
    
    labels = [l.replace('\n', ' ') for l in base_2015['labels']]
    A_nas = np.array(base_2015['A_matrix'])
    A_imp = np.array(base_2015['A_imp_matrix'])
    
    # 2. CONSOLIDATED VAB 2021
    vab_2021 = np.zeros(67)
    for state_vab in vab_mapping.values():
        vab_2021 += np.array(state_vab)
    
    # 3. SCALE TO VBP 2021
    # VBP = VAB / (1 - sum(A_nat) - sum(A_imp))
    sum_A_nat = A_nas.sum(axis=0)
    sum_A_imp = A_imp.sum(axis=0)
    
    # Safety floor to avoid division by zero
    vab_ratio = 1 - sum_A_nat - sum_A_imp
    vab_ratio[vab_ratio < 0.05] = 0.4 # Default conservative margin if ratio is broken
    
    X_2021 = vab_2021 / vab_ratio
    
    # 4. GENERATE FLOWS Z
    Z_2021 = A_nas * X_2021[None, :]
    Z_imp_2021 = A_imp * X_2021[None, :]

    # 5. INTEGRATE TAXES
    # ICMS Hybrid
    with open(path_tax_hybrid, 'r') as f:
        icms_data = json.load(f)
    icms_2021 = np.zeros(67)
    for vec in icms_data.values():
        icms_2021 += np.array(vec)

    # Structural Taxes
    with open(path_tax_struct, 'r') as f:
        struct_data = json.load(f).get('taxes_by_type', {})
    
    # ISS FIX: ISS is specifically for Services (40-67). 
    # Current vector has leakage in Industry. We will re-allocate.
    iss_raw = np.array(struct_data.get('ISS', np.zeros(67)))
    target_iss_total = np.sum(iss_raw)
    
    iss_2021 = np.zeros(67)
    # Mask: Only sectors 40 to 65 (Services, excluding domestic service which is 66)
    service_mask = np.zeros(67)
    service_mask[40:66] = 1.0
    
    # Redistribute target_iss based on Service VAB weights
    vab_services = vab_2021 * service_mask
    if np.sum(vab_services) > 0:
        iss_2021 = (vab_services / np.sum(vab_services)) * target_iss_total
    
    ipi_2021 = np.array(struct_data.get('IPI', np.zeros(67)))
    # IPI FIX: IPI is for Industry (10-33)
    # Ensure IPI doesn't leak into services
    industry_mask = np.zeros(67)
    industry_mask[10:37] = 1.0
    ipi_2021 = ipi_2021 * industry_mask
    
    pis_cofins_2021 = np.array(struct_data.get('PIS_PASEP', np.zeros(67))) + np.array(struct_data.get('COFINS', np.zeros(67)))
    others_2021 = np.array(struct_data.get('CIDE', np.zeros(67))) + np.array(struct_data.get('IOF', np.zeros(67))) + np.array(struct_data.get('II', np.zeros(67)))
    
    total_tax_2021 = icms_2021 + iss_2021 + ipi_2021 + pis_cofins_2021 + others_2021

    # 6. EMPLOYMENT
    if os.path.exists(path_emp_coeff):
        e_coeff = np.load(path_emp_coeff)
        # Patch missing sectors (benchmarks per R$ 1MM)
        if e_coeff[13] == 0: e_coeff[13] = 15.0
        if e_coeff[14] == 0: e_coeff[14] = 15.0
        if e_coeff[62] == 0: e_coeff[62] = 12.0
        if e_coeff[63] == 0: e_coeff[63] = 12.0
        if e_coeff[65] == 0: e_coeff[65] = 10.0
        jobs_2021 = e_coeff * X_2021
    else:
        jobs_2021 = np.zeros(67)

    # 7. EXPORT COMPREHENSIVE MATRIX
    df_summary = pd.DataFrame({
        "Setor": labels,
        "VAB_MM": vab_2021,
        "VBP_MM": X_2021,
        "CI_Nacional_Total": Z_2021.sum(axis=0),
        "CI_Importado_Total": Z_imp_2021.sum(axis=0),
        "ICMS_MM": icms_2021,
        "ISS_MM": iss_2021,
        "IPI_MM": ipi_2021,
        "PIS_COFINS_MM": pis_cofins_2021,
        "Demais_Tributos_MM": others_2021,
        "Total_Tributos_MM": total_tax_2021,
        "Carga_Tributaria_Pct": (total_tax_2021 / vab_2021 * 100),
        "Empregos_Total": jobs_2021
    })
    
    df_Z = pd.DataFrame(Z_2021, index=labels, columns=labels)
    df_A = pd.DataFrame(A_nas, index=labels, columns=labels)

    output_file = 'output/Matriz_Nacional_2021_PERFEITA_v3.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        df_summary.to_excel(writer, sheet_name='Sintese_Setorial', index=False)
        df_Z.to_excel(writer, sheet_name='Fluxos_Z_Nacionais')
        df_A.to_excel(writer, sheet_name='Coeficientes_A')

    print(f"Sucesso! Matriz Nacional Perfeita salva em {output_file}")
    
    # Audit Check
    print("\n--- Auditoria de Identidade ---")
    identity_chk = Z_2021.sum(axis=0) + Z_imp_2021.sum(axis=0) + vab_2021
    diff_pct = np.abs(identity_chk - X_2021) / X_2021 * 100
    print(f"Desvio Máximo de Identidade (VBP = VAB + CI): {np.max(diff_pct):.4f}%")
    print(f"Total VAB: R$ {np.sum(vab_2021)/1000:.1f} Bi")

if __name__ == "__main__":
    run_synthesis()
