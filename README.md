# Modelo MIP-CGE Brasil

Modelo Multi-Regional de Insumo-Produto e Equilíbrio Geral Computável para o Brasil.

## Estrutura
- **67 setores produtivos** (MIP IBGE 2015)
- **27 Unidades Federativas** (todas as UFs brasileiras)
- **8 tipos de impostos** desagregados
- **Modelo gravitacional** para comércio inter-regional

## Capacidades
- Simulações de eventos e turismo (ex: Carnaval)
- Análise de políticas tributárias
- Impactos regionais com spillovers
- Geração de emprego e arrecadação

## Documentação
- [`GRAVITY_MODEL_STATUS.md`](GRAVITY_MODEL_STATUS.md) - Modelo gravitacional
- [`model_capabilities_report.md`](.gemini/antigravity/brain/7b1534f9-a454-4106-8912-0bc26010f645/model_capabilities_report.md) - Relatório completo de capacidades
- [`icms_regionalization_final.md`](.gemini/antigravity/brain/7b1534f9-a454-4106-8912-0bc26010f645/icms_regionalization_final.md) - Metodologia ICMS regional

## Scripts Principais
- `mrio_official_v4.py` - Motor MRIO oficial (gravitacional setorial)
- `simulate_carnaval_2024.py` - Simulação de impacto de eventos
- `regionalize_icms_v3_final.py` - Regionalização ICMS (CONFAZ)

## Calibração
- **Ano base estrutura:** MIP 2015
- **Ano calibração:** 2021 (CTB + Contas Regionais)
- **ICMS regional:** CONFAZ 2024 (padrão espacial)

## Requisitos
```bash
pip install numpy pandas openpyxl
```

## Uso Rápido
```python
# Simular choque de demanda no RJ
python scripts/carnaval_impact_quick.py
```

## Status
✅ Matriz nacional implementada  
✅ VAB regional calibrado (27 UFs)  
✅ ICMS regionalizado (V2 share-based)  
✅ Modelo gravitacional operacional  
✅ Dashboard funcional  

## Próximas Melhorias
1. Coeficientes de emprego (RAIS/PNAD)
2. Vetor consumo famílias (POF)
3. Margens de comércio e transporte

## Autor
Jonathan [Seu sobrenome]

## Licença
[Definir licença]
