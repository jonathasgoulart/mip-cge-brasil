import numpy as np
import os
import json
from datetime import datetime

def simulate_running_shoes_impact():
    """
    Simula o impacto economico das corridas de rua na industria de tenis
    usando o modelo MIP-CGE de 67 setores.
    
    Choque: R$ 2.0 bilhoes em demanda adicional (crescimento 2024)
    Setores: Calcados (14), Comercio (40), Texteis (12)
    """
    
    print("="*80)
    print(" SIMULACAO: IMPACTO DAS CORRIDAS DE RUA NA INDUSTRIA DE TENIS")
    print("="*80)
    print("\n[CONTEXTO DO MERCADO - 2024]:")
    print("   * Praticantes: 19 milhoes (+29% vs 2023)")
    print("   * Corridas oficiais: 2.827 eventos (+29% vs 2023)")
    print("   * Movimentacao total: R$ 3,5 bilhoes")
    print("   * Choque simulado: R$ 2,0 bilhoes (demanda incremental)\n")
    
    # Diretorios
    final_dir = 'output/final'
    inter_dir = 'output/intermediary'
    
    # =========================================================================
    # 1. CARREGAR MATRIZES NACIONAIS
    # =========================================================================
    print("[STATUS] Carregando matrizes do modelo MIP-CGE...\n")
    
    try:
        # Tentar carregar A_nacional, se não existir, usar A_nas
        a_nacional_path = os.path.join(final_dir, 'A_nacional.npy')
        a_nas_path = os.path.join(inter_dir, 'A_nas.npy')
        
        if os.path.exists(a_nacional_path):
            A_nas = np.load(a_nacional_path)
        elif os.path.exists(a_nas_path):
            A_nas = np.load(a_nas_path)
        else:
            print("[ERRO] Matriz A nao encontrada!")
            return
            
        X_nas = np.load(os.path.join(inter_dir, 'X_nas.npy'))
        VAB_nas = np.load(os.path.join(inter_dir, 'VAB_nacional.npy'))
        e_coeff = np.load(os.path.join(os.path.dirname(inter_dir), 'final', 'emp_coefficients_67x27.npy'))[:, 18]  # RJ
        
        # Carregar labels dos setores
        labels_path = os.path.join(inter_dir, 'sector_labels.txt')
        with open(labels_path, 'r', encoding='utf-8') as f:
            sector_labels = [line.strip() for line in f.readlines()][:67]
        
        n = 67
        print(f"[OK] Matrizes carregadas com sucesso ({n} setores)\n")
        
    except Exception as e:
        print(f"[ERRO] ao carregar matrizes: {e}")
        return
    
    # =========================================================================
    # 2. CALCULAR INVERSA DE LEONTIEF
    # =========================================================================
    print("[CALCULOS] Calculando multiplicadores (Inversa de Leontief)...")
    
    try:
        I = np.eye(n)
        L_nas = np.linalg.inv(I - A_nas)
        
        # Multiplicador medio
        mult_medio = np.mean(np.sum(L_nas, axis=0))
        print(f"   Multiplicador medio nacional: {mult_medio:.3f}\n")
        
    except Exception as e:
        print(f"[ERRO] ao calcular Leontief: {e}")
        return
    
    # =========================================================================
    # 3. DEFINIR CHOQUE DE DEMANDA
    # =========================================================================
    print("[CHOQUE] Definindo choque de demanda setorial:")
    print("   Distribuicao baseada em pesquisa de mercado 2024\n")
    
    shock = np.zeros(n)
    
    # Indices dos setores (base zero)
    idx_calcados = 14  # Fabricacao de calcados e de artefatos de couro
    idx_comercio = 40  # Comercio por atacado e varejo
    idx_texteis = 12   # Fabricacao de produtos texteis
    
    # Valores em R$ milhoes
    shock[idx_calcados] = 1750.0  # R$ 1.750M (70%)
    shock[idx_comercio] = 500.0   # R$ 500M (20%)
    shock[idx_texteis] = 250.0    # R$ 250M (10%)
    
    choque_total = shock.sum()
    
    print(f"   [{idx_calcados}] {sector_labels[idx_calcados][:50]}")
    print(f"       R$ {shock[idx_calcados]:,.0f} M (70%)")
    print(f"\n   [{idx_comercio}] {sector_labels[idx_comercio][:50]}")
    print(f"       R$ {shock[idx_comercio]:,.0f} M (20%)")
    print(f"\n   [{idx_texteis}] {sector_labels[idx_texteis][:50]}")
    print(f"       R$ {shock[idx_texteis]:,.0f} M (10%)")
    print(f"\n   [TOTAL] CHOQUE TOTAL: R$ {choque_total:,.0f} Milhoes\n")
    
    # =========================================================================
    # 4. CALCULAR IMPACTOS NA PRODUCAO
    # =========================================================================
    print("="*80)
    print("RESULTADOS: IMPACTO NA PRODUCAO")
    print("="*80)
    
    # Impacto total (direto + indireto)
    delta_X = L_nas @ shock
    
    # Efeito direto
    efeito_direto = shock.sum()
    
    # Efeito indireto
    efeito_indireto = delta_X.sum() - efeito_direto
    
    # Efeito total
    efeito_total = delta_X.sum()
    
    # Multiplicador de producao
    multiplicador_producao = efeito_total / efeito_direto
    
    print(f"\n[DIRETO]      Efeito DIRETO:        R$ {efeito_direto:,.2f} Milhoes")
    print(f"[INDIRETO]    Efeito INDIRETO:      R$ {efeito_indireto:,.2f} Milhoes")
    print(f"[TOTAL]       Efeito TOTAL:         R$ {efeito_total:,.2f} Milhoes")
    print(f"\n[MULTIPLICADOR] MULTIPLICADOR:        {multiplicador_producao:.3f}x")
    print(f"   (cada R$ 1,00 investido gera R$ {multiplicador_producao:.2f} na economia)\n")
    
    # =========================================================================
    # 5. IMPACTO NO EMPREGO
    # =========================================================================
    print("="*80)
    print("RESULTADOS: IMPACTO NO EMPREGO")
    print("="*80)
    
    # Empregos gerados por setor
    delta_E_setor = e_coeff * delta_X
    
    # Total de empregos
    empregos_totais = delta_E_setor.sum()
    
    # Empregos por R$ milhao investido
    empregos_por_milhao = empregos_totais / choque_total
    
    print(f"\n[EMPREGOS] EMPREGOS GERADOS:     {empregos_totais:,.0f} postos de trabalho")
    print(f"[INTENSIDADE] Intensidade:       {empregos_por_milhao:.1f} empregos/R$ 1M investido\n")
    
    # =========================================================================
    # 5B. IMPACTO TRIBUTARIO
    # =========================================================================
    print("="*80)
    print("RESULTADOS: IMPACTO TRIBUTARIO (ARRECADACAO)")
    print("="*80)
    
    # Carregar coeficientes tributarios
    try:
        tax_data_path = os.path.join('output', 'tax_data.json')
        with open(tax_data_path, 'r') as f:
            tax_data = json.load(f)
        
        # Coeficientes tributarios totais por setor
        coef_tax_total = np.array(tax_data['coef_tax_total'])
        
        # Coeficientes por tipo de imposto
        coef_icms = np.array(tax_data['coef_by_type']['ICMS'])
        coef_ipi = np.array(tax_data['coef_by_type']['IPI'])
        coef_iss = np.array(tax_data['coef_by_type']['ISS'])
        coef_pis = np.array(tax_data['coef_by_type']['PIS_PASEP'])
        coef_cofins = np.array(tax_data['coef_by_type']['COFINS'])
        
        # Calcular arrecadacao por setor
        arrecadacao_total_setor = coef_tax_total * delta_X
        
        # Arrecadacao por tipo de imposto
        arrecad_icms = (coef_icms * delta_X).sum()
        arrecad_ipi = (coef_ipi * delta_X).sum()
        arrecad_iss = (coef_iss * delta_X).sum()
        arrecad_pis = (coef_pis * delta_X).sum()
        arrecad_cofins = (coef_cofins * delta_X).sum()
        
        # Total de arrecadacao
        arrecadacao_total = arrecadacao_total_setor.sum()
        
        print(f"\n[ARRECADACAO TOTAL] R$ {arrecadacao_total:,.2f} Milhoes\n")
        
        print("Decomposicao por Tipo de Imposto:")
        print(f"  ICMS (Estadual):           R$ {arrecad_icms:>10,.2f} M  ({arrecad_icms/arrecadacao_total*100:>5.1f}%)")
        print(f"  ISS (Municipal):           R$ {arrecad_iss:>10,.2f} M  ({arrecad_iss/arrecadacao_total*100:>5.1f}%)")
        print(f"  IPI (Federal):             R$ {arrecad_ipi:>10,.2f} M  ({arrecad_ipi/arrecadacao_total*100:>5.1f}%)")
        print(f"  PIS/PASEP (Federal):       R$ {arrecad_pis:>10,.2f} M  ({arrecad_pis/arrecadacao_total*100:>5.1f}%)")
        print(f"  COFINS (Federal):          R$ {arrecad_cofins:>10,.2f} M  ({arrecad_cofins/arrecadacao_total*100:>5.1f}%)")
        print(f"  {'-'*70}")
        print(f"  TOTAL:                     R$ {arrecadacao_total:>10,.2f} M  (100.0%)")
        
        # Divisao por esfera
        arrecad_estadual = arrecad_icms
        arrecad_municipal = arrecad_iss
        arrecad_federal = arrecad_ipi + arrecad_pis + arrecad_cofins
        
        print(f"\nDistribuicao por Esfera de Governo:")
        print(f"  Federal:  R$ {arrecad_federal:>10,.2f} M  ({arrecad_federal/arrecadacao_total*100:>5.1f}%)")
        print(f"  Estadual: R$ {arrecad_estadual:>10,.2f} M  ({arrecad_estadual/arrecadacao_total*100:>5.1f}%)")
        print(f"  Municipal:R$ {arrecad_municipal:>10,.2f} M  ({arrecad_municipal/arrecadacao_total*100:>5.1f}%)")
        
        # Aliquota efetiva
        aliquota_efetiva = (arrecadacao_total / efeito_total) * 100
        print(f"\n[ALIQUOTA EFETIVA] {aliquota_efetiva:.2f}% sobre a producao total")
        
        # Arrecadacao por R$ milhao de choque
        arrecad_por_milhao = arrecadacao_total / choque_total
        print(f"[INTENSIDADE] R$ {arrecad_por_milhao:.2f} de arrecadacao por R$ 1M de choque\n")
        
        # Guardar para exportacao
        tax_results = {
            "arrecadacao_total_r_milhoes": float(arrecadacao_total),
            "arrecadacao_por_tipo": {
                "icms": float(arrecad_icms),
                "iss": float(arrecad_iss),
                "ipi": float(arrecad_ipi),
                "pis": float(arrecad_pis),
                "cofins": float(arrecad_cofins)
            },
            "arrecadacao_por_esfera": {
                "federal": float(arrecad_federal),
                "estadual": float(arrecad_estadual),
                "municipal": float(arrecad_municipal)
            },
            "aliquota_efetiva_percentual": float(aliquota_efetiva),
            "arrecadacao_por_r_milhao_choque": float(arrecad_por_milhao)
        }
        
        print("[OK] Analise tributaria concluida!")
        
    except FileNotFoundError:
        print("[AVISO] tax_data.json nao encontrado. Pulando analise tributaria.")
        tax_results = None
    except Exception as e:
        print(f"[ERRO] ao calcular impostos: {e}")
        tax_results = None
    
    # =========================================================================
    # 6. TOP SETORES BENEFICIADOS
    # =========================================================================
    print("="*80)
    print("TOP 15 SETORES MAIS BENEFICIADOS")
    print("="*80)
    print(f"\n{'Pos':<5}{'Setor':<50}{'Producao (R$M)':<18}{'Empregos':>12}")
    print("-"*85)
    
    # Ordenar setores por impacto na producao
    top_indices = np.argsort(delta_X)[::-1][:15]
    
    for pos, idx in enumerate(top_indices, 1):
        nome = sector_labels[idx][:47]
        producao = delta_X[idx]
        empregos = delta_E_setor[idx]
        direto = "*D*" if shock[idx] > 0 else "   "
        
        print(f"{pos:<5}{direto} {nome:<48}{producao:>12,.1f}   {empregos:>10,.0f}")
    
    print("\n   (*D* = Recebeu choque direto)")
    
    # =========================================================================
    # 7. ANALISE DE ENCADEAMENTOS
    # =========================================================================
    print("\n" + "="*80)
    print("ANALISE DE ENCADEAMENTOS PRODUTIVOS")
    print("="*80)
    
    # Setores que NAO receberam choque direto mas foram impactados
    setores_indiretos = [(i, delta_X[i]) for i in range(n) 
                         if shock[i] == 0 and delta_X[i] > 10]
    setores_indiretos.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 10 setores impactados INDIRETAMENTE:\n")
    print(f"{'Setor':<50}{'Impacto (R$M)':>15}")
    print("-"*65)
    
    for idx, impacto in setores_indiretos[:10]:
        nome = sector_labels[idx][:47]
        print(f"{nome:<50}{impacto:>12,.1f}")
    
    # =========================================================================
    # 8. EXPORTAR RESULTADOS
    # =========================================================================
    print("\n" + "="*80)
    print("EXPORTANDO RESULTADOS")
    print("="*80 + "\n")
    
    results = {
        "metadata": {
            "data_simulacao": datetime.now().isoformat(),
            "descricao": "Impacto economico das corridas de rua na industria de tenis",
            "modelo": "MIP-CGE Brasil 67 setores",
            "ano_base": 2015,
            "ano_referencia": 2024
        },
        "mercado": {
            "praticantes_milhoes": 19.0,
            "crescimento_percentual": 29.0,
            "movimentacao_total_bilhoes": 3.5,
            "choque_simulado_bilhoes": 2.0
        },
        "choque_setorial": {
            "calcados_r_milhoes": float(shock[idx_calcados]),
            "comercio_r_milhoes": float(shock[idx_comercio]),
            "texteis_r_milhoes": float(shock[idx_texteis]),
            "total_r_milhoes": float(choque_total)
        },
        "impacto_producao": {
            "efeito_direto_r_milhoes": float(efeito_direto),
            "efeito_indireto_r_milhoes": float(efeito_indireto),
            "efeito_total_r_milhoes": float(efeito_total),
            "multiplicador": float(multiplicador_producao)
        },
        "impacto_emprego": {
            "empregos_totais": int(empregos_totais),
            "empregos_por_r_milhao": float(empregos_por_milhao)
        },
        "impacto_tributario": tax_results if tax_results else {},
        "top_setores": [
            {
                "posicao": int(pos),
                "indice": int(idx),
                "nome": sector_labels[idx],
                "impacto_producao_r_milhoes": float(delta_X[idx]),
                "empregos_gerados": int(delta_E_setor[idx]),
                "recebeu_choque_direto": bool(shock[idx] > 0)
            }
            for pos, idx in enumerate(top_indices, 1)
        ],
        "impacto_por_setor": [
            {
                "indice": int(i),
                "nome": sector_labels[i],
                "choque_r_milhoes": float(shock[i]),
                "producao_total_r_milhoes": float(delta_X[i]),
                "empregos": int(delta_E_setor[i])
            }
            for i in range(n)
        ]
    }
    
    # Salvar JSON
    output_path = os.path.join('output', 'running_shoes_impact_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Resultados salvos em: {output_path}")
    
    # Salvar CSV simplificado
    csv_path = os.path.join('output', 'running_shoes_impact_summary.csv')
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("Setor,Indice,Choque_R$M,Impacto_Producao_R$M,Empregos\n")
        for i in range(n):
            f.write(f'"{sector_labels[i]}",{i},{shock[i]:.2f},{delta_X[i]:.2f},{int(delta_E_setor[i])}\n')
    
    print(f"[OK] CSV salvo em: {csv_path}")
    
    # =========================================================================
    # 9. RESUMO EXECUTIVO
    # =========================================================================
    print("\n" + "="*80)
    print("RESUMO EXECUTIVO")
    print("="*80)
    
    print(f"""
IMPACTO ECONOMICO DAS CORRIDAS DE RUA NA INDUSTRIA DE TENIS

* Investimento/Demanda Adicional:  R$ {choque_total:,.0f} Milhoes
* Impacto Total na Producao:       R$ {efeito_total:,.0f} Milhoes
* Multiplicador de Producao:       {multiplicador_producao:.2f}x
* Empregos Gerados:                {empregos_totais:,.0f} postos
{f'* Arrecadacao Tributaria:          R$ {arrecadacao_total:,.0f} Milhoes' if tax_results else ''}

PRINCIPAIS SETORES BENEFICIADOS:
   1. {sector_labels[top_indices[0]]}
   2. {sector_labels[top_indices[1]]}
   3. {sector_labels[top_indices[2]]}
{f'''
ARRECADACAO POR ESFERA:
   - Federal:  R$ {arrecad_federal:,.0f} M ({arrecad_federal/arrecadacao_total*100:.1f}%)
   - Estadual: R$ {arrecad_estadual:,.0f} M ({arrecad_estadual/arrecadacao_total*100:.1f}%)
   - Municipal:R$ {arrecad_municipal:,.0f} M ({arrecad_municipal/arrecadacao_total*100:.1f}%)
''' if tax_results else ''}
INTERPRETACAO:
   Para cada R$ 1,00 de demanda adicional por tenis e produtos relacionados
   a corridas de rua, a economia brasileira gera R$ {multiplicador_producao:.2f} em producao
   total, criando {empregos_por_milhao:.1f} empregos por R$ 1 milhao investido{f' e R$ {arrecad_por_milhao:.2f} em arrecadacao tributaria' if tax_results else ''}.
    """)
    
    print("="*80)
    print("SIMULACAO CONCLUIDA COM SUCESSO!")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    simulate_running_shoes_impact()
