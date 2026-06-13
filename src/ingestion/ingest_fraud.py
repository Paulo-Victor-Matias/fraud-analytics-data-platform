import pandas as pd
from pathlib import Path

INPUT_FILE = "data/raw/fraud/extracted/creditcard.csv"
OUTPUT_FILE = "data/bronze/fraud_transactions.parquet"

def extract():
  print("Extraindo dados...")

  df = pd.read_csv(INPUT_FILE)

  print(f"Registros encontrados: {len(df):,}")

  return df

def transform(df):
  print("Transformação: nenhuma regra aplicada")

  return df

def load(df):
  print("Salvando arquivo parquet...")

  Path("data/bronze").mkdir(
    parents=True, 
    exist_ok=True
  )

  df.to_parquet(
    OUTPUT_FILE, 
    index=False
  )


def main():
  df = extract()
  df = transform(df)

  load(df)

  print("Pipeline concluído com sucesso!")


if __name__ == "__main__":
    main()