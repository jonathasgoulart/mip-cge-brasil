# 🧠 MASTER PROJECT STATE - MIP-CGE Brasil

> **ESTADO ATUAL DO PROJETO EM 05/03/2026**
> Este arquivo é a "Memória Central" para o Antigravity. Deve ser consultado no início de cada sessão.

## 🛠️ 1. Infraestrutura & Tecnologias
- **Backend API**: FastAPI (Python 3.11).
  - *Estado*: 100% Portátil. Caminhos absolutos removidos em favor de caminhos relativos ao diretório raiz.
  - *Arquivo Core*: `api/main.py`
- **Frontend Dashboard**: Vue/React/HTML no Render.
  - *Estado*: DEPLOYED EM PRODUÇÃO
  - *URL Oficial*: [https://mip-cge-dashboard.onrender.com/](https://mip-cge-dashboard.onrender.com/)
  - *Nota*: O dashboard local antigo foi obsoleto (movido para `_obsolete_dashboard`).
- **Deploy & DevOps**: 
  - Repositório Git sincronizado: `https://github.com/jonathasgoulart/mip-cge-brasil`

## 📊 2. Estrutura de Dados (Ref: [OFFICIAL_MATRICES_REFERENCE.md](file:///c:/Users/jonat/Documents/MIP%20e%20CGE/OFFICIAL_MATRICES_REFERENCE.md))
- **MRIO v4 (2021)**: Matriz inter-regional (1809x1809) baseada em 27 UFs e 67 setores.
  - *Arquivos*: `output/final/A_mrio_official_v4.npy`, `trade_prob_sectoral_v4.npy`
- **Matriz de Emprego (PNAD 2021)**: Pessoas Ocupadas (PO) e Renda para todos os 67 setores e 27 UFs.
  - *Arquivos*: `emp_coefficients_67x27.npy`, `inc_coefficients_67x27.npy`
- **Base Fiscal**: Coeficientes de impostos (ICMS, IPI, ISS, etc.) e Importação (II) por setor.
  - *Arquivos*: `data/processed/2021_final/tax_matrix.json`

## ⚙️ 3. Scripts Essenciais (Ref: [SCRIPTS_REFERENCE.md](file:///c:/Users/jonat/Documents/MIP%20e%20CGE/SCRIPTS_REFERENCE.md))
| Script | Função | Status |
|---|---|---|
| `scripts/mrio_official_v4.py` | Gerador do Modelo Gravitacional Core | ★ Produção |
| `api/simulators/demand_shock.py` | Engine de Simulação (Leontief) | ★ Produção |
| `scripts/integrated_pipeline.py` | Processamento regional (FLQ) | ★ Produção |
| `scripts/export_dashboard_data.py`| Sincronização API -> Dashboard | ★ Produção |

## 🧪 4. Simulações Realizadas e Documentadas
- **Impacto Beyoncé/Rock in Rio/Carnaval**: Choques positivos RJ.
- **Cenário Guerra no Irã (Recessivo)**: Choque negativo S18/S21.
- **Integração Goiás**: Correção estrutural de multiplicadores. 
  - *Descoberta*: Refino em GO tem multiplicador 1.0 (integrado via imports, não via produção local).

## 🚀 5. Onde Paramos & Próximos Passos
- [x] Sincronização total com GitHub.
- [x] Dockerização e portabilidade do sistema.
- [x] Simulação de impacto geoeconômico (Guerra Irã).
- [/] **PENDENTE**: Criar Aba de "Gestão de Crises" no Dashboard para simular choques negativos (como o do Irã) visualmente.
- [/] **PENDENTE**: Landing Page institucional do simulador online.

## ⚠️ Instruções Críticas para a IA
1. **NÃO USE CAMINHOS ABSOLUTOS** (`C:\Users...`). Use `os.path.join(os.getcwd(), ...)` ou caminhos relativos.
2. **SETORES (67)**: Sempre use o mapeamento oficial 2021. Se precisar dos labels, consulte `api/main.py`.
3. **RESPEITE O CORE**: Antes de criar um script novo, verifique se a lógica já não existe em `api/simulators/`.
