from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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
                    "data_extracao": datetime.today().strftime("%Y-%m-%d"),  
                    "destino": destino.text,
                    "preco": preco.text,
                    "descricao": f"{descricao.text} {descricao_completa.text}",
                    "url": navegador.current_url  
                })
    return resultados


urls = [
    "https://www.transalpino.pt/cat/5-praias/",
    "https://www.transalpino.pt/cat/3-cruzeiros/",
    "https://www.transalpino.pt/cat/1-pacotes/",
    "https://www.transalpino.pt/cat/4-lua-de-mel/",
    "https://www.transalpino.pt/cat/9-cidades/" 
]

caminho_banco = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\database", "destinosbrasilbronze.duckdb"
)
con = duckdb.connect(caminho_banco)

con.execute("""
    CREATE TABLE IF NOT EXISTS Transalpino (
        data_extracao DATE,
        destino VARCHAR,
        preco VARCHAR,
        descricao VARCHAR,
        url VARCHAR
    )
""")

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")  
navegador = webdriver.Chrome(options=options)

try:
    for url in urls:
        navegador.get(url)
        resultados = extrair_viagens_brasil(navegador)
        
        if resultados:
            con.executemany("""
                INSERT INTO Transalpino (data_extracao, destino, preco, descricao, url)
                VALUES (?, ?, ?, ?, ?)
            """, [
                (r["data_extracao"], r["destino"], r["preco"], r["descricao"], r["url"]) 
                for r in resultados
            ])
    

finally:
    navegador.quit()
    con.close()  