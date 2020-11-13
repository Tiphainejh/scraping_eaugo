import time
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from datetime import datetime
import requests
import os
import urllib3
from openpyxl import load_workbook
from openpyxl.styles import Font, Color
from openpyxl.workbook import Workbook
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('log-level=3')
browser = webdriver.Chrome("chromedriver.exe", options=options)
browser.implicitly_wait(10)

# récupère le prix d'un produit spécifique
def get_price(url, site):
    try :
        if site =="sanitaire-pas-cher":
            r = requests.get(url,verify=False, headers={"Host": "www.sanitaire-pas-cher.fr"})
            soup = BeautifulSoup(r.text, 'lxml')
            div = soup.find(id="main")
            price = div.find(class_="product-price")
        else :
            browser.get(url)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            if site =="sobrico":
                price = soup.find(class_="product__price-actual")
                if price != None :
                    price = price['content']
            elif site == "manomano":
                price = soup.find(class_="prices__price prices__main-price__price").find(class_="price-integer")
            elif site == "domotelec" or site == "factorydirect":
                price = soup.find(class_="price")
            elif site == "eau-go" or site == "domomat":
                price = soup.find(class_="our_price_display")
        return price

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        sys.exit(1)

# Uniformise les prix des produits
def get_uniform_price(price, site):
    if type(price) is not str:
        price = price.text

    if site == "sobrico" :
        pass
    elif site == "domotelec":
        price = price.replace("\u20ac","")
        price = price.replace("\xa0","")
        price = price.replace(",",".")
    elif site == "factorydirect":
        price = price.replace("\u20ac","")
    elif site == "sanitaire-pas-cher" :
        price = price.replace(",",".")
        price = price.replace("\xa0","")
        price = price.replace("\u20ac","")
    elif site == "manomano":
        price = price.replace(" ","")
    elif site == "eau-go" or site == "domomat": 
        price = price.replace("TTC", "")
        price = price.replace(" ", "")
        price = price.replace(",",".")
        price = price.replace("\u20ac","")

    return price

def get_prices(product):

    with open((product['json']), 'r') as f:
        products = json.load(f)

    comparison = list()
    for i, a in enumerate(products):
        for site in products[a]['urls'].keys():
            url = products[a]['urls'][site]
            if url != "" : 
                price = get_price(url, site)
                if price != None :
                    price = get_uniform_price(price, site)
                    comparison.append([a, products[a]['id'], site, float(price), 0])
                else :
                    comparison.append([a, products[a]['id'], site, float(0), 0])
            else :
                comparison.append([a, products[a]['id'], site, float(0), 0])
        
        print(product['type'] + " : "+str(i+1) +" sur " + str(len(products)) + " effectué(s).")
    return comparison


#compare les prix 
def compare_prices(product):
    comparison = get_prices(product)
    stores = product['nb_stores']
    products = int(len(comparison)/stores)
    for i in range(products) :
        index = i*stores
        prices = [comparison[i][3] for i in range(index, index+stores)]
        prixMin = min([p for p in prices if p !=0.0])
        idPrixMin = prices.index(prixMin)
        if prices[-1] == prixMin :
            comparison[index + stores - 1][4] = 1
        else :
            comparison[index + idPrixMin][4] = 1
    return comparison
    

#crée le fichier excel
def create_file(product,):
    comparison = compare_prices(product)
    date_time = datetime.now()
    date = date_time.strftime("%Y-%m-%d")

    comparison_file = product['excel']
    if os.path.exists(comparison_file) :
        wb = load_workbook(comparison_file)
    else :
        wb = Workbook()

    if date in wb.sheetnames :
        date = date_time.strftime("%Y-%m-%d %H %M %S")

    wb.create_sheet(index = 0, title = date)
    ws = wb.worksheets[0]

    row = 1
    col = 1

    for nom, identifiant, site, price, cheapest in (comparison):
        ws.cell(row=row, column=col).value = nom
        ws.cell(row=row, column=col + 1).value = identifiant
        ws.cell(row=row, column=col + 2).value = site
        ws.cell(row=row, column=col + 3).value = price

        if cheapest == 1 and site != "eau-go":
            ws.cell(row=row, column=col + 3).font = Font(bold=True, color = "FF0000")
        elif cheapest == 1 and site == "eau-go":
            ws.cell(row=row, column=col + 3).font = Font(bold=True, color = "1B7B0F")
        
        if site == "eau-go" :
            row +=1
        row += 1

    wb.save(comparison_file)

category = {"adoucisseur": {"json": "adoucisseurs.json", "excel": "comparaison_adoucisseurs.xlsx", "nb_stores": 4, "type": "Adoucisseurs"},
"chauffe_eau": {"json": "chauffe_eaux.json", "excel": "comparaison_chauffe_eaux.xlsx", "nb_stores": 5, "type": "Chauffe eaux"}}


for c in category :
    create_file(category[c])