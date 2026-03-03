"""
VALIDAÇÃO: Extração MIP 2015 - Verificar se JSON está correto

Este script mostra EXATAMENTE como os dados foram extraídos do Excel oficial
e permite validar manualmente comparando com o arquivo mip_2015_67.xls
"""

import pandas as pd
import numpy as np
import json

print("="*80)
print("VALIDAÇÃO: Origem dos Dados no JSON")
print("="*80)

# Arquivo fonte
excel_path = 'data/raw/mip_2015_67.xls'
json_path = 'output/intermediary/perfectionist_base_2015.json'

print(f"\nArquivo Excel: {excel_path}")
print(f"Arquivo JSON:  {json_path}\n")

# ===========================================================================
# LABELS DOS SETORES
# ===========================================================================
print("="*80)
print("1. LABELS DOS SETORES (Nomes das atividades)")
print("="*80)
print("\nABA USADA: Tabela 14 (sheet_name='14')")
print("DESCRIÇÃO: Matriz de Coeficientes Técnicos Simétrica (Destino x Destino)")
print("EXTRAÇÃO:  skiprows=3, iloc[1:68, 1]")
print("           -> Linhas 5-71 do Excel (após pular 3+1 cabeçalhos)")
print("           -> Coluna B (índice 1) com descrições dos setores\n")

df_14 = pd.read_excel(excel_path, sheet_name='14', skiprows=3)
labels_extracted = df_14.iloc[1:68, 1].astype(str).values

print(f"Total de labels extraídas: {len(labels_extracted)}")
print("\nPrimeiras 5 labels:")
for i in range(5):
    print(f"  [{i}] {labels_extracted[i]}")

print("\nÚltimas 5 labels:")
for i in range(62, 67):
    print(f"  [{i}] {labels_extracted[i]}")

print("\nLabels AUDIOVISUAIS identificadas:")
for i, label in enumerate(labels_extracted):
    if any(keyword in label.lower() for keyword in ['edição', 'televisão', 'rádio', 'cinema', 'artística', 'espetáculo']):
        print(f"  [{i}] {label}")

# Comparar com JSON
with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

print(f"\n[OK] JSON contem {len(json_data['labels'])} labels")
print(f"[OK] Match com extração: {len(labels_extracted) == len(json_data['labels'])}")

# ===========================================================================
# MATRIZ A (COEFICIENTES TÉCNICOS)
# ===========================================================================
print("\n" + "="*80)
print("2. MATRIZ A - Coeficientes Técnicos (67x67)")
print("="*80)
print("\nABA USADA: Tabela 14 (sheet_name='14')")
print("DESCRIÇÃO: aij = quanto o setor j compra do setor i por unidade produzida")
print("EXTRAÇÃO:  iloc[1:68, 2:69]")
print("           -> Linhas 5-71, Colunas C-BS do Excel\n")

A_extracted = df_14.iloc[1:68, 2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values
print(f"Dimensão da matriz A: {A_extracted.shape}")
print(f"Soma total dos coeficientes: {A_extracted.sum():,.4f}")
print(f"Valor mínimo: {A_extracted.min():.6f}")
print(f"Valor máximo: {A_extracted.max():.6f}")

# Verificar se é menor que 1 (propriedade dos coeficientes técnicos)
col_sums = A_extracted.sum(axis=0)
print(f"\nSoma por coluna (deve ser < 1 para ser produtivo):")
print(f"  Mínimo: {col_sums.min():.4f}")
print(f"  Máximo: {col_sums.max():.4f}")
print(f"  Média:  {col_sums.mean():.4f}")

A_json = np.array(json_data['A_matrix'])
print(f"\n[OK] Dimensão no JSON: {A_json.shape}")
print(f"[OK] Match com extração: {np.allclose(A_extracted, A_json)}")

# ===========================================================================
# PRODUÇÃO (VBP) E CONSUMO INTERMEDIÁRIO
# ===========================================================================
print("\n" + "="*80)
print("3. VALOR BRUTO DE PRODUÇÃO (X) - Vetor 67")
print("="*80)
print("\nABA USADA: Tabela 01 (sheet_name='01') - RECURSOS")
print("DESCRIÇÃO: Total de recursos por atividade")
print("EXTRAÇÃO:  Linha 'Total' (busca automática), colunas 7:74")
print("           -> Colunas H-BX do Excel (67 atividades)\n")

df_01 = pd.read_excel(excel_path, sheet_name='01', skiprows=3)
total_row_mask = df_01.iloc[:, 0].astype(str).str.contains('Total', case=False, na=False)
vbp_row = df_01[total_row_mask].iloc[0]
X_extracted = vbp_row.iloc[7:74].apply(pd.to_numeric, errors='coerce').fillna(0).values

print(f"Total de valores extraídos: {len(X_extracted)}")
print(f"VBP total Brasil: R$ {X_extracted.sum():,.0f} milhões")
print(f"\nMaiores setores por VBP:")
top_5 = np.argsort(X_extracted)[::-1][:5]
for rank, idx in enumerate(top_5, 1):
    print(f"  {rank}. [{idx}] {labels_extracted[idx][:50]}: R$ {X_extracted[idx]:,.0f} Mi")

X_json = np.array(json_data['X_2015'])
print(f"\n[OK] Match com JSON: {np.allclose(X_extracted, X_json)}")

print("\n" + "="*80)
print("4. CONSUMO INTERMEDIÁRIO (CI) - Vetor 67")
print("="*80)
print("\nABA USADA: Tabela 02 (sheet_name='02') - USOS")
print("DESCRIÇÃO: Total de consumo intermediário por atividade")
print("EXTRAÇÃO:  Linha 'Total', colunas 2:69")
print("           -> Soma do que cada setor compra de insumos\n")

df_02 = pd.read_excel(excel_path, sheet_name='02', skiprows=3)
ci_total_row_mask = df_02.iloc[:, 0].astype(str).str.contains('Total', case=False, na=False)
ci_total_row = df_02[ci_total_row_mask].iloc[0]
CI_extracted = ci_total_row.iloc[2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values

print(f"CI total Brasil: R$ {CI_extracted.sum():,.0f} milhões")

CI_json = np.array(json_data['CI_total_2015'])
print(f"[OK] Match com JSON: {np.allclose(CI_extracted, CI_json)}")

# ===========================================================================
# VAB CALCULADO
# ===========================================================================
print("\n" +"="*80)
print("5. VALOR ADICIONADO BRUTO (VAB) - Calculado")
print("="*80)
print("\nFÓRMULA: VAB = VBP - CI")
print("         (Produção - Insumos = Valor Adicionado)\n")

VAB_calculated = X_extracted - CI_extracted
VAB_json = np.array(json_data['VAB_plus_2015'])

print(f"VAB total Brasil: R$ {VAB_calculated.sum():,.0f} milhões")
print(f"% do VBP: {VAB_calculated.sum()/X_extracted.sum()*100:.2f}%")

print(f"\n[OK] Match com JSON: {np.allclose(VAB_calculated, VAB_json)}")

print("\n" + "="*80)
print("SETORES AUDIOVISUAIS - Validação Cruzada")
print("="*80)

audiovisual_indices = {
    47: "Edição e edição integrada à impressão",
    48: "Atividades de televisão, rádio, cinema e gravação/edição de som e imagem",
    64: "Atividades artísticas, criativas e de espetáculos"
}

print("\nDados extraídos do Excel vs. JSON:")
print(f"{'Idx':<4} {'VAB (Excel)':<15} {'VAB (JSON)':<15} {'Match':<8} Setor")
print("-"*90)

for idx, descricao in audiovisual_indices.items():
    vab_excel = VAB_calculated[idx]
    vab_json_val = VAB_json[idx]
    match = "[OK]" if abs(vab_excel - vab_json_val) < 0.01 else "[X]"
    print(f"{idx:<4} R$ {vab_excel:>11,.0f}  R$ {vab_json_val:>11,.0f}  {match:<8} {descricao[:40]}")

print("\n" + "="*80)
print("CONCLUSÃO DA VALIDAÇÃO")
print("="*80)

validations = [
    ("Labels (67 setores)", len(labels_extracted) == len(json_data['labels'])),
    ("Matriz A (67x67)", np.allclose(A_extracted, A_json)),
    ("VBP/Produção (67)", np.allclose(X_extracted, X_json)),
    ("Consumo Intermediário (67)", np.allclose(CI_extracted, CI_json)),
    ("VAB Calculado (67)", np.allclose(VAB_calculated, VAB_json)),
]

all_valid = all(v[1] for v in validations)

for item, status in validations:
    symbol = "[OK]" if status else "[X]"
    print(f"{symbol} {item}: {'OK' if status else 'ERRO'}")

print("\n" + ("="*80))
if all_valid:
    print("RESULTADO: JSON ESTÁ CORRETO E CORRESPONDE AO EXCEL OFICIAL!")
    print("Todas as verificações passaram. Os dados foram extraídos corretamente.")
else:
    print("ATENÇÃO: Foram encontradas divergências!")
    print("Revisar o processo de extração.")
print("="*80)
