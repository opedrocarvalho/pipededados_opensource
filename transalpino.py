from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def extrair_viagens_brasil(navegador):
    cidades = navegador.find_elements(By.CLASS_NAME, "item-title")
    precos = navegador.find_elements(By.CSS_SELECTOR, ".item-price")
    descricoes = navegador.find_elements(By.CLASS_NAME, "item-descr")

    resultados = []

    if cidades and precos and descricoes:
        for cidade, preco, descr in zip(cidades, precos, descricoes):
            if "brasil" in descr.text.lower():
                resultados.append((cidade.text, preco.text))
    return resultados

urls = [
    "https://www.transalpino.pt/cat/5-praias/",
    "https://www.transalpino.pt/cat/3-cruzeiros/",
    "https://www.transalpino.pt/cat/1-pacotes/",
    "https://www.transalpino.pt/cat/4-lua-de-mel/",
    "https://www.transalpino.pt/cat/9-cidades/"
]

options = Options()
options.add_argument("--start-maximized")

navegador = webdriver.Chrome(options=options)

resultados_all = []

try:
    for url in urls:
        navegador.get(url)
        resultados = extrair_viagens_brasil(navegador)
        resultados_all.extend(resultados)
finally:
    navegador.quit()

if resultados_all:
    for cidade, preco in resultados_all:
        print(f"Cidade: {cidade} Preço: {preco}")
