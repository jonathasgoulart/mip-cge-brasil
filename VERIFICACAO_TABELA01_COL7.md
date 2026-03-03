# Referência: Onde Verificar Coluna 7 na Tabela 01

## Planilha: `mip_2015_67.xls`, Aba "01"

### Estrutura do Excel (sem skiprows):

```
Linha 1 (Excel): [vazia]
Linha 2 (Excel): [vazia]  
Linha 3 (Excel): Cabeçalho = "Produção das atividades (valores correntes em 1 000 000 R$)"
Linha 4 (Excel): Código CNAE = "0191 Agricultura, inclusive o apoio..."
Linha 5 (Excel): [vazia]
...
Linha com "Total": Essa é a linha que contém os valores de VBP
```

### Coluna 7 (Coluna H do Excel):

**Linha 3, Coluna 7 (H3):** "Produção das atividades..."  
**Linha 4, Coluna 7 (H4):** código + descrição do primeiro setor

### No código Python:

```python
df = pd.read_excel('...', sheet_name='01', skiprows=3)
# Após skiprows=3, a linha 4 do Excel vira iloc[0]

# Buscar linha "Total"
total_row = df[df.iloc[:, 0].str.contains('Total', case=False, na=False)].iloc[0]

# Extrair VBP das atividades
X_2015 = total_row.iloc[7:74]  # Colunas H até BX (67 colunas)
```

### Para Verificar Manualmente no Excel:

1. Abra `data/raw/mip_2015_67.xls`
2. Vá para aba **"01"**
3. Identifique a linha que começa com **"Total"** (deve estar por volta da linha 130+)
4. Nessa linha, veja:
   - **Coluna H (7)** = VBP do 1º setor (Agricultura)
   - **Coluna I (8)** = VBP do 2º setor (Pecuária)
   - ...
   - **Coluna BX (73)** = VBP do 67º setor (Serviços domésticos)

### Confirmação:

✅ **Coluna 7 (H) está CORRETA** se contém o valor de VBP para **Agricultura**

⚠️ Se a coluna H contiver outros dados (produtos, impostos, etc.), então a extração está pegando a coluna errada.

---

## Como Conferir:

Execute no Excel ou LibreOffice:
1. Aba "01" → Encontre linha "Total"
2. Veja coluna H dessa linha
3. Compare com valor esperado de Agricultura (~309.000 milhões em 2015)
