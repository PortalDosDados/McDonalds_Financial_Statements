# ==========================================
# ETAPA 1: IMPORTS
# ==========================================
import kagglehub
import os
import shutil

# ==========================================
# ETAPA 2: DOWNLOAD DO DATASET
# ==========================================
dataset = "mikhail1681/mcdonalds-financial-statements-2002-2022"

print("Baixando dataset do Kaggle...")
path = kagglehub.dataset_download(dataset)

print(f"Dataset baixado em: {path}")

# ==========================================
# ETAPA 3: ORGANIZAR NA PASTA DO PROJETO
# ==========================================
destino = "data"
os.makedirs(destino, exist_ok=True)

print("Movendo arquivos para pasta /data ...")

for file in os.listdir(path):
    origem_arquivo = os.path.join(path, file)
    destino_arquivo = os.path.join(destino, file)

    shutil.copy(origem_arquivo, destino_arquivo)

print("Arquivos prontos na pasta /data")
