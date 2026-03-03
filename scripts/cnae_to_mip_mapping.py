"""
COMPLETE CNAE to MIP Mapping for Regional ICMS Distribution

This module provides the complete mapping between:
- 87 CNAE 2.0 Divisions (from CONFAZ 2024)
- 67 MIP 2015 Product Sectors (IBGE Input-Output Matrix)

Based on:
- CONFAZ 2026.01.08.xls (ICMS data)
- MIP 2015 Tabela 05.csv (Product classification)

Mapping completed: 2024-01-24
"""

import json
import numpy as np

# Mapping of MIP codes to sector numbers (from Tabela 05.csv headers)
# Used for reference in documentation
MIP_SECTORS_REFERENCE = {
    1: ("0191", "Agricultura, inclusive apoio à agricultura e pós-colheita"),
    2: ("0192", "Pecuária, inclusive apoio à pecuária"),
    3: ("0280", "Produção florestal; pesca e aquicultura"),
    4: ("0580", "Extração de carvão mineral e de minerais não-metálicos"),
    5: ("0680", "Extração de petróleo e gás, inclusive atividades de apoio"),
    6: ("0791", "Extração de minério de ferro, inclusive beneficiamentos"),
    7: ("0792", "Extração de minerais metálicos não ferrosos"),
    8: ("1091", "Abate e produtos de carne, laticínio e pesca"),
    9: ("1092", "Fabricação e refino de açúcar"),
    10: ("1093", "Outros produtos alimentares"),
    11: ("1100", "Fabricação de bebidas"),
    12: ("1200", "Fabricação de produtos do fumo"),
    13: ("1300", "Fabricação de produtos têxteis"),
    14: ("1400", "Confecção de artefatos do vestuário e acessórios"),
    15: ("1500", "Fabricação de calçados e artefatos de couro"),
    16: ("1600", "Fabricação de produtos da madeira"),
    17: ("1700", "Fabricação de celulose, papel e produtos de papel"),
    18: ("1800", "Impressão e reprodução de gravações"),
    19: ("1991", "Refino de petróleo e coquerias"),
    20: ("1992", "Fabricação de biocombustíveis"),
    21: ("2091", "Fabricação de químicos orgânicos e inorgânicos, resinas"),
    22: ("2092", "Fabricação de defensivos, desinfestantes, tintas"),
    23: ("2093", "Fabricação de produtos de limpeza, cosméticos"),
    24: ("2100", "Fabricação de produtos farmoquímicos e farmacêuticos"),
    25: ("2200", "Fabricação de produtos de borracha e material plástico"),
    26: ("2300", "Fabricação de produtos de minerais não metálicos"),
    27: ("2491", "Produção de ferro gusa, siderurgia, tubos de aço"),
    28: ("2492", "Metalurgia de metais não ferrosos e fundição"),
    29: ("2500", "Fabricação de produtos de metal, exceto máquinas"),
    30: ("2600", "Fabricação de equipamentos de informática, eletrônicos"),
    31: ("2700", "Fabricação de máquinas e equipamentos elétricos"),
    32: ("2800", "Fabricação de máquinas e equipamentos mecânicos"),
    33: ("2991", "Fabricação de automóveis, caminhões e ônibus"),
    34: ("2992", "Fabricação de peças para veículos automotores"),
    35: ("3000", "Fabricação de outros equipamentos de transporte"),
    36: ("3180", "Fabricação de móveis e produtos diversos"),
    37: ("3300", "Manutenção, reparação e instalação de máquinas"),
    38: ("3500", "Energia elétrica, gás natural e outras utilidades"),
    39: ("3680", "Água, esgoto e gestão de resíduos"),
    40: ("4180", "Construção"),
    41: ("4580", "Comércio por atacado e varejo"),
    42: ("4900", "Transporte terrestre"),
    43: ("5000", "Transporte aquaviário"),
    44: ("5100", "Transporte aéreo"),
    45: ("5280", "Armazenamento, auxiliares dos transportes e correio"),
    46: ("5500", "Alojamento"),
    47: ("5600", "Alimentação"),
    48: ("5800", "Edição e edição integrada à impressão"),
    49: ("5980", "Atividades de televisão, rádio, cinema e gravação"),
    50: ("6100", "Telecomunicações"),
    51: ("6280", "Desenvolvimento de sistemas e serviços de informação"),
    52: ("6480", "Intermediação financeira, seguros e previdência"),
    53: ("6800", "Atividades imobiliárias"),
    54: ("6980", "Atividades jurídicas, contábeis, consultoria"),
    55: ("7180", "Serviços de arquitetura, engenharia, P&D"),
    56: ("7380", "Outras atividades profissionais, científicas"),
    57: ("7700", "Aluguéis não imobiliários e gestão de ativos"),
    58: ("7880", "Outras atividades administrativas e serviços"),
    59: ("8000", "Atividades de vigilância, segurança e investigação"),
    60: ("8400", "Administração pública, defesa e seguridade social"),
    61: ("8591", "Educação pública"),
    62: ("8592", "Educação privada"),
    63: ("8691", "Saúde pública"),
    64: ("8692", "Saúde privada"),
    65: ("9080", "Atividades artísticas, criativas e espetáculos"),
    66: ("9480", "Organizações associativas e outros serviços pessoais"),
    67: ("9700", "Serviços domésticos"),
}

# Complete CNAE to MIP mapping
CNAE_TO_MIP_MAPPING = {
    
    # AGRICULTURA E PECUÁRIA
    1: {"mip": [1, 2], "type": "1:N", "dist": "vab", "note": "Agricultura + Pecuária"},
    2: {"mip": [3], "type": "1:1", "dist": "direct", "note": "Produção florestal"},
    3: {"mip": [3], "type": "1:1", "dist": "direct", "note": "Pesca (mesmo setor que florestal no MIP)"},
    
    # INDÚSTRIAS EXTRATIVAST
    5: {"mip": [4], "type": "1:1", "dist": "direct", "note": "Carvão mineral"},
    6: {"mip": [5], "type": "1:1", "dist": "direct", "note": "Petróleo e gás"},
    7: {"mip": [6, 7], "type": "1:N", "dist": "vab", "note": "Minério ferro + não-ferrosos"},
    8: {"mip": [4], "type": "1:1", "dist": "direct", "note": "Minerais não-metálicos (mesmo setor que carvão)"},
    9: {"mip": [5], "type": "1:1", "dist": "direct", "note": "Apoio à extração (integrado ao setor 5)"},
    
    # ALIMENTOS E BEBIDAS
    10: {"mip": [8, 9, 10], "type": "1:N", "dist": "vab", "note": "Produtos alimentícios diversos"},
    11: {"mip": [11], "type": "1:1", "dist": "direct", "note": "Bebidas"},
    12: {"mip": [12], "type": "1:1", "dist": "direct", "note": "Produtos do fumo"},
    
    # TÊXTIL E VESTUÁRIO
    13: {"mip": [13], "type": "1:1", "dist": "direct", "note": "Têxteis"},
    14: {"mip": [14], "type": "1:1", "dist": "direct", "note": "Vestuário"},
    15: {"mip": [15], "type": "1:1", "dist": "direct", "note": "Calçados e couro"},
    
    # MADEIRA E PAPEL
    16: {"mip": [16], "type": "1:1", "dist": "direct", "note": "Produtos de madeira"},
    17: {"mip": [17], "type": "1:1", "dist": "direct", "note": "Celulose e papel"},
    18: {"mip": [18], "type": "1:1", "dist": "direct", "note": "Impressão"},
    
    # DERIVADOS DE PETRÓLEO E QUÍMICOS
    19: {"mip": [19, 20], "type": "1:N", "dist": "vab", "note": "Refino petróleo + biocombustíveis"},
    20: {"mip": [21, 22, 23], "type": "1:N", "dist": "vab", "note": "Químicos diversos incluindo defensivos e cosméticos"},
    21: {"mip": [24], "type": "1:1", "dist": "direct", "note": "Farmacêuticos"},
    22: {"mip": [25], "type": "1:1", "dist": "direct", "note": "Borracha e plástico"},
    23: {"mip": [26], "type": "1:1", "dist": "direct", "note": "Minerais não-metálicos processados"},
    
    # METALURGIA E METAL-MECÂNICA
    24: {"mip": [27, 28], "type": "1:N", "dist": "vab", "note": "Siderurgia + metalurgia não-ferrosos"},
    25: {"mip": [29], "type": "1:1", "dist": "direct", "note": "Produtos de metal"},
    26: {"mip": [30], "type": "1:1", "dist": "direct", "note": "Equipamentos informática e eletrônicos"},
    27: {"mip": [31], "type": "1:1", "dist": "direct", "note": "Máquinas elétricas"},
    28: {"mip": [32], "type": "1:1", "dist": "direct", "note": "Máquinas mecânicas"},
    29: {"mip": [33, 34], "type": "1:N", "dist": "vab", "note": "Veículos + peças"},
    30: {"mip": [35], "type": "1:1", "dist": "direct", "note": "Outros equipamentos transporte"},
    31: {"mip": [36], "type": "1:1", "dist": "direct", "note": "Móveis"},
    32: {"mip": [36], "type": "1:1", "dist": "direct", "note": "Produtos diversos (mesmo setor móveis)"},
    33: {"mip": [37], "type": "1:1", "dist": "direct", "note": "Manutenção e reparação"},
    
    # UTILIDADES
    35: {"mip": [38], "type": "1:1", "dist": "direct", "note": "Energia elétrica e gás"},
    36: {"mip": [39], "type": "1:1", "dist": "direct", "note": "Água"},
    37: {"mip": [39], "type": "1:1", "dist": "direct", "note": "Esgoto (mesmo setor água)"},
    38: {"mip": [39], "type": "1:1", "dist": "direct", "note": "Resíduos (mesmo setor água)"},
    39: {"mip": [39], "type": "1:1", "dist": "direct", "note": "Descontaminação (mesmo setor água)"},
    
    # CONSTRUÇÃO
    41: {"mip": [40], "type": "1:1", "dist": "direct", "note": "Edificações"},
    42: {"mip": [40], "type": "1:1", "dist": "direct", "note": "Infraestrutura (mesmo setor)"},
    43: {"mip": [40], "type": "1:1", "dist": "direct", "note": "Serviços especializados construção"},
    
    # COMÉRCIO
    45: {"mip": [41], "type": "1:1", "dist": "direct", "note": "Comércio veículos"},
    46: {"mip": [41], "type": "1:1", "dist": "direct", "note": "Comércio atacado"},
    47: {"mip": [41], "type": "1:1", "dist": "direct", "note": "Comércio varejo"},
    
    # TRANSPORTE
    49: {"mip": [42], "type": "1:1", "dist": "direct", "note": "Transporte terrestre"},
    50: {"mip": [43], "type": "1:1", "dist": "direct", "note": "Transporte aquaviário"},
    51: {"mip": [44], "type": "1:1", "dist": "direct", "note": "Transporte aéreo"},
    52: {"mip": [45], "type": "1:1", "dist": "direct", "note": "Armazenamento e auxiliares"},
    53: {"mip": [45], "type": "1:1", "dist": "direct", "note": "Correio (mesmo setor)"},
    
    # ALOJAMENTO E ALIMENTAÇÃO
    55: {"mip": [46], "type": "1:1", "dist": "direct", "note": "Alojamento"},
    56: {"mip": [47], "type": "1:1", "dist": "direct", "note": "Alimentação"},
    
    # INFORMAÇÃO E COMUNICAÇÃO
    58: {"mip": [48], "type": "1:1", "dist": "direct", "note": "Edição"},
    59: {"mip": [49], "type": "1:1", "dist": "direct", "note": "Cinema, TV, gravação"},
    60: {"mip": [49], "type": "1:1", "dist": "direct", "note": "Rádio e TV (mesmo setor)"},
    61: {"mip": [50], "type": "1:1", "dist": "direct", "note": "Telecomunicações"},
    62: {"mip": [51], "type": "1:1", "dist": "direct", "note": "TI"},
    63: {"mip": [51], "type": "1:1", "dist": "direct", "note": "Serviços de informação (mesmo setor)"},
    
    # ATIVIDADES FINANCEIRAS
    64: {"mip": [52], "type": "1:1", "dist": "direct", "note": "Serviços financeiros"},
    65: {"mip": [52], "type": "1:1", "dist": "direct", "note": "Seguros (mesmo setor)"},
    66: {"mip": [52], "type": "1:1", "dist": "direct", "note": "Auxiliares financeiros (mesmo setor)"},
    
    # ATIVIDADES IMOBILIÁRIAS
    68: {"mip": [53], "type": "1:1", "dist": "direct", "note": "Atividades imobiliárias"},
    
    # ATIVIDADES PROFISSIONAIS
    69: {"mip": [54], "type": "1:1", "dist": "direct", "note": "Jurídicas e contábeis"},
    70: {"mip": [54], "type": "1:1", "dist": "direct", "note": "Consultoria (mesmo setor)"},
    71: {"mip": [55], "type": "1:1", "dist": "direct", "note": "Arquitetura, engenharia, P&D"},
    72: {"mip": [55], "type": "1:1", "dist": "direct", "note": "Pesquisa científica (mesmo setor)"},
    73: {"mip": [56], "type": "1:1", "dist": "direct", "note": "Publicidade"},
    74: {"mip": [56], "type": "1:1", "dist": "direct", "note": "Outras atividades profissionais"},
    75: {"mip": [56], "type": "1:1", "dist": "direct", "note": "Veterinária (mesmo setor)"},
    
    # ATIVIDADES ADMINISTRATIVAS  
    77: {"mip": [57], "type": "1:1", "dist": "direct", "note": "Aluguéis não-imobiliários"},
    78: {"mip": [58], "type": "1:1", "dist": "direct", "note": "Seleção de mão-de-obra"},
    79: {"mip": [58], "type": "1:1", "dist": "direct", "note": "Agências de viagem"},
    80: {"mip": [59], "type": "1:1", "dist": "direct", "note": "Vigilância e segurança"},
    81: {"mip": [58], "type": "1:1", "dist": "direct", "note": "Serviços para edifícios"},
    82: {"mip": [58], "type": "1:1", "dist": "direct", "note": "Serviços de escritório"},
    
    # ADMINISTRAÇÃO PÚBLICA E SERVIÇOS SOCIAIS
    84: {"mip": [60], "type": "1:1", "dist": "direct", "note": "Administração pública"},
    85: {"mip": [61, 62], "type": "1:N", "dist": "vab", "note": "Educação (dividir público/privado por VAB)"},
    86: {"mip": [63, 64], "type": "1:N", "dist": "vab", "note": "Saúde (dividir público/privado por VAB)"},
    87: {"mip": [63, 64], "type": "1:N", "dist": "vab", "note": "Saúde integrada (mesmo tratamento)"},
    88: {"mip": [64], "type": "1:1", "dist": "direct", "note": "Assistência social (alocar privado)"},
    
    # ARTES E OUTROS SERVIÇOS
    90: {"mip": [65], "type": "1:1", "dist": "direct", "note": "Atividades artísticas"},
    91: {"mip": [65], "type": "1:1", "dist": "direct", "note": "Patrimônio cultural (mesmo setor)"},
    92: {"mip": [65], "type": "1:1", "dist": "direct", "note": "Jogos de azar (mesmo setor)"},
    93: {"mip": [65], "type": "1:1", "dist": "direct", "note": "Atividades esportivas"},
    94: {"mip": [66], "type": "1:1", "dist": "direct", "note": "Organizações associativas"},
    95: {"mip": [37], "type": "1:1", "dist": "direct", "note": "Reparação (mesmo setor manutenção)"},
    96: {"mip": [66], "type": "1:1", "dist": "direct", "note": "Outros serviços pessoais"},
    97: {"mip": [67], "type": "1:1", "dist": "direct", "note": "Serviços domésticos"},
    99: {"mip": [60], "type": "1:1", "dist": "direct", "note": "Organismos internacionais (admin pública)"},
}

def get_mip_sectors(cnae_div):
    """Get MIP sectors for CNAE division"""
    return CNAE_TO_MIP_MAPPING.get(cnae_div, {}).get("mip", [])

def distribute_icms(cnae_div, icms_value, vab_nacional=None):
    """
    Distribute ICMS from CNAE to MIP sectors
    
    Args:
        cnae_div: CNAE division number
        icms_value: ICMS value in millions
        vab_nacional: dict {mip_sector: vab_value} for weighting
        
    Returns:
        dict {mip_sector: icms_value}
    """
    mapping = CNAE_TO_MIP_MAPPING.get(cnae_div)
    if not mapping:
        return {}
    
    mip_sectors = mapping["mip"]
    dist_type = mapping["dist"]
    
    if dist_type == "direct":
        return {mip_sectors[0]: icms_value}
    
    elif dist_type == "vab":
        if vab_nacional:
            total_vab = sum(vab_nacional.get(s, 0) for s in mip_sectors)
            if total_vab > 0:
                return {s: icms_value * vab_nacional.get(s, 0)/total_vab for s in mip_sectors}
        # Fallback: uniform
        n = len(mip_sectors)
        return {s: icms_value/n for s in mip_sectors}
    
    return {}

def validate():
    """Validate mapping completeness"""
    print("="*70)
    print("VALIDACAO DO MAPEAMENTO CNAE -> MIP")
    print("="*70)
    
    # Load CNAE list
    with open('output/cnae_divisions_confaz.json', 'r', encoding='utf-8') as f:
        cnae_data = json.load(f)
    
    all_cnae = sorted(cnae_data['divisions'].keys(), key=int)
    mapped_cnae = sorted(CNAE_TO_MIP_MAPPING.keys())
    
    # Coverage
    print(f"\n[1/3] Cobertura CNAE:")
    print(f"  Total CNAE no CONFAZ: {len(all_cnae)}")
    print(f"  CNAE mapeados: {len(mapped_cnae)}")
    
    unmapped = [c for c in all_cnae if int(c) not in mapped_cnae]
    if unmapped:
        print(f"  CNAE não mapeados: {unmapped}")
    else:
        print(f"  [OK] Todos os CNAE mapeados!")
    
    # MIP coverage
    all_mip_covered = set()
    for m in CNAE_TO_MIP_MAPPING.values():
        all_mip_covered.update(m["mip"])
    
    print(f"\n[2/3] Cobertura MIP:")
    print(f"  Total setores MIP: 67")
    print(f"  Setores cobertos: {len(all_mip_covered)}")
    
    uncovered_mip = set(range(1, 68)) - all_mip_covered
    if uncovered_mip:
        print(f"  MIP não cobertos: {sorted(uncovered_mip)}")
    else:
        print(f"  [OK] Todos os setores MIP cobertos!")
    
    # Stats
    direct = sum(1 for m in CNAE_TO_MIP_MAPPING.values() if m["dist"] == "direct")
    vab_dist = sum(1 for m in CNAE_TO_MIP_MAPPING.values() if m["dist"] == "vab")
    
    print(f"\n[3/3] Estatísticas:")
    print(f"  Mapeamentos 1:1 (direto): {direct}")
    print(f"  Mapeamentos 1:N (distribuir por VAB): {vab_dist}")
    print(f"  Total: {direct + vab_dist}")
    
    print(f"\n{'='*70}\n")
    
    return len(unmapped) == 0 and len(uncovered_mip) == 0

if __name__ == "__main__":
    validate()
