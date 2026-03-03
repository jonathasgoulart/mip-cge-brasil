import numpy as np
import json
import os

def simulate_carnaval_light():
    """Ultra-light Carnival simulation using estimated multipliers"""
    
    print("="*70)
    print("CARNAVAL RIO 2024 - ESTIMATIVA DE IMPACTO ECONÔMICO")
    print("="*70)
    
    # === PARÂMETROS DE ENTRADA ===
    # Estimativa baseada em dados históricos (Riotur/Sebrae 2023)
    GASTO_DIRETO = 6000  # Milhões de R$ (6 bilhões)
    
    # Multiplicadores médios do Rio (calibrados pelo modelo MRIO)
    MULT_PRODUCAO = 1.65   # Cada R$1 gasto gera R$1.65 de produção total
    MULT_EMPREGO = 12.5    # Empregos por milhão investido
    TAXA_IMPOSTO = 0.0932  # 9.32% (da matriz 2021 atualizada)
    
    # Distribuição por tipo de imposto (% do total)
    DISTRIBUICAO_IMPOSTOS = {
        "ICMS": 0.484,      # 48.4% (maior componente)
        "PIS_PASEP": 0.064,
        "COFINS": 0.243,
        "ISS": 0.067,
        "IPI": 0.050,
        "IOF": 0.042,
        "II": 0.047,
        "CIDE": 0.004
    }
    
    print(f"\n[PREMISSAS]")
    print(f"  Gasto Direto Estimado:           R$ {GASTO_DIRETO:,.0f} Milhões")
    print(f"  Multiplicador de Produção:       {MULT_PRODUCAO:.2f}x")
    print(f"  Multiplicador de Emprego:        {MULT_EMPREGO:.1f} vagas/M R$")
    print(f"  Taxa Efetiva de Impostos:        {TAXA_IMPOSTO*100:.2f}%")
    
    # === CÁLCULOS ===
    producao_total = GASTO_DIRETO * MULT_PRODUCAO
    empregos_total = GASTO_DIRETO * MULT_EMPREGO
    impostos_total = producao_total * TAXA_IMPOSTO
    
    # Impostos por tipo
    impostos_por_tipo = {
        nome: impostos_total * pct 
        for nome, pct in DISTRIBUICAO_IMPOSTOS.items()
    }
    
    # === RESULTADOS ===
    print(f"\n{'='*70}")
    print("RESULTADOS - IMPACTO TOTAL")
    print(f"{'='*70}")
    
    print(f"\n[PIB] Valor Agregado Bruto")
    print(f"   Gasto Direto:                    R$ {GASTO_DIRETO:>10,.0f} Milhões")
    print(f"   Produção Total Gerada:           R$ {producao_total:>10,.0f} Milhões")
    print(f"   Efeito Multiplicador:           R$ {producao_total - GASTO_DIRETO:>10,.0f} Milhões")
    
    print(f"\n[EMPREGO]")
    print(f"   Total de Postos de Trabalho:     {empregos_total:>10,.0f} vagas")
    print(f"   Empregos Diretos (~40%):         {empregos_total*0.4:>10,.0f} vagas")
    print(f"   Empregos Indiretos (~60%):       {empregos_total*0.6:>10,.0f} vagas")
    
    print(f"\n[ARRECADACAO] Tributaria")
    print(f"   Total Arrecadado:                R$ {impostos_total:>10,.2f} Milhões")
    print(f"   % sobre Gasto Direto:            {impostos_total/GASTO_DIRETO*100:>10.1f}%")
    
    print(f"\n   Distribuição por Esfera:")
    
    # Agrupar por esfera governamental
    estadual = impostos_por_tipo['ICMS']
    municipal = impostos_por_tipo['ISS']
    federal = sum(v for k, v in impostos_por_tipo.items() 
                  if k not in ['ICMS', 'ISS'])
    
    print(f"      Estado (ICMS):                R$ {estadual:>8,.2f} M ({estadual/impostos_total*100:.1f}%)")
    print(f"      Município (ISS):              R$ {municipal:>8,.2f} M ({municipal/impostos_total*100:.1f}%)")
    print(f"      União (Demais):               R$ {federal:>8,.2f} M ({federal/impostos_total*100:.1f}%)")
    
    print(f"\n   Detalhamento por Tipo de Imposto:")
    sorted_taxes = sorted(impostos_por_tipo.items(), 
                         key=lambda x: x[1], reverse=True)
    for nome, valor in sorted_taxes:
        nome_display = nome.replace('_', '/').upper()
        pct = (valor/impostos_total*100)
        print(f"      {nome_display:12s}: R$ {valor:>8,.2f} M ({pct:>5.1f}%)")
    
    # === SETORES MAIS BENEFICIADOS ===
    print(f"\n[SETORES] Mais Impactados (Estimativa)")
    print("-" * 70)
    
    setores_impacto = [
        ("Artes, Cultura e Entretenimento", 2000, 0.35),
        ("Alojamento (Hotéis/Pousadas)", 1500, 0.25),
        ("Alimentação (Bares/Restaurantes)", 1200, 0.20),
        ("Transporte (Terrestre/Aéreo)", 800, 0.13),
        ("Comércio Varejista", 500, 0.08)
    ]
    
    for setor, producao_direta, share in setores_impacto:
        producao_total_setor = producao_direta * MULT_PRODUCAO
        empregos_setor = producao_direta * MULT_EMPREGO
        print(f"  {setor:42s}: R$ {producao_total_setor:>7,.0f} M | {empregos_setor:>6,.0f} vagas")
    
    print(f"\n{'='*70}")
    print("FONTE: Modelo MRIO Brasil (27 UFs) - 2021")
    print("NOTA: Multiplicadores calibrados com dados IBGE + Receita Federal")
    print(f"{'='*70}")
    
    # === SALVAR RESULTADOS ===
    resultados = {
        "evento": "Carnaval Rio de Janeiro 2024",
        "premissas": {
            "gasto_direto_milhoes": GASTO_DIRETO,
            "multiplicador_producao": MULT_PRODUCAO,
            "multiplicador_emprego": MULT_EMPREGO,
            "taxa_imposto": TAXA_IMPOSTO
        },
        "resultados": {
            "producao_total_milhoes": float(producao_total),
            "empregos_totais": float(empregos_total),
            "impostos_totais_milhoes": float(impostos_total),
            "impostos_por_esfera": {
                "estadual_milhoes": float(estadual),
                "municipal_milhoes": float(municipal),
                "federal_milhoes": float(federal)
            },
            "impostos_por_tipo": {
                k: float(v) for k, v in impostos_por_tipo.items()
            }
        }
    }
    
    output_path = 'output/carnaval_2024_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Resultados salvos em: {output_path}\n")
    
    return resultados

if __name__ == "__main__":
    simulate_carnaval_light()
