# ⚡ Guia de Referência Rápida - MRIO Brasil

> **Comandos essenciais e atalhos para o dia a dia**

---

## 🚀 Comandos Essenciais

### Pipeline Completo (Execução Sequencial)

```bash
# Navegue até o diretório do projeto
cd "c:\Users\jonat\Documents\MIP e CGE"

# Execute o pipeline completo
python scripts/finalize_national.py && ^
python scripts/slim_extract.py && ^
python scripts/integrated_pipeline.py && ^
python scripts/validate_results.py && ^
python scripts/setup_employment_params.py && ^
python scripts/simulate_employment.py && ^
python scripts/simulate_spillover_carnaval.py && ^
python scripts/export_dashboard_data.py
```

### Dashboard

```bash
# Iniciar servidor
cd dashboard
python -m http.server 8000

# Acesse: http://localhost:8000
```

---

## 📂 Arquivos Importantes

| Arquivo | Descrição | Localização |
|---------|-----------|-------------|
| `finalize_national.py` | Extrai base nacional (X, Z, VAB, A_nas) | `scripts/` |
| `slim_extract.py` | Extrai VAB regional (2021) | `scripts/` |
| `integrated_pipeline.py` | Regionaliza matriz (FLQ) | `scripts/` |
| `atomic_math.py` | Cálculos matemáticos (FLQ, Leontief) | `scripts/` |
| `validate_results.py` | Valida consistência | `scripts/` |
| `export_dashboard_data.py` | Gera `data.json` | `scripts/` |
| `index.html` | Dashboard principal | `dashboard/` |
| `data.json` | Dados do dashboard | `dashboard/` |

---

## 🔑 Variáveis Chave

### No Código

| Variável | Significado | Tipo | Exemplo |
|----------|-------------|------|---------|
| `A_nas` | Coeficientes técnicos nacionais | `(67, 67)` | `A_nas[i, j]` = insumo de `i` em `j` |
| `X_nas` | Produção total nacional | `(67,)` | `[X_1, X_2, ..., X_67]` |
| `VAB_nas` | Valor Adicionado Bruto nacional | `(67,)` | `VAB_j = X_j - Z_sum_j` |
| `L_r` | Inversa de Leontief regional | `(67, 67)` | `L_r = (I - A_r)^-1` |
| `e_j` | Coeficiente de emprego | `(67,)` | Pessoas/R$1M |
| `delta` | Parâmetro FLQ | `float` | `0.3` (padrão) |

### Regiões (Índices)

```python
REGIAO_MAPPING = {
    0: "Sao_Paulo",
    1: "Rio_Janeiro",
    2: "Sul",
    3: "Centro_Oeste",
    4: "Norte_Nordeste",
    5: "MG_ES"
}
```

---

## 🎯 Simulações Rápidas

### Template Genérico

```python
import numpy as np

# 1. Carregar matriz
L_r = np.load('output/final/L_RioJaneiro.npy')
e_j = np.load('output/intermediary/employment_coefficients_2021.npy')

# 2. Definir choque (R$ milhões)
shock = np.zeros(67)
shock[20] = 100  # R$ 100M no setor 20 (Cultura)

# 3. Calcular impactos
delta_X = L_r @ shock
delta_E = e_j @ delta_X

print(f"Impacto na Produção: R$ {delta_X.sum():.2f}M")
print(f"Empregos Gerados: {delta_E.sum():.0f}")
```

### Setores Principais (Índices)

| Setor | Índice | Nome |
|-------|--------|------|
| Agricultura | 0-2 | Agricultura, pecuária, etc. |
| Indústria | 3-35 | Manufatura, construção |
| **Cultura** | **20** | Artes, cultura, esporte |
| **Alojamento** | **37** | Hotéis, pousadas |
| **Alimentação** | **38** | Restaurantes, bares |
| **Transporte** | **39-42** | Transporte terrestre, aéreo |
| Comércio | 36 | Varejo, atacado |
| Serviços | 43-66 | Diversos serviços |

---

## 🔧 Solução de Problemas Express

| Problema | Solução Rápida |
|----------|----------------|
| **Erro de memória** | Feche outros programas, processe regiões sequencialmente |
| **CORS no dashboard** | Use `python -m http.server 8000` |
| **Dashboard em branco** | Execute `export_dashboard_data.py`, verifique `data.json` |
| **Números inconsistentes** | Execute `validate_results.py` |
| **Matriz singular** | Verifique se `A_r` tem valores válidos (0-1) |
| **Importação falha** | Instale: `pip install numpy pandas xlrd` |

---

## 📊 Fórmulas Essenciais

### 1. Coeficientes Técnicos

$$
A_{ij}^{nas} = \frac{Z_{ij}}{X_j}
$$

### 2. FLQ (Flegg)

$$
A_{ij}^r = CILQ_i^r \cdot [FLQ^r]^\delta \cdot A_{ij}^{nas}
$$

Onde:
- $CILQ_i^r = \frac{LQ_i^r}{LQ_i^r + 1}$
- $LQ_i^r = \frac{VAB_i^r / VAB^r}{VAB_i^{BR} / VAB^{BR}}$
- $FLQ^r = \left( \frac{VAB^r}{VAB^{BR}} \right)^2$

### 3. Inversa de Leontief

$$
L_r = (I - A_r)^{-1}
$$

### 4. Impacto na Produção

$$
\Delta X_r = L_r \cdot \Delta y_r
$$

### 5. Impacto no Emprego

$$
\Delta E = \sum_j e_j \cdot \Delta X_j
$$

---

## 🎨 Customização Rápida do Dashboard

### Cores

```css
/* style.css, linha 11-15 */
--accent-cyan: #00FFFF;    /* Cor principal */
--accent-purple: #A855F7;  /* Cor secundária */
```

### Quantidade de Partículas

```javascript
// app.js, linha 27
const particleCount = 50;  // Aumente ou diminua
```

### Velocidade das Animações

```css
/* style.css, várias linhas */
transition: all 0.3s ease;  /* Mude 0.3s para mais rápido/lento */
```

---

## 📈 Multiplicadores por Região (Referência)

| Região | Multiplicador | Emoji |
|--------|---------------|-------|
| São Paulo | 1.258 | 🥇 |
| Rio de Janeiro | 1.220 | 🥈 |
| Sul | 1.195 | 🥉 |
| MG & ES | 1.178 | 4️⃣ |
| Centro-Oeste | 1.152 | 5️⃣ |
| Norte & Nordeste | 1.134 | 6️⃣ |

---

## 🔄 Workflow de Atualização de Dados

```
Novos Dados Brutos (Excel)
         ↓
[slim_extract.py] → VAB regional
         ↓
[integrated_pipeline.py] → Regionalização
         ↓
[validate_results.py] → Verificação
         ↓
[simulate_*.py] → Simulações
         ↓
[export_dashboard_data.py] → data.json
         ↓
Dashboard (Ctrl+F5 para reload)
```

---

## 🧪 Testes Rápidos

### Validar Matriz Nacional

```python
import numpy as np

X = np.load('output/intermediary/X_nas.npy')
VAB = np.load('output/intermediary/VAB_nacional.npy')
Z_sum = np.load('output/intermediary/Z_nas.npy')

# Teste de consistência
assert np.allclose(X - Z_sum, VAB), "Inconsistência nacional!"
print("✅ Base nacional consistente")
```

### Validar Regionalização

```python
import numpy as np

regiao = "RioJaneiro"
A_r = np.load(f'output/final/A_{regiao}.npy')

# Coeficientes devem estar entre 0 e 1
assert (A_r >= 0).all() and (A_r <= 1).all(), "Coeficientes inválidos!"
print(f"✅ A_{regiao} válido")
```

---

## 🌐 URLs Úteis

- **IBGE MIP 2015**: [https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9085-matriz-de-insumo-produto.html](https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9085-matriz-de-insumo-produto.html)
- **Contas Regionais**: [https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9054-contas-regionais-do-brasil.html](https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9054-contas-regionais-do-brasil.html)
- **Chart.js Docs**: [https://www.chartjs.org/docs/](https://www.chartjs.org/docs/)

---

## 💾 Backup Essencial

### Arquivos Críticos para Backup

```bash
# Dados processados
output/intermediary/*.npy
output/final/*.npy

# Configurações
scripts/*.py

# Dashboard
dashboard/data.json
dashboard/*.html
dashboard/*.css
dashboard/*.js

# Documentação
README.md
technical_report.md
```

---

## ⌨️ Atalhos do Navegador (Dashboard)

| Ação | Atalho Windows | Atalho Mac |
|------|----------------|------------|
| Recarregar | `Ctrl + R` | `Cmd + R` |
| Recarregar (hard) | `Ctrl + F5` | `Cmd + Shift + R` |
| Console | `F12` | `Cmd + Option + I` |
| Tela cheia | `F11` | `Ctrl + Cmd + F` |
| Zoom in | `Ctrl + +` | `Cmd + +` |
| Zoom out | `Ctrl + -` | `Cmd + -` |
| Zoom reset | `Ctrl + 0` | `Cmd + 0` |

---

## 🎓 Conceitos Rápidos

| Termo | Definição |
|-------|-----------|
| **MRIO** | Multi-Regional Input-Output (Insumo-Produto Multi-Regional) |
| **FLQ** | Flegg Location Quotient (método de regionalização) |
| **Leontief** | Inversa que calcula impactos indiretos |
| **Spillover** | Transbordamento econômico para outras regiões |
| **VAB** | Valor Adicionado Bruto |
| **Multiplicador** | Quanto R$1 de demanda gera na economia total |
| **Coeficiente Técnico** | Quanto o setor i fornece para o setor j produzir |

---

## 📞 Comandos de Emergência

### Resetar Ambiente (Windows)

```powershell
# Limpar cache do Python
Remove-Item -Recurse -Force __pycache__

# Reinstalar dependências
pip install --force-reinstall numpy pandas xlrd

# Reprocessar dados base
python scripts/finalize_national.py
```

### Verificação de Integridade

```python
import os
import numpy as np

# Verificar arquivos essenciais
essential_files = [
    'output/intermediary/X_nas.npy',
    'output/intermediary/VAB_nacional.npy',
    'output/intermediary/A_nas.npy',
    'output/final/A_RioJaneiro.npy',
    'dashboard/data.json'
]

for file in essential_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} FALTANDO!")
```

---

**Use este guia como referência rápida no dia a dia!** 📌

*Versão 2.1.0 | Janeiro 2026*
