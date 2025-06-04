from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
import os
import duckdb

data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_json = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json", 
    f"jetmar_resultados_{data_hoje}.json"
)
caminho_banco = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json", 
    "destinosbrasilbronze.duckdb"
)

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")  
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

navegador = webdriver.Chrome(options=options)

try:
    url = "https://www.jetmar.com.uy/paquetes/shop?location=america%20del%20sur,brasil"
    navegador.get(url)
    time.sleep(5)

    pacotes = navegador.find_elements(By.CSS_SELECTOR, 'div.row.d-flex.justify-content-center app-package-search-result')

    resultados = []

    for pacote in pacotes:
        try:
            destino = pacote.find_element(By.CSS_SELECTOR, 'h5').text.strip()
            descricao = pacote.find_element(By.CSS_SELECTOR, 'div.g-package-value-adds').text.strip()
            preco = pacote.find_element(By.CSS_SELECTOR, 'span.g-flight-price').text.strip()
            moeda = pacote.find_element(By.CSS_SELECTOR, 'span.g-flight-price-currency.mr-1').text.strip()
            resultados.append({
                "destino": destino,
                "descricao": descricao,
                "preco": f"{moeda} {preco}"
            })
        except Exception as e:
            print("Erro ao extrair dados de um pacote:", e)

    # Save to JSON
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    # Save to DuckDB
    con = duckdb.connect(caminho_banco)
    con.execute(f"""
        CREATE OR REPLACE TABLE Jetmar AS 
        SELECT * FROM read_json_auto('{caminho_json}')
    """)
    con.close()

finally:
    navegador.quit()