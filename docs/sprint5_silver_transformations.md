# Sprint 5 — Transformações da Camada Silver (PySpark)

## Ambiente

- PySpark 4.2.0
- Java: OpenJDK 17 (headless), configurado no WSL/Ubuntu
- Scripts em `src/processing/`

## `transform_fraud_silver.py`

Origem: `data/bronze/fraud_transactions.parquet` (284.807 registros)
Destino: `data/silver/fraud_transactions.parquet`

Transformações aplicadas:
- **Nulos**: verificação por coluna — nenhum nulo encontrado
- **Duplicidade**: `dropDuplicates()` — removidos **1.081 registros duplicados**, não detectados em nenhuma etapa anterior do pipeline (ingestão ou consultas SQL)
- **Filtro**: remoção de transações com `Amount` negativo (inconsistência de negócio) — nenhum registro removido nessa checagem

**Resultado**: 284.807 → 283.726 registros (-1.081)

## `transform_susep_seguros_silver.py`

Origem: `data/bronze/susep_seguros.parquet` (1.784.838 registros)
Destino: `data/silver/susep_seguros.parquet`

Transformações aplicadas:
- **Conversão monetária**: 17 colunas armazenadas como `text` com vírgula decimal (formato BR) convertidas para `double` via `regexp_replace(',', '.')` + `cast`
- **Padronização de tipo**: `coramo` convertido de `double precision` para `bigint`, resolvendo a inconsistência de tipo já documentada na Sprint 1 (divergia do tipo em `susep_ramos`)
- **Chave de JOIN nula**: 2 registros com `coramo` nulo removidos — sem essa chave, o registro não pode ser associado a nenhum ramo, tornando-o inutilizável para as análises do projeto
- **Nulos em colunas monetárias**: 16 registros com `sinistro_retido` vazio no CSV original, preenchidos com `0.0` (decisão: ausência de valor tratada como ausência de sinistro retido, não como dado faltante crítico)
- **Duplicidade**: nenhum registro duplicado encontrado

**Resultado**: 1.784.838 → 1.784.836 registros (-2)

## Decisões de tratamento de nulo — justificativa

| Situação | Decisão | Motivo |
|---|---|---|
| `coramo` nulo | Remover linha | É a chave usada para JOIN com `susep_ramos`; sem ela, o registro não é analisável |
| Colunas monetárias nulas | Preencher com 0.0 | Nulo aqui representa ausência de movimentação naquele mês/ramo, não erro de coleta |
| Duplicidade (fraude) | Remover | Registros idênticos em todas as colunas não agregam informação nova, apenas distorceriam contagens/somas |

## Achados de qualidade de dado (carry-over para Sprint 6+)

- Dataset de fraude tinha 1.081 duplicados não detectados anteriormente — reforça a importância da camada Silver como ponto de verificação, mesmo em fontes "confiáveis"
- SUSEP: apenas 18 registros problemáticos em 1,78 milhão (0,001%) — a base é, de forma geral, bem estruturada, com poucas exceções pontuais
