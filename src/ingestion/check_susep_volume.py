import pandas as pd

INPUT_FILE = "data/raw/susep/base_completa/Ses_seguros.csv"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="latin-1", low_memory=False)

print("=== VOLUME ===")
print(f"Total de linhas: {len(df):,}")
print(f"Total de colunas: {df.shape[1]}")
print(f"Colunas: {list(df.columns)}")

print("\n=== PERIODICIDADE ===")
col_data = "damesano" if "damesano" in df.columns else None
if col_data:
    print(f"Menor período: {df[col_data].min()}")
    print(f"Maior período: {df[col_data].max()}")
    print(f"Qtd de períodos distintos: {df[col_data].nunique()}")
else:
    print("Coluna 'damesano' não encontrada. Colunas disponíveis:", list(df.columns))
