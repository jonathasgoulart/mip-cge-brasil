import numpy as np
import json

def consolidate_vab_regional():
    """
    Consolidate individual UF VAB files into single JSON
    """
    
    print("="*70)
    print("CONSOLIDATING REGIONAL VAB DATA")
    print("="*70)
    
    UFS = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
           'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
           'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    
    vab_regional = {}
    
    print(f"\nLoading VAB for {len(UFS)} UFs...")
    
    for uf in UFS:
        file_path = f'output/intermediary/VAB_{uf}.npy'
        try:
            vab = np.load(file_path)
            if len(vab) == 67:
                vab_regional[uf] = vab.tolist()
                print(f"  {uf}: R$ {np.sum(vab)/1e6:.2f} Tri ({len(vab)} setores)")
            else:
                print(f"  {uf}: ERRO - {len(vab)} setores (esperado: 67)")
        except FileNotFoundError:
            print(f"  {uf}: Arquivo nao encontrado")
        except Exception as e:
            print(f"  {uf}: Erro - {e}")
    
    # Save consolidated data
    output_path = 'output/vab_regional_67s.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vab_regional, f, indent=2)
    
    print(f"\n[OK] Saved {len(vab_regional)} UFs to: {output_path}")
    
    # Calculate totals
    total_vab = sum(np.sum(vab) for vab in vab_regional.values())
    print(f"\nTotal VAB Regional: R$ {total_vab/1e6:.2f} Trilhoes")
    
    # Top 5
    uf_totals = [(uf, np.sum(vab)) for uf, vab in vab_regional.items()]
    uf_totals_sorted = sorted(uf_totals, key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 5 UFs (VAB):")
    for uf, total in uf_totals_sorted[:5]:
        print(f"  {uf}: R$ {total/1e6:.2f} Tri ({total/total_vab*100:.1f}%)")
    
    print(f"\n{'='*70}\n")
    
    return vab_regional

if __name__ == "__main__":
    consolidate_vab_regional()
