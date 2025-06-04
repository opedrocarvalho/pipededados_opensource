from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime
import os
import duckdb

data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_json = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json", f"solferias_resultados_{data_hoje}.json"
)
caminho_banco = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json", "destinosbrasilbronze.duckdb"
)

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless") 

navegador = webdriver.Chrome(options=options)

try:
    navegador.get("https://www.solferias.pt/#zona/view/59")

    WebDriverWait(navegador, 15).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "itemBgBlue"))
    )

    destinos = navegador.find_elements(By.CLASS_NAME, "listThumbnailTitle")
    precos = navegador.find_elements(By.CSS_SELECTOR, ".listThumbnailText span")

    resultados = []

    if destinos and precos:
        for destino, preco in zip(destinos, precos):
            resultados.append({"destino": destino.text, "preco": preco.text})

    with open(caminho_json, mode="w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    # Conecta ao DuckDB e insere os dados na tabela Panam
    con = duckdb.connect(caminho_banco)
    con.execute(f"""
        CREATE OR REPLACE TABLE Sol_Ferias AS 
        SELECT * FROM read_json_auto('{caminho_json}')
    """)
    con.close()

finally:
    navegador.quit()
