import logging
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

BRONZE_FILE = "data/bronze/fraud_transactions.parquet"
SILVER_FILE = "data/silver/fraud_transactions.parquet"
LOG_FILE = "logs/processing.log"

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("transform_fraud_silver")


def extract(spark):
    logger.info("Lendo camada Bronze: %s", BRONZE_FILE)

    if not Path(BRONZE_FILE).exists():
        logger.error("Arquivo Bronze não encontrado: %s", BRONZE_FILE)
        raise FileNotFoundError(f"Arquivo não encontrado: {BRONZE_FILE}")

    df = spark.read.parquet(BRONZE_FILE)
    total_bronze = df.count()
    logger.info("Registros lidos da Bronze: %s", f"{total_bronze:,}")
    return df, total_bronze


def tratar_nulos(df):
    logger.info("Verificando valores nulos por coluna...")

    nulos_por_coluna = df.select(
        [F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]
    ).collect()[0].asDict()

    colunas_com_nulo = {k: v for k, v in nulos_por_coluna.items() if v > 0}

    if colunas_com_nulo:
        logger.warning("Colunas com valores nulos encontradas: %s", colunas_com_nulo)
        df = df.dropna()
        logger.info("Linhas com nulo removidas.")
    else:
        logger.info("Nenhum valor nulo encontrado. Nenhuma linha removida.")

    return df


def tratar_duplicidade(df):
    logger.info("Verificando registros duplicados...")

    total_antes = df.count()
    df = df.dropDuplicates()
    total_depois = df.count()
    duplicados_removidos = total_antes - total_depois

    if duplicados_removidos > 0:
        logger.warning("Registros duplicados removidos: %s", f"{duplicados_removidos:,}")
    else:
        logger.info("Nenhum registro duplicado encontrado.")

    return df


def aplicar_filtro(df):
    logger.info("Aplicando filtro: removendo transações com Amount negativo (inconsistência)")

    total_antes = df.count()
    df = df.filter(F.col("Amount") >= 0)
    total_depois = df.count()
    removidos = total_antes - total_depois

    logger.info("Registros removidos pelo filtro de Amount negativo: %s", removidos)
    return df


def load(df):
    logger.info("Salvando camada Silver em: %s", SILVER_FILE)

    try:
        Path("data/silver").mkdir(parents=True, exist_ok=True)
        df.coalesce(1).write.mode("overwrite").parquet(SILVER_FILE)
    except Exception:
        logger.exception("Falha ao salvar a camada Silver: %s", SILVER_FILE)
        raise

    logger.info("Arquivo salvo com sucesso: %s", SILVER_FILE)


def main():
    logger.info("===== Início da execução: transform_fraud_silver =====")

    spark = SparkSession.builder.appName("transform_fraud_silver").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    try:
        df, total_bronze = extract(spark)
        df = tratar_nulos(df)
        df = tratar_duplicidade(df)
        df = aplicar_filtro(df)

        total_silver = df.count()
        logger.info(
            "Resumo da transformação: Bronze=%s | Silver=%s | Removidos=%s",
            f"{total_bronze:,}", f"{total_silver:,}", f"{total_bronze - total_silver:,}",
        )

        load(df)
        logger.info("Pipeline Silver concluído com sucesso!")
    except Exception:
        logger.error("Pipeline finalizado com erro. Consulte os detalhes acima.")
        raise
    finally:
        spark.stop()
        logger.info("===== Fim da execução: transform_fraud_silver =====\n")


if __name__ == "__main__":
    main()
