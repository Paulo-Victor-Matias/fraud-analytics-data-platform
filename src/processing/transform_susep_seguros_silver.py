import logging
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

BRONZE_FILE = "data/bronze/susep_seguros.parquet"
SILVER_FILE = "data/silver/susep_seguros.parquet"
LOG_FILE = "logs/processing.log"

# Colunas monetarias que vieram como texto com virgula decimal (formato BR)
COLUNAS_MONETARIAS = [
    "premio_direto", "premio_de_seguros", "premio_retido", "premio_ganho",
    "sinistro_direto", "sinistro_retido", "desp_com", "premio_emitido2",
    "premio_emitido_cap", "despesa_resseguros", "sinistro_ocorrido",
    "receita_resseguro", "sinistros_ocorridos_cap",
    "recuperacao_sinistros_ocorridos_cap", "rvne", "conveniodpvat",
    "consorciosefundos",
]

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("transform_susep_seguros_silver")


def extract(spark):
    logger.info("Lendo camada Bronze: %s", BRONZE_FILE)

    if not Path(BRONZE_FILE).exists():
        logger.error("Arquivo Bronze não encontrado: %s", BRONZE_FILE)
        raise FileNotFoundError(f"Arquivo não encontrado: {BRONZE_FILE}")

    df = spark.read.parquet(BRONZE_FILE)
    total_bronze = df.count()
    logger.info("Registros lidos da Bronze: %s", f"{total_bronze:,}")
    return df, total_bronze


def converter_colunas_monetarias(df):
    logger.info("Convertendo %s colunas de texto (virgula BR) para numeric", len(COLUNAS_MONETARIAS))

    for coluna in COLUNAS_MONETARIAS:
        df = df.withColumn(
            coluna,
            F.regexp_replace(F.col(coluna), ",", ".").cast(DoubleType())
        )

    logger.info("Conversão concluída.")
    return df


def padronizar_coramo(df):
    logger.info("Padronizando tipo da coluna coramo para bigint")
    df = df.withColumn("coramo", F.col("coramo").cast("bigint"))
    return df


def remover_coramo_nulo(df):
    logger.info("Verificando registros com coramo nulo (chave de JOIN com susep_ramos)...")

    total_antes = df.count()
    df = df.filter(F.col("coramo").isNotNull())
    total_depois = df.count()
    removidos = total_antes - total_depois

    if removidos > 0:
        logger.warning(
            "Registros removidos por coramo nulo (sem chave para JOIN com ramos): %s",
            removidos,
        )
    else:
        logger.info("Nenhum registro com coramo nulo encontrado.")

    return df


def tratar_nulos(df):
    logger.info("Verificando valores nulos gerados pela conversão monetária...")

    nulos_por_coluna = df.select(
        [F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in COLUNAS_MONETARIAS]
    ).collect()[0].asDict()

    colunas_com_nulo = {k: v for k, v in nulos_por_coluna.items() if v > 0}

    if colunas_com_nulo:
        logger.warning("Nulos encontrados após conversão (provável valor vazio no original): %s", colunas_com_nulo)
        df = df.fillna(0.0, subset=COLUNAS_MONETARIAS)
        logger.info("Nulos nas colunas monetárias preenchidos com 0.0")
    else:
        logger.info("Nenhum nulo gerado na conversão.")

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
    logger.info("===== Início da execução: transform_susep_seguros_silver =====")

    spark = SparkSession.builder.appName("transform_susep_seguros_silver").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    try:
        df, total_bronze = extract(spark)
        df = converter_colunas_monetarias(df)
        df = padronizar_coramo(df)
        df = remover_coramo_nulo(df)
        df = tratar_nulos(df)
        df = tratar_duplicidade(df)

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
        logger.info("===== Fim da execução: transform_susep_seguros_silver =====\n")


if __name__ == "__main__":
    main()
