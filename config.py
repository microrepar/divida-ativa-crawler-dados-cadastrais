import contextlib
import csv
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

HERE = Path(__name__).parent

(HERE / 'data' / 'external').mkdir(parents=True, exist_ok=True)
(HERE / 'data' / 'interim').mkdir(parents=True, exist_ok=True)
(HERE / 'data' / 'processed').mkdir(parents=True, exist_ok=True)
(HERE / 'data' / 'raw').mkdir(parents=True, exist_ok=True)


# Defina o caminho para o arquivo CSV
caminho_arquivo1 = HERE / 'data' / 'raw' / "memo_imobiliario.csv"
caminho_arquivo2 = HERE / 'data' / 'raw' / "memo_mobiliario.csv"

# Defina os dados que serão escritos na coluna
dados_coluna = ["tipo", "inscricao", "status"]  # Substitua pelos seus próprios dados

if not caminho_arquivo1.exists():
    # Escreva os dados no arquivo CSV
    with open(caminho_arquivo1, "w", newline="") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        escritor_csv.writerow(dados_coluna)

if not caminho_arquivo2.exists():
    # Escreva os dados no arquivo CSV
    with open(caminho_arquivo2, "w", newline="") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        escritor_csv.writerow(dados_coluna)


class Config:

    URL = os.getenv('URL')
    URL_IMOB = os.getenv('URL_IMOB')
    URL_MOB = os.getenv('URL_MOB')

    USUARIO = os.getenv('USUARIO')
    SENHA   = os.getenv('SENHA')
