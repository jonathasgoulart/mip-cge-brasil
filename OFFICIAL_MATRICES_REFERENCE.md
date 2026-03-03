# Referencia Oficial de Matrizes e Dados do Projeto MIP-CGE Brasil

> Ultima atualizacao: 28/02/2026
> Ano-base: 2021

---

## 1. MRIO Inter-Regional (Modelo Gravitacional v4)

| Arquivo | Dim. | Descricao |
|---------|------|-----------|
| `A_mrio_official_v4.npy` | (1809, 1809) | Matriz de coeficientes tecnicos inter-regional (27 UFs x 67 setores = 1809) |
| `trade_prob_sectoral_v4.npy` | (27, 27, 67) | Probabilidades de comercio inter-regional por setor (modelo gravitacional com beta setorial) |
| `beta_sectoral_calibration.json` | - | Parametros beta do modelo gravitacional: 0.8 (commodities), 1.5 (manufatura), 3.0 (servicos) |
| `region_order_v4.txt` | - | Ordem das 27 UFs na MRIO |

**Script gerador**: `scripts/mrio_official_v4.py`
**Como funciona**: Combina a matriz nacional com o modelo gravitacional de distancias (Haversine) e beta setorial para estimar fluxos de comercio inter-regional. Para o RJ, usa matrizes regionais hibridas especificas.

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

## 5. Dados Fiscais

| Arquivo | Descricao |
|---------|-----------|
| `ICMS_Burden_RJ_Official.csv/.xlsx` | Carga de ICMS por setor no RJ (ICMS/VBP) |
| `data/processed/2021_final/tax_matrix.json` | Aliquotas de ISS e ICMS por setor |
| `data/processed/2021_final/tax_matrix_hybrid_by_state.json` | Aliquotas fiscais hibridas por estado |
| `data/processed/2021_final/export_ratios.json` | Razoes de exportacao por setor |

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
