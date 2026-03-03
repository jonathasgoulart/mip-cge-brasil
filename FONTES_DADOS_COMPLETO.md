# MAPEAMENTO COMPLETO: Fontes de Dados de Todas as Matrizes MIP

## 🚨 PROBLEMA IDENTIFICADO

**Extração atual do JSON usa linhas ERRADAS:**
- ❌ **Atual:** `iloc[1:68]` = Linhas 5-71 do Excel  
- ✅ **Correto:** `iloc[2:69]` = Linhas 6-72 do Excel

**Impacto:** Todos os índices estão deslocados em -1!

---

## Fontes de Dados Detalhadas

### 1. JSON: `perfectionist_base_2015.json`

**Script:** `extract_perfectionist_base.py`  
**Fonte:** `data/raw/mip_2015_67.xls` (Excel IBGE oficial)

#### Tabela 14 (Matriz A + Labels)
```python
skiprows=3
Labels: df.iloc[1:68, 1]  # ❌ ERRADO! Deveria ser [2:69]
Matriz A: df.iloc[1:68, 2:69]  # ❌ ERRADO! Deveria ser [2:69, 2:69]
```

**Linhas extraídas (atual ERRADO):**
- Excel linhas 5-71 (falta linha 72, pega linha extra 4)
- Primeira label: `nan` (linha 5 Excel) ← ERRO!
- Segunda label: "Agricultura" (linha 6 Excel)

**Linhas CORRETAS (deveria ser):**
- Excel linhas 6-72
- Primeira label: "Agricultura" (linha 6 Excel)
- Última label: "Serviços domésticos" (linha 72 Excel)

#### Tabela 01 (VBP/Produção)
```python
skiprows=3
Linha "Total", colunas 7:74
X_2015 = vbp_row.iloc[7:74]
```
**Status:** ⚠️ Precisa verificar se linha 7 está correta

#### Tabela 02 (Consumo Intermediário)
```python
skiprows=3
Linha "Total", colunas 2:69
CI_total_2015 = ci_total_row.iloc[2:69]
```
**Status:** ⚠️ Precisa verificar

#### Tabela 12 (Importados)
```python
skiprows=3
A_imp = df_12.iloc[1:111, 2:69]  # 110 produtos x 67 atividades
```
**Status:** ⚠️ Precisa verificar

---

### 2. NPY: `A_nas.npy`, `X_nas.npy`, `VAB_nacional.npy`

**Script:** `finalize_national.py`  
**Fonte:** `data/processed/mip_2015/*.csv` (CSVs processados)

#### A_nas (Matriz de Coeficientes)
```python
Arquivo: data/processed/mip_2015/14.csv
skiprows: 5 linhas (via next(reader))
Extração: row[2:69] para cada uma das 67 linhas
```
**Status:** ⚠️ Fonte CSV - verificar origem dos CSVs

#### X_nas (VBP)
```python
Arquivo: data/processed/mip_2015/01.csv
Linha "Total", colunas j+7 (j de 0 a 66)
```

#### VAB_nacional
```python
Calculado: VAB = X_nas - CI_total
CI_total de: data/processed/mip_2015/02.csv
Linha "Total", colunas j+2 (j de 0 a 66)
```

---

### 3. MRIO: `A_mrio_official_v4.npy`

**Script:** `mrio_official_v4.py`  
**Fonte:** Múltiplas

```python
Base: A_nas.npy (Nacional)
Regionalização: VAB_{UF}.npy (27 UFs)
Trade flows: Modelo gravitacional
```

**Dimensão:** 27 UFs × 67 setores = 1809 × 1809

---

### 4. VAB Regional: `VAB_{UF}.npy`

**Scripts:** Vários (`extract_vab_real.py`, `rebuild_regional_vab_v3.py`, etc.)  
**Fontes:**
- Contas Regionais IBGE (API Sidra)
- Distribuição por CNAE → MIP 67 setores

---

## 🔍 Causa da Divergência VAB

### JSON (R$ 5,2 trilhões)
- ❌ Extração COM ERRO de índices
- Fonte: Excel direto
- Incluindo: linha extra nan + faltando última linha válida

### NPY (R$ 7,7 trilhões)  
- Fonte: CSVs processados
- ⚠️ CSVs podem ter processamento diferente do Excel original

---

## ✅ Ações Necessárias

### URGENTE:
1. **Corrigir `extract_perfectionist_base.py`:**
   - Mudar `iloc[1:68]` → `iloc[2:69]`
   - Regenerar JSON

2. **Verificar origem dos CSVs:**
   - Como foram gerados de `mip_2015_67.xls`?
   - Quais transformações foram aplicadas?

3. **Revalidar TODOS os índices audiovisuais:**
   - Com correção, índices mudarão!

### Médio Prazo:
4. Documentar processo completo de dados
5. Criar testes automatizados de consistência
6. Estabelecer UMA fonte canônica oficial

---

## 📋 Checklist de Verificação

- [ ] Verificar linha inicial Excel Tabela 14 (linha 6 ou 5?)
- [ ] Confirmar que linha 72 tem "Serviços domésticos"
- [ ] Mapear origem dos CSVs em `data/processed/`
- [ ] Reextrair JSON com índices corretos
- [ ] Comparar novo JSON com NPY
- [ ] Atualizar índices audiovisuais
- [ ] Revalidar análise completa
