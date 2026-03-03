import numpy as np
import os

def run_integrated():
    print("--- STARTING INTEGRATED PIPELINE (REFINED) ---")
    inter_dir = 'output/intermediary'
    os.makedirs(inter_dir, exist_ok=True)
    
    # 1. Load National Components
    A_nas = np.load(os.path.join(inter_dir, 'A_nas.npy'))
    X_nas = np.load(os.path.join(inter_dir, 'X_nas.npy'))
    VAB_nas = np.load(os.path.join(inter_dir, 'VAB_nacional.npy'))
    Z_nas = np.load(os.path.join(inter_dir, 'Z_nas.npy'))
    
    # 2. Load Regional VAB (from slim_extract.py)
    # vab_matrix_raw has shape (33, 20)
    # Indices correspond to TabelaX.xls and SheetX.j
    vab_matrix_raw = np.load(os.path.join(inter_dir, 'vab_matrix_raw.npy'))
    
    # 3. Precise Sector Mapping (MIP 67 -> CR 18)
    # Sheet indices: 2 to 19 (which correspond to CR 1 to CR 18)
    mapping = {}
    
    # CR 1 (Ag) -> Sheet 2: MIP 0-8
    for s in range(0, 9): mapping[s] = 2
    # CR 2 (Pec) -> Sheet 3: MIP 9-12
    for s in range(9, 13): mapping[s] = 3
    # CR 3 (Silv) -> Sheet 4: MIP 13-14
    for s in range(13, 15): mapping[s] = 4
    # CR 4 (Extr) -> Sheet 5: MIP 15-19
    for s in range(15, 20): mapping[s] = 5
    # CR 5 (Transf) -> Sheet 6: MIP 20-36 (Original 67 sectors)
    for s in range(20, 37): mapping[s] = 6
    # CR 6 (Elet/Agua) -> Sheet 7: MIP 37-38
    for s in range(37, 39): mapping[s] = 7
    # CR 7 (Const) -> Sheet 8: MIP 39
    mapping[39] = 8
    # CR 8 (Comer) -> Sheet 9: MIP 40
    mapping[40] = 9
    # CR 9 (Transp) -> Sheet 10: MIP 41-44
    for s in range(41, 45): mapping[s] = 10
    # CR 10 (Aloj) -> Sheet 11: MIP 45-46
    for s in range(45, 47): mapping[s] = 11
    # CR 11 (Info/Com) -> Sheet 12: MIP 47-50
    for s in range(47, 51): mapping[s] = 12
    # CR 12 (Fin) -> Sheet 13: MIP 51
    mapping[51] = 13
    # CR 13 (Imob) -> Sheet 14: MIP 52
    mapping[52] = 14
    # CR 14 (Prof/Adm) -> Sheet 15: MIP 53-58
    for s in range(53, 59): mapping[s] = 15
    # CR 15 (Adm Pub/Edu Pub/Saude Pub) -> Sheet 16: MIP 59, 60, 62
    for s in [59, 60, 62]: mapping[s] = 16
    # CR 16 (Edu Priv/Saude Priv) -> Sheet 17: MIP 61, 63
    for s in [61, 63]: mapping[s] = 17
    # CR 17 (Artes/Serv) -> Sheet 18: MIP 64-65
    for s in range(64, 66): mapping[s] = 18
    # CR 18 (Domestico) -> Sheet 19: MIP 66
    mapping[66] = 19
    
    # Validation: Do we have all 67 from 0 to 66?
    assert len(mapping) == 67
    
    # 4. Regional Aggregation
    REGIOES_MAP = {
        'Sul': [25, 26, 27],
        'Centro_Oeste': [29, 30, 31, 32],
        'Norte_Nordeste': list(range(2, 9)) + list(range(10, 19)),
        'Rio_de_Janeiro': [22],
        'Sao_Paulo': [23],
        'Minas_EspiritoSanto': [20, 21]
    }
    
    # National VAB aggregated to CR 18 for share calculation
    # We use Sheet indices 2 to 19 as keys
    VAB_nas_agg_CR = np.zeros(20) # Buffer
    for s, sheet_idx in mapping.items():
        VAB_nas_agg_CR[sheet_idx] += VAB_nas[s]
    
    vab_nas_sum_67 = np.zeros(67)
    
    for reg, ufs in REGIOES_MAP.items():
        print(f"Processing Region: {reg}")
        vab_reg_67 = np.zeros(67)
        
        # Sum regional weights for CR 18
        reg_weights_CR = np.zeros(20)
        for uf in ufs:
            reg_weights_CR += vab_matrix_raw[uf]
            
        # Distribute based on MIP shares
        for s, sheet_idx in mapping.items():
            if VAB_nas_agg_CR[sheet_idx] > 0:
                share = reg_weights_CR[sheet_idx] / VAB_nas_agg_CR[sheet_idx]
                vab_reg_67[s] = VAB_nas[s] * share
            else:
                # Should not happen with real data
                vab_reg_67[s] = 0
                
        np.save(os.path.join(inter_dir, f'VAB_{reg}.npy'), vab_reg_67)
        vab_nas_sum_67 += vab_reg_67
        
    np.save(os.path.join(inter_dir, 'VAB_nas_agg.npy'), vab_nas_sum_67)
    print("Done! Integrated data ready for Flegg.")

if __name__ == "__main__":
    run_integrated()
