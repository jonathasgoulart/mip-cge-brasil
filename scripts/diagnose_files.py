import csv
import os
import sys

def benchmark_file(path):
    print(f"\n[DIAGNOSTICO] Verificando: {path}")
    if not os.path.exists(path):
        print("  !!! Arquivo não encontrado.")
        return
    
    # Tenta detectar encoding básico
    encodings = ['utf-8', 'latin-1', 'iso-8859-1']
    valid_enc = None
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                f.read(1024)
            valid_enc = enc
            break
        except:
            continue
    
    if not valid_enc:
        print("  !!! Falha ao detectar encoding.")
        return

    print(f"  - Encoding detectado: {valid_enc}")
    
    # Verifica dimensões
    with open(path, 'r', encoding=valid_enc) as f:
        reader = csv.reader(f)
        row_count = 0
        col_counts = set()
        for row in reader:
            row_count += 1
            col_counts.add(len(row))
            if row_count > 1000: break # Limite de amostragem
            
    print(f"  - Linhas amostradas: {row_count}")
    print(f"  - Variação de colunas: {col_counts}")

# Testar arquivos críticos
benchmark_file('data/processed/mip_2015/11.csv')
benchmark_file('data/processed/mip_2015/14.csv')
benchmark_file('data/processed/contas_regionais_2021_t1/Tabela1.1.csv')
benchmark_file('data/processed/contas_regionais_2021_t1/Tabela1.20.csv')

print("\nDiagnóstico concluído.")
sys.stdout.flush()
