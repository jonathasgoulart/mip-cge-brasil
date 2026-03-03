
import json
import numpy as np
import csv

def run():
    print("=== RELATÓRIO DE CARGA TRIBUTÁRIA SETORIAL (FINAL) ===")
    
    path_tax = 'data/processed/2021_final/tax_matrix_hybrid_by_state.json'
    path_vab = 'data/processed/2021_final/vab_regional.json'
    path_labels = 'output/intermediary/sector_labels.txt'
    
    with open(path_tax, 'r') as f:
        tax_matrix = json.load(f)
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
        
    labels = [f"Setor {i+1}" for i in range(67)]
    try:
        with open(path_labels, 'r', encoding='latin1') as f:
            labels = [l.strip() for l in f if l.strip()]
    except: pass
    
    # Init Vectors
    total_tax_vec = np.zeros(67)
    total_vab_vec = np.zeros(67)
    
    # Include Structural Taxes (IPI/PIS/COFINS) to get FULL Burden?
    # Yes. User wants THE Burden.
    path_tax_struct = 'data/processed/2021_final/tax_matrix.json'
    with open(path_tax_struct, 'r') as f:
        tax_struct = json.load(f).get('taxes_by_type', {})
        
    other_taxes_keys = ["IPI", "ISS", "PIS_PASEP", "COFINS", "CIDE", "IOF", "II"]
    other_tax_vectors = {k: np.array(tax_struct[k]) for k in other_taxes_keys if k in tax_struct}
    
    # Calculate Sums
    for uf, vec in tax_matrix.items():
        if uf in vab_regional:
             total_tax_vec += np.array(vec) # Hybrid ICMS
             total_vab_vec += np.array(vab_regional[uf])
             
    # Add Structural Taxes (Nationally)
    # The structural vectors are National Totals. Just add them.
    # Note: tax_struct values are in Millions (checked in step 954).
    # tax_matrix values are in Millions.
    # vab_regional values are in Millions.
    for k, vec in other_tax_vectors.items():
        total_tax_vec += vec
        
    # Calculate Burden
    print(f"{'ID':<3} | {'Setor':<40} | {'VAB (Bi)':<10} | {'Tax (Bi)':<10} | {'Carga %':<10}")
    print("-" * 80)
    
    results = []
    for i in range(67):
        vab = total_vab_vec[i]
        tax = total_tax_vec[i]
        burden = (tax/vab)*100 if vab > 0 else 0
        
        label = labels[i][:40] if i < len(labels) else f"Setor {i+1}"
        
        results.append({
            "id": i+1,
            "label": label,
            "vab": vab,
            "tax": tax,
            "burden": burden
        })
        
    # Sort by Burden
    results.sort(key=lambda x: x['burden'], reverse=True)
    
    for r in results:
        # Filter insane anomalies? Or show them?
        # Show all.
        try:
            safe_lbl = r['label'].encode('ascii', 'ignore').decode('ascii')
        except:
            safe_lbl = "Label Error"
            
        print(f"{r['id']:<3} | {safe_lbl:<40} | {r['vab']/1000:<10.1f} | {r['tax']/1000:<10.1f} | {r['burden']:<10.1f}%")
        
    # Export
    with open('output/carga_setorial_2021.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Setor", "VAB (Bi)", "Tax (Bi)", "Carga (%)"])
        for r in results:
            writer.writerow([r['id'], r['label'], r['vab']/1000, r['tax']/1000, r['burden']])
            
if __name__ == "__main__":
    run()
