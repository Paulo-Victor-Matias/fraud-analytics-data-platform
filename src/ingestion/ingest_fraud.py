import logging
from pathlib import Path

import pandas as pd

INPUT_FILE = "data/raw/fraud/extracted/creditcard.csv"
OUTPUT_FILE = "data/bronze/fraud_transactions.parquet"
LOG_FILE = "logs/ingestion.log"

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ingest_fraud")


def extract():
    logger.info("Iniciando extração de: %s", INPUT_FILE)

    if not Path(INPUT_FILE).exists():
        logger.error("Arquivo de entrada não encontrado: %s", INPUT_FILE)
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT_FILE}")

    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception:
        logger.exception("Falha ao ler o arquivo CSV: %s", INPUT_FILE)
        raise

    if len(df) == 0:
        logger.error("Arquivo lido, mas contém 0 registros: %s", INPUT_FILE)
        raise ValueError(f"Nenhum registro encontrado em {INPUT_FILE}")

    logger.info("Extração concluída. Registros encontrados: %s", f"{len(df):,}")
    return df


def transform(df):
    logger.info("Transformação: nenhuma regra aplicada nesta etapa (camada Bronze)")
    return df


def load(df):
    logger.info("Salvando arquivo Parquet em: %s", OUTPUT_FILE)

    try:
        Path("data/bronze").mkdir(parents=True, exist_ok=True)
        df.to_parquet(OUTPUT_FILE, index=False)
    except Exception:
        logger.exception("Falha ao salvar o arquivo Parquet: %s", OUTPUT_FILE)
        raise

    logger.info("Arquivo salvo com sucesso: %s", OUTPUT_FILE)


def validate(df):
    registros_salvos = pd.read_parquet(OUTPUT_FILE).shape[0]

    if registros_salvos != len(df):
        logger.error(
            "Divergência na validação! Extraídos: %s | Salvos: %s",
            len(df), registros_salvos,
        )
        raise ValueError("Quantidade de registros salvos não bate com a extraída.")

    logger.info("Validação OK: %s registros conferidos.", f"{registros_salvos:,}")


def main():
    logger.info("===== Início da execução: ingest_fraud =====")
    try:
        df = extract()
        df = transform(df)
        load(df)
        validate(df)
        logger.info("Pipeline concluído com sucesso!")
    except Exception:
        logger.error("Pipeline finalizado com erro. Consulte os detalhes acima.")
        raise
    finally:
        logger.info("===== Fim da execução: ingest_fraud =====\n")


if __name__ == "__main__":
    main()
