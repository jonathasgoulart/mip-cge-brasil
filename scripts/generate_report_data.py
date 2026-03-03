"""
Gera dados detalhados para o relatorio da Economia Criativa.
Inclui:
  - Spillover por estado via MRIO v4
  - Impacto setorial completo (67 setores)
  - Decomposicao criativo vs nao-criativo detalhada
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(r'C:\Users\jonat\Documents\MIP e CGE')
OUTPUT_DIR = BASE_DIR / 'output'
FINAL_DIR = OUTPUT_DIR / 'final'
REGIONAL_DIR = OUTPUT_DIR / 'regional_matrices'
DATA_DIR = BASE_DIR / 'data' / 'processed' / '2021_final'
N = 67
RJ_IDX_MRIO = 18  # RJ index in UF_ORDER (for MRIO: sectors 18*67 to 19*67-1)

UF_ORDER = [
    'RO','AC','AM','RR','PA','AP','TO',
    'MA','PI','CE','RN','PB','PE','AL','SE','BA',
    'MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF',
]

UF_NAMES = {
    'RO':'Rondônia','AC':'Acre','AM':'Amazonas','RR':'Roraima','PA':'Pará',
    'AP':'Amapá','TO':'Tocantins','MA':'Maranhão','PI':'Piauí','CE':'Ceará',
    'RN':'Rio Grande do Norte','PB':'Paraíba','PE':'Pernambuco','AL':'Alagoas',
    'SE':'Sergipe','BA':'Bahia','MG':'Minas Gerais','ES':'Espírito Santo',
    'RJ':'Rio de Janeiro','SP':'São Paulo','PR':'Paraná','SC':'Santa Catarina',
    'RS':'Rio Grande do Sul','MS':'Mato Grosso do Sul','MT':'Mato Grosso',
    'GO':'Goiás','DF':'Distrito Federal',
}

CREATIVE_SEGMENTS = {
    'Audiovisual & Mídia': [29, 47, 48],
    'Tecnologia & Software': [50],
    'Eventos & Artes': [55, 64],
    'Turismo & Gastronomia': [45, 46],
    'Design & Serviços Criativos': [53, 54, 56],
}
ALL_CREATIVE = sorted(set(i for v in CREATIVE_SEGMENTS.values() for i in v))

SECTOR_LABELS = []

EVENTS = {
    'Rock in Rio': {
        'desc': 'Festival de música (7 dias, ~700 mil pessoas)',
        'shock': {64:800,45:400,46:300,40:150,41:150,50:100,48:50,55:50},
    },
    'Carnaval': {
        'desc': 'Carnaval do Rio (6 dias, ~7 milhões de foliões)',
        'shock': {64:2000,45:1500,46:1200,41:600,40:500,43:200},
    },
}


def main():
    print("Gerando dados detalhados para relatorio...")

    # Load sector labels
    with open(OUTPUT_DIR / 'intermediary' / 'sector_labels.txt', 'r', encoding='utf-8') as f:
        labels = [l.strip() for l in f.readlines()]

    # Load MRIO (1809x1809)
    print("  Carregando MRIO v4 (1809x1809)...")
    A_mrio = np.load(FINAL_DIR / 'A_mrio_official_v4.npy')

    # Leontief MRIO
    print("  Calculando Leontief MRIO...")
    I = np.eye(A_mrio.shape[0])
    L_mrio = np.linalg.inv(I.astype(np.float64) - A_mrio.astype(np.float64))
    print(f"  [OK] L_mrio: {L_mrio.shape}")

    # Employment coefficients 67x27
    emp_c = np.load(FINAL_DIR / 'emp_coefficients_67x27.npy')
    inc_c = np.load(FINAL_DIR / 'inc_coefficients_67x27.npy')

    # Fiscal data (RJ only for direct, but we'll approximate interstate)
    rj_mip = pd.read_excel(REGIONAL_DIR / 'MIP_2021_RJ.xlsx', sheet_name='Sintese')
    X_rj = rj_mip['VBP_MM'].values
    with open(DATA_DIR / 'tax_matrix_hybrid_by_state.json', 'r') as f:
        icms_rj = np.array(json.load(f)['RJ'])
    icms_rates_rj = np.divide(icms_rj, X_rj, out=np.zeros(N), where=X_rj > 0)

    with open(DATA_DIR / 'tax_matrix.json', 'r') as f:
        tax_data = json.load(f)
    iss_nas = np.array(tax_data['taxes_by_type']['ISS'])
    iss_rates = np.divide(iss_nas, X_rj, out=np.zeros(N), where=X_rj > 0)

    all_results = {}

    for event_name, event_cfg in EVENTS.items():
        print(f"\n  Processando {event_name}...")

        # Build 1809-dim shock vector (inject into RJ sectors only)
        F_mrio = np.zeros(A_mrio.shape[0])
        rj_offset = RJ_IDX_MRIO * N  # Start of RJ sectors in MRIO
        for sector, value in event_cfg['shock'].items():
            F_mrio[rj_offset + sector] = value

        # Run MRIO Leontief
        X_mrio = L_mrio @ F_mrio

        # Extract results by state
        state_results = []
        for uf_idx, uf in enumerate(UF_ORDER):
            start = uf_idx * N
            end = start + N
            X_uf = X_mrio[start:end]
            emp_uf = X_uf * emp_c[:, uf_idx]
            renda_uf = X_uf * inc_c[:, uf_idx]

            prod_total = X_uf.sum()
            emp_total = emp_uf.sum()
            renda_total = renda_uf.sum()

            # Creative vs non-creative
            prod_criativo = sum(X_uf[i] for i in ALL_CREATIVE)
            emp_criativo = sum(emp_uf[i] for i in ALL_CREATIVE)

            state_results.append({
                'uf': uf,
                'nome': UF_NAMES[uf],
                'producao': float(prod_total),
                'empregos': float(emp_total),
                'renda': float(renda_total),
                'prod_criativo': float(prod_criativo),
                'emp_criativo': float(emp_criativo),
            })

        # Sort by production (excluding RJ for spillover ranking)
        state_results_sorted = sorted(state_results, key=lambda x: x['producao'], reverse=True)

        # Detailed sectoral impact (RJ only, all 67 sectors)
        X_rj_detail = X_mrio[rj_offset:rj_offset+N]
        emp_rj_detail = X_rj_detail * emp_c[:, RJ_IDX_MRIO]
        renda_rj_detail = X_rj_detail * inc_c[:, RJ_IDX_MRIO]
        icms_rj_detail = X_rj_detail * icms_rates_rj
        iss_rj_detail = X_rj_detail * iss_rates

        sector_detail = []
        for s in range(N):
            sector_detail.append({
                'idx': s,
                'setor': labels[s],
                'producao': float(X_rj_detail[s]),
                'empregos': float(emp_rj_detail[s]),
                'renda': float(renda_rj_detail[s]),
                'icms': float(icms_rj_detail[s]),
                'iss': float(iss_rj_detail[s]),
                'criativo': s in ALL_CREATIVE,
                'choque_direto': float(event_cfg['shock'].get(s, 0)),
            })

        # Non-creative sectors benefited (top 15)
        non_creative_sectors = [s for s in sector_detail if not s['criativo'] and s['producao'] > 0.1]
        non_creative_sectors.sort(key=lambda x: x['producao'], reverse=True)

        # Creative segments breakdown
        seg_detail = {}
        for seg_name, seg_idx in CREATIVE_SEGMENTS.items():
            seg_detail[seg_name] = {
                'producao': float(sum(X_rj_detail[i] for i in seg_idx)),
                'empregos': float(sum(emp_rj_detail[i] for i in seg_idx)),
                'renda': float(sum(renda_rj_detail[i] for i in seg_idx)),
                'icms': float(sum(icms_rj_detail[i] for i in seg_idx)),
                'iss': float(sum(iss_rj_detail[i] for i in seg_idx)),
                'setores': [labels[i] for i in seg_idx],
            }

        choque_total = sum(event_cfg['shock'].values())
        prod_total_br = sum(s['producao'] for s in state_results)
        prod_rj = X_rj_detail.sum()
        prod_outros = prod_total_br - prod_rj

        all_results[event_name] = {
            'descricao': event_cfg['desc'],
            'choque_total': float(choque_total),
            'producao_total_brasil': float(prod_total_br),
            'producao_rj': float(prod_rj),
            'producao_outros_estados': float(prod_outros),
            'multiplicador_rj': float(prod_rj / choque_total),
            'multiplicador_brasil': float(prod_total_br / choque_total),
            'empregos_total_brasil': float(sum(s['empregos'] for s in state_results)),
            'empregos_rj': float(emp_rj_detail.sum()),
            'renda_total_brasil': float(sum(s['renda'] for s in state_results)),
            'renda_rj': float(renda_rj_detail.sum()),
            'icms_rj': float(icms_rj_detail.sum()),
            'iss_rj': float(iss_rj_detail.sum()),
            'fiscal_rj': float(icms_rj_detail.sum() + iss_rj_detail.sum()),
            'spillover_por_estado': state_results_sorted,
            'setores_detalhados_rj': sorted(sector_detail, key=lambda x: x['producao'], reverse=True),
            'setores_nao_criativos_rj': non_creative_sectors[:15],
            'segmentos_criativos': seg_detail,
        }

        print(f"    Producao Brasil: R$ {prod_total_br:,.0f} Mi")
        print(f"    Producao RJ:     R$ {prod_rj:,.0f} Mi ({prod_rj/prod_total_br*100:.1f}%)")
        print(f"    Spillover:       R$ {prod_outros:,.0f} Mi para outros estados")
        print(f"    Empregos Brasil: {sum(s['empregos'] for s in state_results):,.0f}")

    # Save
    out_path = OUTPUT_DIR / 'relatorio_economia_criativa_dados.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Dados salvos: {out_path}")

    # Also save creative economy study data
    study_path = OUTPUT_DIR / 'estudo_economia_criativa_rj.json'
    if study_path.exists():
        with open(study_path, 'r', encoding='utf-8') as f:
            study_data = json.load(f)
        all_results['estudo_central'] = study_data

    final_path = OUTPUT_DIR / 'relatorio_economia_criativa_completo.json'
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"[OK] Dados completos: {final_path}")


if __name__ == "__main__":
    main()
