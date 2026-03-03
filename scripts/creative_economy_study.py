"""
Estudo: O Efeito Multiplicador da Economia Criativa Fluminense
==============================================================
Script central que calcula multiplicadores, encadeamentos, impacto fiscal
e decomposição setorial para a Economia Criativa do Rio de Janeiro.

Usa: Matriz RJ oficial (UFRJ/CEPERJ 2019), coeficientes 2021, MRIO v4.
"""

import numpy as np
import pandas as pd
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
INTER_DIR = OUTPUT_DIR / 'intermediary'
FINAL_DIR = OUTPUT_DIR / 'final'
REGIONAL_DIR = OUTPUT_DIR / 'regional_matrices'
DATA_DIR = BASE_DIR / 'data' / 'processed' / '2021_final'

N_SECTORS = 67

# Labels dos 67 setores
SECTOR_LABELS = [
    "Agricultura, inclusive o apoio à agricultura e a pós-colheita",
    "Pecuária, inclusive o apoio à pecuária",
    "Produção florestal; pesca e aquicultura",
    "Extração de carvão mineral e de minerais não metálicos",
    "Extração de petróleo e gás, inclusive as atividades de apoio",
    "Extração de minério de ferro, inclusive beneficiamentos e a aglomeração",
    "Extração de minerais metálicos não ferrosos, inclusive beneficiamentos",
    "Abate e produtos de carne, inclusive os produtos do laticínio e da pesca",
    "Fabricação e refino de açúcar",
    "Outros produtos alimentares",
    "Fabricação de bebidas",
    "Fabricação de produtos do fumo",
    "Fabricação de produtos têxteis",
    "Confecção de artefatos do vestuário e acessórios",
    "Fabricação de calçados e de artefatos de couro",
    "Fabricação de produtos da madeira",
    "Fabricação de celulose, papel e produtos de papel",
    "Impressão e reprodução de gravações",
    "Refino de petróleo e coquerias",
    "Fabricação de biocombustíveis",
    "Fabricação de químicos orgânicos e inorgânicos, resinas e elastômeros",
    "Fabricação de defensivos, desinfestantes, tintas e químicos diversos",
    "Fabricação de produtos de limpeza, cosméticos/perfumaria e higiene pessoal",
    "Fabricação de produtos farmoquímicos e farmacêuticos",
    "Fabricação de produtos de borracha e de material plástico",
    "Fabricação de produtos de minerais não metálicos",
    "Produção de ferro gusa/ferroligas, siderurgia e tubos de aço sem costura",
    "Metalurgia de metais não ferosos e a fundição de metais",
    "Fabricação de produtos de metal, exceto máquinas e equipamentos",
    "Fabricação de equipamentos de informática, produtos eletrônicos e ópticos",
    "Fabricação de máquinas e equipamentos elétricos",
    "Fabricação de máquinas e equipamentos mecânicos",
    "Fabricação de automóveis, caminhões e ônibus, exceto peças",
    "Fabricação de peças e acessórios para veículos automotores",
    "Fabricação de outros equipamentos de transporte, exceto veículos automotores",
    "Fabricação de móveis e de produtos de indústrias diversas",
    "Manutenção, reparação e instalação de máquinas e equipamentos",
    "Energia elétrica, gás natural e outras utilidades",
    "Água, esgoto e gestão de resíduos",
    "Construção",
    "Comércio por atacado e varejo",
    "Transporte terrestre",
    "Transporte aquaviário",
    "Transporte aéreo",
    "Armazenamento, atividades auxiliares dos transportes e correio",
    "Alojamento",
    "Alimentação",
    "Edição e edição integrada à impressão",
    "Atividades de televisão, rádio, cinema e gravação/edição de som e imagem",
    "Telecomunicações",
    "Desenvolvimento de sistemas e outros serviços de informação",
    "Intermediação financeira, seguros e previdência complementar",
    "Atividades imobiliárias",
    "Atividades jurídicas, contábeis, consultoria e sedes de empresas",
    "Serviços de arquitetura, engenharia, testes/análises técnicas e P&D",
    "Outras atividades profissionais, científicas e técnicas",
    "Aluguéis não imobiliários e gestão de ativos de propriedade intelectual",
    "Outras atividades administrativas e serviços complementares",
    "Atividades de vigilância, segurança e investigação",
    "Administração pública, defesa e seguridade social",
    "Educação pública",
    "Educação privada",
    "Saúde pública",
    "Saúde privada",
    "Atividades artísticas, criativas e de espetáculos",
    "Organizações associativas e outros serviços pessoais",
    "Serviços domésticos",
]

# ============================================================================
# MAPEAMENTO DA ECONOMIA CRIATIVA (5 segmentos → índices MIP 0-based)
# ============================================================================

CREATIVE_SEGMENTS = {
    "Audiovisual & Mídia": {
        "indices": [47, 48],
        "descricao": "Edição, TV, rádio, cinema, gravação de som e imagem"
    },
    "Tecnologia & Software": {
        "indices": [50],
        "descricao": "Desenvolvimento de sistemas e serviços de informação"
    },
    "Eventos & Artes": {
        "indices": [64],
        "descricao": "Atividades artísticas, criativas e de espetáculos"
    },
    "Turismo & Gastronomia": {
        "indices": [45, 46],
        "descricao": "Alojamento e alimentação"
    },
    "Design & Serviços Criativos": {
        "indices": [29, 55, 56],
        "descricao": "Equipamentos eletrônicos, atividades profissionais, propriedade intelectual"
    },
}

# Todos os índices criativos (flat)
ALL_CREATIVE_INDICES = []
for seg in CREATIVE_SEGMENTS.values():
    ALL_CREATIVE_INDICES.extend(seg["indices"])
ALL_CREATIVE_INDICES = sorted(set(ALL_CREATIVE_INDICES))


# ============================================================================
# CARREGAMENTO DE DADOS
# ============================================================================

def load_data():
    """Carrega todas as matrizes e coeficientes necessários."""
    print("=" * 70)
    print("ESTUDO: O EFEITO MULTIPLICADOR DA ECONOMIA CRIATIVA FLUMINENSE")
    print("=" * 70)

    data = {}

    # 1. Matriz A local RJ (UFRJ/CEPERJ)
    print("\n[1/7] Carregando matriz A local RJ...")
    A_local = pd.read_excel(
        REGIONAL_DIR / 'A_RIO_LOCAIS_67x67.xlsx', index_col=0
    ).values
    data['A_local'] = A_local
    print(f"  [OK] A_local: {A_local.shape}")

    # 2. Matriz A inter-regional RJ
    print("[2/7] Carregando matriz de vazamento RJ...")
    A_inter = pd.read_excel(
        REGIONAL_DIR / 'A_RIO_INTER_67x67.xlsx', index_col=0
    ).values
    data['A_inter'] = A_inter
    print(f"  [OK] A_inter: {A_inter.shape}")

    # 3. Leontief inversa
    print("[3/7] Calculando inversa de Leontief (Tipo I)...")
    I = np.eye(N_SECTORS)
    L = np.linalg.inv(I - A_local)
    data['L'] = L
    print(f"  [OK] Leontief: {L.shape}, multiplicador medio: {L.sum(axis=0).mean():.3f}")

    # 4. Coeficientes de emprego (da matriz oficial 67x27)
    print("[4/7] Carregando coeficientes de emprego (matriz oficial 67x27)...")
    emp_67x27 = np.load(FINAL_DIR / 'emp_coefficients_67x27.npy')
    rj_idx = 18  # RJ e o indice 18 na ordem UF_ORDER
    e_coeffs = emp_67x27[:, rj_idx]
    data['e_coeffs'] = e_coeffs
    print(f"  [OK] Empregos RJ: {e_coeffs.shape}, setores com dados: {(e_coeffs > 0).sum()}/67")

    # 5. Coeficientes de renda (da matriz oficial 67x27, ja em R$Mi/R$Mi)
    print("[5/7] Carregando coeficientes de renda (matriz oficial 67x27)...")
    inc_67x27 = np.load(FINAL_DIR / 'inc_coefficients_67x27.npy')
    inc_coeffs = inc_67x27[:, rj_idx]
    data['inc_coeffs'] = inc_coeffs
    print(f"  [OK] Renda RJ: {inc_coeffs.shape} (em R$Mi/R$Mi)")

    # 6. VAB regional RJ
    print("[6/7] Carregando VAB RJ...")
    vab_rj = np.load(INTER_DIR / 'VAB_RJ.npy')
    data['vab_rj'] = vab_rj
    vab_nas = np.load(INTER_DIR / 'VAB_nacional.npy')
    data['vab_nas'] = vab_nas
    print(f"  [OK] VAB RJ: R$ {vab_rj.sum() / 1e3:.1f} Bi | Nacional: R$ {vab_nas.sum() / 1e3:.1f} Bi")

    # 7. Dados fiscais
    print("[7/7] Carregando dados fiscais...")
    tax_path = DATA_DIR / 'tax_matrix.json'
    icms_path = DATA_DIR / 'tax_matrix_hybrid_by_state.json'

    data['tax_rates'] = {}
    if tax_path.exists():
        with open(tax_path, 'r') as f:
            tax_data = json.load(f)
        # ISS rates (national proxy)
        x_nas = np.load(INTER_DIR / 'X_nas.npy')
        iss_nas = np.array(tax_data['taxes_by_type'].get('ISS', np.zeros(67).tolist()))
        data['iss_rates'] = np.divide(iss_nas, x_nas, out=np.zeros(67), where=x_nas != 0)
        print(f"  [OK] ISS rates carregados")
    else:
        data['iss_rates'] = np.zeros(67)

    if icms_path.exists():
        with open(icms_path, 'r') as f:
            icms_data = json.load(f)
        icms_rj = np.array(icms_data.get('RJ', np.zeros(67).tolist()))
        # Carregar VBP RJ para calcular alíquotas
        rj_mip_path = REGIONAL_DIR / 'MIP_2021_RJ.xlsx'
        if rj_mip_path.exists():
            df_rj = pd.read_excel(rj_mip_path, sheet_name='Sintese')
            x_rj = df_rj['VBP_MM'].values
            data['icms_rates'] = np.divide(icms_rj, x_rj, out=np.zeros(67), where=x_rj != 0)
            data['x_rj'] = x_rj
        else:
            data['icms_rates'] = np.zeros(67)
            data['x_rj'] = vab_rj * 2  # Aproximação
        print(f"  [OK] ICMS rates RJ carregados")
    else:
        data['icms_rates'] = np.zeros(67)

    return data


# ============================================================================
# ANÁLISE 1: CONTEXTO — PESO DA ECONOMIA CRIATIVA NO RJ
# ============================================================================

def analyze_context(data):
    """Seção 2 do estudo: Contextualização."""
    print("\n" + "=" * 70)
    print("SEÇÃO 2: CONTEXTUALIZAÇÃO — O PESO DA ECONOMIA CRIATIVA NO RJ")
    print("=" * 70)

    vab_rj = data['vab_rj']
    vab_nas = data['vab_nas']
    total_rj = vab_rj.sum()
    total_nas = vab_nas.sum()

    results = {
        "vab_total_rj_bi": total_rj / 1e3,
        "vab_total_brasil_bi": total_nas / 1e3,
        "share_rj_no_brasil_pct": total_rj / total_nas * 100,
        "segmentos": {}
    }

    print(f"\nVAB Total RJ: R$ {total_rj / 1e3:,.1f} Bi")
    print(f"VAB Total Brasil: R$ {total_nas / 1e3:,.1f} Bi")
    print(f"Participação RJ no Brasil: {total_rj / total_nas * 100:.1f}%")

    print(f"\n{'Segmento Criativo':<30} {'VAB RJ (Mi)':<15} {'% PIB RJ':<12} {'VAB BR (Mi)':<15} {'LQ':>8}")
    print("-" * 80)

    total_creative_rj = 0
    total_creative_br = 0

    for seg_name, seg_info in CREATIVE_SEGMENTS.items():
        idx = seg_info["indices"]
        vab_seg_rj = vab_rj[idx].sum()
        vab_seg_br = vab_nas[idx].sum()
        share_rj = vab_seg_rj / total_rj * 100
        # Location Quotient
        lq = (vab_seg_rj / total_rj) / (vab_seg_br / total_nas) if vab_seg_br > 0 else 0

        total_creative_rj += vab_seg_rj
        total_creative_br += vab_seg_br

        results["segmentos"][seg_name] = {
            "vab_rj_mi": float(vab_seg_rj),
            "vab_br_mi": float(vab_seg_br),
            "share_pib_rj_pct": float(share_rj),
            "location_quotient": float(lq)
        }

        print(f"{seg_name:<30} {vab_seg_rj:>12,.0f} {share_rj:>9.2f}% {vab_seg_br:>12,.0f} {lq:>8.2f}")

    share_creative = total_creative_rj / total_rj * 100
    lq_creative = (total_creative_rj / total_rj) / (total_creative_br / total_nas)

    results["total_criativo_rj_mi"] = float(total_creative_rj)
    results["total_criativo_br_mi"] = float(total_creative_br)
    results["share_criativo_pib_rj_pct"] = float(share_creative)
    results["lq_criativo_total"] = float(lq_creative)

    print("-" * 80)
    print(f"{'TOTAL ECONOMIA CRIATIVA':<30} {total_creative_rj:>12,.0f} {share_creative:>9.2f}% {total_creative_br:>12,.0f} {lq_creative:>8.2f}")

    if lq_creative > 1:
        print(f"\n  ► RJ tem ESPECIALIZAÇÃO em Economia Criativa (LQ = {lq_creative:.2f} > 1)")
    else:
        print(f"\n  ► RJ NÃO tem especialização em Economia Criativa (LQ = {lq_creative:.2f} < 1)")

    return results


# ============================================================================
# ANÁLISE 2: MULTIPLICADORES E ENCADEAMENTOS
# ============================================================================

def analyze_multipliers(data):
    """Seção 5 do estudo: Multiplicadores e Encadeamentos."""
    print("\n" + "=" * 70)
    print("SEÇÃO 5: MULTIPLICADORES E ENCADEAMENTOS DA ECONOMIA CRIATIVA")
    print("=" * 70)

    L = data['L']
    e_coeffs = data['e_coeffs']
    inc_coeffs = data['inc_coeffs']
    A_inter = data['A_inter']

    results = {"por_segmento": {}, "ranking_encadeamento": []}

    # Multiplicadores de produção por coluna da Leontief
    mult_prod = L.sum(axis=0)  # Vetor (67,): multiplicador de cada setor

    # Backward linkage normalizado
    bl = mult_prod / mult_prod.mean()

    # Forward linkage: soma por linha da Leontief
    # (usa a Ghosh, ou seja, L por linha)
    mult_forward = L.sum(axis=1)
    fl = mult_forward / mult_forward.mean()

    print(f"\n{'Segmento':<30} {'Mult.Prod.':<12} {'BL':>8} {'FL':>8} {'Emp/R$1Bi':>12} {'Renda(Mi)':>12} {'Vazam.%':>10}")
    print("-" * 95)

    for seg_name, seg_info in CREATIVE_SEGMENTS.items():
        idx = seg_info["indices"]

        # Choque unitario de R$ 1 Bi distribuido igualmente entre os setores do segmento
        shock = np.zeros(N_SECTORS)
        per_sector = 1000.0 / len(idx)  # R$ 1 Bi = R$ 1000 Mi
        for i in idx:
            shock[i] = per_sector

        # Impacto na producao (Tipo I)
        x_impact = L @ shock
        total_prod = x_impact.sum()
        multiplicador = total_prod / 1000.0

        # Emprego gerado
        jobs = (e_coeffs * x_impact).sum()

        # Renda gerada (inc_coeffs ja em R$Mi/R$Mi)
        income = (inc_coeffs * x_impact).sum()

        # Vazamento inter-regional
        leakage = (A_inter @ x_impact).sum()
        leakage_pct = leakage / total_prod * 100 if total_prod > 0 else 0

        # BL/FL medio do segmento
        seg_bl = bl[idx].mean()
        seg_fl = fl[idx].mean()

        results["por_segmento"][seg_name] = {
            "multiplicador_producao": float(multiplicador),
            "backward_linkage": float(seg_bl),
            "forward_linkage": float(seg_fl),
            "empregos_por_bi": float(jobs),
            "renda_por_bi_mi": float(income),
            "vazamento_pct": float(leakage_pct),
            "impacto_producao_mi": float(total_prod),
            "impacto_setorial": {}
        }

        print(f"{seg_name:<30} {multiplicador:>9.3f}x {seg_bl:>8.3f} {seg_fl:>8.3f} {jobs:>10,.0f} {income:>10,.1f} {leakage_pct:>8.1f}%")

        # Decomposição: top 5 setores não-criativos mais impactados
        impact_other = []
        for j in range(N_SECTORS):
            if j not in ALL_CREATIVE_INDICES and x_impact[j] > 0:
                impact_other.append((j, SECTOR_LABELS[j], float(x_impact[j])))
        impact_other.sort(key=lambda x: x[2], reverse=True)
        results["por_segmento"][seg_name]["top5_encadeados"] = [
            {"idx": t[0], "setor": t[1], "impacto_mi": t[2]}
            for t in impact_other[:5]
        ]

    # Ranking geral de encadeamentos (BL + FL > 2 = setor-chave)
    print(f"\n{'='*70}")
    print("ENCADEAMENTOS: SETORES CRIATIVOS vs ECONOMIA GERAL")
    print(f"{'='*70}")
    print(f"\n{'Setor Criativo':<55} {'BL':>8} {'FL':>8} {'Tipo':>15}")
    print("-" * 90)

    for i in ALL_CREATIVE_INDICES:
        tipo = ""
        if bl[i] > 1 and fl[i] > 1:
            tipo = "SETOR-CHAVE *"
        elif bl[i] > 1:
            tipo = "Forte p/ trás"
        elif fl[i] > 1:
            tipo = "Forte p/ frente"
        else:
            tipo = "Independente"

        results["ranking_encadeamento"].append({
            "idx": i, "setor": SECTOR_LABELS[i],
            "bl": float(bl[i]), "fl": float(fl[i]), "tipo": tipo
        })

        print(f"[{i:>2}] {SECTOR_LABELS[i]:<52} {bl[i]:>8.3f} {fl[i]:>8.3f} {tipo:>15}")

    return results


# ============================================================================
# ANÁLISE 3: DECOMPOSIÇÃO — QUEM SE BENEFICIA DA ECONOMIA CRIATIVA?
# ============================================================================

def analyze_decomposition(data):
    """Quanto cada setor da economia se beneficia quando o criativo cresce."""
    print("\n" + "=" * 70)
    print("DECOMPOSIÇÃO: QUEM SE BENEFICIA QUANDO O CRIATIVO CRESCE?")
    print("=" * 70)

    L = data['L']

    # Choque agregado: R$ 1 Bi distribuído pelo criativo (proporcional ao VAB)
    vab_rj = data['vab_rj']
    vab_creative = vab_rj[ALL_CREATIVE_INDICES]
    total_vab_creative = vab_creative.sum()

    shock = np.zeros(N_SECTORS)
    if total_vab_creative > 0:
        for i, idx in enumerate(ALL_CREATIVE_INDICES):
            shock[idx] = 1000.0 * (vab_rj[idx] / total_vab_creative)
    else:
        for idx in ALL_CREATIVE_INDICES:
            shock[idx] = 1000.0 / len(ALL_CREATIVE_INDICES)

    x_impact = L @ shock
    total = x_impact.sum()

    # Separar impacto criativo vs não-criativo
    impact_creative = sum(x_impact[i] for i in ALL_CREATIVE_INDICES)
    impact_other = total - impact_creative

    results = {
        "choque_total_mi": 1000.0,
        "impacto_total_mi": float(total),
        "multiplicador_agregado": float(total / 1000.0),
        "impacto_criativo_mi": float(impact_creative),
        "impacto_nao_criativo_mi": float(impact_other),
        "efeito_indireto_pct": float(impact_other / total * 100),
        "top_beneficiados": []
    }

    print(f"\nChoque: R$ 1.000 Mi na Economia Criativa")
    print(f"Impacto Total: R$ {total:,.0f} Mi (Multiplicador: {total / 1000:.3f}x)")
    print(f"  Dentro do criativo: R$ {impact_creative:,.0f} Mi ({impact_creative / total * 100:.1f}%)")
    print(f"  Fora do criativo:   R$ {impact_other:,.0f} Mi ({impact_other / total * 100:.1f}%)")

    print(f"\n{'Rank':<5} {'Setor Beneficiado':<55} {'Impacto (Mi)':>12} {'%':>8}")
    print("-" * 82)

    # Ranking de todos os setores por impacto
    sector_impacts = [(i, SECTOR_LABELS[i], x_impact[i]) for i in range(N_SECTORS) if x_impact[i] > 0.01]
    sector_impacts.sort(key=lambda x: x[2], reverse=True)

    for rank, (idx, name, impact) in enumerate(sector_impacts[:15], 1):
        marker = " *" if idx in ALL_CREATIVE_INDICES else ""
        pct = impact / total * 100
        results["top_beneficiados"].append({
            "rank": rank, "idx": idx, "setor": name,
            "impacto_mi": float(impact), "pct": float(pct),
            "e_criativo": idx in ALL_CREATIVE_INDICES
        })
        print(f"{rank:<5} {name:<55} {impact:>10,.1f} {pct:>7.1f}%{marker}")

    return results


# ============================================================================
# ANÁLISE 4: IMPACTO FISCAL
# ============================================================================

def analyze_fiscal_impact(data):
    """Impacto fiscal (ICMS + ISS) da Economia Criativa."""
    print("\n" + "=" * 70)
    print("IMPACTO FISCAL: ICMS + ISS DA ECONOMIA CRIATIVA")
    print("=" * 70)

    L = data['L']
    icms_rates = data['icms_rates']
    iss_rates = data['iss_rates']

    results = {"por_segmento": {}}

    print(f"\n{'Segmento':<30} {'Choque (Mi)':<12} {'ICMS (Mi)':>10} {'ISS (Mi)':>10} {'Total Tax':>10} {'Tax/Choque':>12}")
    print("-" * 90)

    for seg_name, seg_info in CREATIVE_SEGMENTS.items():
        idx = seg_info["indices"]
        shock = np.zeros(N_SECTORS)
        per_sector = 1000.0 / len(idx)
        for i in idx:
            shock[i] = per_sector

        x_impact = L @ shock
        icms_generated = (icms_rates * x_impact).sum()
        iss_generated = (iss_rates * x_impact).sum()
        total_tax = icms_generated + iss_generated
        retorno = total_tax / 1000.0 * 100

        results["por_segmento"][seg_name] = {
            "choque_mi": 1000.0,
            "icms_mi": float(icms_generated),
            "iss_mi": float(iss_generated),
            "total_tax_mi": float(total_tax),
            "retorno_fiscal_pct": float(retorno)
        }

        print(f"{seg_name:<30} {1000:>10,.0f} {icms_generated:>10,.1f} {iss_generated:>10,.1f} {total_tax:>10,.1f} {retorno:>10.1f}%")

    return results


# ============================================================================
# ANÁLISE 5: SIMULAÇÃO DE RENÚNCIA FISCAL
# ============================================================================

def analyze_tax_waiver(data):
    """Se o RJ renuncia R$ 100M de ICMS para o criativo, qual o retorno?"""
    print("\n" + "=" * 70)
    print("SIMULAÇÃO: RETORNO SOBRE RENÚNCIA FISCAL")
    print("=" * 70)

    L = data['L']
    e_coeffs = data['e_coeffs']
    inc_coeffs = data['inc_coeffs']
    icms_rates = data['icms_rates']
    iss_rates = data['iss_rates']
    vab_rj = data['vab_rj']

    renuncia = 100.0  # R$ 100 Mi

    # A renúncia fiscal é redistribuída como choque de demanda no setor criativo
    # (hipótese: 100% da renúncia vira investimento/consumo nos setores criativos)
    shock = np.zeros(N_SECTORS)
    vab_creative = vab_rj[ALL_CREATIVE_INDICES]
    total_vab = vab_creative.sum()

    if total_vab > 0:
        for idx in ALL_CREATIVE_INDICES:
            shock[idx] = renuncia * (vab_rj[idx] / total_vab)
    else:
        for idx in ALL_CREATIVE_INDICES:
            shock[idx] = renuncia / len(ALL_CREATIVE_INDICES)

    x_impact = L @ shock
    total_prod = x_impact.sum()
    total_jobs = (e_coeffs * x_impact).sum()
    total_income = (inc_coeffs * x_impact).sum()
    icms_return = (icms_rates * x_impact).sum()
    iss_return = (iss_rates * x_impact).sum()
    total_tax_return = icms_return + iss_return

    roi_fiscal = total_tax_return / renuncia

    results = {
        "renuncia_mi": float(renuncia),
        "producao_gerada_mi": float(total_prod),
        "multiplicador": float(total_prod / renuncia),
        "empregos_gerados": float(total_jobs),
        "renda_gerada_mi": float(total_income),
        "icms_retornado_mi": float(icms_return),
        "iss_retornado_mi": float(iss_return),
        "total_tax_retornado_mi": float(total_tax_return),
        "roi_fiscal": float(roi_fiscal),
    }

    print(f"\n  Cenario: Renuncia fiscal de R$ {renuncia:,.0f} Mi para a Economia Criativa")
    print(f"  -------------------------------------------------------")
    print(f"  Producao Gerada:               R$ {total_prod:>10,.1f} Mi")
    print(f"  Multiplicador:                  {total_prod / renuncia:>10.2f}x")
    print(f"  Empregos Sustentados:           {total_jobs:>10,.0f}")
    print(f"  Renda Gerada:                   R$ {total_income:>10,.1f} Mi")
    print(f"  -------------------------------------------------------")
    print(f"  ICMS Retornado:                 R$ {icms_return:>10,.1f} Mi")
    print(f"  ISS Retornado:                  R$ {iss_return:>10,.1f} Mi")
    print(f"  Total Tributos Retornados:      R$ {total_tax_return:>10,.1f} Mi")
    print(f"  ROI Fiscal:                     {roi_fiscal:>10.2f}x")

    if roi_fiscal > 1:
        print(f"\n  >> A renuncia SE PAGA: cada R$ 1,00 renunciado retorna R$ {roi_fiscal:.2f} em tributos")
    else:
        print(f"\n  >> A renuncia NAO se paga diretamente, mas gera {total_jobs:.0f} empregos e R$ {total_income:.1f} Mi em renda")

    return results


# ============================================================================
# ANÁLISE 6: MULTIPLICADOR DE EMPREGO (QUANTOS EMPREGOS POR VAGA CRIATIVA)
# ============================================================================

def analyze_employment_multiplier(data):
    """Para cada vaga criada no criativo, quantas são geradas na economia."""
    print("\n" + "=" * 70)
    print("MULTIPLICADOR DE EMPREGO: VAGAS CRIATIVAS → VAGAS TOTAIS")
    print("=" * 70)

    L = data['L']
    e_coeffs = data['e_coeffs']

    results = {"por_segmento": {}}

    print(f"\n{'Segmento':<30} {'Emp.Direto':>12} {'Emp.Total':>12} {'Mult.Emp.':>12}")
    print("-" * 70)

    for seg_name, seg_info in CREATIVE_SEGMENTS.items():
        idx = seg_info["indices"]

        # Choque unitário
        shock = np.zeros(N_SECTORS)
        per_sector = 1000.0 / len(idx)
        for i in idx:
            shock[i] = per_sector

        # Emprego direto (só no setor criativo)
        emp_direto = sum(e_coeffs[i] * shock[i] for i in idx)

        # Emprego total (via Leontief)
        x_impact = L @ shock
        emp_total = (e_coeffs * x_impact).sum()

        mult_emp = emp_total / emp_direto if emp_direto > 0 else 0

        results["por_segmento"][seg_name] = {
            "emprego_direto": float(emp_direto),
            "emprego_total": float(emp_total),
            "multiplicador_emprego": float(mult_emp)
        }

        print(f"{seg_name:<30} {emp_direto:>10,.0f} {emp_total:>10,.0f} {mult_emp:>10.2f}x")

    return results


# ============================================================================
# EXPORTAÇÃO
# ============================================================================

def export_results(all_results):
    """Exporta todos os resultados para JSON e Excel."""
    out_dir = OUTPUT_DIR
    json_path = out_dir / 'estudo_economia_criativa_rj.json'
    excel_path = out_dir / 'estudo_economia_criativa_rj.xlsx'

    # JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Resultados salvos em: {json_path}")

    # Excel — múltiplas abas
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Aba 1: Contexto
        ctx = all_results.get("contexto", {})
        if ctx.get("segmentos"):
            rows = []
            for seg, vals in ctx["segmentos"].items():
                rows.append({"Segmento": seg, **vals})
            pd.DataFrame(rows).to_excel(writer, sheet_name='Contexto', index=False)

        # Aba 2: Multiplicadores
        mult = all_results.get("multiplicadores", {})
        if mult.get("por_segmento"):
            rows = []
            for seg, vals in mult["por_segmento"].items():
                row = {"Segmento": seg}
                row.update({k: v for k, v in vals.items() if not isinstance(v, (dict, list))})
                rows.append(row)
            pd.DataFrame(rows).to_excel(writer, sheet_name='Multiplicadores', index=False)

        # Aba 3: Decomposição
        dec = all_results.get("decomposicao", {})
        if dec.get("top_beneficiados"):
            pd.DataFrame(dec["top_beneficiados"]).to_excel(
                writer, sheet_name='Decomposicao', index=False
            )

        # Aba 4: Fiscal
        fis = all_results.get("fiscal", {})
        if fis.get("por_segmento"):
            rows = [{"Segmento": seg, **vals} for seg, vals in fis["por_segmento"].items()]
            pd.DataFrame(rows).to_excel(writer, sheet_name='Fiscal', index=False)

        # Aba 5: Emprego
        emp = all_results.get("emprego", {})
        if emp.get("por_segmento"):
            rows = [{"Segmento": seg, **vals} for seg, vals in emp["por_segmento"].items()]
            pd.DataFrame(rows).to_excel(writer, sheet_name='Emprego', index=False)

        # Aba 6: Renúncia
        ren = all_results.get("renuncia_fiscal", {})
        if ren:
            pd.DataFrame([ren]).to_excel(writer, sheet_name='Renuncia_Fiscal', index=False)

    print(f"[OK] Excel exportado em: {excel_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    data = load_data()

    all_results = {}

    # Seção 2: Contexto
    all_results["contexto"] = analyze_context(data)

    # Seção 5: Multiplicadores e Encadeamentos
    all_results["multiplicadores"] = analyze_multipliers(data)

    # Decomposição
    all_results["decomposicao"] = analyze_decomposition(data)

    # Impacto Fiscal
    all_results["fiscal"] = analyze_fiscal_impact(data)

    # Multiplicador de Emprego
    all_results["emprego"] = analyze_employment_multiplier(data)

    # Renúncia Fiscal
    all_results["renuncia_fiscal"] = analyze_tax_waiver(data)

    # Exportar
    export_results(all_results)

    print("\n" + "=" * 70)
    print("ESTUDO COMPLETO. Resultados prontos para relatório.")
    print("=" * 70)


if __name__ == "__main__":
    main()
