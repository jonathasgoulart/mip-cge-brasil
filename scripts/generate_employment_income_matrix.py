"""
Matriz Oficial de Emprego e Renda: 67 setores x 27 UFs
=======================================================
Fonte: PNAD Continua 2021 - 4o trimestre
Mapeamento: Codigo CNAE PNAD (223 codigos) -> MIP 67 setores (0-indexed)

Cada codigo PNAD e mapeado individualmente para o setor MIP correto,
sem perda de desagregacao.

Output (em output/final/):
  - employment_matrix_67x27.npy        (67, 27)  PO por setor x UF
  - income_matrix_67x27.npy            (67, 27)  Renda anual R$ Mi por setor x UF
  - emp_coefficients_67x27.npy         (67, 27)  PO / VAB
  - inc_coefficients_67x27.npy         (67, 27)  Renda / VAB
  - employment_income_67x27_summary.xlsx          Resumo legivel
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
FINAL_DIR = OUTPUT_DIR / 'final'
DATA_DIR = BASE_DIR / 'data'

N_SECTORS = 67
N_REGIONS = 27
FATOR_ANUALIZACAO = 13.3  # 12 meses + 13o + ferias

UF_ORDER = [
    'RO', 'AC', 'AM', 'RR', 'PA', 'AP', 'TO',
    'MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA',
    'MG', 'ES', 'RJ', 'SP',
    'PR', 'SC', 'RS',
    'MS', 'MT', 'GO', 'DF',
]

IBGE_TO_UF = {
    11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO',
    21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB', 26: 'PE', 27: 'AL',
    28: 'SE', 29: 'BA',
    31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP',
    41: 'PR', 42: 'SC', 43: 'RS',
    50: 'MS', 51: 'MT', 52: 'GO', 53: 'DF',
}

SECTOR_LABELS = [
    "Agricultura",                       # 0
    "Pecuaria",                          # 1
    "Florestal/Pesca/Aquicultura",       # 2
    "Carvao/Min.NMetalicos",             # 3
    "Petroleo e Gas",                    # 4
    "Min.Ferro",                         # 5
    "Min.Met.NFerrosos",                 # 6
    "Carne/Laticinio/Pesca",             # 7
    "Acucar",                            # 8
    "Outros Alimentares",                # 9
    "Bebidas",                           # 10
    "Fumo",                              # 11
    "Texteis",                           # 12
    "Vestuario",                         # 13
    "Calcados/Couro",                    # 14
    "Madeira",                           # 15
    "Celulose/Papel",                    # 16
    "Impressao/Gravacoes",               # 17
    "Refino Petroleo/Coque",             # 18
    "Biocombustiveis",                   # 19
    "Quim.Org/Inorg/Resinas",            # 20
    "Defensivos/Tintas/Quim.Div",        # 21
    "Limpeza/Cosmeticos",                # 22
    "Farmoquimicos/Farmaceuticos",       # 23
    "Borracha/Plastico",                 # 24
    "Min.NMetalicos",                    # 25
    "Siderurgia/Ferro-gusa",             # 26
    "Met.NFerrosos/Fundicao",            # 27
    "Prod.Metal",                        # 28
    "Inform/Eletronicos/Opticos",        # 29
    "Maq.Eletricas",                     # 30
    "Maq.Mecanicas",                     # 31
    "Automoveis/Caminhoes/Onibus",       # 32
    "Pecas Veiculos",                    # 33
    "Outros Eq.Transporte",              # 34
    "Moveis/Diversos",                   # 35
    "Manut./Reparacao/Inst.Maq",         # 36
    "Eletricidade/Gas",                  # 37
    "Agua/Esgoto/Residuos",              # 38
    "Construcao",                        # 39
    "Comercio",                          # 40
    "Transp.Terrestre",                  # 41
    "Transp.Aquaviario",                 # 42
    "Transp.Aereo",                      # 43
    "Armaz./Correio",                    # 44
    "Alojamento",                        # 45
    "Alimentacao",                       # 46
    "Edicao",                            # 47
    "TV/Radio/Cinema/Som",               # 48
    "Telecomunicacoes",                  # 49
    "TI/Sistemas/Info",                  # 50
    "Financeiro/Seguros",                # 51
    "Imobiliario",                       # 52
    "Juridico/Contabil/Consult",         # 53
    "Arquitetura/Eng/P&D",               # 54
    "Outras Prof/Cientif",               # 55
    "Alugueis/Prop.Intelectual",         # 56
    "Admin/Serv.Complementares",         # 57
    "Vigilancia/Seguranca",              # 58
    "Admin.Publica",                     # 59
    "Educ.Publica",                      # 60
    "Educ.Privada",                      # 61
    "Saude.Publica",                     # 62
    "Saude.Privada",                     # 63
    "Artes/Cultura/Esportes",            # 64
    "Assoc./Serv.Pessoais",              # 65
    "Domesticos",                        # 66
]

# =========================================================================
# MAPEAMENTO COMPLETO: CNAE PNAD (223 codigos) -> MIP 67 (0-indexed)
# =========================================================================
# Cada codigo PNAD e mapeado individualmente.
# Fonte: Tabela IBGE "Atividades SCN nivel 67 x CNAE 2.0"

CNAE_TO_MIP = {
    # === MIP 0: Agricultura, inclusive apoio a agricultura e pos-colheita ===
    1101: 0,   # Cultivo de arroz
    1102: 0,   # Cultivo de milho
    1103: 0,   # Cultivo de algodao herbaceo
    1104: 0,   # Cultivo de algodao
    1105: 0,   # Cultivo de cana-de-acucar
    1106: 0,   # Cultivo de fumo (cultivo, nao industrializacao)
    1107: 0,   # Cultivo de soja
    1108: 0,   # Cultivo de mandioca
    1109: 0,   # Cultivo de outras lavouras temporarias
    1110: 0,   # Horticultura
    1111: 0,   # Cultivo de flores e plantas ornamentais
    1112: 0,   # Cultivo de frutas citricas
    1113: 0,   # Cultivo de cafe
    1114: 0,   # Cultivo de cacau
    1115: 0,   # Cultivo de uva
    1116: 0,   # Cultivo de banana
    1117: 0,   # Cultivo de outras frutas permanentes
    1118: 0,   # Producao de sementes e mudas certificadas
    1119: 0,   # Lavoura nao especificada
    1401: 0,   # Atividades de apoio a agricultura e pos-colheita
    1500: 0,   # Caca e servicos relacionados (proxy: agro)
    1999: 0,   # Agropecuaria nao especificada (proxy: agro)

    # === MIP 1: Pecuaria, inclusive apoio a pecuaria ===
    1201: 1,   # Criacao de bovinos
    1202: 1,   # Criacao de outros animais de grande porte
    1203: 1,   # Criacao de caprinos e ovinos
    1204: 1,   # Criacao de suinos
    1205: 1,   # Criacao de aves
    1206: 1,   # Apicultura
    1207: 1,   # Sericicultura
    1208: 1,   # Criacao de outros animais
    1209: 1,   # Pecuaria nao especificada
    1402: 1,   # Atividades de apoio a pecuaria

    # === MIP 2: Producao florestal; pesca e aquicultura ===
    2000: 2,   # Producao florestal
    3001: 2,   # Pesca
    3002: 2,   # Aquicultura

    # === MIP 3: Extracao de carvao mineral e minerais nao metalicos ===
    5000: 3,   # Extracao de carvao mineral
    8001: 3,   # Extracao de pedras, areia e argila
    8002: 3,   # Extracao de gemas
    8009: 3,   # Extracao de minerais nao metalicos n.e.

    # === MIP 4: Extracao de petroleo e gas, inclusive apoio ===
    6000: 4,   # Extracao de petroleo e gas natural
    9000: 4,   # Atividades de apoio a extracao de minerais

    # === MIP 5: Extracao de minerio de ferro ===
    # PNAD nao separa ferro de nao-ferrosos. Codigos 7001/7002 serao
    # divididos entre MIP 5 e 6 usando VAB como peso.
    7001: 5,   # Extracao de minerios de metais preciosos -> proxy ferro
    7002: 6,   # Extracao de minerais metalicos n.e. -> proxy nao-ferrosos

    # === MIP 7: Abate/carne, inclusive laticinio e pesca ===
    10010: 7,  # Abate e fabricacao de produtos de carne e pescado
    10030: 7,  # Laticinios

    # === MIP 8: Fabricacao e refino de acucar ===
    10092: 8,  # Fabricacao e refino do acucar

    # === MIP 9: Outros produtos alimentares ===
    10021: 9,  # Conservas de frutas/legumes
    10022: 9,  # Oleos vegetais e gorduras
    10091: 9,  # Moagem, amilaceos, alimentos para animais
    10093: 9,  # Torrefacao e moagem de cafe
    10099: 9,  # Outros produtos alimenticios

    # === MIP 10: Bebidas ===
    11000: 10, # Fabricacao de bebidas

    # === MIP 11: Fumo ===
    12000: 11, # Processamento/fabricacao de produtos do fumo

    # === MIP 12: Texteis ===
    13001: 12, # Preparacao de fibras, fiacao e tecelagem
    13002: 12, # Fabricacao de artefatos texteis, exceto vestuario

    # === MIP 13: Vestuario ===
    14001: 13, # Confeccao vestuario, exceto sob medida
    14002: 13, # Confeccao sob medida

    # === MIP 14: Calcados e couro ===
    15011: 14, # Curtimento e preparacoes de couro
    15012: 14, # Artigos de viagem e artefatos de couro
    15020: 14, # Fabricacao de calcados

    # === MIP 15: Madeira ===
    16001: 15, # Serrarias
    16002: 15, # Produtos de madeira, cortica, material trancado

    # === MIP 16: Celulose e papel ===
    17001: 16, # Celulose, papel, cartolina, papel-cartao
    17002: 16, # Embalagens de papel, artefatos de papel

    # === MIP 17: Impressao e reproducao de gravacoes ===
    18000: 17, # Impressao e reproducao de gravacoes

    # === MIP 18: Refino de petroleo e coquerias ===
    19010: 18, # Coquerias
    19020: 18, # Fabricacao de produtos derivados do petroleo
    19030: 18, # Fabricacao de biocombustiveis
    # NOTA: CNAE 19030 (biocombustiveis) e da divisao 19. Na MIP,
    # biocombustiveis e setor separado (MIP 19), mas na PNAD
    # esta junto com refino. Vamos dividir por VAB.

    # === MIP 20: Quimicos organicos/inorganicos, resinas, elastomeros ===
    20010: 20, # Produtos quimicos inorganicos
    20020: 20, # Produtos quimicos organicos

    # === MIP 21: Defensivos, tintas, quimicos diversos ===
    20090: 21, # Outros quimicos (proxy: defensivos/tintas/diversos)

    # === MIP 22: Limpeza, cosmeticos, perfumaria ===
    # PNAD nao separa div 20 em 3 setores MIP. Usamos 20090 como proxy.
    # MIP 22 sera preenchido por VBP-split quando possivel.

    # === MIP 23: Farmoquimicos e farmaceuticos ===
    21000: 23, # Fabricacao de produtos farmoquimicos e farmaceuticos

    # === MIP 24: Borracha e plastico ===
    22010: 24, # Fabricacao de produtos de borracha
    22020: 24, # Fabricacao de produtos de material plastico

    # === MIP 25: Minerais nao metalicos ===
    23010: 25, # Fabricacao de vidro e produtos de vidro
    23091: 25, # Fabricacao de produtos ceramicos
    23099: 25, # Outros produtos de minerais nao metalicos

    # === MIP 26: Siderurgia, ferro-gusa, tubos ===
    24001: 26, # Producao de ferro-gusa e ferroligas

    # === MIP 27: Metalurgia de metais nao ferrosos e fundicao ===
    24002: 27, # Siderurgia (na verdade, 24002 = metalurgia nao-ferrosos na PNAD)
    24003: 27, # Fundicao

    # === MIP 28: Produtos de metal ===
    25001: 28, # Fabricacao de estruturas metalicas e caldeiraria
    25002: 28, # Forjaria, tratamentos, metalurgia do po, servicos de usinagem

    # === MIP 29: Informatica, eletronicos, opticos ===
    26010: 29, # Fabricacao de componentes eletronicos
    26020: 29, # Fabricacao de equipamentos de informatica
    26021: 29, # Fabricacao de equipamentos de informatica (alt)
    26030: 29, # Fabricacao de equipamentos de comunicacao
    26041: 29, # Aparelhos eletromedicos/eletroterapeuticos/irradiacao
    26042: 29, # Aparelhos eletromedicos (variante)
    26049: 29, # Outros aparelhos eletronicos e opticos

    # === MIP 30: Maquinas e equipamentos eletricos ===
    27010: 30, # Geradores, transformadores, motores eletricos
    27090: 30, # Outros equipamentos eletricos

    # === MIP 31: Maquinas e equipamentos mecanicos ===
    28000: 31, # Fabricacao de maquinas e equipamentos

    # === MIP 32: Automoveis, caminhoes, onibus ===
    29001: 32, # Fabricacao de automoveis, caminhonetas, caminhoes, onibus

    # === MIP 33: Pecas e acessorios para veiculos ===
    29002: 33, # Fabricacao de pecas e acessorios para veiculos

    # === MIP 34: Outros equipamentos de transporte ===
    30010: 34, # Construcao de embarcacoes
    30020: 34, # Fabricacao de veiculos ferroviarios
    30030: 34, # Fabricacao de aeronaves
    30090: 34, # Outros equipamentos de transporte

    # === MIP 35: Moveis e produtos de industrias diversas ===
    31000: 35, # Fabricacao de moveis
    32001: 35, # Joalheria, bijuteria
    32002: 35, # Instrumentos musicais
    32003: 35, # Artigos pesca/esporte/brinquedos
    32009: 35, # Produtos diversos

    # === MIP 36: Manutencao, reparacao, instalacao de maq/equip ===
    33001: 36, # Manutencao e reparacao de maquinas
    33002: 36, # Instalacao de maquinas e equipamentos

    # === MIP 37: Eletricidade, gas natural, outras utilidades ===
    35010: 37, # Geracao/transmissao/distribuicao de energia eletrica
    35021: 37, # Producao/distribuicao de combustiveis gasosos
    35022: 37, # Producao/distribuicao de vapor, agua quente, ar condicionado

    # === MIP 38: Agua, esgoto e gestao de residuos ===
    36000: 38, # Captacao/tratamento/distribuicao de agua
    37000: 38, # Esgoto
    38000: 38, # Coleta/tratamento/disposicao de residuos
    39000: 38, # Descontaminacao

    # === MIP 39: Construcao ===
    41000: 39, # Construcao de edificios
    42000: 39, # Obras de infraestrutura
    43000: 39, # Servicos especializados para construcao

    # === MIP 40: Comercio por atacado e varejo ===
    45010: 40, # Comercio de veiculos
    45020: 40, # Manutencao/reparacao de veiculos
    45030: 40, # Comercio de pecas para veiculos
    45040: 40, # Comercio/manut. motocicletas
    48010: 40, # Representantes comerciais
    48020: 40, # Comercio de materias-primas agricolas
    48030: 40, # Comercio de alimentos/bebidas/fumo
    48041: 40, # Comercio de tecidos/armarinho
    48042: 40, # Comercio de vestuario/calcados
    48050: 40, # Comercio de madeira/material construcao
    48060: 40, # Comercio de combustiveis
    48071: 40, # Comercio farmaceutico/cosmeticos
    48072: 40, # Comercio de papelaria/livros
    48073: 40, # Comercio de eletrodomesticos/moveis
    48074: 40, # Comercio de equipamentos TI
    48075: 40, # Comercio de maquinas/equipamentos
    48076: 40, # Comercio de combustiveis solidos/liquidos
    48077: 40, # Comercio de produtos usados
    48078: 40, # Comercio de residuos e sucatas
    48079: 40, # Comercio de produtos novos n.e.
    48080: 40, # Supermercado e hipermercado
    48090: 40, # Lojas de departamento
    48100: 40, # Comercio ambulante e feiras

    # === MIP 41: Transporte terrestre ===
    49010: 41, # Transporte ferroviario/metroferroviario
    49030: 41, # Transporte rodoviario de passageiros
    49040: 41, # Transporte rodoviario de carga
    49090: 41, # Outros transportes terrestres

    # === MIP 42: Transporte aquaviario ===
    50000: 42, # Transporte aquaviario

    # === MIP 43: Transporte aereo ===
    51000: 43, # Transporte aereo

    # === MIP 44: Armazenamento, auxiliares transportes, correio ===
    52010: 44, # Armazenamento, carga e descarga
    52020: 44, # Atividades auxiliares dos transportes
    53001: 44, # Correio
    53002: 44, # Malote e entrega

    # === MIP 45: Alojamento ===
    55000: 45, # Alojamento

    # === MIP 46: Alimentacao ===
    56011: 46, # Restaurantes e servicos de alimentacao
    56012: 46, # Catering, bufe, comida preparada
    56020: 46, # Servicos ambulantes de alimentacao

    # === MIP 47: Edicao e edicao integrada a impressao ===
    58000: 47, # Edicao e edicao integrada a impressao

    # === MIP 48: TV, radio, cinema, gravacao de som/imagem ===
    59000: 48, # Cinema, video, TV, gravacao de som/musica
    60001: 48, # Atividades de radio
    60002: 48, # Atividades de televisao

    # === MIP 49: Telecomunicacoes ===
    61000: 49, # Telecomunicacoes

    # === MIP 50: Desenvolvimento de sistemas e servicos de informacao ===
    62000: 50, # Servicos de TI
    63000: 50, # Prestacao de servicos de informacao

    # === MIP 51: Intermediacao financeira, seguros, previdencia ===
    64000: 51, # Servicos financeiros
    65000: 51, # Seguros e previdencia privada
    66001: 51, # Atividades auxiliares servicos financeiros
    66002: 51, # Atividades auxiliares seguros/previdencia/saude

    # === MIP 52: Atividades imobiliarias ===
    68000: 52, # Atividades imobiliarias

    # === MIP 53: Juridicas, contabeis, consultoria, sedes de empresas ===
    69000: 53, # Juridicas, contabilidade, auditoria
    70000: 53, # Consultoria em gestao empresarial

    # === MIP 54: Arquitetura, engenharia, testes, P&D ===
    71000: 54, # Arquitetura, engenharia, testes
    72000: 54, # Pesquisa e desenvolvimento cientifico

    # === MIP 55: Outras atividades profissionais, cientificas, tecnicas ===
    73010: 55, # Publicidade
    73020: 55, # Pesquisas de mercado
    74000: 55, # Outras atividades profissionais/cientificas
    75000: 55, # Atividades veterinarias

    # === MIP 56: Alugueis nao imobiliarios e gestao de ativos de PI ===
    77010: 56, # Aluguel de objetos pessoais/domesticos
    77020: 56, # Aluguel de meios de transporte/maquinas

    # === MIP 57: Outras atividades administrativas e servicos complementares ===
    78000: 57, # Selecao e locacao de mao de obra
    79000: 57, # Agencias de viagem
    81011: 57, # Servicos de limpeza e apoio a edificios
    81012: 57, # Condominios prediais
    81020: 57, # Atividades paisagisticas
    82001: 57, # Servicos de escritorio e apoio administrativo
    82002: 57, # Atividades de teleatendimento
    82003: 57, # Organizacao de eventos (exceto culturais/esportivos)
    82009: 57, # Outros servicos prestados a empresas

    # === MIP 58: Vigilancia, seguranca, investigacao ===
    80000: 58, # Vigilancia, seguranca, transporte de valores

    # === MIP 59: Administracao publica, defesa, seguridade social ===
    84011: 59, # Admin publica - Federal
    84012: 59, # Admin publica - Estadual
    84013: 59, # Admin publica - Municipal
    84014: 59, # Defesa
    84015: 59, # Outros servicos coletivos - Federal
    84016: 59, # Outros servicos coletivos - Estadual
    84017: 59, # Outros servicos coletivos - Municipal
    84020: 59, # Seguridade social obrigatoria
    99000: 59, # Organismos internacionais (proxy)

    # === EDUCACAO: dividida entre pub (MIP 60) e priv (MIP 61) ===
    # Mapeamos inicialmente tudo para MIP 60 e separamos depois
    # usando os proprios dados PNAD (creche/fundamental/medio = mais pub,
    # superior/outros = mais priv)
    85011: 60, # Creche (predominantemente publica)
    85012: 60, # Pre-escola e ensino fundamental (predominantemente publica)
    85013: 60, # Ensino medio (predominantemente publica)
    85014: 61, # Educacao superior (misto, mas ~40% privada)
    85021: 61, # Servicos auxiliares a educacao (misto)
    85029: 61, # Outras atividades de ensino (predominantemente privada)

    # === SAUDE: dividida entre pub (MIP 62) e priv (MIP 63) ===
    # Hospitais sao mistos. Ambulatorial/profissionais tendem a privados.
    86001: 62, # Atendimento hospitalar (mais publico)
    86002: 63, # Atencao ambulatorial medicos/odontologos (mais privado)
    86003: 63, # Complementacao diagnostica/terapeutica (mais privado)
    86004: 63, # Profissionais de saude exceto medicos (mais privado)
    86009: 63, # Atencao a saude n.e. (proxy privado)
    87000: 62, # Assistencia social com alojamento (publico)
    88000: 62, # Assistencia social sem alojamento (publico)

    # === MIP 64: Atividades artisticas, criativas e espetaculos ===
    90000: 64, # Atividades artisticas, criativas e espetaculos
    91000: 64, # Patrimonio cultural e ambiental
    92000: 64, # Jogos de azar e apostas
    93011: 64, # Atividades esportivas
    93012: 64, # Atividades de condicionamento fisico
    93020: 64, # Atividades de recreacao e lazer

    # === MIP 65: Organizacoes associativas e outros servicos pessoais ===
    94010: 65, # Associativas patronais/empresariais
    94020: 65, # Sindicais
    94091: 65, # Religiosas e filosoficas
    94099: 65, # Outras associativas
    96010: 65, # Lavanderias, tinturarias
    96020: 65, # Cabeleireiros, tratamento de beleza
    96030: 65, # Funerarias
    96090: 65, # Outros servicos pessoais

    # === MIP 36: Reparacao (mapeia para Manutencao) ===
    95010: 36, # Reparacao de equipamentos de informatica/comunicacao
    95030: 36, # Reparacao de objetos pessoais e domesticos

    # === MIP 66: Servicos domesticos ===
    97000: 66, # Servicos domesticos

    # === Codigo 0: Atividades mal definidas ===
    0: -1,     # Nao mapeavel -> sera distribuido proporcionalmente
}

# Setores que precisam de split adicional via VBP
# (PNAD agrupa codigos que cobrem mais de um setor MIP)
VBP_SPLITS = [
    # CNAE 19030 (biocombustiveis) esta mapeado junto com 19010/19020 no setor 18
    # Precisamos separar MIP 18 (Refino) e MIP 19 (Biocombustiveis)
    {'source': 18, 'targets': [18, 19]},
    # CNAE div 20: mapeamos 20010/20020->20, 20090->21
    # MIP 22 (Limpeza/cosmeticos) fica sem dados diretos -> split de MIP 21
    {'source': 21, 'targets': [21, 22]},
]


def main():
    print("=" * 70)
    print("GERANDO MATRIZ OFICIAL DE EMPREGO E RENDA (67 x 27) - v3")
    print("Mapeamento por codigo CNAE individual (223 codigos)")
    print("=" * 70)

    os.makedirs(FINAL_DIR, exist_ok=True)

    # =====================================================================
    # 1. Carregar PNAD
    # =====================================================================
    print("\n[1/6] Carregando PNAD Continua 2021...")
    pnad_path = DATA_DIR / 'Massa de rendimento e PO - PNADC042021.xlsx'
    df = pd.read_excel(pnad_path, sheet_name='VALOR NOMINAL - TODOS OS TRAB', skiprows=1)
    df['CNAE_INT'] = df['CNAE'].fillna(-1).astype(int)
    df['UF_SIGLA'] = df['UF'].map(IBGE_TO_UF)
    df['MIP'] = df['CNAE_INT'].map(CNAE_TO_MIP)
    print(f"  {len(df)} registros, {df['UF'].nunique()} UFs")

    # Diagnostico de mapeamento
    unmapped = df[df['MIP'].isna() & (df['CNAE_INT'] > 0)]
    if len(unmapped) > 0:
        print(f"  [AVISO] {len(unmapped)} registros com CNAE nao mapeado:")
        for cnae, po in unmapped.groupby('CNAE_INT')['POP. OCUPADA'].sum().items():
            print(f"    CNAE {cnae}: {po:,.0f} PO")

    # =====================================================================
    # 2. Carregar VAB regional
    # =====================================================================
    print("[2/6] Carregando VAB regional...")
    with open(DATA_DIR / 'processed' / '2021_final' / 'vab_regional.json', 'r') as f:
        vab_data = json.load(f)
    print(f"  {len(vab_data)} UFs, {len(list(vab_data.values())[0])} setores")

    # =====================================================================
    # 3. Processar cada UF
    # =====================================================================
    print("[3/6] Processando 27 UFs...")

    po_matrix = np.zeros((N_SECTORS, N_REGIONS))
    renda_matrix = np.zeros((N_SECTORS, N_REGIONS))

    for uf_idx, uf_sigla in enumerate(UF_ORDER):
        ibge_code = [k for k, v in IBGE_TO_UF.items() if v == uf_sigla][0]
        df_uf = df[(df['UF'] == ibge_code) & (df['MIP'].notna()) & (df['MIP'] >= 0)].copy()

        if len(df_uf) == 0:
            continue

        df_uf['MIP'] = df_uf['MIP'].astype(int)

        agg = df_uf.groupby('MIP').agg({
            'POP. OCUPADA': 'sum',
            'MASSA DE RENDIMENTOS': 'sum'
        })

        po = np.zeros(N_SECTORS)
        renda = np.zeros(N_SECTORS)

        for mip_idx, row in agg.iterrows():
            if 0 <= mip_idx < N_SECTORS:
                po[mip_idx] += row['POP. OCUPADA']
                renda[mip_idx] += row['MASSA DE RENDIMENTOS']

        # Anualizar
        renda *= FATOR_ANUALIZACAO

        # VAB desta UF para splits
        vab = np.array(vab_data.get(uf_sigla, np.zeros(N_SECTORS).tolist()))

        # VBP splits para setores agrupados
        for split in VBP_SPLITS:
            src = split['source']
            targets = split['targets']
            if po[src] > 0 and src in targets:
                total_vab = sum(vab[t] for t in targets)
                if total_vab > 0:
                    po_total = po[src]
                    renda_total = renda[src]
                    for t in targets:
                        w = vab[t] / total_vab
                        po[t] = po_total * w
                        renda[t] = renda_total * w

        po_matrix[:, uf_idx] = po
        renda_matrix[:, uf_idx] = renda

    # Converter renda para R$ Mi
    renda_matrix = renda_matrix / 1e6

    print(f"  PO total: {po_matrix.sum():,.0f}")
    print(f"  Renda total: R$ {renda_matrix.sum():,.0f} Mi")

    # =====================================================================
    # 4. Calcular coeficientes
    # =====================================================================
    print("[4/6] Calculando coeficientes...")

    vab_matrix = np.zeros((N_SECTORS, N_REGIONS))
    for uf_idx, uf_sigla in enumerate(UF_ORDER):
        vab_matrix[:, uf_idx] = np.array(vab_data.get(uf_sigla, np.zeros(N_SECTORS).tolist()))

    emp_coeffs = np.divide(po_matrix, vab_matrix,
                           out=np.zeros_like(po_matrix), where=vab_matrix > 0)
    inc_coeffs = np.divide(renda_matrix, vab_matrix,
                           out=np.zeros_like(renda_matrix), where=vab_matrix > 0)

    # Fallback com media nacional para celulas zeradas
    po_nacional = po_matrix.sum(axis=1)
    vab_nacional = vab_matrix.sum(axis=1)
    emp_nacional = np.divide(po_nacional, vab_nacional,
                             out=np.zeros(N_SECTORS), where=vab_nacional > 0)
    inc_nacional_vec = np.divide(renda_matrix.sum(axis=1), vab_nacional,
                                 out=np.zeros(N_SECTORS), where=vab_nacional > 0)

    filled = 0
    for s in range(N_SECTORS):
        for r in range(N_REGIONS):
            if emp_coeffs[s, r] == 0 and vab_matrix[s, r] > 0 and emp_nacional[s] > 0:
                emp_coeffs[s, r] = emp_nacional[s]
                inc_coeffs[s, r] = inc_nacional_vec[s]
                filled += 1

    print(f"  Celulas preenchidas com media nacional: {filled}")

    # =====================================================================
    # 5. Salvar matrizes oficiais 67x27
    # =====================================================================
    print("[5/5] Salvando matrizes oficiais...")

    np.save(FINAL_DIR / 'employment_matrix_67x27.npy', po_matrix)
    np.save(FINAL_DIR / 'income_matrix_67x27.npy', renda_matrix)
    np.save(FINAL_DIR / 'emp_coefficients_67x27.npy', emp_coeffs)
    np.save(FINAL_DIR / 'inc_coefficients_67x27.npy', inc_coeffs)

    # Excel
    summary_path = FINAL_DIR / 'employment_income_67x27_summary.xlsx'
    with pd.ExcelWriter(summary_path, engine='openpyxl') as writer:
        # Aba Emprego
        rows_emp = []
        for s in range(N_SECTORS):
            row = {'Idx': s, 'Setor': SECTOR_LABELS[s]}
            for r, uf in enumerate(UF_ORDER):
                row[f'PO_{uf}'] = po_matrix[s, r]
            row['PO_Brasil'] = po_matrix[s, :].sum()
            row['Coef_Medio'] = emp_nacional[s]
            rows_emp.append(row)
        pd.DataFrame(rows_emp).to_excel(writer, sheet_name='Emprego', index=False)

        # Aba Renda
        rows_inc = []
        for s in range(N_SECTORS):
            row = {'Idx': s, 'Setor': SECTOR_LABELS[s]}
            for r, uf in enumerate(UF_ORDER):
                row[f'Renda_{uf}'] = renda_matrix[s, r]
            row['Renda_Brasil'] = renda_matrix[s, :].sum()
            rows_inc.append(row)
        pd.DataFrame(rows_inc).to_excel(writer, sheet_name='Renda', index=False)

        # Metadata
        meta = {
            'Fonte': 'PNAD Continua 2021 - 4o trimestre',
            'Mapeamento': '223 codigos CNAE PNAD -> MIP 67 (individual)',
            'Anualizacao': f'{FATOR_ANUALIZACAO}x',
            'PO_Total': po_matrix.sum(),
            'Renda_Total_Mi': renda_matrix.sum(),
            'Setores_com_dados': int((po_nacional > 0).sum()),
        }
        pd.DataFrame([meta]).T.to_excel(writer, sheet_name='Metadata')

    # =====================================================================
    # DIAGNOSTICO
    # =====================================================================
    print(f"\n{'='*70}")
    print("DIAGNOSTICO FINAL")
    print(f"{'='*70}")
    print(f"  PO Total Brasil: {po_matrix.sum():,.0f}")
    print(f"  Renda Total Brasil: R$ {renda_matrix.sum():,.0f} Mi")

    n_with_data = (po_nacional > 0).sum()
    print(f"  Setores com dados: {n_with_data}/67")
    zeros = [i for i in range(67) if po_nacional[i] == 0]
    if zeros:
        print(f"  Setores zerados: {zeros}")
        for z in zeros:
            print(f"    [{z}] {SECTOR_LABELS[z]} (VAB nacional: R$ {vab_nacional[z]:,.0f} Mi)")

    # Setores criativos
    creative = {45: 'Alojamento', 46: 'Alimentacao', 47: 'Edicao',
                48: 'TV/Radio/Cinema', 50: 'TI/Software', 64: 'Artes'}
    print(f"\n  Setores Criativos (Brasil):")
    for idx, name in creative.items():
        print(f"    [{idx:>2}] {name:<20} PO={po_nacional[idx]:>12,.0f}  Coef={emp_nacional[idx]:>8.2f}")

    # Top UFs
    print(f"\n  Top 5 UFs por PO:")
    uf_totals = [(UF_ORDER[r], po_matrix[:, r].sum()) for r in range(N_REGIONS)]
    uf_totals.sort(key=lambda x: x[1], reverse=True)
    for uf, total in uf_totals[:5]:
        print(f"    {uf}: {total:>12,.0f}")

    print(f"\n  [OK] Arquivos salvos em: {FINAL_DIR}")


if __name__ == "__main__":
    main()
