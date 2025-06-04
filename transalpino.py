from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime
import os
import duckdb

def extrair_viagens_brasil(navegador):
    destinos = navegador.find_elements(By.CLASS_NAME, "item-title")
    precos = navegador.find_elements(By.CSS_SELECTOR, ".item-price")
    descricoes = navegador.find_elements(By.CLASS_NAME, "item-descr")
    descricoes_completas = navegador.find_elements(By.CLASS_NAME, "item-desc")

    resultados = []

    if destinos and precos and descricoes and descricoes_completas:
        for destino, preco, descricao, descricao_completa in zip(destinos, precos, descricoes, descricoes_completas):
                resultados.append({
                    "destino": destino.text,
                    "preco": preco.text,
                    "descricao": f"{descricao.text} {descricao_completa.text}"  
                })
    return resultados

urls = [
    "https://www.transalpino.pt/cat/5-praias/",
    "https://www.transalpino.pt/cat/3-cruzeiros/",
    "https://www.transalpino.pt/cat/1-pacotes/",
    "https://www.transalpino.pt/cat/4-lua-de-mel/",
    "https://www.transalpino.pt/cat/9-cidades/" 
]

data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_json = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json", f"transalpino_resultados_{data_hoje}.json"
)
caminho_banco = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json", "destinosbrasilbronze.duckdb"
)

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")  

navegador = webdriver.Chrome(options=options)

resultados_all = []

try:
    for url in urls:
        navegador.get(url)
        resultados = extrair_viagens_brasil(navegador)
        resultados_all.extend(resultados)
finally:
    navegador.quit()

with open(caminho_json, mode="w", encoding="utf-8") as f:
    json.dump(resultados_all, f, ensure_ascii=False, indent=2)

con = duckdb.connect(caminho_banco)
con.execute(f"""
    CREATE OR REPLACE TABLE Transalpino AS 
    SELECT * FROM read_json_auto('{caminho_json}')
""")
con.close()