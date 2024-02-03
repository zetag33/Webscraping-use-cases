
from selenium import webdriver
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
import builtwith
import concurrent.futures
import threading

csv_lock = threading.Lock()


def remove_last_number(url):
    pattern = r'/(\d+)$'
    match = re.search(pattern, url)

    if match:
        last_number = match.group(1)
        url_without_last_number = url[:-len(last_number)]
        return url_without_last_number
    else:
        return url

def get_csv(data ,province ,city):
    with csv_lock:
        # Aquesta funció s'encarrega d'escriure el fitxer csv, en cas de que ja existeixi simplement escriu les dades al final del mateix fitxer
        # Obtenim la data d'avui
        current_date = datetime.now().strftime("%Y_%m_%d")
        # Fixem el nom del fitxer i la ruta, es genera amb la data d'execució. Si ja s'ha generat previament ho comprovarem i escriurem al final
        csv_file = f"C:\\Users\\Usuario\\PycharmProjects\\paginas_amarillas\\paginas_amarillas_{current_date}.csv"

        # Comprovem si el fitxer ja existeix
        file_exists = os.path.isfile(csv_file)

        # Escrivim el fitxer o afegim al fitxer
        with open(csv_file, mode='a' if file_exists else 'w', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:
                # creem un header
                header = ["Title", "Price", "Reduction", "Rooms", "Bathrooms", "Meters", "Province"]
                writer.writerow(header)

            # Escrivim les dades
            writer.writerows(data)
        # Enviem missatge d'exit
        return print(f'Csv data written successfully {province}{city}')

def options():

    options = ChromeOptions()
    # Activem javascript
    options.add_argument("--enable-javascript")
    # Associem al driver un useragent humà
    options.add_argument \
        ("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    options.add_argument("--headless")
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



def get_province(url):
    url = remove_last_number(url)
    match = re.search(r'/([^/]+)/([^/]+)/$', url)
    if match:
        province = match.group(1)
    else:
        province = None
    return province

def get_city(url):
    url = remove_last_number(url)
    match = re.search(r'/([^/]+)/([^/]+)/$', url)
    if match:
        city = match.group(2)
    else:
        city = None
    return city

def get_category(url):
    url = remove_last_number(url)
    url_parts = url.split('/')
    category = url_parts[4]
    return category

def get_soup(url):
    driver = webdriver_example()
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

def type_checker(soup):
    map = soup.find('div', class_="mapping")
    if map:
        type = 2
    else:
        type = 1
    return type

def parse_one(soup, province, city):
    boxes = soup.find_all('div', class_="box")
    data = []
    for box in boxes:
        name = box.find('span', {'itemprop': 'name'})
        if name is not None:
            name = name.text
            category_p = box.find('p', class_='categ')
            category = category_p.text if category_p else "-"
            address_span = box.find('span', {'itemprop': 'streetAddress'})
            postal_code_span = box.find('span', {'itemprop': 'postalCode'})
            address = address_span.text if address_span else "-"
            postal_code = postal_code_span.text if postal_code_span else "-"
            telephone_span = box.find('span', {'itemprop': 'telephone'})
            telephone = telephone_span.text if telephone_span else "-"
            web_span = box.find('a', class_='web')
            web = web_span.get('href') if web_span else "-"
            try:
                techno = builtwith.builtwith(web) if web != "-" else "-"
            except Exception:
                techno = "Unable to decode"
            description_span = box.find('div', {'itemprop': 'description'})
            if description_span:
                p_tag_span = description_span.find('p')
                description = p_tag_span.text if p_tag_span else "-"
            else:
                description = "-"
            data.append((name, category, address, postal_code, telephone, web, techno, description, province, city))
        else:
            pass
    get_csv(data, province, city)
    return print(f'Se han escrito{len(data)}')

def get_next_link(soup):
    pagination_ul = soup.find('ul', class_='pagination')
    print(pagination_ul)
    if pagination_ul:
        li_tags = pagination_ul.find_all('li')
        print(li_tags)
        if str(li_tags[-1]) == '<li></li>':
            last_li = li_tags[-2]
        else:
            last_li = li_tags[-1]
        print(last_li)
        last_a = last_li.find('a')
        print(last_a)
        href_value = last_a.get('href') if last_a else ''
        print(href_value)
        if href_value is not None and href_value != 'javascript:void()':
            next_link = href_value
        else:
            next_link = ''
    else:
        next_link = ''
    return next_link

def parse_two(soup ,province ,city ,category):
    boxes = soup.find_all('div', class_="box")
    data = []
    for box in boxes:
        name = box.find('h2', {'itemprop': 'name'})
        if name is not None:
            name = name.text
            categoria = category
            address_span = box.find('span', {'itemprop': 'streetAddress'})
            address = address_span.text if address_span else "-"
            postal_code_span = box.find('span', {'itemprop': 'postalCode'})
            postal_code = postal_code_span.text if postal_code_span else "-"
            telephone_span = box.find('span', {'itemprop': 'telephone'})
            telephone = telephone_span.text if telephone_span else "-"
            web = '-'
            techno = '-'
            description = '-'
            data.append((name, categoria, address, postal_code, telephone, web, techno, description, province, city))
        else:
            pass
    get_csv(data ,province ,city)
    return print(f'Se han escrito {len(data)} de {categoria}')


def micro_url(url):
    province = get_province(url)
    print(province)
    city = get_city(url)
    print(city)
    category = get_category(url)
    print(category)
    soup = get_soup(url)
    type = type_checker(soup)
    print(type)
    if type == 1:
        parse_one(soup ,province ,city)
        next_link = get_next_link(soup)
    else:
        parse_two(soup ,province ,city, category)
        next_link = ''
    print(next_link)
    while next_link != '':
        print("I'm in next_link")
        province = get_province(next_link)
        city = get_city(next_link)
        category = get_category(next_link)
        soup = get_soup(next_link)
        print(f'Scrapped {next_link}')
        type = type_checker(soup)
        if type == 1:
            parse_one(soup, province, city)
            next_link = get_next_link(soup)
        else:
            parse_two(soup, province, city ,category)
            next_link = ''
        print(f'Getting {next_link} 1')
    print('Scapped the while loop 1')
    print(url, "Scraped succesfully")

def main():

    with open('C:\\Users\\Usuario\\PycharmProjects\\paginas_amarillas\\urls.txt', 'r') as file:
        url_list = [line.strip() for line in file]

    # Set the maximum number of parallel processes
    max_processes = 10
    with concurrent.futures.ProcessPoolExecutor(max_processes) as executor:
        futures = [executor.submit(micro_url, url) for url in url_list]
        for future in concurrent.futures.as_completed(futures):
            # Process has completed
            print(f"Number of completed processes: {len([f for f in futures if f.done()])}")
    # Wait for all processes to finish
    concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)


if __name__ == "__main__":
    initial = time.time()
    main()
    end_time = time.time()
    elapsed_time = end_time - initial
    print(f"Processed in {elapsed_time} seconds.")



