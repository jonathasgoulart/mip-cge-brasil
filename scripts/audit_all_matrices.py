"""
AUDITORIA COMPLETA: Verificar dimensões de todas as matrizes MIP

Este script carrega e verifica a consistência de todas as matrizes .npy
"""

import numpy as np
import os
from pathlib import Path

BASE = Path('c:/Users/jonat/Documents/MIP e CGE')
INTER_DIR = BASE / 'output/intermediary'
FINAL_DIR = BASE / 'output/final'

print("="*80)
print("AUDITORIA: Dimensões de Todas as Matrizes MIP")
print("="*80)

# Matrizes principais nacionais
matrices_to_check = {
    'Nacional': {
        'A_nas.npy': (67, 67),
        'X_nas.npy': (67,),
        'Z_nas.npy': (67, 67),
        'VAB_nacional.npy': (67,),
    },
    'Regional VAB': {
        'VAB_AC.npy': (67,),
        'VAB_SP.npy': (67,),
        'VAB_RJ.npy': (67,),
        'VAB_MG.npy': (67,),
    },
    'MRIO': {
        'A_mrio_official_v4.npy': None,  # Verificar dimensão
        'trade_prob_sectoral_v4.npy': None,
    }
}

issues = []
all_ok = True

for category, files in matrices_to_check.items():
    print(f"\n{'='*80}")
    print(f"CATEGORIA: {category}")
    print(f"{'='*80}")
    
    for filename, expected_shape in files.items():
        # Tentar em intermediary primeiro, depois final
        filepath = INTER_DIR / filename
        if not filepath.exists():
            filepath = FINAL_DIR / filename
        
        if not filepath.exists():
            issues.append(f"[ERRO] {filename}: Arquivo não encontrado")
            print(f"  [X] {filename}: NÃO ENCONTRADO")
            all_ok = False
            continue
        
        try:
            arr = np.load(filepath)
            shape_str = str(arr.shape)
            
            if expected_shape is not None:
                if arr.shape == expected_shape:
                    print(f"  [OK] {filename}: {shape_str}")
                else:
                    issues.append(f"[ERRO] {filename}: Esperado {expected_shape}, encontrado {arr.shape}")
                    print(f"  [X] {filename}: {shape_str} (esperado {expected_shape})")
                    all_ok = False
            else:
                print(f"  [?] {filename}: {shape_str}")
                
        except Exception as e:
            issues.append(f"[ERRO] {filename}: Erro ao carregar - {str(e)}")
            print(f"  [X] {filename}: ERRO ao carregar")
            all_ok = False

# Verificar se JSON e NPY têm mesmas dimensões
print(f"\n{'='*80}")
print("VERIFICAÇÃO: JSON vs NPY Consistency")
print(f"{'='*80}")

import json

json_path = BASE / 'output/intermediary/perfectionist_base_2015.json'
with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Comparar
A_npy = np.load(INTER_DIR / 'A_nas.npy')
X_npy = np.load(INTER_DIR / 'X_nas.npy')
VAB_npy = np.load(INTER_DIR / 'VAB_nacional.npy')

A_json = np.array(json_data['A_matrix'])
X_json = np.array(json_data['X_2015'])
VAB_json = np.array(json_data['VAB_plus_2015'])

print(f"\nA (Matriz de Coeficientes):")
print(f"  NPY: {A_npy.shape}")
print(f"  JSON: {A_json.shape}")
print(f"  Match: {A_npy.shape == A_json.shape}")

print(f"\nX (Produção/VBP):")
print(f"  NPY: {X_npy.shape}")
print(f"  JSON: {X_json.shape}")
print(f"  Match: {X_npy.shape == X_json.shape}")

print(f"\nVAB:")
print(f"  NPY: {VAB_npy.shape}")
print(f"  JSON: {VAB_json.shape}")
print(f"  Match: {VAB_npy.shape == VAB_json.shape}")

# Verificar se valores são iguais
if np.allclose(A_npy, A_json, rtol=1e-6):
    print(f"\n[OK] Matriz A: NPY e JSON são idênticos")
else:
    diff = np.abs(A_npy - A_json).max()
    print(f"\n[!] Matriz A: Diferença máxima = {diff}")
    issues.append(f"[AVISO] Matriz A tem diferenças entre NPY e JSON")

if np.allclose(X_npy, X_json, rtol=1e-6):
    print(f"[OK] X: NPY e JSON são idênticos")
else:
    diff = np.abs(X_npy - X_json).max()
    print(f"[!] X: Diferença máxima = {diff}")
    issues.append(f"[AVISO] X tem diferenças entre NPY e JSON")

if np.allclose(VAB_npy, VAB_json, rtol=1e-6):
    print(f"[OK] VAB: NPY e JSON são idênticos")
else:
    diff = np.abs(VAB_npy - VAB_json).max()
    print(f"[!] VAB: Diferença máxima = {diff}")
    issues.append(f"[AVISO] VAB tem diferenças entre NPY e JSON")

# Verificar MRIO
print(f"\n{'='*80}")
print("VERIFICAÇÃO ESPECIAL: MRIO Dimensions")
print(f"{'='*80}")

A_mrio_path = FINAL_DIR / 'A_mrio_official_v4.npy'
if A_mrio_path.exists():
    A_mrio = np.load(A_mrio_path)
    print(f"A_MRIO: {A_mrio.shape}")
    print(f"  Esperado: (6*67, 6*67) = (402, 402) para 6 regiões")
    if A_mrio.shape == (402, 402):
        print(f"  [OK] Dimensão correta!")
    else:
        print(f"  [!] Dimensão inesperada!")
        issues.append(f"[AVISO] A_MRIO tem dimensão inesperada: {A_mrio.shape}")

# SUMÁRIO FINAL
print(f"\n{'='*80}")
print("SUMÁRIO DA AUDITORIA")
print(f"{'='*80}")

if all_ok and len(issues) == 0:
    print("\n[SUCESSO] Todas as matrizes estão corretas e consistentes!")
    print("  - Dimensões corretas (67 setores)")
    print("  - JSON e NPY consistentes")
else:
    print(f"\n[ATENÇÃO] Encontrados {len(issues)} problemas:\n")
    for issue in issues:
        print(f"  {issue}")
        
print(f"\n{'='*80}")
