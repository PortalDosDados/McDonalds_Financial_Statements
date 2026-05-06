"""ETL para tratar e modelar os demonstrativos em esquema fato/dimensão.

Funcionalidades implementadas:
- `load_raw`: carrega CSVs de `data/` (concatena se houver mais de um).
- `clean_df`: normaliza nomes, converte datas e numéricos detectados.
- `model_fact_dimension`: detecta coluna de data, entidades e medidas; cria `dim_date`, `dim_entity` e `fact_financials`.
- `save_models`: salva fact/dimensions em `data/models/`.

O código tenta mapear colunas automaticamente por heurísticas (palavras-chave). Ajuste conforme o CSV real se necessário.
"""

from pathlib import Path
import re
import pandas as pd
import numpy as np
from typing import Dict


def download_data():
    """Opcional: chamar externamente o script PowerShell `scripts/download_data.ps1`."""
    raise NotImplementedError(
        "Use scripts/download_data.ps1 ou execute a chamada kaggle manualmente."
    )


def load_raw(data_dir: str = "data") -> pd.DataFrame:
    """Carrega todos os CSVs em `data/` e concatena em um único DataFrame.

    Se não encontrar CSVs, lança FileNotFoundError.
    """
    p = Path(data_dir)
    csvs = list(p.glob("**/*.csv"))
    if not csvs:
        raise FileNotFoundError(
            "Nenhum CSV encontrado em data/. Execute o script de download."
        )
    dfs = []
    for f in csvs:
        try:
            dfs.append(pd.read_csv(f))
        except Exception:
            dfs.append(pd.read_csv(f, engine="python"))
    if not dfs:
        raise FileNotFoundError("Falha ao carregar CSVs em data/.")
    if len(dfs) == 1:
        return dfs[0]
    return pd.concat(dfs, ignore_index=True, sort=False)


def _standardize_colname(c: str) -> str:
    c = str(c).strip()
    c = c.replace("\n", " ")
    c = re.sub(r"[^0-9a-zA-Z]+", "_", c)
    c = re.sub(r"_+", "_", c)
    return c.strip("_").lower()


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza colunas, converte datas e detecta/limpa colunas numéricas.

    - Normaliza nomes de colunas (snake_case, lowercase).
    - Converte colunas com 'date' ou 'year' para datetime quando possível.
    - Detecta colunas com valores monetários/numéricos e converte para float.
    """
    df = df.copy()
    # Normaliza nomes
    col_map = {c: _standardize_colname(c) for c in df.columns}
    df.rename(columns=col_map, inplace=True)

    # Detecta e converte colunas de data
    date_candidates = [
        c for c in df.columns if "date" in c or "period" in c or c == "year"
    ]
    for c in date_candidates:
        try:
            if df[c].dtype == object or np.issubdtype(df[c].dtype, np.number):
                if df[c].dropna().astype(str).str.match(r"^\d{4}$").all():
                    df[c] = pd.to_datetime(
                        df[c].astype(int).astype(str) + "-01-01", errors="coerce"
                    )
                else:
                    df[c] = pd.to_datetime(df[c], errors="coerce")
        except Exception:
            continue

    # Converte colunas numericas escritas com $ (monetary) ou com vírgula
    def try_clean_numeric(s: pd.Series) -> pd.Series:
        if s.dtype == object:
            sample = s.dropna().astype(str).head(10).tolist()
            joined = " ".join(sample)
            if any(ch in joined for ch in ["$", "(", ",", ")"]) or re.search(
                r"\d+[,\.]\d{3}", joined
            ):
                cleaned = (
                    s.astype(str)
                    .str.replace(r"[\$,\s]", "", regex=True)
                    .str.replace(r"\(([^)]+)\)", r"-\1", regex=True)
                )
                return pd.to_numeric(cleaned, errors="coerce")
        return s

    for c in df.columns:
        df[c] = try_clean_numeric(df[c])

    return df


def model_fact_dimension(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Gera `dim_date`, possivelmente `dim_entity` e `fact_financials`.

    Heurística:
    - Detecta coluna datetime; cria `dim_date` com `date_id` e `date`.
    - Detecta coluna de entidade (company, issuer, ticker) para `dim_entity`.
    - Considera todas as colunas numéricas como medidas da fact.
    - Se tiver colunas categóricas relevantes (segment, account), preserva como dimensão.
    """
    df = df.copy()
    # detecta coluna de data
    date_col = None
    for c in df.columns:
        if np.issubdtype(df[c].dtype, np.datetime64):
            date_col = c
            break
    # fallback: coluna 'year'
    if date_col is None and "year" in df.columns:
        try:
            df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(
                pd.Int64Dtype()
            )
            df["__date"] = pd.to_datetime(
                df["year"].astype(str) + "-01-01", errors="coerce"
            )
            date_col = "__date"
        except Exception:
            date_col = None

    if date_col is None:
        for key in ["fiscal_year", "period", "report_date"]:
            if key in df.columns:
                try:
                    df[key] = pd.to_datetime(df[key], errors="coerce")
                    date_col = key
                    break
                except Exception:
                    continue

    dims = {}
    if date_col is not None:
        dim_date = (
            pd.DataFrame({"date": pd.to_datetime(df[date_col], errors="coerce")})
            .dropna()
            .drop_duplicates()
            .sort_values("date")
            .reset_index(drop=True)
        )
        dim_date["date_id"] = dim_date.index + 1
        dim_date["year"] = dim_date["date"].dt.year
        dim_date["month"] = dim_date["date"].dt.month
        dims["dim_date"] = dim_date[["date_id", "date", "year", "month"]]
        df = df.merge(dims["dim_date"], left_on=date_col, right_on="date", how="left")
    else:
        df["date_id"] = pd.NA

    # detecta entidade (company, entity, issuer, ticker)
    entity_col = None
    for k in ["company", "entity", "issuer", "ticker", "symbol"]:
        if k in df.columns:
            entity_col = k
            break

    if entity_col is not None:
        dim_entity = df[[entity_col]].drop_duplicates().reset_index(drop=True)
        dim_entity["entity_id"] = dim_entity.index + 1
        dim_entity.rename(columns={entity_col: "entity_name"}, inplace=True)
        dims["dim_entity"] = dim_entity[["entity_id", "entity_name"]]
        df = df.merge(
            dims["dim_entity"], left_on=entity_col, right_on="entity_name", how="left"
        )
    else:
        df["entity_id"] = pd.NA

    # colunas numéricas -> medidas
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_cols = [c for c in num_cols if c not in ("date_id", "entity_id")]

    if not num_cols:
        num_cols = [
            c
            for c in df.columns
            if any(
                k in c
                for k in (
                    "revenue",
                    "income",
                    "profit",
                    "assets",
                    "equity",
                    "expense",
                    "cash",
                )
            )
        ]

    fact_cols = ["date_id", "entity_id"] + num_cols
    fact_cols = [c for c in fact_cols if c in df.columns]
    fact = df[fact_cols].copy()

    dims["fact_financials"] = fact

    return dims


def save_models(models: Dict[str, pd.DataFrame], out_dir: str = "data/models") -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in models.items():
        safe_name = re.sub(r"[^0-9a-zA-Z_]+", "_", name)
        path = out / f"{safe_name}.csv"
        df.to_csv(path, index=False)


def save_clean(df: pd.DataFrame, out_path: str = "data/cleaned_mcdo.csv"):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


if __name__ == "__main__":
    print(
        "ETL implementado: use load_raw(), clean_df(), model_fact_dimension(), save_models()"
    )
