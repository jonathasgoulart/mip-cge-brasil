
# Guia para Coleta de Dados: Empregos por UF e Setor (2021)

Para integrarmos os dados reais de ocupação na sua matriz e termos multiplicadores perfeitos, o ideal é que os dados sigam o formato abaixo. 

### 1. Formato Sugerido (CSV ou Excel)

O formato mais fácil para eu processar é uma tabela "Longa" (Tidy Data) com estas 3 colunas:

| UF | Nome_do_Setor_IBGE | Pessoal_Ocupado_2021 |
| :--- | :--- | :--- |
| RJ | Agricultura... | 120500 |
| RJ | Pecuária... | 45000 |
| SP | Agricultura... | 890000 |

### 2. Dica sobre a Granularidade (18 vs 67 setores)

Geralmente, o IBGE divulga dados estaduais na mesma agregação das Contas Regionais (**18 a 40 setores**). 
- **Não se preocupe em "quebrar" para 67:** Se você encontrar os dados nos 18 setores originais do IBGE, pode me enviar assim mesmo. 
- Eu farei a desagregação estatística para os 67 setores usando os pesos da Matriz Nacional (como fizemos com o VAB).

### 3. Lista de Referência (Nossos 67 Setores)
Para evitar erros de digitação, aqui estão os nomes exatos que usamos na nossa MIP. Se você puder colocar o código do setor (0 a 66), ajuda ainda mais:

1. Agricultura
2. Pecuária
3. Produção florestal; pesca e aquicultura
... (até o 66. Serviços Domésticos)

### 4. Onde encontrar o dado no IBGE?
O melhor lugar é o **SIDRA - Tabela 5938** (Contas Regionais), mas filtrando pela variável **"Pessoal Ocupado"** em vez de "Valor Adicionado".

---

**Como você prefere me enviar?** 
- Pode copiar e colar uma amostra aqui.
- Ou me dizer o nome das colunas se você já tiver o arquivo.

Assim que você me passar isso, eu atualizo automaticamente as 27 matrizes estaduais com o **Dado Real de Emprego**, e os seus Multiplicadores de Emprego serão os mais precisos possíveis!
