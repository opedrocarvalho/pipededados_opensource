from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--start-maximized")

navegador = webdriver.Chrome(options=options)

try:
    navegador.get("https://www.solferias.pt/#zona/view/59")

    WebDriverWait(navegador, 15).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "itemBgBlue"))
    )

    cidades = navegador.find_elements(By.CLASS_NAME, "listThumbnailTitle")
    
    precos = navegador.find_elements(By.CSS_SELECTOR, ".listThumbnailText span")

    if cidades and precos:
        for cidade, preco in zip(cidades, precos):
            print(f"Cidade: {cidade.text}  Preço: {preco.text}")

finally:

    navegador.quit()

# Conversão de moeda 
