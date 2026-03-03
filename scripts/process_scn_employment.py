"""
Processa dados de Pessoal Ocupado do IBGE SCN 2021
Para uso quando o usuário baixar o arquivo manualmente

INSTRUÇÕES:
1. Baixe o arquivo SCN com Pessoal Ocupado do IBGE
2. Salve em: data/scn_pessoal_ocupado_2021.xls (ou .xlsx)
3. Execute: python scripts/process_scn_employment.py
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

DATA_DIR = Path('data')
OUTPUT_DIR = Path('output/intermediary')

def processar_scn_employment():
    """
    Processa arquivo SCN de Pessoal Ocupado
    """
    
    print("="*70)
    print("PROCESSAMENTO: Pessoal Ocupado SCN 2021")
    print("="*70)
    
    # Procurar arquivo
    possible_files = [
        'scn_pessoal_ocupado_2021.xls',
        'scn_pessoal_ocupado_2021.xlsx',
        'tab3_scn_2021.xls',
        'tab3_scn_2021.xlsx',
    ]
    
    arquivo_encontrado = None
    for filename in possible_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            arquivo_encontrado = filepath
            break
    
    if not arquivo_encontrado:
        print("\n[ERRO] Arquivo não encontrado!")
        print("\nArquivos procurados:")
        for f in possible_files:
            print(f"  - data/{f}")
        print("\nPor favor:")
        print("1. Baixe o arquivo do IBGE")
        print("2. Salve em data/scn_pessoal_ocupado_2021.xls")
        print("3. Execute este script novamente")
        return False
    
    print(f"\n[OK] Arquivo encontrado: {arquivo_encontrado.name}")
    
    # Ler arquivo
    print("\n[1/5] Lendo arquivo Excel...")
    try:
        # Tentar diferentes formatos
        df = pd.read_excel(arquivo_encontrado, sheet_name=0, header=None)
        print(f"  Shape: {df.shape}")
        print(f"  Primeiras linhas:")
        print(df.head())
        
    except Exception as e:
        print(f"  [ERRO] {e}")
        return False
    
    # Aqui você precisará me dizer a estrutura exata
    print("\n[!] ATENÇÃO: Estrutura do arquivo")
    print("Por favor, abra o arquivo e me diga:")
    print("  1. Em qual linha começam os dados?")
    print("  2. Quais são os nomes das colunas?")
    print("  3. Qual coluna tem 'Pessoal Ocupado' de 2021?")
    print("  4. Qual coluna tem os nomes dos setores/atividades?")
    
    # Salvar amostra para inspeção
    sample_file = OUTPUT_DIR / 'scn_employment_sample.json'
    sample = {
        "shape": list(df.shape),
        "columns": [str(c) for c in df.columns[:10]],
        "first_rows": df.head(10).to_dict(),
    }
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Amostra salva em: {sample_file}")
    print("\nPróximo passo: Me envie essas informações para eu ajustar o script!")
    
    return True

if __name__ == "__main__":
    success = processar_scn_employment()
    
    if success:
        print("\n" + "="*70)
        print("AGUARDANDO: Informações sobre estrutura do arquivo")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("AGUARDANDO: Download do arquivo")
        print("="*70)
