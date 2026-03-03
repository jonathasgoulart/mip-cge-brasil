"""
Simulacao de Eventos Criativos: Rock in Rio e Carnaval
======================================================
Analisa o impacto economico de grandes eventos no RJ
com foco na Economia Criativa.

Secoes:
  1. Definicao dos choques por evento
  2. Impacto total via Leontief (direto + indireto)
  3. Decomposicao: quanto vai para setores criativos vs nao-criativos
  4. Emprego e renda gerados
  5. Impacto fiscal (ICMS + ISS)
  6. Comparacao cruzada dos dois eventos

Output: output/simulacao_eventos_criativos_rj.xlsx
        output/simulacao_eventos_criativos_rj.json
"""

import numpy as np
import pandas as pd
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
FINAL_DIR = OUTPUT_DIR / 'final'
REGIONAL_DIR = OUTPUT_DIR / 'regional_matrices'
DATA_DIR = BASE_DIR / 'data' / 'processed' / '2021_final'

N_SECTORS = 67
RJ_IDX = 18  # indice do RJ na ordem UF_ORDER

# Segmentos criativos (mesma definicao do estudo central)
CREATIVE_SEGMENTS = {
    'Audiovisual & Midia': [29, 47, 48],
    'Tecnologia & Software': [50],
    'Eventos & Artes': [55, 64],
    'Turismo & Gastronomia': [45, 46],
    'Design & Servicos Criativos': [53, 54, 56],
}

ALL_CREATIVE = []
for indices in CREATIVE_SEGMENTS.values():
    ALL_CREATIVE.extend(indices)
ALL_CREATIVE = sorted(set(ALL_CREATIVE))

# =========================================================================
# DEFINICAO DOS CHOQUES DE DEMANDA (R$ Mi)
# =========================================================================
# Fontes: Riotur, Sebrae, SPTuris, pesquisas de gasto do turista

EVENTS = {
    'Rock in Rio': {
        'descricao': 'Festival de musica (7 dias, ~700 mil pessoas)',
        'choque_total': 2000.0,  # R$ 2 Bi
        'distribuicao': {
            # Setor MIP (0-indexed): R$ Mi
            64: 800,   # Artes/Espetaculos (ingressos, producao, artistas)
            45: 400,   # Alojamento (hoteis, Airbnb)
            46: 300,   # Alimentacao (bares, restaurantes, dentro do evento)
            40: 150,   # Comercio (merchandising, varejo)
            41: 150,   # Transporte terrestre (taxi, app, onibus)
            50: 100,   # TI/Sistemas (streaming, apps, infraestrutura digital)
            48: 50,    # TV/Radio/Cinema (cobertura, transmissao)
            55: 50,    # Outras profissionais (design, producao, fotografia)
        },
    },
    'Carnaval': {
        'descricao': 'Carnaval do Rio (6 dias, ~7 milhoes de folioes)',
        'choque_total': 6000.0,  # R$ 6 Bi
        'distribuicao': {
            64: 2000,  # Artes/Espetaculos (escolas, blocos, shows)
            45: 1500,  # Alojamento (hoteis, ocupacao ~95%)
            46: 1200,  # Alimentacao (ambulantes, bares, restaurantes)
            41: 600,   # Transporte terrestre (mobilidade urbana)
            40: 500,   # Comercio (fantasias, bebidas, acessorios)
            43: 200,   # Transporte aereo (turismo domestico/internacional)
        },
    },
}


def load_data():
    """Carrega todas as matrizes necessarias."""
    print("Carregando dados...")
    data = {}

    # Matriz A local do RJ
    A_local_path = REGIONAL_DIR / 'A_RIO_LOCAIS_67x67.xlsx'
    data['A_local'] = pd.read_excel(A_local_path, index_col=0).values
    print(f"  [OK] A_local RJ: {data['A_local'].shape}")

    # Matriz A inter-regional do RJ
    A_inter_path = REGIONAL_DIR / 'A_RIO_INTER_67x67.xlsx'
    data['A_inter'] = pd.read_excel(A_inter_path, index_col=0).values
    print(f"  [OK] A_inter RJ: {data['A_inter'].shape}")

    # Leontief inversa
    I = np.eye(N_SECTORS)
    data['L'] = np.linalg.inv(I - data['A_local'])
    print(f"  [OK] Leontief: mult. medio {data['L'].sum(axis=0).mean():.3f}")

    # Coeficientes de emprego (67x27 -> coluna RJ)
    emp_67x27 = np.load(FINAL_DIR / 'emp_coefficients_67x27.npy')
    data['e_coeffs'] = emp_67x27[:, RJ_IDX]
    print(f"  [OK] Emprego RJ: {(data['e_coeffs'] > 0).sum()}/67 setores")

    # Coeficientes de renda (67x27 -> coluna RJ, em R$Mi/R$Mi)
    inc_67x27 = np.load(FINAL_DIR / 'inc_coefficients_67x27.npy')
    data['inc_coeffs'] = inc_67x27[:, RJ_IDX]

    # Labels dos setores
    labels_path = OUTPUT_DIR / 'intermediary' / 'sector_labels.txt'
    with open(labels_path, 'r', encoding='utf-8') as f:
        data['labels'] = [l.strip() for l in f.readlines()]
    
    # Dados fiscais
    rj_mip = pd.read_excel(REGIONAL_DIR / 'MIP_2021_RJ.xlsx', sheet_name='Sintese')
    X_rj = rj_mip['VBP_MM'].values

    with open(DATA_DIR / 'tax_matrix.json', 'r') as f:
        tax_data = json.load(f)
    
    # VBP nacional para ISS rates
    iss_nas = np.array(tax_data['taxes_by_type']['ISS'])
    with open(DATA_DIR / 'vab_regional.json', 'r') as f:
        vab_all = json.load(f)
    # Usar VBP do RJ como base
    data['iss_rates'] = np.divide(iss_nas, X_rj, out=np.zeros(N_SECTORS), where=X_rj > 0)

    with open(DATA_DIR / 'tax_matrix_hybrid_by_state.json', 'r') as f:
        icms_rj = np.array(json.load(f)['RJ'])
    data['icms_rates'] = np.divide(icms_rj, X_rj, out=np.zeros(N_SECTORS), where=X_rj > 0)

    print(f"  [OK] Taxas fiscais carregadas")
    return data


def simulate_event(event_name, event_config, data):
    """Simula um evento e retorna resultados detalhados."""
    print(f"\n{'='*70}")
    print(f"SIMULACAO: {event_name.upper()}")
    print(f"{event_config['descricao']}")
    print(f"{'='*70}")

    # Montar vetor de choque
    F = np.zeros(N_SECTORS)
    for sector, value in event_config['distribuicao'].items():
        F[sector] = value

    choque_total = F.sum()
    choque_criativo = sum(F[i] for i in ALL_CREATIVE)
    choque_nao_criativo = choque_total - choque_criativo

    print(f"\nChoque total: R$ {choque_total:,.0f} Mi")
    print(f"  Direcionado a setores criativos: R$ {choque_criativo:,.0f} Mi ({choque_criativo/choque_total*100:.1f}%)")
    print(f"  Direcionado a nao-criativos:     R$ {choque_nao_criativo:,.0f} Mi ({choque_nao_criativo/choque_total*100:.1f}%)")

    # Impacto via Leontief
    X_impact = data['L'] @ F
    producao_total = X_impact.sum()
    multiplicador = producao_total / choque_total

    print(f"\nProducao total gerada: R$ {producao_total:,.0f} Mi")
    print(f"Multiplicador: {multiplicador:.3f}x")

    # Decomposicao criativo vs nao-criativo
    prod_criativo = sum(X_impact[i] for i in ALL_CREATIVE)
    prod_nao_criativo = producao_total - prod_criativo

    print(f"\nDecomposicao do impacto:")
    print(f"  Setores criativos:     R$ {prod_criativo:,.0f} Mi ({prod_criativo/producao_total*100:.1f}%)")
    print(f"  Setores nao-criativos: R$ {prod_nao_criativo:,.0f} Mi ({prod_nao_criativo/producao_total*100:.1f}%)")

    # Impacto por segmento criativo
    print(f"\nImpacto por segmento criativo:")
    seg_results = {}
    for seg_name, seg_indices in CREATIVE_SEGMENTS.items():
        prod_seg = sum(X_impact[i] for i in seg_indices)
        emp_seg = sum(X_impact[i] * data['e_coeffs'][i] for i in seg_indices)
        renda_seg = sum(X_impact[i] * data['inc_coeffs'][i] for i in seg_indices)
        seg_results[seg_name] = {
            'producao': prod_seg,
            'empregos': emp_seg,
            'renda': renda_seg,
        }
        print(f"  {seg_name:<30} R$ {prod_seg:>8,.0f} Mi | {emp_seg:>8,.0f} empregos | R$ {renda_seg:>6,.0f} Mi renda")

    # Emprego total
    empregos = X_impact * data['e_coeffs']
    emp_total = empregos.sum()
    emp_criativo = sum(empregos[i] for i in ALL_CREATIVE)

    print(f"\nEmpregos gerados: {emp_total:,.0f}")
    print(f"  Em setores criativos: {emp_criativo:,.0f} ({emp_criativo/emp_total*100:.1f}%)")

    # Renda
    renda = X_impact * data['inc_coeffs']
    renda_total = renda.sum()

    print(f"Renda gerada: R$ {renda_total:,.0f} Mi")

    # Impacto fiscal
    icms = (X_impact * data['icms_rates']).sum()
    iss = (X_impact * data['iss_rates']).sum()
    fiscal_total = icms + iss

    print(f"\nImpacto fiscal:")
    print(f"  ICMS: R$ {icms:,.1f} Mi")
    print(f"  ISS:  R$ {iss:,.1f} Mi")
    print(f"  Total: R$ {fiscal_total:,.1f} Mi ({fiscal_total/choque_total*100:.1f}% do choque)")

    # Vazamento inter-regional
    vazamento = (data['A_inter'] @ X_impact).sum()
    print(f"\nVazamento para outros estados: R$ {vazamento:,.0f} Mi ({vazamento/producao_total*100:.1f}%)")

    # Top 10 setores beneficiados
    print(f"\nTop 10 setores beneficiados:")
    top_idx = np.argsort(X_impact)[-10:][::-1]
    for rank, idx in enumerate(top_idx, 1):
        is_creative = "*" if idx in ALL_CREATIVE else " "
        print(f"  {rank:>2}. [{idx:>2}] {data['labels'][idx]:<55} R$ {X_impact[idx]:>8,.0f} Mi {is_creative}")

    return {
        'evento': event_name,
        'descricao': event_config['descricao'],
        'choque_total': float(choque_total),
        'choque_criativo': float(choque_criativo),
        'producao_total': float(producao_total),
        'multiplicador': float(multiplicador),
        'prod_criativo': float(prod_criativo),
        'prod_nao_criativo': float(prod_nao_criativo),
        'pct_criativo': float(prod_criativo / producao_total * 100),
        'empregos_total': float(emp_total),
        'empregos_criativos': float(emp_criativo),
        'renda_total': float(renda_total),
        'icms': float(icms),
        'iss': float(iss),
        'fiscal_total': float(fiscal_total),
        'vazamento': float(vazamento),
        'segmentos': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in seg_results.items()},
        'top_setores': [
            {'idx': int(i), 'setor': data['labels'][i],
             'producao': float(X_impact[i]),
             'empregos': float(empregos[i]),
             'criativo': i in ALL_CREATIVE}
            for i in top_idx
        ],
    }


def compare_events(results):
    """Comparacao cruzada dos eventos."""
    print(f"\n{'='*70}")
    print("COMPARACAO CRUZADA: ROCK IN RIO vs CARNAVAL")
    print(f"{'='*70}")

    headers = ['Metrica', results[0]['evento'], results[1]['evento'], 'Ratio']
    r0, r1 = results[0], results[1]

    comparisons = [
        ('Choque (R$ Mi)', r0['choque_total'], r1['choque_total']),
        ('Producao total (R$ Mi)', r0['producao_total'], r1['producao_total']),
        ('Multiplicador', r0['multiplicador'], r1['multiplicador']),
        ('% Impacto criativo', r0['pct_criativo'], r1['pct_criativo']),
        ('Empregos totais', r0['empregos_total'], r1['empregos_total']),
        ('Empregos criativos', r0['empregos_criativos'], r1['empregos_criativos']),
        ('Renda gerada (R$ Mi)', r0['renda_total'], r1['renda_total']),
        ('ICMS+ISS (R$ Mi)', r0['fiscal_total'], r1['fiscal_total']),
        ('Empregos/R$ 1Bi', r0['empregos_total']/(r0['choque_total']/1000),
                            r1['empregos_total']/(r1['choque_total']/1000)),
        ('Fiscal/Choque %', r0['fiscal_total']/r0['choque_total']*100,
                            r1['fiscal_total']/r1['choque_total']*100),
    ]

    print(f"\n{'Metrica':<30} {'Rock in Rio':>15} {'Carnaval':>15} {'Ratio C/R':>10}")
    print("-" * 75)
    for name, v0, v1 in comparisons:
        ratio = v1 / v0 if v0 > 0 else 0
        if name in ('Multiplicador', '% Impacto criativo', 'Fiscal/Choque %'):
            print(f"{name:<30} {v0:>15.2f} {v1:>15.2f} {ratio:>9.2f}x")
        elif name in ('Empregos totais', 'Empregos criativos', 'Empregos/R$ 1Bi'):
            print(f"{name:<30} {v0:>15,.0f} {v1:>15,.0f} {ratio:>9.2f}x")
        else:
            print(f"{name:<30} {v0:>15,.1f} {v1:>15,.1f} {ratio:>9.2f}x")

    # Comparacao por segmento criativo
    print(f"\nImpacto por segmento criativo (R$ Mi):")
    print(f"{'Segmento':<30} {'Rock in Rio':>15} {'Carnaval':>15}")
    print("-" * 65)
    for seg in CREATIVE_SEGMENTS:
        v0 = r0['segmentos'][seg]['producao']
        v1 = r1['segmentos'][seg]['producao']
        print(f"{seg:<30} {v0:>15,.0f} {v1:>15,.0f}")


def main():
    print("=" * 70)
    print("IMPACTO DE GRANDES EVENTOS NA ECONOMIA CRIATIVA DO RJ")
    print("=" * 70)

    data = load_data()

    results = []
    for event_name, event_config in EVENTS.items():
        r = simulate_event(event_name, event_config, data)
        results.append(r)

    compare_events(results)

    # Salvar
    out_json = OUTPUT_DIR / 'simulacao_eventos_criativos_rj.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] JSON: {out_json}")

    # Excel
    out_xlsx = OUTPUT_DIR / 'simulacao_eventos_criativos_rj.xlsx'
    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        for r in results:
            # Aba por evento: top setores
            df_top = pd.DataFrame(r['top_setores'])
            df_top.to_excel(writer, sheet_name=r['evento'][:31], index=False)

            # Aba segmentos
            seg_rows = []
            for seg, vals in r['segmentos'].items():
                seg_rows.append({'Segmento': seg, **vals})
            pd.DataFrame(seg_rows).to_excel(writer, sheet_name=f"{r['evento'][:20]}_Segmentos", index=False)

        # Aba comparacao
        comp_rows = [
            {'Metrica': 'Choque (R$ Mi)', 'Rock in Rio': results[0]['choque_total'], 'Carnaval': results[1]['choque_total']},
            {'Metrica': 'Producao Total (R$ Mi)', 'Rock in Rio': results[0]['producao_total'], 'Carnaval': results[1]['producao_total']},
            {'Metrica': 'Multiplicador', 'Rock in Rio': results[0]['multiplicador'], 'Carnaval': results[1]['multiplicador']},
            {'Metrica': '% Impacto Criativo', 'Rock in Rio': results[0]['pct_criativo'], 'Carnaval': results[1]['pct_criativo']},
            {'Metrica': 'Empregos Totais', 'Rock in Rio': results[0]['empregos_total'], 'Carnaval': results[1]['empregos_total']},
            {'Metrica': 'Empregos Criativos', 'Rock in Rio': results[0]['empregos_criativos'], 'Carnaval': results[1]['empregos_criativos']},
            {'Metrica': 'Renda (R$ Mi)', 'Rock in Rio': results[0]['renda_total'], 'Carnaval': results[1]['renda_total']},
            {'Metrica': 'ICMS+ISS (R$ Mi)', 'Rock in Rio': results[0]['fiscal_total'], 'Carnaval': results[1]['fiscal_total']},
        ]
        pd.DataFrame(comp_rows).to_excel(writer, sheet_name='Comparacao', index=False)

    print(f"[OK] Excel: {out_xlsx}")
    print(f"\n{'='*70}")
    print("SIMULACOES COMPLETAS.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
