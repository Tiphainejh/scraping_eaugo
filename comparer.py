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
start_col = 2
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
                price = soup.find(class_="prices__price prices__main-price__price")
                while price == None: #sometimes selenium returns None
                    r = requests.get(url)
                    soup = BeautifulSoup(r.text, 'lxml')
                    price = soup.find(class_="prices__price prices__main-price__price")
                price=price.find(class_="price-integer")
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
    price = float(price)

    return price

def get_prices(product):

    with open((product['json']), 'r') as f:
        products = json.load(f)

    comparison = list()
    
    for i, a in enumerate(products):
        ligne = [a, products[a]['id']]
        for s in range(product['nb_stores']):
            ligne.insert(start_col+s, 0)
        
        ligne.insert(product['nb_stores'], 0)
        ligne.insert(product['nb_stores']+1, 0)

        comparison.append(list(ligne))
        for n, site in enumerate(products[a]['urls'].keys()):
            url = products[a]['urls'][site]
            if url != "" : 
                price = get_price(url, site)
                if price != None :
                    price = get_uniform_price(price, site)
                else :
                    price = "Plus en stock"
                comparison[i][start_col+n] = price
        
        print(product['type'] + " : "+str(i+1) +" sur " + str(len(products)) + " effectué(s).")
    return comparison


#compare les prix 
def compare_prices(product):
    comparison = get_prices(product)
    stores = product['nb_stores']
    products = len(comparison)
    eaugo_price_id = len(comparison[0]) - 3

    for i in range(products) :
        prices = [comparison[i][p] for p in range(start_col,start_col+stores)]
        min_price = min([p for p in prices if p !=0.0 and type(p)!= str])
        min_price_id = prices.index(min_price) + start_col
        eaugo_price = prices[-1]

        if eaugo_price == min_price :
            prices2 = [prices[i] for i in range(len(prices)-1) if prices[i] !=0.0 and type(prices[i])!= str]
            if prices2 != []:
                min_price2 = min(prices2)
            else :
                min_price2 = min_price
            if min_price_id == eaugo_price_id :
                comparison[i][-1] = (1 - eaugo_price / min_price2) * 100
                comparison[i][-2] = eaugo_price_id
            else:
                comparison[i][-1] = 0
                comparison[i][-2] = eaugo_price_id
        else :
            comparison[i][-1] = (1 - min_price / eaugo_price) * 100
            comparison[i][-2] = min_price_id

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
    ws.cell(row=1, column=1).value = "Produit"
    ws.cell(row=1, column=2).value = "Référence"

    if product['type'] == "Chauffe eaux":
        ws.cell(row=1, column=3).value = "Sobrico"
        ws.cell(row=1, column=4).value = "Factorydirect"
        ws.cell(row=1, column=5).value = "Domotelec"
        ws.cell(row=1, column=6).value = "Domomat"
        ws.cell(row=1, column=7).value = "Eau-go"
        ws.cell(row=1, column=8).value = "Ecart"
    elif product['type'] == "Adoucisseurs":
        ws.cell(row=1, column=3).value = "Manomano"
        ws.cell(row=1, column=4).value = "Sanitaire-pas-cher"
        ws.cell(row=1, column=5).value = "Domomat"
        ws.cell(row=1, column=6).value = "Eau-go"
        ws.cell(row=1, column=7).value = "Ecart"

    row = 2
    col = 1
    stores = product['nb_stores']
    eaugo_price_id = len(comparison[0]) - 3

    for i in range(len(comparison)):
        ws.cell(row=row, column=col).value = comparison[i][0]
        ws.cell(row=row, column=col + 1).value = comparison[i][1]
        for s in range(start_col, start_col+stores):

            ws.cell(row=row, column=col + s).value = comparison[i][s]
            if s == comparison[i][-2]:
                if s != eaugo_price_id:
                    ws.cell(row=row, column=col + s).font = Font(bold=True, color = "FF0000")
                else:
                    ws.cell(row=row, column=col + s).font = Font(bold=True, color = "1B7B0F")
        ws.cell(row=row, column= col + start_col+stores).value = str(int(comparison[i][-1])) + "%"
        row += 1

    wb.save(comparison_file)

category = {"adoucisseur": {"json": "adoucisseurs.json", "excel": "comparaison_adoucisseurs.xlsx", "nb_stores": 4, "type": "Adoucisseurs"},
"chauffe_eau": {"json": "chauffe_eaux.json", "excel": "comparaison_chauffe_eaux.xlsx", "nb_stores": 5, "type": "Chauffe eaux"}}

for c in category :
    create_file(category[c])
