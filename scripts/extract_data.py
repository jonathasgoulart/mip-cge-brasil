import zipfile
import os

zip_path = 'data/raw/contas_regionais_2021.zip'
extract_path = 'data/raw/contas_regionais_2021'

if not os.path.exists(extract_path):
    os.makedirs(extract_path)

print(f"Extracting {zip_path} to {extract_path}...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

print("Extraction Complete.")
print("Files in extract path:")
for file in os.listdir(extract_path):
    print(f" - {file}")
