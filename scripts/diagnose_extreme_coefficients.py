import json
import numpy as np

def diagnose_extreme_coefficients():
    """
    Find sectors/UFs with extreme ICMS coefficients
    """
    
    print("="*70)
    print("DIAGNOSTIC: EXTREME ICMS COEFFICIENTS IN V3")
    print("="*70)
    
    # Load V3 results
    with open('output/icms_regional_v3_sectoral.json', 'r', encoding='utf-8') as f:
        v3 = json.load(f)
    
    # Load VAB
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_data = json.load(f)
    
    # Load MIP sector names
    with open('output/mip_67_sectors.json', 'r', encoding='utf-8') as f:
        mip_sectors = json.load(f)
    
    UFS = sorted(v3['by_uf'].keys())
    n_setores = 67
    
    print(f"\n[1/3] Building matrices...")
    
    # Build ICMS and VAB matrices
    icms_matrix = np.zeros((len(UFS), n_setores))
    vab_matrix = np.zeros((len(UFS), n_setores))
    
    for i, uf in enumerate(UFS):
        icms_matrix[i, :] = v3['by_uf'][uf]['icms_by_sector_milhoes']
        vab_matrix[i, :] = vab_data[uf]
    
    # Calculate coefficients
    with np.errstate(divide='ignore', invalid='ignore'):
        tau_matrix = icms_matrix / vab_matrix
        tau_matrix = np.nan_to_num(tau_matrix, nan=0, posinf=0, neginf=0)
    
    print(f"  ICMS matrix: {icms_matrix.shape}")
    print(f"  VAB matrix: {vab_matrix.shape}")
    print(f"  Tau matrix: {tau_matrix.shape}")
    
    # Find extremes
    print(f"\n[2/3] Finding extreme coefficients...")
    
    # Top 20 highest coefficients
    flat_indices = np.argsort(tau_matrix.flatten())[::-1][:20]
    
    print(f"\n{'Rank':<6} {'UF':<5} {'Setor':<8} {'ICMS (mi)':<15} {'VAB (mi)':<15} {'Tau (%)':<10} {'Descricao'}")
    print("-"*100)
    
    anomalies = []
    
    for rank, flat_idx in enumerate(flat_indices, 1):
        i_uf = flat_idx // n_setores
        j_setor = flat_idx % n_setores
        
        uf = UFS[i_uf]
        setor_num = j_setor + 1
        icms_val = icms_matrix[i_uf, j_setor]
        vab_val = vab_matrix[i_uf, j_setor]
        tau_val = tau_matrix[i_uf, j_setor]
        
        # Get sector description
        setor_info = mip_sectors['sectors'].get(str(setor_num), {})
        desc = setor_info.get('description', 'N/A')[:40]
        
        print(f"{rank:<6} {uf:<5} {setor_num:<8} {icms_val:<15.2f} {vab_val:<15.2f} {tau_val*100:<10.2f} {desc}")
        
        if tau_val > 0.30:  # More than 30%
            anomalies.append({
                'uf': uf,
                'setor': setor_num,
                'icms': icms_val,
                'vab': vab_val,
                'tau_pct': tau_val * 100,
                'description': desc
            })
    
    # Analyze anomalies
    print(f"\n[3/3] Analyzing anomalies (tau > 30%)...")
    print(f"  Total anomalies: {len(anomalies)}")
    
    if anomalies:
        print(f"\n  Possible causes:")
        
        # Check for zero/very low VAB
        low_vab = [a for a in anomalies if a['vab'] < 1.0]  # Less than 1 million
        if low_vab:
            print(f"    - {len(low_vab)} cases with VAB < R$ 1 milhao (possible VAB error)")
            for a in low_vab[:3]:
                print(f"      * {a['uf']} Setor {a['setor']}: VAB = R$ {a['vab']:.2f} mi")
        
        # Check for very high ICMS
        high_icms = [a for a in anomalies if a['icms'] > 1000]  # More than 1 billion
        if high_icms:
            print(f"    - {len(high_icms)} cases with ICMS > R$ 1 bilhao")
            for a in high_icms[:3]:
                print(f"      * {a['uf']} Setor {a['setor']}: ICMS = R$ {a['icms']:.2f} mi")
        
        # Check which sectors appear most
        from collections import Counter
        setor_counts = Counter([a['setor'] for a in anomalies])
        print(f"\n  Most affected sectors:")
        for setor, count in setor_counts.most_common(5):
            setor_info = mip_sectors['sectors'].get(str(setor), {})
            desc = setor_info.get('description', 'N/A')
            print(f"    Setor {setor}: {count} UFs affected - {desc}")
    
    # Check mapping issues
    print(f"\n{'='*70}")
    print("INVESTIGATING CNAE MAPPING")
    print("="*70)
    
    # Load CONFAZ to see which CNAE divisions contribute most
    with open('output/confaz_icms_2024_by_uf.json', 'r', encoding='utf-8') as f:
        confaz = json.load(f)
    
    # For the worst anomaly, trace back which CNAE contributed
    if anomalies:
        worst = anomalies[0]
        print(f"\nWorst case: {worst['uf']} Setor {worst['setor']} (tau = {worst['tau_pct']:.1f}%)")
        print(f"  ICMS: R$ {worst['icms']:.2f} milhoes")
        print(f"  VAB:  R$ {worst['vab']:.2f} milhoes")
        
        # Check which CNAE divisions map to this MIP sector
        from cnae_to_mip_mapping import CNAE_TO_MIP_MAPPING
        
        contributing_cnae = []
        for cnae_div, mapping in CNAE_TO_MIP_MAPPING.items():
            if worst['setor'] in mapping['mip']:
                contributing_cnae.append(cnae_div)
        
        print(f"\n  CNAE divisions mapping to MIP {worst['setor']}: {contributing_cnae}")
        
        # Check CONFAZ values for these CNAEs in this UF
        uf_confaz = confaz['by_uf_by_cnae'][worst['uf']]
        print(f"\n  CONFAZ values for {worst['uf']}:")
        for key, value in uf_confaz.items():
            try:
                cnae_num = int(key.split(": ")[1].split(" -")[0])
                if cnae_num in contributing_cnae:
                    print(f"    CNAE {cnae_num}: R$ {value/1e6:.2f} milhoes")
            except:
                pass
    
    print(f"\n{'='*70}\n")
    
    return anomalies

if __name__ == "__main__":
    diagnose_extreme_coefficients()
