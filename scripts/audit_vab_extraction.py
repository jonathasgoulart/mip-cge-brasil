import xlrd
import os
import re

RAW_DIR = 'data/raw/contas_regionais_2021'
OUTPUT_REPORT = 'output/vab_audit_report.txt'

# Map Filename Index to UF
FILE_MAP = {
    2: 'RO', 3: 'AC', 4: 'AM', 5: 'RR', 6: 'PA', 7: 'AP', 8: 'TO',
    10: 'MA', 11: 'PI', 12: 'CE', 13: 'RN', 14: 'PB', 15: 'PE', 16: 'AL', 17: 'SE', 18: 'BA',
    20: 'MG', 21: 'ES', 22: 'RJ', 23: 'SP',
    25: 'PR', 26: 'SC', 27: 'RS',
    29: 'MS', 30: 'MT', 31: 'GO', 32: 'DF'
}

# Expected Sectors (Keywords -> Internal Index 0-17)
# Using broad keywords to match diverse headers
KEYWORDS = [
    (0, ['agricultura', 'agrícola']),
    (1, ['pecuária', 'animais']),
    (2, ['florestal', 'silvicultura']),
    (3, ['pesca', 'aquicultura']),
    (4, ['extrativas', 'minerais']),
    (5, ['transformação', 'fabril']),
    (6, ['eletricidade', 'gás', 'água', 'esgoto', 'resíduos']),
    (7, ['construção']),
    (8, ['comércio']),
    (9, ['transporte', 'armazenagem', 'correio']),
    (10, ['alojamento', 'alimentação']),
    (11, ['informação', 'comunicação']),
    (12, ['financeiras', 'seguros']),
    (13, ['imobiliárias']),
    (14, ['profissionais', 'científicas', 'técnicas']),
    (15, ['administração pública', 'defesa', 'seguridade']),
    (16, ['educação', 'saúde', 'privadas', 'mercantis']), # Note: IBGE sometimes splits Edu/Saude. Check logic.
    # Note: "Educação e saúde privadas" is one block? Or separate? 
    # "Admin Pub" is usually "Admin, defesa, educacao e saude PUBLICAS".
    # Let's verify specific headers found in debug later.
    (17, ['artes', 'cultura', 'esporte']),
    (18, ['serviços domésticos'])
]

# Note: My previous map had 18 items (0-17). Here I listed 19?
# 0-3: Agro split (4)
# 4: Ext
# 5: Transf
# 6: Util
# 7: Const
# 8: Com
# 9: Transp
# 10: Aloj
# 11: Info
# 12: Fin
# 13: Imob
# 14: Prof
# 15: Pub (Admin + Edu Pub + Saude Pub)
# 16: Priv (Edu Priv + Saude Priv) ?? Check IBGE structure.
# 17: Artes
# 18: Domesticos
# Total 19 groups? 
# Original SECTOR_MAP had 17 items? No, 0..17 is 18 items.
# Let's adjust list to match SECTOR_MAP size (18 items).
# My SECTOR_MAP had:
# 37,38 -> 5 (Eletricidade)
# 66 -> 17 (Domestico)
# So indices 0 to 17.
# Let's try to match 0-17.

EXPECTED_GROUPS = {
    0: "Agricultura",
    1: "Pecuária",
    2: "Produção Florestal",
    3: "Pesca",
    4: "Indústrias Extrativas",
    5: "Indústrias de Transformação",
    6: "Eletricidade e Água",
    7: "Construção",
    8: "Comércio",
    9: "Transporte",
    10: "Alojamento e Alimentação",
    11: "Informação e Comunicação",
    12: "Ativ. Financeiras",
    13: "Ativ. Imobiliárias",
    14: "Ativ. Profissionais",
    15: "Admin Pública (e Educ/Saúde Pub)",
    16: "Educ/Saúde Privadas", # Wait, check headers
    17: "Artes e Outros Serviços",
    18: "Serviços Domésticos" # Wait, 19 items again? 
    # Let's stick to Semantic Matching and SEE what we find. 
    # Logic: Scan file -> List found sectors -> Report.
}

def clean_text(text):
    return str(text).lower().strip().replace('ç', 'c').replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

def run_audit():
    report = []
    report.append("=== AUDITORIA DE EXTRAÇÃO DE VAB REGIONAL (2021) ===")
    report.append("Premissa: Encontrar valor '2021' em abas identificadas por palavras-chave.")
    report.append("")

    total_ufs_ok = 0
    
    for file_idx, uf in FILE_MAP.items():
        filename = f'Tabela{file_idx}.xls'
        path = os.path.join(RAW_DIR, filename)
        
        report.append(f"\nUF: {uf} (Arquivo: {filename})")
        
        if not os.path.exists(path):
            report.append("  [CRÍTICO] Arquivo NÃO ENCONTRADO.")
            continue
            
        try:
            wb = xlrd.open_workbook(path, on_demand=True)
            found_sectors = {}
            
            # Scan ALL sheets
            report.append(f"  Total de Abas: {wb.nsheets}")
            
            for s_idx in range(wb.nsheets):
                try:
                    sheet = wb.sheet_by_index(s_idx)
                    # Read first 20 rows to find Header/Title
                    header_text = ""
                    for r in range(min(20, sheet.nrows)):
                        row_vals = sheet.row_values(r)
                        # Join all text cells
                        txt = " ".join([str(x) for x in row_vals if isinstance(x, str)])
                        header_text += " " + clean_text(txt)
                        
                    # Identify Sector
                    sector_id = -1
                    sector_name = "Unknown"
                    
                    # Heuristics
                    # Heuristics (Partial matches to avoid encoding/prefix issues)
                    # "gricultura", "ecuria", "xtrativ", "ransform"
                    if "gricultura" in header_text: sector_id = 0; sector_name="Agro" 
                    elif "pecu" in header_text and "ria" in header_text: sector_id = 1; sector_name="Pecuária"
                    elif "florestal" in header_text or "silvicultura" in header_text: sector_id = 2; sector_name="Forestal"
                    elif "pesca" in header_text or "aquicultura" in header_text: sector_id = 3; sector_name="Pesca"
                    elif "xtrativa" in header_text: sector_id = 4; sector_name="Extrativas"
                    elif "transforma" in header_text: sector_id = 5; sector_name="Transformação"
                    elif "eletricidade" in header_text and "s" in header_text: sector_id = 6; sector_name="Eletricidade/Água"
                    elif "constru" in header_text: sector_id = 7; sector_name="Construção"
                    elif "com" in header_text and "rcio" in header_text: sector_id = 8; sector_name="Comércio"
                    elif "transporte" in header_text: sector_id = 9; sector_name="Transporte"
                    elif "alojamento" in header_text: sector_id = 10; sector_name="Alojamento"
                    elif "informa" in header_text and "comunica" in header_text: sector_id = 11; sector_name="Informação"
                    elif "financeira" in header_text: sector_id = 12; sector_name="Financeiras"
                    elif "imobili" in header_text: sector_id = 13; sector_name="Imobiliárias"
                    elif "profissionai" in header_text: sector_id = 14; sector_name="Profissionais"
                    elif "publica" in header_text and "administra" in header_text: sector_id = 15; sector_name="Admin Pública"
                    elif "privada" in header_text: sector_id = 16; sector_name="Edu/Saúde Priv"
                    elif "artes" in header_text: sector_id = 17; sector_name="Artes"
                    elif "dom" in header_text and "stico" in header_text: sector_id = 18; sector_name="Domésticos"
                    
                    # DEBUG SPECIFIC FOR RO SHEET 2
                    if "tabela2.xls" in filename.lower() and s_idx == 2:
                        print(f"DEBUG RO Sheet 2 Header: '{header_text[:100]}...'")
                        print(f"Matched Sector: {sector_name}")
                    
                    if sector_id != -1:
                        # Find 2021 Value
                        val_2021 = None
                        for r in range(sheet.nrows):
                            c0 = str(sheet.cell_value(r, 0)).strip()
                            # Strict Check
                            # Avoid matching "Valor ... 2010-2021"
                            if c0 == '2021' or c0 == '2021.0':
                                try:
                                    # Try Col 5
                                    val = sheet.cell_value(r, 5) 
                                    if "tabela2.xls" in filename.lower() and s_idx == 2:
                                        print(f"  DEBUG RO Found 2021 Row {r}. Val Col 5: '{val}' ({type(val)})")
                                        
                                    if isinstance(val, (int, float)):
                                        val_2021 = val
                                    elif isinstance(val, str) and val.replace('.','').replace(',','').isdigit():
                                         val_2021 = float(val)
                                except:
                                    pass
                                break
                        
                        if val_2021 is not None:
                            found_sectors[sector_id] = (sector_name, val_2021, s_idx)
                        else:
                            # Try finding last row?
                             pass
                            
                except Exception as e:
                    pass

            # Audit Found Sectors
            report.append(f"  Setores Identificados: {len(found_sectors)}")
            # Sort by ID
            total_vab = 0
            for sid in sorted(found_sectors.keys()):
                name, val, sidx = found_sectors[sid]
                report.append(f"    [{sid}] {name:<15} : {val:15,.2f} (Sheet {sidx})")
                total_vab += val
            
            report.append(f"  >> TOTAL VAB (Proxy): {total_vab:,.2f}")
            if total_vab == 0:
                report.append("  [ALERTA] VAB TOTAL É ZERO!")
            
            if len(found_sectors) < 10:
                report.append("  [ALERTA] POUCOS SETORES ENCONTRADOS! Verifique palavras-chave.")
                
        except Exception as e:
            report.append(f"  [ERRO] Falha ao ler arquivo: {e}")

    # Write Report
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print(f"Audit Complete. Report saved to {OUTPUT_REPORT}")
    # Print summary to stdout
    print("\n".join(report[:30])) # Show header and first UF

if __name__ == "__main__":
    run_audit()
