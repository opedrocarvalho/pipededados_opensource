from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
from datetime import datetime
import os
import duckdb

data_hoje = datetime.today().strftime("%Y-%m-%d")
caminho_json = os.path.join(
    r"C:\Users\Pedro Carvalho\Desktop\json", 
    f"panam_resultados_{data_hoje}.json"
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
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)

resultados = []

try:
    driver.get("https://www.panam.cl/")
    
    # Fechar pop-up de cookies se existir
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "cookie-btn")))
        cookie_btn.click()
    except:
        pass
    
    # Rolagem para garantir que o menu está visível
    driver.execute_script("window.scrollTo(0, 0)")
    
    # Esperar e clicar no menu Destinos com JavaScript como fallback
    destinos_menu = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "DESTINOS")))
    try:
        destinos_menu.click()
    except:
        driver.execute_script("arguments[0].click();", destinos_menu)
    
    # Esperar o carregamento do submenu
    time.sleep(2)
    
    # Clicar em Sudamérica com tentativa alternativa
    sudamerica_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "SUDAMÉRICA")))
    try:
        sudamerica_link.click()
    except:
        driver.execute_script("arguments[0].click();", sudamerica_link)
        time.sleep(2)
    
    # Selecionar Brasil no dropdown
    select_pais = wait.until(EC.presence_of_element_located((By.ID, "paisPrograma")))
    select = Select(select_pais)
    select.select_by_visible_text("BRASIL")
    time.sleep(3)

    # Extrair informações dos destinos
    destinos = driver.find_elements(By.CSS_SELECTOR, "div.booking-item-container")
    for destino in destinos:
        try:
            paragrafos = destino.find_elements(By.CSS_SELECTOR, "div.booking-item-rating p")
            info_destino = "\n".join([p.text.strip() for p in paragrafos if p.text.strip()])

            preco_dolar = destino.find_element(By.CSS_SELECTOR, "h5.text-color > strong").text

            resultados.append({
                "destino": info_destino,
                "preco_usd": preco_dolar
            })
        except Exception as e:
            print("Erro ao extrair informações de um destino:", e)

finally:
    driver.quit()

    # Salvar em JSON
    with open(caminho_json, mode="w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    # Salvar no DuckDB
    con = duckdb.connect(caminho_banco)
    con.execute(f"""
        CREATE OR REPLACE TABLE Panam AS 
        SELECT * FROM read_json_auto('{caminho_json}')
    """)
    con.close()