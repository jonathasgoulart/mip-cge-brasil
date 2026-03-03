import json

def verify_units():
    """
    Verificar unidades do CONFAZ
    
    ICMS 2024 esperado: ~R$ 500-600 bilhões (crescimento nominal de 2021)
    Se CONFAZ mostra R$ 2.4 "trilhões", as unidades originais são MIL REAIS
    """
    
    print("="*70)
    print("VERIFICACAO DE UNIDADES - CONFAZ")
    print("="*70)
    
    # Load CONFAZ data
    with open('output/confaz_icms_2024_by_uf.json', 'r') as f:
        confaz = json.load(f)
    
    raw_value = confaz['total_brasil_milhoes']
    
    print(f"\nValor raw no arquivo JSON:")
    print(f"  {raw_value:,.2f}")
    
    # Test different unit interpretations
    print(f"\nInterpretações possíveis:")
    print(f"  1. Se o valor está em REAIS:")
    print(f"     Total = R$ {raw_value/1e12:.2f} Trilhões")
    print(f"     (Impossível - ICMS não é tão alto)")
    
    print(f"\n  2. Se o valor está em MIL REAIS:")
    print(f"     Total = R$ {raw_value/1e9:.2f} Bilhões")
    print(f"     (Razoável - cresceria ~10%/ano desde 2021)")
    
    print(f"\n  3. Se o valor está em MILHÕES:")
    print(f"     Total = R$ {raw_value/1e6:.2f} Bilhões")  
    print(f"     (Muito baixo - menor que 2021)")
    
    # Compare with CTB 2021
    with open('output/tax_data.json', 'r') as f:
        tax_data = json.load(f)
    
    import numpy as np
    icms_2021 = np.sum(tax_data['taxes_by_type']['ICMS'])
    
    print(f"\n{'='*70}")
    print(f"REFERÊNCIA CTB 2021:")
    print(f"  ICMS 2021 = R$ {icms_2021/1e3:.2f} Bilhões")
    
    # Expected 2024 (3 years of nominal growth ~6%/year)
    expected_2024 = icms_2021 * (1.06 ** 3)
    print(f"  ICMS 2024 esperado (~6%/ano): R$ {expected_2024/1e3:.2f} Bilhões")
    
    # Which interpretation is closest?
    interp1 = raw_value / 1e9  # Assuming thousands
    interp2 = raw_value / 1e6  # Assuming millions
    interp3 = raw_value / 1e12  # Assuming units
    
    expected_bilhoes = expected_2024 / 1e3
    
    diff1 = abs(interp1 - expected_bilhoes) / expected_bilhoes
    diff2 = abs(interp2 - expected_bilhoes) / expected_bilhoes
    diff3 = abs(interp3 - expected_bilhoes) / expected_bilhoes
    
    print(f"\n{'='*70}")
    print(f"DIAGNÓSTICO:")
    print(f"{'='*70}")
    
    if diff1 < diff2 and diff1 < diff3:
        print(f"\n✓ CONCLUSÃO: Valores estão em MIL REAIS")
        print(f"  CONFAZ 2024 = R$ {interp1:.2f} Bilhões")
        print(f"  Desvio vs esperado: {diff1*100:.1f}%")
        print(f"\nAÇÃO NECESSÁRIA:")
        print(f"  Dividir todos os valores por 1.000.000 (não 1.000.000.000)")
        return "thousands"
    elif diff2 < diff1 and diff2 < diff3:
        print(f"\n✓ CONCLUSÃO: Valores estão em MILHÕES")
        print(f"  CONFAZ 2024 = R$ {interp2:.2f} Bilhões  ")
        print(f"  Desvio vs esperado: {diff2*100:.1f}%")
        return "millions"
    else:
        print(f"\n? INCONCLUSIVO - verificar arquivo original")
        return "unknown"

if __name__ == "__main__":
    verify_units()
