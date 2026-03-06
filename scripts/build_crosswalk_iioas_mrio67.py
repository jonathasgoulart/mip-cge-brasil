"""
Constrói o crosswalk entre os 68 setores da IIOAS_BRUF_2019 (NEREUS/USP)
e os 67 setores da MRIO v6.1 (IBGE 67×67).

Resultado: crosswalk_iioas_mrio67.json e crosswalk_iioas_mrio67.csv
"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r'C:\Users\jonat\Documents\MIP e CGE')
OUTPUT = BASE / 'output' / 'crosswalk'
OUTPUT.mkdir(parents=True, exist_ok=True)

# ── 68 setores da IIOAS (S01–S68) ──────────────────────────────────────────
IIOAS_SECTORS = {
    1:  "Agricultura, inclusive o apoio à agricultura e a pós-colheita",
    2:  "Pecuária, inclusive o apoio à pecuária",
    3:  "Produção florestal; pesca e aquicultura",
    4:  "Extração de carvão mineral e de minerais não-metálicos",
    5:  "Extração de petróleo e gás, inclusive as atividades de apoio",
    6:  "Extração de minério de ferro, inclusive beneficiamentos e a aglomeração",
    7:  "Extração de minerais metálicos não-ferrosos, inclusive beneficiamentos",
    8:  "Abate e produtos de carne, inclusive os produtos do laticínio e da pesca",
    9:  "Fabricação e refino de açúcar",
    10: "Outros produtos alimentares",
    11: "Fabricação de bebidas",
    12: "Fabricação de produtos do fumo",
    13: "Fabricação de produtos têxteis",
    14: "Confecção de artefatos do vestuário e acessórios",
    15: "Fabricação de calçados e de artefatos de couro",
    16: "Fabricação de produtos da madeira",
    17: "Fabricação de celulose, papel e produtos de papel",
    18: "Impressão e reprodução de gravações",
    19: "Refino de petróleo e coquerias",
    20: "Fabricação de biocombustíveis",
    21: "Fabricação de químicos orgânicos e inorgânicos, resinas e elastômeros",
    22: "Fabricação de defensivos, desinfestantes, tintas e químicos diversos",
    23: "Fabricação de produtos de limpeza, cosméticos/perfumaria e higiene pessoal",
    24: "Fabricação de produtos farmoquímicos e farmacêuticos",
    25: "Fabricação de produtos de borracha e de material plástico",
    26: "Fabricação de produtos de minerais não-metálicos",
    27: "Produção de ferro-gusa/ferroligas, siderurgia e tubos de aço sem costura",
    28: "Metalurgia de metais não-ferosos e a fundição de metais",
    29: "Fabricação de produtos de metal, exceto máquinas e equipamentos",
    30: "Fabricação de equipamentos de informática, produtos eletrônicos e ópticos",
    31: "Fabricação de máquinas e equipamentos elétricos",
    32: "Fabricação de máquinas e equipamentos mecânicos",
    33: "Fabricação de automóveis, caminhões e ônibus, exceto peças",
    34: "Fabricação de peças e acessórios para veículos automotores",
    35: "Fabricação de outros equipamentos de transporte, exceto veículos automotores",
    36: "Fabricação de móveis e de produtos de indústrias diversas",
    37: "Manutenção, reparação e instalação de máquinas e equipamentos",
    38: "Energia elétrica, gás natural e outras utilidades",
    39: "Água, esgoto e gestão de resíduos",
    40: "Construção",
    41: "Comércio e reparação de veículos automotores e motocicletas",  # Parte de MRIO-41
    42: "Comércio por atacado e a varejo, exceto veículos automotores",  # Parte de MRIO-41
    43: "Transporte terrestre",
    44: "Transporte aquaviário",
    45: "Transporte aéreo",
    46: "Armazenamento, atividades auxiliares dos transportes e correio",
    47: "Alojamento",
    48: "Alimentação",
    49: "Edição e edição integrada à impressão",
    50: "Atividades de televisão, rádio, cinema e gravação/edição de som e imagem",
    51: "Telecomunicações",
    52: "Desenvolvimento de sistemas e outros serviços de informação",
    53: "Intermediação financeira, seguros e previdência complementar",
    54: "Atividades imobiliárias",
    55: "Atividades jurídicas, contábeis, consultoria e sedes de empresas",
    56: "Serviços de arquitetura, engenharia, testes/análises técnicas e P&D",
    57: "Outras atividades profissionais, científicas e técnicas",
    58: "Aluguéis não-imobiliários e gestão de ativos de propriedade intelectual",
    59: "Outras atividades administrativas e serviços complementares",
    60: "Atividades de vigilância, segurança e investigação",
    61: "Administração pública, defesa e seguridade social",
    62: "Educação pública",
    63: "Educação privada",
    64: "Saúde pública",
    65: "Saúde privada",
    66: "Atividades artísticas, criativas e de espetáculos",
    67: "Organizações associativas e outros serviços pessoais",
    68: "Serviços domésticos",
}

# ── 67 setores da MRIO v6.1 (sector_labels.txt) ────────────────────────────
MRIO67_SECTORS = {
    1:  "Agricultura, inclusive o apoio à agricultura e a pós-colheita",
    2:  "Pecuária, inclusive o apoio à pecuária",
    3:  "Produção florestal; pesca e aquicultura",
    4:  "Extração de carvão mineral e de minerais não metálicos",
    5:  "Extração de petróleo e gás, inclusive as atividades de apoio",
    6:  "Extração de minério de ferro, inclusive beneficiamentos e a aglomeração",
    7:  "Extração de minerais metálicos não ferrosos, inclusive beneficiamentos",
    8:  "Abate e produtos de carne, inclusive os produtos do laticínio e da pesca",
    9:  "Fabricação e refino de açúcar",
    10: "Outros produtos alimentares",
    11: "Fabricação de bebidas",
    12: "Fabricação de produtos do fumo",
    13: "Fabricação de produtos têxteis",
    14: "Confecção de artefatos do vestuário e acessórios",
    15: "Fabricação de calçados e de artefatos de couro",
    16: "Fabricação de produtos da madeira",
    17: "Fabricação de celulose, papel e produtos de papel",
    18: "Impressão e reprodução de gravações",
    19: "Refino de petróleo e coquerias",
    20: "Fabricação de biocombustíveis",
    21: "Fabricação de químicos orgânicos e inorgânicos, resinas e elastômeros",
    22: "Fabricação de defensivos, desinfestantes, tintas e químicos diversos",
    23: "Fabricação de produtos de limpeza, cosméticos/perfumaria e higiene pessoal",
    24: "Fabricação de produtos farmoquímicos e farmacêuticos",
    25: "Fabricação de produtos de borracha e de material plástico",
    26: "Fabricação de produtos de minerais não metálicos",
    27: "Produção de ferro gusa/ferroligas, siderurgia e tubos de aço sem costura",
    28: "Metalurgia de metais não ferosos e a fundição de metais",
    29: "Fabricação de produtos de metal, exceto máquinas e equipamentos",
    30: "Fabricação de equipamentos de informática, produtos eletrônicos e ópticos",
    31: "Fabricação de máquinas e equipamentos elétricos",
    32: "Fabricação de máquinas e equipamentos mecânicos",
    33: "Fabricação de automóveis, caminhões e ônibus, exceto peças",
    34: "Fabricação de peças e acessórios para veículos automotores",
    35: "Fabricação de outros equipamentos de transporte, exceto veículos automotores",
    36: "Fabricação de móveis e de produtos de indústrias diversas",
    37: "Manutenção, reparação e instalação de máquinas e equipamentos",
    38: "Energia elétrica, gás natural e outras utilidades",
    39: "Água, esgoto e gestão de resíduos",
    40: "Construção",
    41: "Comércio por atacado e varejo",  # FUSÃO de IIOAS-S41 + IIOAS-S42
    42: "Transporte terrestre",
    43: "Transporte aquaviário",
    44: "Transporte aéreo",
    45: "Armazenamento, atividades auxiliares dos transportes e correio",
    46: "Alojamento",
    47: "Alimentação",
    48: "Edição e edição integrada à impressão",
    49: "Atividades de televisão, rádio, cinema e gravação/edição de som e imagem",
    50: "Telecomunicações",
    51: "Desenvolvimento de sistemas e outros serviços de informação",
    52: "Intermediação financeira, seguros e previdência complementar",
    53: "Atividades imobiliárias",
    54: "Atividades jurídicas, contábeis, consultoria e sedes de empresas",
    55: "Serviços de arquitetura, engenharia, testes/análises técnicas e P & D",
    56: "Outras atividades profissionais, científicas e técnicas",
    57: "Aluguéis não imobiliários e gestão de ativos de propriedade intelectual",
    58: "Outras atividades administrativas e serviços complementares",
    59: "Atividades de vigilância, segurança e investigação",
    60: "Administração pública, defesa e seguridade social",
    61: "Educação pública",
    62: "Educação privada",
    63: "Saúde pública",
    64: "Saúde privada",
    65: "Atividades artísticas, criativas e de espetáculos",
    66: "Organizações associativas e outros serviços pessoais",
    67: "Serviços domésticos",
}

# ── Regras de mapeamento IIOAS → MRIO67 ────────────────────────────────────
# Tipo:
#   "direct"   → 1-para-1, mesmo setor
#   "aggregate" → N IIOAS → 1 MRIO (fusão)
#   "drop"     → setor IIOAS não existe na MRIO67 (será excluído ou somado)
#   "split"    → 1 IIOAS → N MRIO (divisão — não ocorre aqui)

CROSSWALK = []

# S01–S40: mapeamento direto 1:1
for i in range(1, 41):
    CROSSWALK.append({
        "iioas_idx": i,         # 0-indexed = i-1
        "iioas_code": f"S{i:02d}",
        "iioas_label": IIOAS_SECTORS[i],
        "mrio67_idx": i,        # 0-indexed = i-1
        "mrio67_code": f"M{i:02d}",
        "mrio67_label": MRIO67_SECTORS[i],
        "mapping_type": "direct",
        "note": ""
    })

# S41 + S42 (IIOAS) → M41 (MRIO): fusão comércio
CROSSWALK.append({
    "iioas_idx": 41,
    "iioas_code": "S41",
    "iioas_label": IIOAS_SECTORS[41],
    "mrio67_idx": 41,
    "mrio67_code": "M41",
    "mrio67_label": MRIO67_SECTORS[41],
    "mapping_type": "aggregate",
    "note": "S41 + S42 IIOAS → M41 MRIO (IIOAS desmembra comércio de veículos do resto)"
})
CROSSWALK.append({
    "iioas_idx": 42,
    "iioas_code": "S42",
    "iioas_label": IIOAS_SECTORS[42],
    "mrio67_idx": 41,
    "mrio67_code": "M41",
    "mrio67_label": MRIO67_SECTORS[41],
    "mapping_type": "aggregate",
    "note": "S41 + S42 IIOAS → M41 MRIO (IIOAS desmembra comércio de veículos do resto)"
})

# S43–S67 (IIOAS) → M42–M66 (MRIO): deslocamento por -1 por causa da fusão acima
for i in range(43, 68):
    m = i - 1  # offset de 1 pela fusão S41+S42→M41
    CROSSWALK.append({
        "iioas_idx": i,
        "iioas_code": f"S{i:02d}",
        "iioas_label": IIOAS_SECTORS[i],
        "mrio67_idx": m,
        "mrio67_code": f"M{m:02d}",
        "mrio67_label": MRIO67_SECTORS[m],
        "mapping_type": "direct",
        "note": "Offset -1 por causa da fusão S41+S42→M41"
    })

# S68 (IIOAS: Serviços domésticos) → M67 (MRIO: Serviços domésticos)
CROSSWALK.append({
    "iioas_idx": 68,
    "iioas_code": "S68",
    "iioas_label": IIOAS_SECTORS[68],
    "mrio67_idx": 67,
    "mrio67_code": "M67",
    "mrio67_label": MRIO67_SECTORS[67],
    "mapping_type": "direct",
    "note": "Offset -1 por causa da fusão S41+S42→M41"
})

# ── Validação ───────────────────────────────────────────────────────────────
print(f"Total de linhas no crosswalk: {len(CROSSWALK)}")
print(f"Setores IIOAS cobertos: {sorted(set(r['iioas_idx'] for r in CROSSWALK))}")
mrio_covered = sorted(set(r['mrio67_idx'] for r in CROSSWALK))
print(f"Setores MRIO67 cobertos: {mrio_covered}")
print(f"Número único de setores MRIO67: {len(mrio_covered)}")

# Verificar se todos os 67 setores MRIO estão cobertos
missing = set(range(1, 68)) - set(mrio_covered)
if missing:
    print(f"ATENÇÃO: Setores MRIO67 sem cobertura: {missing}")
else:
    print("OK: Todos os 67 setores MRIO67 cobertos!")

# ── Verificar consistência dos labels ────────────────────────────────────────
print("\nVerificação de correspondência de labels (direto 1:1):")
mismatches = 0
for row in CROSSWALK:
    if row["mapping_type"] == "direct":
        iioas_l = row["iioas_label"].lower().replace("-", " ").replace(",", "")
        mrio_l = row["mrio67_label"].lower().replace("-", " ").replace(",", "")
        # Comparação simplificada (primeiros 30 chars)
        if iioas_l[:30] != mrio_l[:30]:
            print(f"  DIFF S{row['iioas_idx']:02d}→M{row['mrio67_idx']:02d}: '{row['iioas_label'][:50]}' vs '{row['mrio67_label'][:50]}'")
            mismatches += 1
if mismatches == 0:
    print("  Todos os labels diretos conferem!")

# ── Salvar JSON ──────────────────────────────────────────────────────────────
json_out = {
    "metadata": {
        "description": "Crosswalk entre os 68 setores da IIOAS_BRUF_2019 (NEREUS/USP) e os 67 setores da MRIO v6.1 (IBGE)",
        "iioas_sectors": 68,
        "mrio67_sectors": 67,
        "key_difference": "IIOAS desagrega Comercio (S41 veiculos + S42 geral) que MRIO unifica em M41",
        "source_iioas": "IIOAS_BRUF_2019.xlsx - aba Setores",
        "source_mrio": "sector_labels.txt (output/intermediary/)",
    },
    "crosswalk": CROSSWALK
}
json_path = OUTPUT / "crosswalk_iioas_mrio67.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_out, f, ensure_ascii=False, indent=2)
print(f"\nJSON salvo: {json_path}")

# ── Salvar CSV ──────────────────────────────────────────────────────────────
csv_path = OUTPUT / "crosswalk_iioas_mrio67.csv"
with open(csv_path, "w", encoding="utf-8") as f:
    f.write("iioas_idx,iioas_code,iioas_label,mrio67_idx,mrio67_code,mrio67_label,mapping_type,note\n")
    for row in CROSSWALK:
        f.write(f"{row['iioas_idx']},{row['iioas_code']},\"{row['iioas_label']}\",{row['mrio67_idx']},{row['mrio67_code']},\"{row['mrio67_label']}\",{row['mapping_type']},\"{row['note']}\"\n")
print(f"CSV salvo:  {csv_path}")

# ── Imprimir tabela resumo ───────────────────────────────────────────────────
print("\n" + "="*80)
print(f"{'IIOAS':^8} {'Label IIOAS':^45} {'MRIO':^6} {'Label MRIO67':^45} {'Tipo':^10}")
print("="*80)
seen = set()
for row in CROSSWALK:
    key = (row['iioas_idx'], row['mrio67_idx'])
    if key not in seen:
        seen.add(key)
        il = row['iioas_label'][:43]
        ml = row['mrio67_label'][:43]
        t = row['mapping_type'][:9]
        flag = " <<" if t == "aggregate" else ""
        print(f"  S{row['iioas_idx']:02d}  {il:<45} → M{row['mrio67_idx']:02d}  {ml:<45}  {t}{flag}")
print("="*80)
