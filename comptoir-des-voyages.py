from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime
import os
import duckdb

data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_json = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json",
    f"comptoir_resultados_{data_hoje}.json"
)
caminho_banco = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json",
    "destinosbrasilbronze.duckdb"
)

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless") 
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://www.comptoirdesvoyages.fr/voyage-pays/bresil/bra")
    
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "module__tripCard__card__info")))

    resultados = []
    cards = driver.find_elements(By.CLASS_NAME, "module__tripCard__card__info")

    for card in cards:
        try:
            destino = card.find_element(By.CLASS_NAME, "module__tripCard__card__link").text.strip()
            url = card.find_element(By.CLASS_NAME, "module__tripCard__card__link").get_attribute("href").strip()
            descricao = card.find_element(By.TAG_NAME, "span").text.strip()
            duracao = card.find_element(By.CLASS_NAME, "module__tripCard__card__duration").text.strip()
            preco = card.find_element(By.CLASS_NAME, "module__tripCard__card__price").text.strip()

            resultados.append({
                "destino": destino,
                "url": url,
                "descricao": descricao,
                "duracao": duracao,
                "preco": preco
            })
        except Exception as e:
            print("Erro ao processar:", e)

    # Salvar em JSON
    with open(caminho_json, mode="w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    # Salvar no DuckDB
    con = duckdb.connect(caminho_banco)
    con.execute(f"""
        CREATE OR REPLACE TABLE Comptoir_Des_Voyages AS 
        SELECT * FROM read_json_auto('{caminho_json}')
    """)
    con.close()

finally:
    driver.quit()