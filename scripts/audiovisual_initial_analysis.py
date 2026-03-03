"""
Análise Inicial do Setor Audiovisual Brasileiro

Análise com dados disponíveis:
- Arrecadação ICMS (CONFAZ 2024)
- Matrizes nacionais (VAB, coeficientes técnicos)
- Multiplicadores de emprego e renda
- Identificação dos setores audiovisuais
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
import sys

# Importar configurações
from audiovisual_analysis_config import *

def load_national_matrices():
    """Carrega matrizes nacionais"""
    print("Carregando matrizes nacionais...")
    
    A_nas = np.load(A_NAS_PATH)
    X_nas = np.load(X_NAS_PATH)
    VAB_nas = np.load(VAB_NAS_PATH)
    
    print(f"  A_nas: {A_nas.shape}")
    print(f"  X_nas: {X_nas.shape}")
    print(f"  VAB_nas: {VAB_nas.shape}")
    
    return A_nas, X_nas, VAB_nas

def load_social_coefficients():
    """Carrega coeficientes de emprego e renda"""
    print("\nCarregando coeficientes sociais...")
    
    emp_coeffs = np.load(EMPLOYMENT_COEFFS_PATH)
    inc_coeffs = np.load(INCOME_COEFFS_PATH)
    h_shares = np.load(HOUSEHOLD_CONSUMPTION_PATH)
    
    print(f"  Employment coefficients: {emp_coeffs.shape}")
    print(f"  Income coefficients: {inc_coeffs.shape}")
    print(f"  Household consumption shares: {h_shares.shape}")
    
    return emp_coeffs, inc_coeffs, h_shares

def load_confaz_data():
    """Carrega dados de arrecadação ICMS do CONFAZ"""
    print("\nCarregando dados CONFAZ ICMS...")
    
    with open(CONFAZ_PATH, 'r', encoding='utf-8') as f:
        confaz = json.load(f)
    
    # Converter para formato esperado se necessário
    if isinstance(confaz, list):
        # Já está no formato correto [{'uf': 'XX', 'dados': {...}}]
        print(f"  UFs disponíveis: {len(confaz)}")
    elif isinstance(confaz, dict):
        # Converter dict para list
        confaz_list = []
        for uf, dados in confaz.items():
            confaz_list.append({'uf': uf, 'dados': dados})
        confaz = confaz_list
        print(f"  UFs disponíveis: {len(confaz)}")
    
    return confaz

def load_sector_labels():
    """Carrega labels oficiais dos setores do JSON base"""
    with open(TAX_MATRIX_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('labels', SECTOR_LABELS_67)

def analyze_audiovisual_sectors():
    """Análise inicial dos setores audiovisuais"""
    print("\n" + "="*80)
    print("ANÁLISE INICIAL DO SETOR AUDIOVISUAL BRASILEIRO")
    print("="*80)
    
    # Carregar dados
    A_nas, X_nas, VAB_nas = load_national_matrices()
    emp_coeffs, inc_coeffs, h_shares = load_social_coefficients()
    confaz = load_confaz_data()
    
    # Carregar labels corretas dos setores
    SECTOR_LABELS = load_sector_labels()
    
    # =========================================================================
    # BLOCO 1: IDENTIFICAÇÃO E DIMENSIONAMENTO NACIONAL
    # =========================================================================
    print("\n" + "-"*80)
    print("BLOCO 1: DIMENSIONAMENTO NACIONAL DO SETOR AUDIOVISUAL")
    print("-"*80)
    
    # Setores core
    print("\n1.1 SETORES CORE DO AUDIOVISUAL:")
    vab_core_total = 0
    x_core_total = 0
    
    for idx in CORE_INDICES:
        vab = VAB_nas[idx]
        x = X_nas[idx]
        vab_core_total += vab
        x_core_total += x
        
        print(f"\n[{idx}] {SECTOR_LABELS_67[idx]}")
        print(f"    VAB (2015): R$ {vab:,.0f} milhões")
        print(f"    Produção Bruta: R$ {x:,.0f} milhões")
        print(f"    Coef. VAB/X: {vab/x:.3f}")
        print(f"    Emprego (empregos/R$ Mi): {emp_coeffs[idx]:.2f}")
        print(f"    Renda (R$/R$ Mi prod): R$ {inc_coeffs[idx]:,.0f}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL SETOR AUDIOVISUAL CORE (2015):")
    print(f"  VAB: R$ {vab_core_total:,.0f} milhões")
    print(f"  Produção Bruta: R$ {x_core_total:,.0f} milhões")
    print(f"  % do VAB total: {vab_core_total/VAB_nas.sum()*100:.2f}%")
    print(f"  % da Produção total: {x_core_total/X_nas.sum()*100:.2f}%")
    
    # Atualizar para 2021 (usando IPCA)
    vab_core_2021 = vab_core_total * IPCA_2015_2021
    print(f"\n  VAB atualizado (2021): R$ {vab_core_2021:,.0f} milhões")
    
    # Calcular emprego direto
    emp_direto_core = sum(emp_coeffs[idx] * X_nas[idx] for idx in CORE_INDICES)
    print(f"  Emprego direto estimado: {emp_direto_core:,.0f} pessoas")
    
    # =========================================================================
    # BLOCO 2: MULTIPLICADORES NACIONAIS
    # =========================================================================
    print("\n" + "-"*80)
    print("BLOCO 2: MULTIPLICADORES NACIONAIS (TIPO I)")
    print("-"*80)
    
    # Calcular Leontief
    I = np.eye(N_SECTORS)
    L = np.linalg.inv(I - A_nas)
    
    print("\nMultiplicadores de Produção (soma das colunas de L):")
    for idx in CORE_INDICES:
        mult_prod = L[:, idx].sum()
        print(f"  [{idx}] {SECTOR_LABELS_67[idx][:60]}: {mult_prod:.3f}")
        print(f"       (Para cada R$ 1 investido, gera R$ {mult_prod:.2f} de produção total)")
    
    # Multiplicador de emprego
    print("\nMultiplicadores de Emprego:")
    for idx in CORE_INDICES:
        # Emprego direto + indireto
        emp_mult = (emp_coeffs @ L[:, idx]) / emp_coeffs[idx] if emp_coeffs[idx] > 0 else 0
        print(f"  [{idx}] {SECTOR_LABELS_67[idx][:60]}: {emp_mult:.3f}")
        print(f"       (Para cada 1 emprego direto, gera {emp_mult:.2f} empregos totais)")
    
    # =========================================================================
    # BLOCO 3: ENCADEAMENTOS SETORIAIS
    # =========================================================================
    print("\n" + "-"*80)
    print("BLOCO 3: ENCADEAMENTOS SETORIAIS")
    print("-"*80)
    
    # Índices de Rasmussen-Hirschman
    L_mean = L.mean()
    
    print("\nÍndices de Encadeamento (Rasmussen-Hirschman):")
    for idx in CORE_INDICES:
        # Backward linkage (poder de dispersão)
        BL = L[:, idx].sum() / (L_mean * N_SECTORS)
        
        # Forward linkage (sensibilidade de dispersão)
        FL = L[idx, :].sum() / (L_mean * N_SECTORS)
        
        print(f"\n[{idx}] {SECTOR_LABELS_67[idx]}")
        print(f"    Backward Linkage (demanda outros setores): {BL:.3f}")
        print(f"    Forward Linkage (é demandado por outros): {FL:.3f}")
        
        # Classificação
        if BL > 1 and FL > 1:
            tipo = "SETOR-CHAVE (alto impacto ambos lados)"
        elif BL > 1:
            tipo = "IMPULSOR (puxa outros setores)"
        elif FL > 1:
            tipo = "ESTRATÉGICO (é muito demandado)"
        else:
            tipo = "INDEPENDENTE (baixo encadeamento)"
        
        print(f"    Classificação: {tipo}")
    
    # Top fornecedores
    print("\n" + "-"*80)
    print("TOP 10 SETORES FORNECEDORES DO AUDIOVISUAL")
    print("-"*80)
    
    for idx in CORE_INDICES:
        print(f"\n[{idx}] {SECTOR_LABELS_67[idx]}:")
        
        # Pegar coeficientes técnicos (quanto cada setor vende para audiovisual)
        A_col = A_nas[:, idx]
        top_suppliers = np.argsort(A_col)[::-1][:10]
        
        for rank, supplier_idx in enumerate(top_suppliers, 1):
            if A_col[supplier_idx] > 0:
                print(f"  {rank}. [{supplier_idx}] {SECTOR_LABELS_67[supplier_idx][:50]}: "
                      f"{A_col[supplier_idx]:.4f} ({A_col[supplier_idx]*100:.2f}%)")
    
    # =========================================================================
    # BLOCO 4: ARRECADAÇÃO ICMS (CONFAZ 2024)
    # =========================================================================
    print("\n" + "-"*80)
    print("BLOCO 4: ARRECADAÇÃO DE ICMS - SETOR AUDIOVISUAL (2024)")
    print("-"*80)
    
    # Chave relevante no CONFAZ
    cnae_key = "Soma de Divisão: 90 - ATIVIDADES ARTÍSTICAS, CRIATIVAS E DE ESPETÁCULOS"
    
    print(f"\nArrecadação por UF - {cnae_key}:")
    print(f"{'UF':<4} {'Estado':<20} {'ICMS (R$ mil)':<20} {'% Brasil':<10}")
    print("-" * 60)
    
    icms_total_brasil = 0
    icms_by_uf = {}
    
    for uf_data in confaz:
        uf = uf_data['uf']
        dados = uf_data.get('dados', {})
        icms = dados.get(cnae_key, 0)
        
        icms_by_uf[uf] = icms
        icms_total_brasil += icms
    
    # Ordenar por arrecadação
    icms_sorted = sorted(icms_by_uf.items(), key=lambda x: x[1], reverse=True)
    
    for uf, icms in icms_sorted[:10]:  # Top 10
        pct = (icms / icms_total_brasil * 100) if icms_total_brasil > 0 else 0
        uf_name = UF_NAMES.get(uf, uf)
        print(f"{uf:<4} {uf_name:<20} R$ {icms:>15,.2f}   {pct:>6.2f}%")
    
    print("-" * 60)
    print(f"{'BRASIL':<25} R$ {icms_total_brasil:>15,.2f}   100.00%")
    
    # Converter para milhões
    icms_total_milhoes = icms_total_brasil / 1000
    print(f"\nTotal ICMS audiovisual (2024): R$ {icms_total_milhoes:,.1f} milhões")
    
    # Comparar com VAB
    vab_core_2024 = vab_core_total * IPCA_2015_2024
    aliquota_efetiva = (icms_total_milhoes / vab_core_2024) * 100
    print(f"VAB estimado (2024): R$ {vab_core_2024:,.0f} milhões")
    print(f"Alíquota efetiva ICMS/VAB: {aliquota_efetiva:.2f}%")
    
    # =========================================================================
    # RESUMO EXECUTIVO
    # =========================================================================
    print("\n" + "="*80)
    print("RESUMO EXECUTIVO - SETOR AUDIOVISUAL BRASILEIRO")
    print("="*80)
    
    print(f"""
1. TAMANHO DO SETOR (2015):
   - VAB: R$ {vab_core_total:,.0f} milhões ({vab_core_total/VAB_nas.sum()*100:.2f}% do PIB)
   - Produção Bruta: R$ {x_core_total:,.0f} milhões
   - Emprego direto: ~{emp_direto_core:,.0f} pessoas
   
2. TAMANHO ATUALIZADO (2021):
   - VAB: R$ {vab_core_2021:,.0f} milhões
   
3. MULTIPLICADORES MÉDIOS:
   - Produção: {np.mean([L[:, idx].sum() for idx in CORE_INDICES]):.2f}x
   - Emprego: {np.mean([(emp_coeffs @ L[:, idx]) / emp_coeffs[idx] if emp_coeffs[idx] > 0 else 0 for idx in CORE_INDICES]):.2f}x
   
4. ARRECADAÇÃO ICMS (2024):
   - Total: R$ {icms_total_milhoes:,.1f} milhões
   - Top 3 estados: {icms_sorted[0][0]} (R$ {icms_sorted[0][1]/1000:.1f} Mi), 
                     {icms_sorted[1][0]} (R$ {icms_sorted[1][1]/1000:.1f} Mi), 
                     {icms_sorted[2][0]} (R$ {icms_sorted[2][1]/1000:.1f} Mi)
   
5. PRÓXIMOS PASSOS:
   - Análise MRIO (spillovers interestaduais)
   - Coleta de dados PNAD/RAIS (emprego detalhado)
   - Desagregação música/cinema/eventos
   - Cálculo de multiplicadores Tipo II (efeito renda)
    """)
    
    # Salvar resultados
    results = {
        "vab_2015": float(vab_core_total),
        "producao_2015": float(x_core_total),
        "vab_2021": float(vab_core_2021),
        "emprego_direto": float(emp_direto_core),
        "icms_2024_milhoes": float(icms_total_milhoes),
        "participacao_pib_pct": float(vab_core_total/VAB_nas.sum()*100),
        "setores_core": {int(idx): SECTOR_LABELS_67[idx] for idx in CORE_INDICES},
        "top_10_ufs_icms": [(uf, float(icms/1000)) for uf, icms in icms_sorted[:10]],
    }
    
    output_path = OUTPUT_DIR / "audiovisual_analysis_initial.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em: {output_path}")
    
    return results

if __name__ == "__main__":
    results = analyze_audiovisual_sectors()
