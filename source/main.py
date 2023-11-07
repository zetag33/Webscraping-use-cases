# Importo totes les llibreries i moduls necessaris entre ells BeautifulSoup, selenium, csv, datetime o os
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


# Defineixo un llistat de proxies, cada tupla es una proxy, amb la seva ip(url en aquest cas), el port de conexió
# i el driver a fer servir. En aquest cas jo he fet servir un servei de pagament, smartproxy.com, això s'hem ha fet necesari
# ja que els llistats de proxies gratuites son dificils d'aconseguir i poc fiables. Sino fem servir proxy, la pagina web
# ens acaba bloquejant al fer 3 o 4 peticions seguides, en canvi quan les fem amb proxy com que cada una prové d'una ip diferent
# la pagina web no ens bloqueja, son proxies residencials espanyoles, no fa falta credencials de la proxy ja que tinc la meva ip
# "whitelisted" al proveidor de les proxies, el que vol dir que al detectar la meva ip ja no fa falta posar contraseña ni usuari.
# Aqui me n'he adonat que això es car, ja que descarreguem molts gb de dades al descarregar tot el codi carregat de javascript de la
# pagina web, tinc pendent en el futur optimitzar això, fer les peticions headless, no carregar imatges i intentar agafar només el necesari
# en comptes de tot el codi de la web, em queda pendent per futurs projectes, ja que sino no crec que el webscraping surti rentable
# el proveïdor cobra 6€ per cada GB.
proxy_list = [('es.smartproxy.com',10001,"CHROME"),
              ('es.smartproxy.com',10002,"CHROME"),
              ('es.smartproxy.com',10003,"CHROME"),
              ('es.smartproxy.com',10004,"CHROME"),
              ('es.smartproxy.com',10005,"CHROME"),
              ('es.smartproxy.com',10006,"CHROME"),
              ('es.smartproxy.com',10007,"CHROME"),
              ('es.smartproxy.com',10008,"CHROME"),
              ('es.smartproxy.com',10009,"CHROME"),
              ('es.smartproxy.com',10010,"CHROME")]


# Aquesta funcio s'encarrega d'entrar a la url original que conté tots els enllaços individuals de cada provincia.
# I extreurels.
def get_zone_links():
    # Selenium
    # Carreguem un driver mitjançant una funció que explicaré més endavant
    driver = webdriver_example()
    # Indiquem la url a scrapejar
    url = "https://www.fotocasa.es/es/comprar/viviendas/espana/todas-las-zonas/l"
    # Fem la petició a la pagina web
    driver.get(url)
    # Fem un sleep per tal de no carregar el servidor
    time.sleep(5)
    # Busquem el desplegable on estan les provincies i el clickem per tal de carregar el codi html amb el desplegable obert
    # i poder obtindre els links de les provincies. Si fem això headless no funcionarà, ja que al obrir la web s'hauria de clickar
    # acceptar a la privacitat de dades perque el desplegable estes disponible, em queda també pendent solucionar això per poder fer headless, però amb un simple click
    # acceptant manualment en aquesta petició s'ens desplega les províncies i s'obté les urls de cada una.
    dropdown = driver.find_element(By.CLASS_NAME, "sui-MoleculeSelectPopover-select")
    dropdown.click()
    # Obtenim el codi font de la web, ja carregat el javascript del desplegable de les provincies
    displayable_html = driver.page_source
    # Parsejem amb beautifulsoup
    soup = BeautifulSoup(displayable_html, 'html.parser')
    # Agafem de tot el codi només el element que conté les href de les provincies, curiosament aquest element em va canviar d'ubicació en el codi de la web en els dies
    # que estava fent aquest robot.
    link_items = soup.find_all('a', class_="sui-LinkBasic")
    # Obtinc les href
    hrefs = [link.get('href') for link in link_items]
    for href in hrefs:
        print(href)
    time.sleep(5)
    driver.quit()
    print(hrefs)
    # Retorno les direccions
    return hrefs

def get_catalonia(hrefs, provinces):
    # Aquesta funció pren dos atributs, un llistat de urls que proporciona la funció anterior dels links i un llistat de les provincies que volem scrapejar
    # Filtrem de tot el llistat de urls només les pertanyents a les provincies que volem
    search_words = provinces
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in search_words) + r')\b'
    filtered_strings = [s for s in hrefs if re.search(pattern, s, re.IGNORECASE)]
    result = []
    # Per cada una d'aquests urls de les provincies desitjades, excloim particulars, obra nova i només agafem les de comprar d'habitatges, basantnos
    # en el patro de les url.
    for url in filtered_strings:
        if not re.search(r"particulares", url) and not re.search(r"obra-nueva", url) and re.match(r"^/es/comprar/viviendas/", url):
            result.append(url)
    return result


def smartproxy(HOSTNAME, PORT, DRIVER):
    # Aquesta funció pren 3 elements, HOSTNAME(direcció ip de la proxy o url de la proxy), PORT i DRIVER
    # Configurem les opcions del driver que crearem posteriorment en un altre funció.
    options = ChromeOptions()
    # Activem javascript
    options.add_argument("--enable-javascript")
    # Associem al driver un useragent humà
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    #options.add_argument("--headless")
    # Desactivem les blink features
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Configurem la proxy a las opcions del driver
    proxy_str = '{hostname}:{port}'.format(hostname=HOSTNAME, port=PORT)
    options.add_argument('--proxy-server={}'.format(proxy_str))
    # Desactivem el carregat d'imatges.
    options.add_argument("--disable-image-loading")

    return options


def webdriver_example():
    # Aquesta funció creara el driver amb les opcions que li especifiquem a la funció anterior
    # Agafem una proxy al atzar
    hostname, port, driver = random.choice(proxy_list)
    # Creem el driver, adaptem a si el browser escollit es firefox o chrome.
    if driver == 'FIREFOX':
        browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()),
                                    options=smartproxy(hostname, port, driver))
    elif driver == 'CHROME':
        # El creem amb les opcions de la proxy escollida cridant a la funcio smartproxy anterior.
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                   options=smartproxy(hostname, port, driver))

    return browser


def get_content(urls, max_pages):
    # Aquesta funció sera la encarregada d'obtindre el contingut, pendra com a parametres el llistat de urls definitiu i
    # un numero maxim de pagines a iterar, es a dir per cada provincia dintre de les urls, aprofindirem en max_pages
    # el scraping, es a dir si max_pages es 4, scrapejarem la original de la provincia i les seguents 4 pagines d'ofertes
    # de la mateixa provincia.
    # No he gestionat el fet que una pagina pugui tindré menys pagines que max_pages, de totes maneres no tindria afectació( si perdriem quantitat de gb a gestionar i temps)
    # ja que no escriuria dades al csv al no existir la pagina. Però per un exemple academic crec que la funció compleix la seva missió.
    # Definim la url base
    base_url = "https://www.fotocasa.es"
    # Per cada url en la url parcial de cada provincia proporcionada
    for i in urls:
        parts = i.split('/')
        for part in parts:
            if '-' in part:
                element = part.split('-')[0]
                break
        # N'obtenim la provincia a la que pertany la url basantnos en la seva sintax i agafant el nom de la provincia.
        provincia = element
        # Fixem un comptador que ens assegurara que no anem més enllà de max_pages.
        # A l'inici de cada iteració per a cada província aquest comptador serà 0.
        counter = 0
        # Mentres el comptador sigui més petit o igual que max_pages, scrapejarem ja sigui la url original de la provincia
        # si el comptador es 0, ja sigui la següent url de la província obtinguda de scrapejar la pagina prèvia, sempre
        # que el comptador sigui menor que max pages
        while counter <= max_pages:
            if counter == 0:
                url = base_url + i
            else:
                url = base_url + next_link
            # Temporitzem el proces
            start_time = time.time()
            # Creem un driver amb les opcions de les proxies
            driver = webdriver_example()
            # Accedim a la web
            driver.get(url)
            # Dormim per no saturar servidors
            time.sleep(5)
            # Sempre que no estiguem al final de la pagina fem scroll per tal de carregar el codi javascript a mesura que scrollejem la pagina.
            # Posem un retard en aquest scrolling per tal de no saturar el servidor i sembla més humà.
            # El scrolling es fa ja apareixin pop ups o no, en aquest cas no té afectació.
            # Adaptar quan scrollejem cada vegada als nostres desitjos amb scroll_height.
            scroll_height = 0
            while True:
                driver.execute_script("window.scrollTo(0, arguments[0]);", scroll_height)
                time.sleep(2)
                scroll_height += 1000
                if scroll_height >= driver.execute_script("return document.body.scrollHeight"):
                    break
            # Obtenim tot el codi de la pagina, incloent el que ha carregat el javascript
            page_source = driver.page_source
            # Dormim
            time.sleep(7)
            # Tanquem sessió
            driver.quit()
            # Parsejem el codi
            soup = BeautifulSoup(page_source, 'html.parser')
            # Obtenim el contenidor d'informació per cada oferta de cada pis
            info_divs = soup.find_all('div', class_='re-CardPackPremium-info')
            # Me n'he adonat compte que a la pagina, algunes pagines de algunes provincies tenen la info a 'div', class_='re-CardPackPremium-info',
            # mentre que d'altres la tenen a 'div', class_='re-CardPackAdvance-info'
            # Desconec el motiu. Entenc que per dificultar el scraping.
            # Dintre de la mateixa pagina mai estan en contenidors diferents, es a dir si en una pagina un pis esta a class_='re-CardPackPremium-info'
            # es que tots en aquella pagina estan en aquest tag i el mateix per l'altre
            # Normalment es a class_='re-CardPackPremium-info', si aquesta busqueda original ens troba més de 10 contenidors de pissos(valor que m'ha semblat acceptable)
            # Ens conformem amb aquestes dades i donen per fet que al container 're-CardPackAdvance-info' en aquest cas no hi ha res
            if len(info_divs) > 10:
                pass
            else:
                # Sino es així i el container previ no existeix o no te dades, busquem l'alternatiu.
                # Amb aquest metode practicament obtenim la info de tots els pissos de totes les pagines amb ratios de dades no obtingudes molt petits.
                info_divs = soup.find_all('div', class_='re-CardPackAdvance-info')
            # creem una llista buida que guardara la info de cada pis en tuples.
            flats = []
            # Per cada container individual n'obtindrem la info de cada pis
            # Tant estiguin a la primera classe de container possible com la segona, el parsejat intern del container no canvia.
            for info_div in info_divs:
                # Obtenim títol
                title = info_div.find('span', class_="re-CardTitle re-CardTitle--big").text
                precio_span = info_div.find('span', class_="re-CardPrice")
                # Obtenim preu, en aquest de no trobar l'element el posem com a null
                price = precio_span.text if precio_span else "-"
                reduccio_span = info_div.find('span', class_="re-CardPriceReduction")
                # Obtenim reduccio, en aquest de no trobar l'element el posem com a null
                reduccio = reduccio_span.text if reduccio_span else "-"
                rooms_span = info_div.find('span', class_="re-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--rooms")
                # Obtenim habitacions, en aquest de no trobar l'element el posem com a null
                rooms = rooms_span.text if rooms_span else "-"
                bathrooms_span = info_div.find('span', class_="re-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--bathrooms")
                # Obtenim banys, en aquest de no trobar l'element el posem com a null
                bathrooms = bathrooms_span.text if bathrooms_span else "-"
                meters_span = info_div.find('span', class_="re-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--surface")
                # Obtenim metres, en aquest de no trobar l'element el posem com a null
                meters = meters_span.text if meters_span else "-"
                # Guardem les dades
                flats.append((title, price, reduccio, rooms, bathrooms, meters, provincia))
            # Una vegada ja tenim scrapejades totes les dades de pisos que ens interessen de la pagina, les escrivim en un csv i a la proxima iteració
            # el container de dades flats, es reassignara a buit, així no guardem dades innecesaries a la memòria i a cada iteració només
            # s'escriuran les dades propies d'aquella iteració. Si el csv ja existeix, escriu al final del document(append)
            get_csv(flats,provincia, counter)
            # Obtenim al link a la proxima pagina de la provincia a scrapejar
            li_tags = soup.find_all('li', class_='sui-MoleculePagination-item')
            # En un inici assumim que no existeix
            href = ''
            # Aquests tags acostumem a ser 4, 3 buits i un que compte la url, per tant si el container es buit simplement passem al següent
            # i quan no ho sigui ens quedem amb la url a href.
            for li_tag in li_tags:
                a_tag = li_tag.find('a', class_='sui-AtomButton sui-AtomButton--primary sui-AtomButton--outline sui-AtomButton--center sui-AtomButton--small sui-AtomButton--link sui-AtomButton--empty sui-AtomButton--rounded')
                if a_tag:
                    href = a_tag.get('href')
                else:
                    pass
            print(href)
            # Guardem la url a seguir a la proxima iteracio
            next_link = href
            end_time = time.time()
            # Obtenim temps total
            execution_time = end_time - start_time
            # Enviem avís per pantalla de la pagina numero i la provincia scrapejades
            print(f'Page {counter + 1} of {provincia} scraped')
            # Quan ha tardat el proces
            print(f"Execution time: {execution_time:.4f} seconds")
            # Quants pissos hem obtingut
            print(len(flats))
            # Augmentem el contador
            counter += 1
            # Dormim com a bona pràctica per no saturar servidor
            time.sleep(20)
            # Quan arribem al número màxim de pagines, surtim d'aquesta província i anem a la següent o ja a finalitzar el proces si pertoca
            if counter > max_pages:
                break
    # Enviem missatge d'éxit del procès
    return print('Succesful')


def get_csv(data, provincia, counter):
    # Aquesta funció s'encarrega d'escriure el fitxer csv, en cas de que ja existeixi simplement escriu les dades al final del mateix fitxer
    # Obtenim la data d'avui
    current_date = datetime.now().strftime("%Y_%m_%d")
    # Fixem el nom del fitxer i la ruta, es genera amb la data d'execució. Si ja s'ha generat previament ho comprovarem i escriurem al final
    csv_file = f"C:\\Users\\Usuario\\PycharmProjects\\PRA1\\fotocasa_{current_date}.csv" # Substituir la ruta per la que naltros volguem

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
    return print(f'Csv data written successfully {provincia} {counter}')

# Apliquem les funcions per obtindre links, filtrar-los i obtindre'n la info.
hrefs = get_zone_links()
urls = get_catalonia(hrefs, ['tarragona', 'lleida', 'girona', 'barcelona'])
# En aquest cas, ja que es un exemple academic simplement scrapejem 5 pagines per provincia, 4 + l'original, el que fan 20 pagines totals
# a aproximadament 30 pisos per pagines, obtindriem dades de 150 pisos per provincia, 600 en total.
get_content(urls, 4)
