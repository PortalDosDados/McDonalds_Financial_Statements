"""Scaffold ETL para tratar e modelar os dados em esquema fato/dimensão.
Uso: completar funções de acordo com os nomes de colunas do CSV baixado.
"""
from pathlib import Path
import pandas as pd


def download_data():
    """Opcional: chama o script PowerShell para baixar os dados localmente."""
    # Pode-se usar subprocess para executar scripts se desejado.
    pass


def load_raw(data_dir: str = 'data') -> pd.DataFrame:
    """Carrega CSVs do diretório data e combina em um DataFrame único."""
    p = Path(data_dir)
    csvs = list(p.glob('**/*.csv'))
    if not csvs:
        raise FileNotFoundError('Nenhum CSV encontrado em data/. Execute o script de download.')
    # Por enquanto carrega o primeiro
    df = pd.read_csv(csvs[0])
    return df


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza genérica: converter numéricos, datas e normalizar colunas."""
    # Implementar limpeza conforme o dataset real
    return df


def model_fact_dimension(df: pd.DataFrame) -> dict:
    """Transforma df em dicionário com 'fact' e 'dimensions' (DataFrames).
    Exemplo:
      return {'fact_financials': fact_df, 'dim_date': dim_date_df, ...}
    """
    # Implementar modelagem fato-dimensão conforme colunas
    return {}


def save_clean(df: pd.DataFrame, out_path: str = 'data/cleaned_mcdo.csv'):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


if __name__ == '__main__':
    print('ETL scaffold. Edite src/etl.py para implementar passos.')
