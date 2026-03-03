# Status: Modelo Gravitacional Inter-regional — MRIO V4

## ✅ IMPLEMENTADO E OPERACIONAL

### Script Oficial
**Arquivo**: `scripts/mrio_official_v4.py`  
**Output**: `output/final/A_mrio_official_v4.npy`  
**Dimensões**: 1809×1809 (27 UFs × 67 setores)

---

## Especificação Técnica

### Modelo Gravitacional Setorial

**Equação de probabilidade de comércio:**
```
P[r→s, setor] = M_s / d_rs^β_setor / Σ_k (M_k / d_rk^β_setor)
```

Onde:
- `M_s` = VAB do estado s (massa econômica)
- `d_rs` = Distância entre r e s (Haversine, km)
- `β_setor` = Elasticidade da distância **por tipo de setor**

### Calibração β Setorial

| Categoria | Setores | β | Justificativa |
|-----------|---------|---|---------------|
| **Commodities** (Agro + Extrativismo) | 1–21 | 0.8 | Viajam longe, baixa fricção |
| **Manufaturados** (Indústria) | 22–52 | 1.5 | Fricção intermediária |
| **Serviços** | 53–67 | 3.0 | Altamente locais |

### Tratamento Especial: Rio de Janeiro

O RJ usa matrizes oficiais **UFRJ/CEPERJ 2019** (não FLQ):
- `A_RIO_LOCAIS_67x67.xlsx` — Coeficientes locais
- `A_RIO_INTER_67x67.xlsx` — Vazamentos interestaduais

Demais estados: Regionalização via **FLQ** (δ = 0.3).

---

## Arquivos Gerados

| Arquivo | Localização | Descrição |
|---------|-------------|-----------|
| `A_mrio_official_v4.npy` | `output/final/` | Matriz MRIO completa |
| `trade_prob_sectoral_v4.npy` | `output/final/` | Probabilidades 27×27×67 |
| `beta_sectoral_calibration.json` | `output/final/` | Parâmetros β |
| `region_order_v4.txt` | `output/final/` | Ordem das UFs |

---

## Módulo de Distâncias

**Arquivo**: `scripts/gravity_params.py`
- Coordenadas das 27 capitais estaduais (lat/lon)
- Função `haversine()` para distâncias
- Distância intra-regional: 50 km (aproximação)

---

## Como Usar

```python
import numpy as np

# Carregar MRIO
A_mrio = np.load('output/final/A_mrio_official_v4.npy')

# Ordem das UFs
with open('output/final/region_order_v4.txt') as f:
    UF_LIST = f.read().strip().split('\n')

# Simular choque no RJ, setor Alojamento (45)
rj_idx = UF_LIST.index('RJ')
shock_idx = rj_idx * 67 + 45
Y = np.zeros(1809)
Y[shock_idx] = 500  # R$ 500 Mi

# Leontief
X = np.linalg.solve(np.eye(1809) - A_mrio, Y)

# Impacto por UF
for i, uf in enumerate(UF_LIST):
    total = X[i*67:(i+1)*67].sum()
    if total > 1:
        print(f"{uf}: R$ {total:,.0f} Mi")
```

---

## Limitações Conhecidas

- ⚠️ Distância euclidiana (Haversine), não rodoviária
- ⚠️ Distância intra-UF fixa (50 km) em vez de proporcional à área
- ⚠️ Sem barreiras comerciais interestaduais

---

## Histórico de Versões

| Versão | Arquivo | Status |
|--------|---------|--------|
| V1 | `mrio_engine.py` | ❌ Removido |
| V2 | `mrio_engine_lite.py` | ❌ Removido |
| V3 | `generate_regional_mrio_v3.py` | ❌ Removido |
| **V4** | **`mrio_official_v4.py`** | **✅ Oficial** |

---

**Última atualização**: 27/02/2026  
**Versão**: 4.0 OFICIAL
