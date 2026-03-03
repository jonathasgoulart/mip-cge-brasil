
# Metodologia: Simulação de Impacto Econômico - Rock in Rio

Para calcularmos o impacto do Rock in Rio com o rigor que a sua nova matriz permite, seguiremos o protocolo de **Choque de Demanda Final**.

## 1. Definição do Vetor de Choque ($F$)
O segredo de uma boa simulação é não "chutar" um valor único, mas distribuir o gasto total do evento pelos setores corretos da matriz (67 setores). 

### Sugestão de Distribuição (Vetor de Demanda):
Com base em estudos anteriores da FGV e dados do evento, distribuiremos o gasto estimado (ex: R$ 1 bilhão) assim:

| Setor MIP | Atividade Economicamente Afetada | % Estimada do Gasto |
| :--- | :--- | :--- |
| **64** | **Artes, Cultura e Espetáculos** (Ingressos, cachês, montagem) | 40% |
| **45** | **Serviços de Alojamento** (Hotéis e AirBnB) | 20% |
| **46** | **Serviços de Alimentação** (Restaurantes, bares, alimentação no local) | 15% |
| **40** | **Comércio** (Venda de souvenirs, varejo em geral no Rio) | 10% |
| **41** | **Transporte Terrestre** (Táxis, APPs, Ônibus) | 8% |
| **43/44** | **Transporte Aéreo e Auxiliares** (Taxas aeroportuárias, passagens) | 7% |

## 2. As Camadas de Impacto

Usaremos a sua Matriz do Rio (Oficial 2019 corrigida para 2021) para rodar o cálculo:

1.  **Impacto Direto:** É o valor gasto pelo turista (ex: O R$ 1.000 que o turista gasta no Rio).
2.  **Impacto Indireto:** É o que a cadeia produtiva compra. O hotel compra energia (Setor 37), comida (Setor 9), segurança (Setor 58). Nossa matriz já calcula isso via **Inversa de Leontief**.
3.  **Impacto Induzido (O Efeito Renda):** É aqui que entra o seu dado de amanhã. Usaremos a massa salarial para ver como esse novo dinheiro vira consumo em setores que não têm nada a ver com o Rock in Rio (ex: Saúde, Educação, Aluguel).

## 3. O que entregaremos no Relatório?

Ao final da simulação, teremos indicadores precisos:
- **PIB Gerado:** Quanto os R$ 1 Bi se multiplicaram (geralmente o multiplicador é de 1.8x a 2.4x).
- **Empregos Totais:** Quantas vagas (diretas e indiretas) foram sustentadas pelo evento.
- **Arrecadação de Impostos:** Quanto o Estado do Rio (ICMS) e a Prefeitura (ISS) arrecadaram com o festival.
- **Transbordamento:** Quanto do gasto no Rock in Rio acabou gerando PIB em outros estados (via nossa Aba 11).

---

### Pergunta para Calibração:
Você já tem um valor total de gasto estimado (ex: R$ 800 Mi, R$ 1 Bi) que gostaria de testar, ou quer que usemos um valor "base" de R$ 1 Bilhão para vermos os multiplicadores puros?
