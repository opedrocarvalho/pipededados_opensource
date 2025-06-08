from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import duckdb


data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_banco = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\databas",
    "destinosbrasilbronze.duckdb"
)


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless") 
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])


driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)
con = duckdb.connect(caminho_banco)

try:

    con.execute("""
        CREATE TABLE IF NOT EXISTS Comptoir_Des_Voyages (
            data_extracao DATE,
            destino VARCHAR,
            url VARCHAR,
            descricao VARCHAR,
            duracao VARCHAR,
            preco VARCHAR
        )
    """)
    

    driver.get("https://www.comptoirdesvoyages.fr/voyage-pays/bresil/bra")
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "module__tripCard__card__info")))


    cards = driver.find_elements(By.CLASS_NAME, "module__tripCard__card__info")
    dados_para_inserir = []

    for card in cards:
        try:
            destino = card.find_element(By.CLASS_NAME, "module__tripCard__card__link").text.strip()
            url = card.find_element(By.CLASS_NAME, "module__tripCard__card__link").get_attribute("href").strip()
            descricao = card.find_element(By.TAG_NAME, "span").text.strip()
            duracao = card.find_element(By.CLASS_NAME, "module__tripCard__card__duration").text.strip()
            preco = card.find_element(By.CLASS_NAME, "module__tripCard__card__price").text.strip()

            dados_para_inserir.append((
                data_hoje,
                destino,
                url,
                descricao,
                duracao,
                preco
            ))
        except Exception as e:
            print(f"Erro ao processar card: {e}")


    if dados_para_inserir:
        con.executemany("""
            INSERT INTO Comptoir_Des_Voyages 
            (data_extracao, destino, url, descricao, duracao, preco)
            VALUES (?, ?, ?, ?, ?, ?)
        """, dados_para_inserir)
        

finally:
    driver.quit()
    con.close()