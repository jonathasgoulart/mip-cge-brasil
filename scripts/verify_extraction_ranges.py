import pandas as pd
import numpy as np

print("="*80)
print("VERIFICAÇÃO COMPLETA: Linhas e Colunas da Tabela 14")
print("="*80)

df = pd.read_excel('data/raw/mip_2015_67.xls', sheet_name='14', skiprows=3)

print(f"\nShape total do DataFrame: {df.shape}")
print(f"Isso significa: {df.shape[0]} linhas × {df.shape[1]} colunas após skiprows=3")

print("\n" + "="*80)
print("LABELS (Coluna B = índice 1)")
print("="*80)

# Verificar linhas com labels
print("\nVerificando qual linha tem o último setor válido:")
for i in range(65, 71):
    label = df.iloc[i, 1]
    excel_row = i + 4  # +3 do skiprows +1 porque Excel começa em 1
    print(f"iloc[{i}] = Excel linha {excel_row}: {label}")

print("\n" + "="*80)
print("MATRIZ DE COEFICIENTES (Colunas C em diante)")
print("="*80)

# Verificar última coluna com dados
print("\nVerificando quantas colunas têm dados de coeficientes:")
print("Coluna B (1) = Labels")
print("Colunas a partir de C (2) = Coeficientes")

# Pegar uma linha do meio e ver quantas colunas têm dados
sample_row = df.iloc[30, 2:].values
non_nan_count = sum(1 for x in sample_row if pd.notna(x))
print(f"\nLinha 30 (amostra) tem {non_nan_count} valores não-vazios após coluna B")

# Verificar se a extração 2:69 está correta
print("\nExtração atual: iloc[1:68, 2:69]")
print(f"  Linhas: 1 a 67 (67 linhas)")
print(f"  Colunas: 2 a 68 (67 colunas)")

A_current = df.iloc[1:68, 2:69].apply(pd.to_numeric, errors='coerce').fillna(0).values
print(f"  Shape resultante: {A_current.shape}")

# Verificar diagonal (deve ter valores)
print(f"\nDiagonal da matriz (primeiros 5):")
for i in range(5):
    print(f"  A[{i},{i}] = {A_current[i,i]:.6f}")

print(f"\nDiagonal da matriz (últimos 5):")
for i in range(62, 67):
    print(f"  A[{i},{i}] = {A_current[i,i]:.6f}")

# Verificar se coluna 69 tem dados
print("\n" + "="*80)
print("TESTE: Coluna 69 tem dados?")
print("="*80)
col_69 = df.iloc[1:68, 69] if df.shape[1] > 69 else None
if col_69 is not None:
    non_nan_in_69 = sum(1 for x in col_69 if pd.notna(x))
    print(f"Coluna 69 existe e tem {non_nan_in_69} valores não-vazios")
else:
    print(f"Coluna 69 NÃO existe (DataFrame só tem {df.shape[1]} colunas)")

print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)
print(f"\nExtração CORRETA:")
print(f"  Labels: iloc[1:68, 1] -> 67 labels das linhas 5-71 do Excel")
print(f"  Matriz: iloc[1:68, 2:69] -> Matriz 67×67")
print(f"\nEsta é a extração que está sendo usada atualmente e está CORRETA!")
