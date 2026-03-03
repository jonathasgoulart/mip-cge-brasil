import json
import numpy as np

def create_v3_national():
    """
    V3 NACIONAL: ICMS setorial usando Make matrix
    
    Sem divisão por UF - apenas total nacional por setor
    Isso evita problema de VAB zero em produtos regionais
    """
    
    print("="*70)
    print("V3 NACIONAL: ICMS SETORIAL (SEM DIVISÃO POR UF)")
    print("="*70)
    
    # Load data
    print("\n[1/3] Loading data...")
    
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        tax_data = json.load(f)
    icms_2021_target = np.sum(tax_data['taxes_by_type']['ICMS'])
    print(f"  Target ICMS 2021: R$ {icms_2021_target/1e3:.2f} Bi")
    
    with open('output/confaz_icms_2024_by_uf.json', 'r', encoding='utf-8') as f:
        confaz = json.load(f)
    
    with open('output/cnae_to_products_final.json', 'r', encoding='utf-8') as f:
        cnae_mapping = json.load(f)
    cnae_to_products = {int(k): v for k, v in cnae_mapping['mapping'].items()}
    
    # Aggregate CONFAZ to national level
    print("\n[2/3] Aggregating CONFAZ to national by CNAE...")
    
    national_cnae = {}
    
    for uf, uf_data in confaz['by_uf_by_cnae'].items():
        for cnae_col_name, icms_reais in uf_data.items():
            try:
                cnae_div = int(cnae_col_name.split(": ")[1].split(" -")[0])
            except:
                continue
            
            national_cnae[cnae_div] = national_cnae.get(cnae_div, 0) + icms_reais
    
    print(f"  CNAE divisions with ICMS: {len(national_cnae)}")
    
    # Map to products
    print("\n[3/3] Mapping to products...")
    
    icms_by_product = np.zeros(67)
    
    for cnae_div, icms_reais in national_cnae.items():
        icms_milhoes = icms_reais / 1e6
        
        product_dist = cnae_to_products.get(cnae_div)
        
        if product_dist:
            for prod_num_str, share in product_dist.items():
                prod_num = int(prod_num_str)
                if 1 <= prod_num <= 67:
                    icms_by_product[prod_num-1] += icms_milhoes * share
    
    total_mapped = np.sum(icms_by_product)
    print(f"  Total mapped: R$ {total_mapped/1e3:.2f} Bi")
    
    # Normalize to 2021
    norm_factor = icms_2021_target / total_mapped
    icms_final = icms_by_product * norm_factor
    
    total_final = np.sum(icms_final)
    print(f"  Final total: R$ {total_final/1e3:.2f} Bi")
    
    # Calculate coefficients using NATIONAL VAB
    with open('output/vab_regional_67s.json', 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
    
    vab_nacional = np.sum([vab_regional[uf] for uf in vab_regional.keys()], axis=0)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        tau_nacional = icms_final / vab_nacional
        tau_nacional = np.nan_to_num(tau_nacional)
    
    mean_tau = np.mean(tau_nacional[tau_nacional > 0])
    max_tau = np.max(tau_nacional)
    min_tau = np.min(tau_nacional[tau_nacional > 0])
    
    print(f"\n  Coefficients:")
    print(f"    Mean: {mean_tau*100:.2f}%")
    print(f"    Range: {min_tau*100:.2f}% - {max_tau*100:.2f}%")
    
    # Save
    results = {
        "version": "v3_nacional",
        "year": 2021,
        "methodology": "CNAE -> Products using Make matrix (national level)",
        "total_icms_milhoes": float(total_final),
        "total_icms_bilhoes": float(total_final / 1e3),
        "icms_by_product_milhoes": icms_final.tolist(),
        "coefficients": tau_nacional.tolist(),
        "statistics": {
            "mean_coefficient_pct": float(mean_tau * 100),
            "min_coefficient_pct": float(min_tau * 100),
            "max_coefficient_pct": float(max_tau * 100)
        }
    }
    
    with open('output/icms_nacional_v3.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved: output/icms_nacional_v3.json")
    
    # Show top sectors
    print(f"\n{'='*70}")
    print("TOP 10 SETORES (ICMS)")
    print("="*70)
    
    top_indices = np.argsort(icms_final)[::-1][:10]
    
    for rank, idx in enumerate(top_indices, 1):
        print(f"{rank:2d}. Setor {idx+1:2d}: R$ {icms_final[idx]/1e3:6.2f} Bi ({tau_nacional[idx]*100:5.2f}%)")
    
    print(f"\n{'='*70}\n")
    
    return results

if __name__ == "__main__":
    create_v3_national()
