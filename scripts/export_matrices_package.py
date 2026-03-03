"""
Script de Exportação Automática das Matrizes MIP-CGE
Este script copia todos os arquivos essenciais para uma pasta de exportação
pronta para compartilhamento.
"""

import os
import shutil
from pathlib import Path

def create_export_package():
    # Diretório base do projeto
    base_project = r"C:\Users\jonat\Documents\MIP e CGE"
    
    # Diretório de destino (criar na área de trabalho)
    desktop = Path.home() / "Desktop"
    export_dir = desktop / "MIP_CGE_Export"
    
    # Criar estrutura de pastas
    folders = {
        'national': export_dir / 'matrices' / 'national',
        'regional': export_dir / 'matrices' / 'regional',
        'social': export_dir / 'matrices' / 'social',
        'fiscal': export_dir / 'matrices' / 'fiscal',
        'scripts': export_dir / 'scripts',
        'docs': export_dir / 'docs'
    }
    
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("EXPORTAÇÃO DE MATRIZES MIP-CGE")
    print("="*60)
    
    # ========== MATRIZES NACIONAIS ==========
    national_files = [
        'A_nas.npy',
        'Z_nas.npy',
        'X_nas.npy',
        'VAB_nacional.npy'
    ]
    
    print("\n[1/5] Copiando Matrizes Nacionais...")
    src_national = Path(base_project) / 'output' / 'intermediary'
    for file in national_files:
        src = src_national / file
        dst = folders['national'] / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (não encontrado)")
    
    # ========== MATRIZES REGIONAIS ==========
    regional_files = [
        'A_RIO_LOCAIS_67x67.xlsx',
        'A_RIO_INTER_67x67.xlsx',
        'MIP_2021_RJ.xlsx'
    ]
    
    print("\n[2/5] Copiando Matrizes Regionais (RJ)...")
    src_regional = Path(base_project) / 'output' / 'regional_matrices'
    for file in regional_files:
        src = src_regional / file
        dst = folders['regional'] / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (não encontrado)")
    
    # ========== MATRIZES SOCIAIS ==========
    social_files = [
        # Removido: coeficientes 1D substituidos por emp_coefficients_67x27.npy em output/final/
        # Removido: coeficientes 1D substituidos por inc_coefficients_67x27.npy em output/final/
        'household_consumption_shares_67.npy'
    ]
    
    print("\n[3/5] Copiando Coeficientes Sociais...")
    src_social = Path(base_project) / 'output' / 'intermediary'
    for file in social_files:
        src = src_social / file
        dst = folders['social'] / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (não encontrado)")
    
    # ========== MATRIZES FISCAIS ==========
    fiscal_files = [
        'tax_matrix.json'
    ]
    
    print("\n[4/5] Copiando Dados Fiscais...")
    src_fiscal = Path(base_project) / 'data' / 'processed' / '2021_final'
    for file in fiscal_files:
        src = src_fiscal / file
        dst = folders['fiscal'] / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (não encontrado)")
    
    # ========== ARQUIVOS DE APOIO ==========
    support_files = [
        ('output/mip_67_sectors.json', 'docs/mip_67_sectors.json'),
        ('output/employment_income_summary_2021.csv', 'docs/employment_income_summary_2021.csv')
    ]
    
    print("\n[5/5] Copiando Arquivos de Apoio...")
    for src_rel, dst_rel in support_files:
        src = Path(base_project) / src_rel
        dst = export_dir / dst_rel
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {dst_rel}")
        else:
            print(f"  ✗ {dst_rel} (não encontrado)")
    
    # ========== CRIAR README ==========
    readme_content = """# Matrizes MIP-CGE 2021 - Exportação Stand-Alone

## Conteúdo deste Pacote

Este pacote contém todas as matrizes necessárias para realizar análises de impacto econômico usando o modelo MIP-CGE do Brasil (base 2021, 67 setores).

### Estrutura de Pastas
- `matrices/national/` - Matrizes nacionais (A, Z, VBP, VAB)
- `matrices/regional/` - Matrizes regionalizadas do Rio de Janeiro
- `matrices/social/` - Coeficientes de emprego e renda (PNAD 2021)
- `matrices/fiscal/` - Alíquotas de impostos por setor
- `docs/` - Arquivos de apoio e descrição dos setores

## Requisitos de Software

```bash
pip install numpy pandas openpyxl
```

## Próximos Passos

Consulte o arquivo `export_guide.md` na pasta de artefatos do Antigravity para exemplos completos de uso.

---
**Versão**: 2021 (67 setores)
"""
    
    readme_path = export_dir / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"\n  ✓ README.md criado")
    
    # ========== FINALIZAÇÃO ==========
    print("\n" + "="*60)
    print("EXPORTAÇÃO CONCLUÍDA!")
    print("="*60)
    print(f"\nPasta de exportação criada em:")
    print(f"  {export_dir}")
    print(f"\nVocê pode compactar esta pasta e compartilhar com outras pessoas.")
    print("="*60)

if __name__ == "__main__":
    create_export_package()
