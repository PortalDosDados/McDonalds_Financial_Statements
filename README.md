# McDonalds Financial Statements

Este repositório contém um notebook e um scaffold para processar os demonstrativos financeiros do McDonald's (2002–2022).

## Setup rápido

1. Criar o ambiente virtual `venv` e instalar dependências:

```powershell
python -m venv venv
.\venv\Scripts\python -m pip install --upgrade pip
.\venv\Scripts\python -m pip install -r requirements.txt
```

2.Baixar os dados do Kaggle (coloque `kaggle.json` em `%USERPROFILE%\.kaggle\kaggle.json`):

```powershell
./scripts/download_data.ps1
```

3.Abrir `main.ipynb` e seguir as células (ETL em `src/etl.py`).

### Observações

- Os dados serão processados em Python e modelados em esquema fato/dimensão para uso posterior no Power BI.
- O script `scripts/download_data.ps1` usa a CLI `kaggle`. Se preferir, rode manualmente:

```powershell
kaggle datasets download -d mikhail1681/mcdonalds-financial-statements-2002-2022 -p data --unzip
```
