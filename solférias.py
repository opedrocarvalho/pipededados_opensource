from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import duckdb

data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_banco = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\database", "destinosbrasilbronze.duckdb"
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
            resultados.append({
                "data_extracao": data_hoje,
                "destino": destino.text,
                "preco": preco.text
            })

    con = duckdb.connect(caminho_banco)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS Sol_Ferias (
            data_extracao DATE,
            destino VARCHAR,
            preco VARCHAR
        )
    """)
    
    if resultados:
        con.executemany("""
            INSERT INTO Sol_Ferias (data_extracao, destino, preco)
            VALUES (?, ?, ?)
        """, [(r["data_extracao"], r["destino"], r["preco"]) for r in resultados])
    
    
    
    con.close()

finally:
    navegador.quit()