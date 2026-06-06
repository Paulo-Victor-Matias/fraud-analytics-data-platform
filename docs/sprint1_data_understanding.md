## Relacionamentos Identificados

### Seguradoras

Ses_seguros.coenti
→ Ses_cias.coenti

Permite identificar a seguradora responsável pelos registros de produção e sinistros.

### Ramos de Seguro

Ses_seguros.coramo
→ Ses_ramos.coramo

Permite identificar o ramo de seguro associado à movimentação financeira.

---

## Métricas de Negócio Identificadas

As principais métricas disponíveis na base SUSEP são:

* premio_direto
* premio_retido
* premio_ganho
* sinistro_direto
* sinistro_retido
* sinistro_ocorrido
* desp_com

Indicadores que poderão ser calculados:

### Sinistralidade

sinistro_ocorrido / premio_ganho

### Participação de Mercado

premio_ganho da seguradora / premio_ganho total do mercado

### Evolução de Prêmios

Comparação mensal e anual da produção das seguradoras.

---

## Dataset de Fraude Financeira

### Arquivo

creditcard.csv

### Volume

284.808 registros

31 colunas

### Variável Alvo

Class

Valores:

* 0 = Transação legítima
* 1 = Transação fraudulenta

### Campos Relevantes

* Time
* Amount
* V1 a V28 (variáveis anonimizadas)
* Class

### Possíveis Aplicações

* Detecção de fraude
* Detecção de anomalias
* Monitoramento de risco
* Criação de indicadores operacionais

---

## Conclusões da Sprint 1

Foram identificadas duas fontes de dados complementares:

1. Base SUSEP, utilizada para análise do mercado segurador brasileiro.
2. Base de fraude financeira, utilizada para simular cenários de detecção de anomalias.

Essas bases servirão como fonte para a construção do Data Lake e das próximas etapas do pipeline de engenharia de dados.
