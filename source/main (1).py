from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import random
import re
import requests
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import csv
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.chrome.service import Service
import os
import concurrent.futures
import threading

def options():

    options = ChromeOptions()
    # Activem javascript
    options.add_argument("--enable-javascript")
    # Associem al driver un useragent humà
    options.add_argument \
        ("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    #options.add_argument("--headless")
    # Desactivem les blink features
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Configurem la proxy a las opcions del driver
    # Desactivem el carregat d'imatges.
    options.add_argument("--disable-image-loading")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-popup-blocking")
    return options



def webdriver_example():

    # El creem amb les opcions de la proxy escollida cridant a la funcio smartproxy anterior.
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                               options=options())

    return browser

def scroll_down_slowly(driver):
    driver.execute_script("window.scrollBy(0, 100);")
    time.sleep(0.5)  # Adjust the sleep time based on your preference

def get_code(palabra: str):
    driver = webdriver_example()
    driver.get("https://es.wallapop.com/")
    search_box = driver.find_element(By.ID, "searchbox-form-input")
    search_query = palabra
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    target_class = "btn-load-more"
    button = driver.find_element(By.ID, target_class)
    if button:
        button.click()
    time.sleep(10)
    scroll_height = 0
    start_time = time.time()
    while True:
        driver.execute_script("window.scrollTo(0, arguments[0]);", scroll_height)
        time.sleep(5)
        scroll_height += 500
        if scroll_height >= driver.execute_script("return document.body.scrollHeight"):
            break
        elapsed_time = time.time() - start_time
        if elapsed_time >= 30:
            break
    info = driver.page_source
    driver.quit()
    return info

def parse_code(info):
    data = []
    soup = BeautifulSoup(info, 'html.parser')
    containers = soup.find_all('div', class_='ItemCard__data')
    for container in containers:
        # Extract price information
        price_span = container.find('span', class_='ItemCard__price')
        price = price_span.text.strip() if price_span else "N/A"

        # Extract title information
        title_p = container.find('p', class_='ItemCard__title')
        title = title_p.text.strip() if title_p else "N/A"
        data.append((title, price))
    return data


def get_csv(data, palabra):
    # Aquesta funció s'encarrega d'escriure el fitxer csv, en cas de que ja existeixi simplement escriu les dades al final del mateix fitxer
    # Obtenim la data d'avui
    current_date = datetime.now().strftime("%Y_%m_%d")
    # Fixem el nom del fitxer i la ruta, es genera amb la data d'execució. Si ja s'ha generat previament ho comprovarem i escriurem al final
    csv_file = f"C:\\Users\\ROG STRIX\\PycharmProjects\\pythonProject\\wallapop_{palabra}_{current_date}.csv"

    # Comprovem si el fitxer ja existeix
    file_exists = os.path.isfile(csv_file)

    # Escrivim el fitxer o afegim al fitxer
    with open(csv_file, mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            # creem un header
            header = ["Title", "Price"]
            writer.writerow(header)

        # Escrivim les dades
        writer.writerows(data)
    # Enviem missatge d'exit
    return print(f'Csv data written successfully {palabra}{current_date}')

def main(palabra: str):
    info = get_code(palabra)
    data = parse_code(info)
    get_csv(data, palabra)


main("secador dyson")
