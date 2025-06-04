from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
import duckdb
import time

# Configurações
data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_banco = os.path.join(r"C:\Users\Pedro Carvalho\Desktop\json", "destinosbrasilbronze.duckdb")

# Configuração do navegador
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

navegador = webdriver.Chrome(options=options)
con = duckdb.connect(caminho_banco)

try:
    con.execute("""
        CREATE OR REPLACE TABLE Jetmar (
            data_extracao DATE,
            destino VARCHAR,
            descricao VARCHAR,
            preco_completo VARCHAR
        )
    """)
    
    url = "https://www.jetmar.com.uy/paquetes/shop?location=america%20del%20sur,brasil"
    navegador.get(url)
    time.sleep(5) 


    dados_para_inserir = []
    pacotes = navegador.find_elements(By.CSS_SELECTOR, 'div.row.d-flex.justify-content-center app-package-search-result')
    
    for pacote in pacotes:
        try:
            destino = pacote.find_element(By.CSS_SELECTOR, 'h5').text.strip()
            descricao = pacote.find_element(By.CSS_SELECTOR, 'div.g-package-value-adds').text.strip()
            preco = pacote.find_element(By.CSS_SELECTOR, 'span.g-flight-price').text.strip()
            moeda = pacote.find_element(By.CSS_SELECTOR, 'span.g-flight-price-currency.mr-1').text.strip()
            
            dados_para_inserir.append((
                data_hoje,
                destino,
                descricao,
                f"{moeda} {preco}",
                url
            ))
        except Exception as e:
            print(f"Erro ao processar pacote: {str(e)}")

    # Inserção em lote no DuckDB
    if dados_para_inserir:
        con.executemany("""
            INSERT INTO Jetmar (data_extracao, destino, descricao, preco_completo)
            VALUES (?, ?, ?, ?)
        """, dados_para_inserir)
        

finally:
    navegador.quit()
    con.close()