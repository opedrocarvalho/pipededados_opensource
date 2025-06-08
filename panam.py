from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import os
import duckdb
import time

data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_banco = os.path.join(r"C:\Users\Pedro Carvalho\Desktop\database", "destinosbrasilbronze.duckdb")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)
con = duckdb.connect(caminho_banco)

try:
    con.execute("""
        CREATE TABLE IF NOT EXISTS Panam (
            data_extracao DATE,
            destino VARCHAR,
            preco_usd VARCHAR,
        )
    """)
    
    
    driver.get("https://www.panam.cl/")
    
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "cookie-btn")))
        cookie_btn.click()
    except:
        pass
    
    driver.execute_script("window.scrollTo(0, 0)")
    destinos_menu = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "DESTINOS")))
    driver.execute_script("arguments[0].click();", destinos_menu)
    time.sleep(2)
    
    sudamerica_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "SUDAMÉRICA")))
    driver.execute_script("arguments[0].click();", sudamerica_link)
    time.sleep(2)
    
    select_pais = wait.until(EC.presence_of_element_located((By.ID, "paisPrograma")))
    Select(select_pais).select_by_visible_text("BRASIL")
    time.sleep(3)

    dados_para_inserir = []
    destinos = driver.find_elements(By.CSS_SELECTOR, "div.booking-item-container")
    
    for destino in destinos:
        try:
            paragrafos = destino.find_elements(By.CSS_SELECTOR, "div.booking-item-rating p")
            info_destino = "\n".join([p.text.strip() for p in paragrafos if p.text.strip()])
            preco_dolar = destino.find_element(By.CSS_SELECTOR, "h5.text-color > strong").text

            dados_para_inserir.append((
                data_hoje,
                info_destino,
                preco_dolar            ))
        except Exception as e:
            print(f"Erro ao processar destino: {str(e)}")

    # Inserção em lote no DuckDB
    if dados_para_inserir:
        con.executemany("""
            INSERT INTO Panam (data_extracao, destino, preco_usd)
            VALUES (?, ?, ?)
        """, dados_para_inserir)


finally:
    driver.quit()
    con.close()