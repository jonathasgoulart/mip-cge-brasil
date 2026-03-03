import pandas as pd
import os

def peek_csv(file_path):
    print(f"\n--- Peeking {file_path} ---")
    try:
        # Load with low_memory to be safe
        df = pd.read_csv(file_path, nrows=10)
        print("Columns:", df.columns.tolist())
        print("First 3 rows:\n", df.head(3).to_string())
    except Exception as e:
        print(f"Error: {e}")

# Check some processed files
peek_csv('data/processed/mip_2015/01.csv')

# Check first few Tabela1 files to find the year 2021
for i in range(1, 20):
    path = f'data/processed/contas_regionais_2021/Tabela1.{i}.csv'
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=5)
        # IBGE tables usually have the year in the first few columns or as a value
        print(f"Checking {path}: {df.iloc[0, :5].values}")
