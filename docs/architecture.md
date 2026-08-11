# Arquitetura do Data Lake

## Fontes de dados

- **SUSEP (Ses_seguros.csv)** — risco regulatório, 1.784.838 linhas, série histórica 1995-2026
- **Credit Card Fraud Detection (creditcard.csv)** — risco transacional, 284.808 linhas

## Fluxo de camadas
- **Raw**: arquivos originais (CSV/ZIP), sem tratamento, não versionados no Git
- **Bronze**: dados convertidos para Parquet, sem regra de negócio aplicada
- **Silver**: dados limpos, tipados, sem duplicidade, com regras de qualidade aplicadas
- **Gold**: dimensões e fatos, unindo visão regulatória (SUSEP) e transacional (fraude) — pronto para consumo em SQL/BI

## Componentes de orquestração e entrega

- **Airflow**: orquestração das tasks de ingestão, Bronze, Silver e Gold
- **Docker**: containerização do ambiente (PostgreSQL, Airflow)
- **PostgreSQL**: banco de destino da camada Gold para consultas SQL e dashboard
