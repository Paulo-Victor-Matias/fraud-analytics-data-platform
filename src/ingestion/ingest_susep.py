import logging
from pathlib import Path

import pandas as pd

RAW_DIR = "data/raw/susep/base_completa"
BRONZE_DIR = "data/bronze"
LOG_FILE = "logs/ingestion.log"

TABELAS = {
    "Ses_seguros.csv": "susep_seguros.parquet",
    "Ses_cias.csv": "susep_cias.parquet",
    "Ses_ramos.csv": "susep_ramos.parquet",
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
logger = logging.getLogger("ingest_susep")


def extract(nome_arquivo):
    caminho = f"{RAW_DIR}/{nome_arquivo}"
    logger.info("Iniciando extração de: %s", caminho)

    if not Path(caminho).exists():
        logger.error("Arquivo de entrada não encontrado: %s", caminho)
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    try:
        df = pd.read_csv(caminho, sep=";", encoding="latin-1", low_memory=False)
    except Exception:
        logger.exception("Falha ao ler o arquivo CSV: %s", caminho)
        raise

    if len(df) == 0:
        logger.error("Arquivo lido, mas contém 0 registros: %s", caminho)
        raise ValueError(f"Nenhum registro encontrado em {caminho}")

    logger.info("Extração concluída. Registros encontrados: %s", f"{len(df):,}")
    return df


def transform(df):
    logger.info("Transformação: nenhuma regra aplicada nesta etapa (camada Bronze)")
    return df


def load(df, nome_saida):
    caminho_saida = f"{BRONZE_DIR}/{nome_saida}"
    logger.info("Salvando arquivo Parquet em: %s", caminho_saida)

    try:
        Path(BRONZE_DIR).mkdir(parents=True, exist_ok=True)
        df.to_parquet(caminho_saida, index=False)
    except Exception:
        logger.exception("Falha ao salvar o arquivo Parquet: %s", caminho_saida)
        raise

    logger.info("Arquivo salvo com sucesso: %s", caminho_saida)
    return caminho_saida


def validate(df, caminho_saida):
    registros_salvos = pd.read_parquet(caminho_saida).shape[0]

    if registros_salvos != len(df):
        logger.error(
            "Divergência na validação! Extraídos: %s | Salvos: %s",
            len(df), registros_salvos,
        )
        raise ValueError("Quantidade de registros salvos não bate com a extraída.")

    logger.info("Validação OK: %s registros conferidos.", f"{registros_salvos:,}")


def main():
    logger.info("===== Início da execução: ingest_susep =====")

    resultados = {}
    try:
        for nome_arquivo, nome_saida in TABELAS.items():
            logger.info("--- Processando tabela: %s ---", nome_arquivo)
            df = extract(nome_arquivo)
            df = transform(df)
            caminho_saida = load(df, nome_saida)
            validate(df, caminho_saida)
            resultados[nome_arquivo] = len(df)

        logger.info("Pipeline concluído com sucesso! Resumo: %s", resultados)
    except Exception:
        logger.error("Pipeline finalizado com erro. Consulte os detalhes acima.")
        raise
    finally:
        logger.info("===== Fim da execução: ingest_susep =====\n")


if __name__ == "__main__":
    main()
