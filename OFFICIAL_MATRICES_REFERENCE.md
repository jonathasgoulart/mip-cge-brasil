# Referencia Oficial de Matrizes e Dados do Projeto MIP-CGE Brasil

> Ultima atualizacao: 06/03/2026
> Ano-base predominante: 2019 (IIOAS-BRUF) e 2021 (PNAD Emprego/Renda)

---

## 1. MRIO Inter-Regional (Versao 7.0 - Substituição Direta)

| Arquivo | Dim. | Descricao |
|---------|------|-----------|
| `A_mrio_official_v7_0.npy` | (1809, 1809) | Matriz de coeficientes tecnicos inter-regional (27 UFs x 67 setores) baseada em Fatores Reais Observados da IIOAS. |
| `trade_shares_iioas_2019.npy` | (27, 27, 67) | Participacoes de mercado inter-regional por setor (Trade Shares), derivadas do consumo efetivo interestadual. |

**Script gerador**: `scripts/build_mrio_v7_0.py`
**Como funciona**: Substitui todo o antigo modelo gravitacional estimado pelos fluxos observados reais inter-regionais da tabela NEREUS/USP (MIIP SS), ajustados pelo VBP Real Estadual.

---

## 2. Matrizes Regionais (67x67 por UF/Regiao)

### 2.1 Matrizes por Macrorregiao (derivadas da MRIO v4)

| Arquivo | Dim. | Regiao |
|---------|------|--------|
| `A_Rio_de_Janeiro.npy` | (67, 67) | RJ (hibrida: dados locais + FLQ) |
| `A_Sao_Paulo.npy` | (67, 67) | SP |
| `A_Minas_EspiritoSanto.npy` | (67, 67) | MG + ES |
| `A_Sul.npy` | (67, 67) | PR + SC + RS |
| `A_Centro_Oeste.npy` | (67, 67) | MS + MT + GO + DF |
| `A_Norte_Nordeste.npy` | (67, 67) | Demais estados |
| `A_nacional.npy` | (67, 67) | Brasil (agregado) |

### 2.2 MIPs Estaduais Completas (Excel, 27 arquivos)

| Padrao | Dim. | Conteudo |
|--------|------|----------|
| `MIP_2021_{UF}.xlsx` | - | MIP completa do estado: abas Sintese (VBP, CI, VAB), A_local (67x67), A_inter (67x67) |

**Disponivel para**: AC, AL, AM, AP, BA, CE, DF, ES, GO, MA, MG, MS, MT, PA, PB, PE, PI, PR, RJ, RN, RO, RR, RS, SC, SE, SP, TO

### 2.3 Matrizes Especificas do RJ (Excel)

| Arquivo | Descricao |
|---------|-----------|
| `A_RIO_LOCAIS_67x67.xlsx` | Coeficientes locais do RJ (intra-estado) |
| `A_RIO_INTER_67x67.xlsx` | Coeficientes inter-regionais do RJ (importados de outros estados) |
| `A_RIO_OFFICIAL_Hybrid_67x67.xlsx` | Hibrida oficial (combina locais + inter) |

---

## 3. Emprego e Renda (PNAD 2021) ★ OFICIAL

| Arquivo | Dim. | Descricao |
|---------|------|-----------|
| `employment_matrix_67x27.npy` | (67, 27) | PO (Pessoas Ocupadas) absoluta por setor x UF |
| `income_matrix_67x27.npy` | (67, 27) | Renda anual (R$ Mi) por setor x UF |
| `emp_coefficients_67x27.npy` | (67, 27) | Coeficiente de emprego: PO / VAB (empregos por R$ Mi de VAB) |
| `inc_coefficients_67x27.npy` | (67, 27) | Coeficiente de renda: Renda / VAB (R$ Mi de renda por R$ Mi de VAB) |
| `employment_income_67x27_summary.xlsx` | - | Resumo legivel (3 abas: Emprego, Renda, Metadata) |

**Fonte**: PNAD Continua 2021 - 4o trimestre (`data/sources/Massa de rendimento e PO - PNADC042021.xlsx`)
**Script gerador**: `scripts/generate_employment_income_matrix.py`
**Cobertura**: 67/67 setores com dados. 223 codigos CNAE mapeados individualmente.
**Ordem das UFs** (eixo 1, indices 0-26): RO, AC, AM, RR, PA, AP, TO, MA, PI, CE, RN, PB, PE, AL, SE, BA, MG, ES, **RJ (18)**, SP, PR, SC, RS, MS, MT, GO, DF

**Como usar**:
```python
import numpy as np
emp = np.load('output/final/emp_coefficients_67x27.npy')
rj = emp[:, 18]   # 67 coeficientes do RJ
sp = emp[:, 19]   # 67 coeficientes de SP
```

---

## 4. VAB Regional

### 4.1 Dados processados (JSON)

| Arquivo | Descricao |
|---------|-----------|
| `data/processed/2021_final/vab_regional.json` | VAB (R$ Mi) por UF x 67 setores. Dict: `{UF: [67 valores]}` |
| `data/processed/2021_final/vab_nacional.npy` | VAB nacional (67 setores) |

### 4.2 VAB por UF (intermediario, .npy)

| Padrao | Dim. | Descricao |
|--------|------|-----------|
| `VAB_{UF}.npy` | (67,) | VAB de cada estado (67 setores, R$ Mi) |
| `VAB_{Regiao}.npy` | (67,) | VAB por macrorregiao agregada |

---

## 5. Dados Fiscais (Base 2019)

| Arquivo | Descricao |
|---------|-----------|
| `data/processed/2021_final/tax_matrix_2019.json` | Total Nacional dos Tributos IBGE expandidos por IPCA. |
| `data/processed/2021_final/tax_matrix_by_state_2019.json` | Matriz oficial de tributos distribuidos por UF (Sharing Factors), com taxas Estado-Especificas (100% calibrado para simulacoes regionais). |
| `data/processed/2021_final/export_ratios.json` | Razoes de exportacao por setor. |

---

## 6. Matrizes Nacionais (intermediarias)

| Arquivo | Dim. | Descricao |
|---------|------|-----------|
| `A_nas.npy` | (67, 67) | Matriz A nacional original (extraida do IBGE/SCN) |
| `Z_nas.npy` | (67, 67) | Matriz de fluxos intermediarios (Z) nacional |
| `Z_nacional.npy` | (67, 67) | Idem (copia de trabalho) |
| `X_nas.npy` | (67,) | Producao total por setor (nacional) |
| `X_nacional.npy` | (67,) | Idem (subconjunto) |

---

## 7. Consumo das Familias

| Arquivo | Dim. | Descricao |
|---------|------|-----------|
| `household_consumption_shares_67_v3.npy` | (67,) | Participacao de cada setor no consumo das familias (versao atual) |
| `household_consumption_shares_67.npy` | (67,) | Versao anterior |
| `household_consumption_shares.npy` | (67,) | Versao original |

---

## 8. Encadeamentos e Multiplicadores

| Arquivo | Descricao |
|---------|-----------|
| `linkages.json` | Backward (BL) e Forward (FL) linkages por estado e setor |
| `validation_multipliers.json` | Multiplicadores de validacao |
| `sector_labels.txt` | Nomes dos 67 setores (para labels de graficos) |

---

## Estrutura de Diretorios

```
output/
  final/               ← OFICIAL: tudo que e usado em producao
  intermediary/         ← Dados de suporte e intermediarios
  regional_matrices/    ← MIPs estaduais (27 Excel)
  archive/              ← Versoes obsoletas (nao mexer)

data/
  sources/              ← Dados brutos (PNAD, etc.) — NAO MEXER
  processed/2021_final/ ← Dados processados (VAB, fiscal)
```
