"""
Configuração para Análise do Setor Audiovisual Brasileiro

Define constantes, caminhos de arquivos e mapeamentos setoriais
para a análise completa do mercado audiovisual (música, vídeo, eventos)
"""

from pathlib import Path
import numpy as np

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"

# Matrizes oficiais
MRIO_PATH = OUTPUT_DIR / "final" / "A_mrio_official_v4.npy"
A_NAS_PATH = OUTPUT_DIR / "intermediary" / "A_nas.npy"
X_NAS_PATH = OUTPUT_DIR / "intermediary" / "X_nas.npy"
VAB_NAS_PATH = OUTPUT_DIR / "intermediary" / "VAB_nacional.npy"

# Coeficientes sociais
EMPLOYMENT_COEFFS_PATH = OUTPUT_DIR / "final" / "emp_coefficients_67x27.npy"
INCOME_COEFFS_PATH = OUTPUT_DIR / "final" / "inc_coefficients_67x27.npy"
HOUSEHOLD_CONSUMPTION_PATH = OUTPUT_DIR / "intermediary" / "household_consumption_shares_67.npy"

# Dados tributários
CONFAZ_PATH = OUTPUT_DIR / "confaz_icms_2024_by_uf.json"
TAX_MATRIX_PATH = OUTPUT_DIR / "intermediary" / "perfectionist_base_2015.json"

# Ordem das UFs
REGION_ORDER_PATH = OUTPUT_DIR / "final" / "region_order_v4.txt"

# =============================================================================
# SETORES AUDIOVISUAIS (Índices 0-based na MIP 67 setores)
# =============================================================================

# Setores CORE do audiovisual (CORRETO: confirmado por debug!)
CORE_AUDIOVISUAL_SECTORS = {
    47: "Edição e edição integrada à impressão",  # Música (editoras)
    48: "Atividades de televisão, rádio, cinema e gravação/edição de som e imagem",  # PRINCIPAL
    64: "Atividades artísticas, criativas e de espetáculos",  # Shows, eventos, teatro
}

# Setores de SUPORTE direto
SUPPORT_AUDIOVISUAL_SECTORS = {
    46: "Alojamento",  # Eventos  
    47: "Alimentação",  # Catering eventos
    42: "Comércio por atacado e varejo",  # Distribuição
    31: "Fabricação de equipamentos de informática, produtos eletrônicos e ópticos",  # Equipamentos
    59: "Outras atividades administrativas e serviços complementares",  # Produção eventos
}

# Setores com TRANSBORDAMENTO significativo
SPILLOVER_SECTORS = {
    49: "Telecomunicações",  # Streaming
    50: "Desenvolvimento de sistemas e outros serviços de informação",  # Plataformas digitais
    43: "Transporte terrestre",  # Logística
    45: "Transporte aéreo",  # Turnês
    63: "Educação privada",  # Escolas de música/cinema
}

# Agregação: todos os setores audiovisuais (core + support)
ALL_AUDIOVISUAL_SECTORS = {**CORE_AUDIOVISUAL_SECTORS, **SUPPORT_AUDIOVISUAL_SECTORS}

# Apenas os índices (para slicing de matrizes)
CORE_INDICES = list(CORE_AUDIOVISUAL_SECTORS.keys())
SUPPORT_INDICES = list(SUPPORT_AUDIOVISUAL_SECTORS.keys())
ALL_INDICES = list(ALL_AUDIOVISUAL_SECTORS.keys())

# =============================================================================
# CNAEs AUDIOVISUAIS (para compatibilização com dados externos)
# =============================================================================

CNAE_AUDIOVISUAL = {
    # Divisão 59 - Cinema, vídeo, TV, gravação de som e edição de música
    "59": {
        "5911-1/01": "Estúdios cinematográficos",
        "5911-1/99": "Produção de vídeos e programas de TV",
        "5912-0/99": "Pós-produção audiovisual",
        "5912-0/02": "Serviços de mixagem sonora",
        "5920-1/00": "Gravação de som e edição de música",
    },
    # Divisão 90 - Atividades artísticas e espetáculos
    "90": {
        "9001-9/01": "Produção teatral",
        "9001-9/02": "Produção musical",
        "9001-9/03": "Produção de espetáculos de dança",
        "9001-9/04": "Produção de espetáculos circenses",
        "9001-9/99": "Outras atividades artísticas",
    },
    # Divisão 82 - Organização de eventos
    "82": {
        "8230-0/01": "Organização de eventos (feiras, congressos, exposições, festas)",
        "8230-0/02": "Casas de festas e eventos",
    },
    # Divisão 77 - Aluguel
    "77": {
        "7729-9/99": "Aluguel de equipamentos para eventos",
    },
    # Divisão 74 - Filmagem
    "74": {
        "7420-0/04": "Filmagem de festas e eventos",
    },
}

# =============================================================================
# REGIÕES (27 UFs)
# =============================================================================

UFS = [
    "RO", "AC", "AM", "RR", "PA", "AP", "TO",  # Norte (7)
    "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA",  # Nordeste (9)
    "MG", "ES", "RJ", "SP",  # Sudeste (4)
    "PR", "SC", "RS",  # Sul (3)
    "MS", "MT", "GO", "DF",  # Centro-Oeste (4)
]

UF_NAMES = {
    "RO": "Rondônia", "AC": "Acre", "AM": "Amazonas", "RR": "Roraima",
    "PA": "Pará", "AP": "Amapá", "TO": "Tocantins",
    "MA": "Maranhão", "PI": "Piauí", "CE": "Ceará", "RN": "Rio Grande do Norte",
    "PB": "Paraíba", "PE": "Pernambuco", "AL": "Alagoas", "SE": "Sergipe", "BA": "Bahia",
    "MG": "Minas Gerais", "ES": "Espírito Santo", "RJ": "Rio de Janeiro", "SP": "São Paulo",
    "PR": "Paraná", "SC": "Santa Catarina", "RS": "Rio Grande do Sul",
    "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "GO": "Goiás", "DF": "Distrito Federal",
}

MACRO_REGIONS = {
    "Norte": ["RO", "AC", "AM", "RR", "PA", "AP", "TO"],
    "Nordeste": ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"],
    "Sudeste": ["MG", "ES", "RJ", "SP"],
    "Sul": ["PR", "SC", "RS"],
    "Centro-Oeste": ["MS", "MT", "GO", "DF"],
}

# =============================================================================
# CONSTANTES
# =============================================================================

N_SECTORS = 67  # Total de setores na MIP
N_REGIONS = 27  # Total de UFs
MRIO_SIZE = N_SECTORS * N_REGIONS  # 1809

# Ano base
YEAR_BASE_MIP = 2015
YEAR_EMPLOYMENT = 2021
YEAR_CONFAZ = 2024

# Inflação acumulada (IPCA) para atualização de valores
# 2015 -> 2021: aproximadamente 34.7%
# 2015 -> 2024: aproximadamente 52.8%
IPCA_2015_2021 = 1.347
IPCA_2015_2024 = 1.528

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_sector_name(idx):
    """Retorna nome do setor dado o índice (0-based)"""
    all_sectors = {**CORE_AUDIOVISUAL_SECTORS, **SUPPORT_AUDIOVISUAL_SECTORS, **SPILLOVER_SECTORS}
    return all_sectors.get(idx, f"Setor {idx}")

def get_mrio_index(uf_idx, sector_idx):
    """
    Converte índices (UF, setor) para índice linear na MRIO
    
    Args:
        uf_idx: índice da UF (0-26)
        sector_idx: índice do setor (0-66)
    
    Returns:
        índice linear na MRIO 1809×1809
    """
    return uf_idx * N_SECTORS + sector_idx

def get_uf_sector_from_mrio(mrio_idx):
    """
    Converte índice linear da MRIO para (UF, setor)
    
    Args:
        mrio_idx: índice linear (0-1808)
    
    Returns:
        tuple: (uf_idx, sector_idx)
    """
    uf_idx = mrio_idx // N_SECTORS
    sector_idx = mrio_idx % N_SECTORS
    return uf_idx, sector_idx

def load_region_order():
    """Carrega ordem das UFs do arquivo"""
    with open(REGION_ORDER_PATH, 'r') as f:
        return [line.strip() for line in f.readlines()]

def get_audiovisual_mrio_indices(uf_idx=None, sector_type='core'):
    """
    Retorna índices do setor audiovisual na MRIO
    
    Args:
        uf_idx: índice da UF (0-26). Se None, retorna para todas UFs
        sector_type: 'core', 'support', 'all', ou 'spillover'
    
    Returns:
        array de índices na MRIO
    """
    if sector_type == 'core':
        sector_indices = CORE_INDICES
    elif sector_type == 'support':
        sector_indices = SUPPORT_INDICES
    elif sector_type == 'all':
        sector_indices = ALL_INDICES
    elif sector_type == 'spillover':
        sector_indices = list(SPILLOVER_SECTORS.keys())
    else:
        raise ValueError(f"Tipo inválido: {sector_type}")
    
    if uf_idx is not None:
        # Apenas uma UF
        return np.array([get_mrio_index(uf_idx, s) for s in sector_indices])
    else:
        # Todas as UFs
        indices = []
        for u in range(N_REGIONS):
            for s in sector_indices:
                indices.append(get_mrio_index(u, s))
        return np.array(indices)

# =============================================================================
# INFORMAÇÕES ADICIONAIS
# =============================================================================

SECTOR_LABELS_67 = [
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
    "Serviços de arquitetura, engenharia, testes/análises técnicas e P & D",
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

if __name__ == "__main__":
    # Teste das funções
    print("=== CONFIGURAÇÃO ANÁLISE AUDIOVISUAL ===\n")
    print(f"Setores CORE: {len(CORE_INDICES)}")
    for idx in CORE_INDICES:
        print(f"  [{idx}] {SECTOR_LABELS_67[idx]}")
    
    print(f"\nSetores SUPORTE: {len(SUPPORT_INDICES)}")
    for idx in SUPPORT_INDICES:
        print(f"  [{idx}] {SECTOR_LABELS_67[idx]}")
    
    print(f"\nTotal UFs: {N_REGIONS}")
    print(f"Total setores: {N_SECTORS}")
    print(f"MRIO size: {MRIO_SIZE}")
    
    # Teste de conversão de índices
    print("\n=== TESTE CONVERSÃO ÍNDICES ===")
    uf_idx = 18  # RJ
    sector_idx = 50  # TV, rádio, cinema
    mrio_idx = get_mrio_index(uf_idx, sector_idx)
    print(f"UF={UFS[uf_idx]}, Setor={sector_idx} -> MRIO index={mrio_idx}")
    
    uf_back, sec_back = get_uf_sector_from_mrio(mrio_idx)
    print(f"MRIO index={mrio_idx} -> UF={UFS[uf_back]}, Setor={sec_back}")
