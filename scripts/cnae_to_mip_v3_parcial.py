"""
CNAE to MIP Mapping V3 PARCIAL - ICMS em Produtos

Foca apenas nos setores onde ICMS realmente incide:
- Agricultura e extração
- Indústria de transformação  
- Energia e telecomunicações
- Comércio (distribui o ICMS embutido nas mercadorias)

Serviços puros (ISS, não ICMS) distribuem por VAB genérico
"""

import json
import numpy as np

# Mapeamento focado em setores com ICMS real
CNAE_TO_MIP_V3_PARCIAL = {
    
    # ========================================================================
    # SETORES COM ICMS DIRETO
    # ========================================================================
    
    # AGRICULTURA E PECUÁRIA (produtos primários)
    1: {"mip": list(range(2, 15)), "dist": "vab", "note": "Agricultura e pecuária completa"},
    2: {"mip": [15], "dist": "direct", "note": "Produção florestal"},
    3: {"mip": [16], "dist": "direct", "note": "Pesca e aquicultura"},
    
    # EXTRAÇÃO
    5: {"mip": [17], "dist": "direct", "note": "Carvão mineral"},
    6: {"mip": [19], "dist": "direct", "note": "Petróleo e gás"},
    7: {"mip": [20, 21], "dist": "vab", "note": "Minerais metálicos"},
    8: {"mip": [18], "dist": "direct", "note": "Minerais não-metálicos"},
    9: {"mip": [19], "dist": "direct", "note": "Apoio à extração"},
    
    # INDÚSTRIA DE ALIMENTOS
    10: {"mip": list(range(22, 36)), "dist": "vab", "note": "Produtos alimentícios"},
    11: {"mip": [36], "dist": "direct", "note": "Bebidas"},
    12: {"mip": [37], "dist": "direct", "note": "Fumo"},
    
    # TÊXTIL E VESTUÁRIO
    13: {"mip": [38, 39, 40], "dist": "vab", "note": "Produtos têxteis"},
    14: {"mip": [41], "dist": "direct", "note": "Vestuário"},
    15: {"mip": [42], "dist": "direct", "note": "Couro e calçados"},
    
    # MADEIRA E PAPEL
    16: {"mip": [43], "dist": "direct", "note": "Produtos de madeira"},
    17: {"mip": [44, 45], "dist": "vab", "note": "Celulose e papel"},
    18: {"mip": [46], "dist": "direct", "note": "Impressão"},
    
    # REFINO E QUÍMICOS
    19: {"mip": list(range(47, 54)), "dist": "vab", "note": "Derivados de petróleo e biocombustíveis"},
    20: {"mip": [54, 55, 56, 57, 58, 59, 60], "dist": "vab", "note": "Produtos químicos"},
    21: {"mip": [62], "dist": "direct", "note": "Farmacêuticos"},
    22: {"mip": [63, 64], "dist": "vab", "note": "Borracha e plástico"},
    23: {"mip": [65, 66, 67], "dist": "vab", "note": "Produtos de minerais não-metálicos"},
    
    # ========================================================================
    # SETORES COM ICMS LIMITADO OU INDIRETO
    # ========================================================================
    
    # METALURGIA - Não tem produto MIP específico, mas tem ICMS
    # Vamos distribuir entre produtos metálicos existentes
    24: {"mip": [63, 64], "dist": "vab", "note": "Metalurgia (proxy: borracha/plástico)"},
    25: {"mip": [63, 64], "dist": "vab", "note": "Produtos de metal"},
    26: {"mip": [64], "dist": "direct", "note": "Equipamentos informática"},
    27: {"mip": [64], "dist": "direct", "note": "Máquinas elétricas"},
    28: {"mip": [64], "dist": "direct", "note": "Máquinas mecânicas"},
    29: {"mip": [64], "dist": "direct", "note": "Veículos (proxy)"},
    30: {"mip": [64], "dist": "direct", "note": "Outros transportes"},
    31: {"mip": [43], "dist": "direct", "note": "Móveis"},
    32: {"mip": [64], "dist": "direct", "note": "Produtos diversos"},
    33: {"mip": [46], "dist": "direct", "note": "Manutenção"},
    
    # UTILIDADES (Energia e água - têm ICMS)
    35: {"mip": list(range(2, 68)), "dist": "vab", "note": "Energia elétrica (distribui por consumo)"},
    36: {"mip": list(range(2, 68)), "dist": "vab", "note": "Água (distribui por consumo)"},
    37: {"mip": list(range(2, 68)), "dist": "vab", "note": "Esgoto"},
    38: {"mip": list(range(2, 68)), "dist": "vab", "note": "Resíduos"},
    39: {"mip": list(range(2, 68)), "dist": "vab", "note": "Descontaminação"},
    
    # CONSTRUÇÃO (tem ICMS sobre materiais)
    41: {"mip": [43, 65, 66, 67], "dist": "vab", "note": "Construção (ICMS dos materiais)"},
    42: {"mip": [43, 65, 66, 67], "dist": "vab", "note": "Obras"},
    43: {"mip": [43, 65, 66, 67], "dist": "vab", "note": "Serviços construção"},
    
    # COMÉRCIO (distribui ICMS embutido nas mercadorias)
    45: {"mip": list(range(2, 68)), "dist": "vab", "note": "Comércio veículos"},
    46: {"mip": list(range(2, 68)), "dist": "vab", "note": "Comércio atacado"},
    47: {"mip": list(range(2, 68)), "dist": "vab", "note": "Comércio varejo"},
    
    # TRANSPORTE (pequeno ICMS, mais ISS)
    49: {"mip": list(range(47, 54)), "dist": "vab", "note": "Transporte terrestre (ICMS combustível)"},
    50: {"mip": list(range(47, 54)), "dist": "vab", "note": "Transporte aquaviário"},
    51: {"mip": list(range(47, 54)), "dist": "vab", "note": "Transporte aéreo"},
    52: {"mip": list(range(2, 68)), "dist": "vab", "note": "Armazenamento"},
    53: {"mip": list(range(2, 68)), "dist": "vab", "note": "Correio"},
    
    # ALOJAMENTO E ALIMENTAÇÃO
    55: {"mip": [35], "dist": "direct", "note": "Alojamento (ICMS de produtos usados)"},
    56: {"mip": list(range(22, 36)), "dist": "vab", "note": "Alimentação (ICMS dos alimentos)"},
    
    # INFORMAÇÃO E COMUNICAÇÃO
    58: {"mip": [46], "dist": "direct", "note": "Edição"},
    59: {"mip": [46], "dist": "direct", "note": "Cinema/TV"},
    60: {"mip": [46], "dist": "direct", "note": "Rádio/TV"},
    61: {"mip": list(range(2, 68)), "dist": "vab", "note": "Telecomunicações (tem ICMS!)"},
    62: {"mip": list(range(2, 68)), "dist": "vab", "note": "TI"},
    63: {"mip": list(range(2, 68)), "dist": "vab", "note": "Serviços informação"},
    
    # ========================================================================
    # SERVIÇOS PUROS (ISS, praticamente sem ICMS)
    # Distribuir genericamente por VAB
    # ========================================================================
    64: {"mip": list(range(2, 68)), "dist": "vab", "note": "Serviços financeiros (ISS)"},
    65: {"mip": list(range(2, 68)), "dist": "vab", "note": "Seguros (ISS)"},
    66: {"mip": list(range(2, 68)), "dist": "vab", "note": "Auxiliares financeiros (ISS)"},
    68: {"mip": list(range(2, 68)), "dist": "vab", "note": "Imobiliárias (ISS)"},
    69: {"mip": list(range(2, 68)), "dist": "vab", "note": "Jurídicas (ISS)"},
    70: {"mip": list(range(2, 68)), "dist": "vab", "note": "Consultoria (ISS)"},
    71: {"mip": list(range(2, 68)), "dist": "vab", "note": "Engenharia (ISS)"},
    72: {"mip": list(range(2, 68)), "dist": "vab", "note": "P&D (ISS)"},
    73: {"mip": list(range(2, 68)), "dist": "vab", "note": "Publicidade (ISS)"},
    74: {"mip": list(range(2, 68)), "dist": "vab", "note": "Profissionais (ISS)"},
    75: {"mip": list(range(2, 68)), "dist": "vab", "note": "Veterinária (ISS)"},
    77: {"mip": list(range(2, 68)), "dist": "vab", "note": "Aluguéis (ISS)"},
    78: {"mip": list(range(2, 68)), "dist": "vab", "note": "Seleção mão-de-obra (ISS)"},
    79: {"mip": list(range(2, 68)), "dist": "vab", "note": "Agências viagem (ISS)"},
    80: {"mip": list(range(2, 68)), "dist": "vab", "note": "Vigilância (ISS)"},
    81: {"mip": list(range(2, 68)), "dist": "vab", "note": "Serviços edifícios (ISS)"},
    82: {"mip": list(range(2, 68)), "dist": "vab", "note": "Serviços escritório (ISS)"},
    84: {"mip": list(range(2, 68)), "dist": "vab", "note": "Admin pública"},
    85: {"mip": list(range(2, 68)), "dist": "vab", "note": "Educação"},
    86: {"mip": list(range(2, 68)), "dist": "vab", "note": "Saúde"},
    87: {"mip": list(range(2, 68)), "dist": "vab", "note": "Saúde integrada"},
    88: {"mip": list(range(2, 68)), "dist": "vab", "note": "Assistência social"},
    90: {"mip": list(range(2, 68)), "dist": "vab", "note": "Artes"},
    91: {"mip": list(range(2, 68)), "dist": "vab", "note": "Patrimônio cultural"},
    92: {"mip": list(range(2, 68)), "dist": "vab", "note": "Jogos"},
    93: {"mip": list(range(2, 68)), "dist": "vab", "note": "Esportes"},
    94: {"mip": list(range(2, 68)), "dist": "vab", "note": "Organizações"},
    95: {"mip": list(range(2, 68)), "dist": "vab", "note": "Reparação"},
    96: {"mip": list(range(2, 68)), "dist": "vab", "note": "Serviços pessoais"},
    97: {"mip": list(range(2, 68)), "dist": "vab", "note": "Serviços domésticos"},
    99: {"mip": list(range(2, 68)), "dist": "vab", "note": "Organismos internacionais"},
}

def distribute_icms_v3(cnae_div, icms_value, vab_nacional=None):
    """
    Distribute ICMS using V3 partial mapping
    """
    mapping = CNAE_TO_MIP_V3_PARCIAL.get(cnae_div)
    if not mapping:
        # Se não mapeado, distribui uniformemente por todos produtos
        return {s: icms_value/66 for s in range(2, 68)}
    
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

print("CNAE->MIP V3 Parcial loaded")
print(f"Mapped divisions: {len(CNAE_TO_MIP_V3_PARCIAL)}")
