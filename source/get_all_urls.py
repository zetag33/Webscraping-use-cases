# This script generates a txt that contains all the urls to be scrapped, those are taken from the initial catalog of cities in the province. For each city we get all its urls that are structured by sector. So there are approximately 168 sectors per city and there are approximately
# 58 cities in my province. Returns 9600 urls that may have child urls and those will be taken care later.
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

def options():

    options = ChromeOptions()
    # Activem javascript
    options.add_argument("--enable-javascript")
    # Associem al driver un useragent humà
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
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


def get_links_provincia(url):
    driver = webdriver_example()
    driver.get(url)
    page_source = driver.page_source
    time.sleep(10)
    soup = BeautifulSoup(page_source, 'html.parser')
    menuscroll_divs = soup.find_all('div', class_="menuscroll")
    hrefs = []
    for div in menuscroll_divs:
        anchor_tags = div.find_all('a', href=True)
        for anchor in anchor_tags:
            hrefs.append(anchor['href'])
    print(len(hrefs), hrefs)
    return hrefs

def get_links_localidad(url):

    driver = webdriver_example()
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    ficha_divs = soup.find_all('div', class_="ficha")
    hrefs = []
    for div in ficha_divs:
        p_tags = div.find_all('p')
        for p in p_tags:
            anchor_tags = p.find_all('a', href=True)
            for anchor in anchor_tags:
                href = anchor['href']
                if 'juzgados' not in href and 'caja-rural' not in href:
                    hrefs.append(href)
    return hrefs


localidades = get_links_provincia('https://www.paginasamarillas.es/all_tarragona_reus.html')
total_links = []
for i in localidades:
    sectores = get_links_localidad(i)
    total_links.append(sectores)
total_links = [item for sublist in total_links for item in sublist]
with open('urls.txt', 'w') as file:
    for link in total_links:
        file.write(link + '\n')
