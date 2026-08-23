import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BRONZE_DIR = "data/bronze"
SCHEMA = "bronze"
LOG_FILE = "logs/ingestion.log"

ARQUIVOS = {
    "fraud_transactions.parquet": "fraud_transactions",
    "susep_seguros.parquet": "susep_seguros",
    "susep_cias.parquet": "susep_cias",
    "susep_ramos.parquet": "susep_ramos",
}

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("load_to_postgres")

load_dotenv()


def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")

    if not all([user, password, host, port, dbname]):
        logger.error("Variáveis de ambiente do banco ausentes. Confira o arquivo .env")
        raise EnvironmentError("Configuração de banco incompleta.")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(url)


def carregar_tabela(engine, arquivo, tabela):
    caminho = f"{BRONZE_DIR}/{arquivo}"
    logger.info("Lendo Parquet: %s", caminho)

    if not Path(caminho).exists():
        logger.error("Arquivo não encontrado: %s", caminho)
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    try:
        df = pd.read_parquet(caminho)
    except Exception:
        logger.exception("Falha ao ler o Parquet: %s", caminho)
        raise

    logger.info("Carregando %s registros em %s.%s", f"{len(df):,}", SCHEMA, tabela)

    try:
        df.to_sql(tabela, engine, schema=SCHEMA, if_exists="replace", index=False, chunksize=50000)
    except Exception:
        logger.exception("Falha ao carregar tabela: %s.%s", SCHEMA, tabela)
        raise

    with engine.connect() as conn:
        resultado = conn.execute(text(f"SELECT COUNT(*) FROM {SCHEMA}.{tabela}"))
        total_no_banco = resultado.scalar()

    if total_no_banco != len(df):
        logger.error(
            "Divergência! Parquet: %s | Banco: %s", len(df), total_no_banco
        )
        raise ValueError(f"Contagem divergente para {tabela}")

    logger.info("Validação OK: %s registros conferidos em %s.%s", f"{total_no_banco:,}", SCHEMA, tabela)


def main():
    logger.info("===== Início da execução: load_to_postgres =====")
    engine = get_engine()

    try:
        for arquivo, tabela in ARQUIVOS.items():
            logger.info("--- Processando: %s -> %s.%s ---", arquivo, SCHEMA, tabela)
            carregar_tabela(engine, arquivo, tabela)

        logger.info("Carga concluída com sucesso para todas as tabelas!")
    except Exception:
        logger.error("Carga finalizada com erro. Consulte os detalhes acima.")
        raise
    finally:
        logger.info("===== Fim da execução: load_to_postgres =====\n")


if __name__ == "__main__":
    main()
