# Referencia de Scripts do Projeto MIP-CGE Brasil

> Ultima atualizacao: 28/02/2026

Os scripts estao organizados por funcao. Scripts marcados com ★ sao **producao** (usados ativamente). Os demais sao utilitarios de desenvolvimento ou versoes anteriores.

---

## 1. GERADORES DE MATRIZES (Infraestrutura Core)

Estes scripts criam os dados fundamentais do projeto. Devem ser executados nesta ordem quando se precisa reconstruir tudo do zero.

### ★ `mrio_official_v4.py` — Modelo Inter-Regional
**Pergunta economica**: *Como os setores de diferentes estados do Brasil se relacionam via comercio inter-regional?*

Gera a MRIO (Multi-Regional Input-Output) de 1809x1809 (27 UFs x 67 setores). Usa modelo gravitacional com beta setorial calibrado (commodities: 0.8, manufatura: 1.5, servicos: 3.0). Para o RJ, usa matrizes hibridas especificas.

**Depende de**: `gravity_params.py`, matrizes A por regiao, VAB regional
**Produz**: `A_mrio_official_v4.npy`, `trade_prob_sectoral_v4.npy`

---

### ★ `generate_employment_income_matrix.py` — Emprego e Renda (67x27)
**Pergunta economica**: *Quantas pessoas estao empregadas e quanta renda e gerada por setor em cada estado?*

Processa a PNAD Continua 2021 (223 codigos CNAE) e gera matrizes oficiais de emprego e renda para todos os 67 setores e 27 UFs. Usado por todos os scripts de simulacao.

**Depende de**: PNAD Excel, VAB regional
**Produz**: `employment_matrix_67x27.npy`, `income_matrix_67x27.npy`, `emp_coefficients_67x27.npy`, `inc_coefficients_67x27.npy`

---

### ★ `gravity_params.py` — Parametros do Modelo Gravitacional
Contem coordenadas das capitais, funcao de distancia (Haversine), e lista de UFs. Modulo auxiliar usado por `mrio_official_v4.py`.

---

### ★ `integrated_pipeline.py` — Pipeline Integrado
**Pergunta economica**: *Como gerar todas as matrizes regionais de uma vez?*

Orquestra a geracao de matrizes regionais para todos os 27 estados a partir da nacional, usando FLQ e o modelo gravitacional.

**Depende de**: `mrio_official_v4.py`, `A_nas.npy`, VAB regional
**Produz**: MIPs estaduais (27 arquivos Excel)

---

### `rebuild_regional_vab_v3.py` — Reconstrucao do VAB Regional
**Pergunta economica**: *Como distribuir o VAB nacional de 67 setores entre os 27 estados?*

Usa dados das Contas Regionais do IBGE para desagregar o VAB nacional em 67 setores por estado. Versao final (v3) com correcoes de outliers.

**Depende de**: Contas Regionais IBGE, MIP nacional
**Produz**: `vab_regional.json`, `VAB_{UF}.npy`

---

### `calculate_linkages.py` — Encadeamentos Produtivos
**Pergunta economica**: *Quais setores tem maior poder de "puxar" a economia (para tras) ou de ser "puxados" (para frente)?*

Calcula Backward Linkages (BL) e Forward Linkages (FL) para cada setor e estado, identificando setores-chave da economia.

**Produz**: `linkages.json`

---

### `generate_consumption_shares_67.py` — Consumo das Familias
**Pergunta economica**: *Como as familias distribuem seus gastos entre os 67 setores?*

Extrai shares de consumo das familias da MIP, necessario para multiplicadores Tipo II (efeito induzido).

**Produz**: `household_consumption_shares_67_v3.npy`

---

## 2. ESTUDOS E ANALISES (Outputs de Pesquisa)

Scripts que respondem perguntas economicas especificas usando as matrizes.

### ★ `creative_economy_study.py` — Economia Criativa Fluminense
**Pergunta economica**: *Qual o efeito multiplicador da Economia Criativa no Rio de Janeiro? Quanto cada R$ 1 investido retorna ao PIB?*

Estudo completo em 6 secoes:
1. **Contextualizacao**: Peso da economia criativa no PIB do RJ, Location Quotients
2. **Multiplicadores**: Multiplicadores de producao e encadeamentos (BL/FL)
3. **Decomposicao**: Quais setores nao-criativos se beneficiam quando o criativo cresce
4. **Impacto Fiscal**: ICMS e ISS gerados pela economia criativa
5. **Emprego**: Multiplicador de emprego (vagas diretas → totais)
6. **Simulacao Fiscal**: ROI de renuncia tributaria

**Produz**: `estudo_economia_criativa_rj.json`, `estudo_economia_criativa_rj.xlsx`

---

### ★ `estimate_workweek_reduction.py` — Reducao da Jornada de Trabalho
**Pergunta economica**: *Qual o impacto economico de reduzir a jornada de 44h para 40h ou 36h semanais?*

Simula o impacto da reducao de jornada no emprego e na producao usando a matrix nacional 67x67, estimando quantos empregos seriam criados/destruidos e o efeito no PIB.

---

### `audiovisual_analysis_config.py` + `audiovisual_initial_analysis.py`
**Pergunta economica**: *Qual a importancia do setor audiovisual para a economia do RJ e do Brasil?*

Analise especifica do setor audiovisual: identificacao de setores CORE, SUPPORT e SPILLOVER, multiplicadores, e participacao no PIB.

---

## 3. SIMULACOES DE IMPACTO (Eventos e Choques)

Estes scripts simulam "o que acontece se..." usando a inversa de Leontief.

### ★ `simulate_carnaval_2024.py` — Impacto do Carnaval
**Pergunta economica**: *Quanto o Carnaval gera para a economia do RJ? Quantos empregos sustenta?*

Simula o impacto economico do Carnaval 2024 no RJ: choque de demanda nos setores de Alojamento, Alimentacao, Transporte, Artes, e calcula efeitos diretos + indiretos via Leontief.

---

### ★ `simulate_rock_in_rio.py` — Impacto do Rock in Rio
**Pergunta economica**: *Qual o impacto economico do Rock in Rio no estado do RJ?*

Similar ao Carnaval mas com perfil de gasto diferente (mais Alojamento, mais TI/Producao, menos Artes populares).

---

### `simulate_carnaval_impact.py` / `simulate_carnaval_impact_v2.py`
Versoes alternativas da simulacao do Carnaval com niveis de detalhe diferentes.

### `simulate_impact_carnaval.py` / `simulate_spillover_carnaval.py`
Foco nos efeitos de transbordamento (spillover) do Carnaval para setores nao diretamente ligados ao evento.

### `simulate_impact_beyonce.py`
**Pergunta economica**: *Qual o impacto economico de um show de grande porte (Beyonce) no RJ?*

### `simulate_running_shoes_impact.py`
**Pergunta economica**: *Qual o impacto de uma politica industrial para tenis de corrida na cadeia produtiva brasileira?*

Analise detalhada da cadeia de producao de tenis: borracha, texteis, plastico, logistica, varejo.

---

## 4. SIMULACOES FISCAIS

### ★ `simulate_reform_scenarios.py` — Cenarios de Reforma Tributaria
**Pergunta economica**: *O que acontece com os precos relativos e a producao se mudarmos a aliquota de ICMS?*

Simula cenarios de reforma tributaria (IBS, aliquota unica) e calcula o impacto setorial nos precos e na producao.

---

### `simulate_sectoral_burden.py` / `simulate_state_burden.py`
**Pergunta economica**: *Qual a carga tributaria efetiva por setor e por estado?*

Calcula a carga ICMS/VBP e ISS/VBP por setor, comparando entre estados e identificando setores sub/sobre-tributados.

---

## 5. PROCESSAMENTO FISCAL (ICMS/ISS)

Scripts que processam dados fiscais brutos e constroem as matrizes de aliquotas.

### ★ `process_taxes_2021.py` — Processamento de Impostos (2021)
Processa dados do CONFAZ (ICMS por estado) e calcula aliquotas efetivas por setor MIP.

### `regionalize_icms_v3_final.py` — Regionalizacao do ICMS
Distribui o ICMS nacional entre os 67 setores usando a tabela de Recursos e Usos.

### `calculate_rj_icms.py` — ICMS Especifico do RJ
Calcula carga de ICMS por setor especificamente para o RJ.

### `calc_export_ratios.py` — Razoes de Exportacao
Calcula a proporcao de cada setor que e exportada (relevante para desoneracoes fiscais).

---

## 6. EXTRACAO E PROCESSAMENTO DE DADOS

Scripts que extraem dados brutos de fontes oficiais (Excel IBGE, CONFAZ, etc.) e transformam em formato utilizavel.

### ★ `extract_vab_real.py` — Extracao do VAB
Extrai VAB das planilhas do IBGE/SCN.

### ★ `re_extract_national.py` — Extracao da MIP Nacional
Re-extrai a Matriz Insumo-Produto nacional do IBGE (67x67).

### `extract_confaz_icms_2024.py` — Extracao CONFAZ
Extrai dados de arrecadacao ICMS do CONFAZ.

### `extract_perfectionist_base.py` — Extracao MIP 2015
Extrai a MIP 2015 como base de comparacao.

### `cnae_to_mip_mapping.py` — Mapeamento CNAE-MIP
Tabela de concordancia detalhada entre codigos CNAE 2.0 e os 67 setores MIP.

---

## 7. EXPORTACAO E DASHBOARD

### ★ `export_dashboard_data.py` — Dados para Dashboard
Exporta dados processados em formato JSON para consumo por dashboards web.

### `export_matrices_package.py` — Pacote de Matrizes
Empacota todas as matrizes oficiais para distribuicao.

### `generate_report_graphics.py` — Graficos para Relatorio
Gera graficos automatizados para relatorios.

---

## 8. AUDITORIA E VALIDACAO

Scripts para verificar integridade e consistencia dos dados.

| Script | Verifica |
|--------|----------|
| `audit_all_matrices.py` | Dimensoes de todas as matrizes |
| `audit_employment_matrix.py` | Consistencia da matriz de emprego |
| `audit_national_mip.py` | MIP nacional (somas, negativos) |
| `audit_taxes_detailed.py` | Aliquotas fiscais (outliers) |
| `validate_gravity_output.py` | Output do modelo gravitacional |
| `validate_linkages.py` | Encadeamentos BL/FL |
| `validate_multipliers.py` | Multiplicadores de producao |
| `validate_tax_matrix.py` | Matriz fiscal |
| `validate_mip_extraction.py` | Extracao da MIP 2015/2021 |

---

## 9. UTILITARIOS DE DESENVOLVIMENTO

Scripts pequenos de debug, inspecao, e correcao pontual. **Nao sao necessarios para producao** — foram criados durante o desenvolvimento para investigar problemas especificos.

| Prefixo | Quantidade | Funcao |
|---------|-----------|--------|
| `debug_*` | ~10 | Debugging pontual de problemas |
| `inspect_*` | ~12 | Inspecao de estrutura de arquivos |
| `check_*` | ~8 | Verificacoes rapidas de dados |
| `fix_*` | ~5 | Correcoes pontuais |
| `compare_*` | ~3 | Comparacao entre versoes |
| `show_*` | ~2 | Visualizacao rapida |

---

## Resumo: Scripts Essenciais (★)

| # | Script | Pergunta que responde |
|---|--------|----------------------|
| 1 | `mrio_official_v4.py` | Como os estados comerciam entre si? |
| 2 | `generate_employment_income_matrix.py` | Quantos empregos e renda por setor/estado? |
| 3 | `integrated_pipeline.py` | Como gerar todas as MIPs regionais? |
| 4 | `creative_economy_study.py` | Qual o multiplicador da economia criativa do RJ? |
| 5 | `simulate_carnaval_2024.py` | Quanto o Carnaval gera para o RJ? |
| 6 | `simulate_rock_in_rio.py` | Qual o impacto do Rock in Rio? |
| 7 | `simulate_reform_scenarios.py` | O que muda com a reforma tributaria? |
| 8 | `estimate_workweek_reduction.py` | O que acontece se reduzir a jornada? |
| 9 | `export_dashboard_data.py` | Exportacao para dashboard |
| 10 | `process_taxes_2021.py` | Carga tributaria por setor/estado |
