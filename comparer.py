import time
import os
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import urllib3
from openpyxl.utils.cell import get_column_letter
from openpyxl import load_workbook
from openpyxl.styles import Font, Color
from openpyxl.workbook import Workbook
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('log-level=3')
driver = webdriver.Chrome("chromedriver.exe", options=options)

products = []
productsPrices = []
comparison = []
sellers = ["Sobrico.com", "Factorydirect", "Domotelec", "ManoMano.fr", "Domomat.com", "Sanitaire-pas-cher", "Eau-Go"]
header = ["Produit","Référence"]
header.extend(sellers)
header.append("Ecart")

eaugo_price_id = 0
nStores = len(sellers)
nProducts = 30

def compare_prices(product, eaugo_price_id):
    min_price = min([p for p in product if isinstance(p, float)])
    min_price_id = product.index(min_price)
    eaugo_price = product[eaugo_price_id]
    print(product)
    if eaugo_price == min_price :
        prices = product[:-3]
        sec_min_price = min([p for p in prices if isinstance(p, float)]) if prices != [] else min_price

        if min_price_id == eaugo_price_id :
            product[-1] = (1 - eaugo_price / sec_min_price) * 100
            product[-2] = eaugo_price_id
        else:
            product[-1] = 0
            product[-2] = min_price_id
    else :
        print(min_price)
        print(eaugo_price)
        product[-1] = (1 - min_price / eaugo_price) * 100
        product[-2] = min_price_id

    return product


def create_file(productPrices):
    global nStores 

    wb = load_workbook(filename = 'suivi.xlsx')
    sheet = wb.active
    rows = sheet.rows

    for r in range(2, sheet.max_row):
        products.append([sheet.cell(row=r, column=1).value])
        products[r-2].append(sheet.cell(row=r, column=3).value)
        products[r-2].append(sheet.cell(row=r, column=10).value)

    priceRows = []

    for i, product in enumerate(products[10:11]) :
        search_page = "https://www.google.fr/search?tbm=shop&q="+str(product[2])+"&restrictBy=gtin="+str(product[2])
        buttonXPath = '//*[@id="yDmH0d"]/c-wiz/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button'
        tableClass = "sh-osd__offer-row"
        priceID = "QXiyfd"
        searchID = "search"
        driver.get(search_page)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        try :
            button = driver.find_element_by_xpath(buttonXPath)
            button.click()
        except:
            pass

        page = wait(driver, 60).until(EC.visibility_of_element_located((By.ID, searchID)))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
 
        url = soup.find_all(lambda tag:tag.name=="a" and "Comparer" in tag.text)[0]["href"].split("?")[0]
        if "/offers" in url: 
            url.replace("/offers", "")
        comp_page = "https://www.google.com" + url + "/online"
        print(product[2])
        print(comp_page)
        driver.get(comp_page)
        table = wait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,tableClass)))

        table = driver.find_elements_by_class_name(tableClass)


        found = False
        priceRows.append([product[0],product[1]])
        for seller in sellers :
            for row in table :
                if seller in row.text:
                    price = row.find_element_by_class_name(priceID)
                    price = float(price.text.replace("\u20ac","").replace("\xa0","").replace("\u202f","").replace(",","."))
                    priceRows[i].append(price)
                    found = True
                    break
            if found == False:
                priceRows[i].append(" ")
            found = False

        
        priceRows[i].append(" ")
        priceRows[i].append(" ")
        # append sellers
        nSellers = len(sellers)

        time.sleep((30-5)*np.random.random()+5)
        print(str(i+1)+"/"+str(nProducts))

    date = datetime.now().strftime("%Y-%m-%d")

    comparison_file = "comparaison.xlsx"
    if os.path.exists(comparison_file) :
        wb = load_workbook(comparison_file)
    else :
        wb = Workbook()

    if date in wb.sheetnames :
        date = datetime.now().strftime("%Y-%m-%d %H %M %S")

    wb.create_sheet(index = 0, title = date)
    ws = wb.worksheets[0]
    eaugo_price_id = header.index("Eau-Go")
    for j in range(1, len(priceRows)+1) :
        comparison = compare_prices(priceRows[j-1], eaugo_price_id)
        print(comparison)
        ws.cell(row=j, column=1).value = comparison[0]
        ws.cell(row=j, column=2).value = comparison[1]
        for s in range(3, 3+nStores):
            ws.cell(row=j, column=s).value = comparison[s-1]
            if s == (comparison[-2]+1):
                if comparison[-2] != (eaugo_price_id):
                    ws.cell(row=j, column=s).font = Font(bold=True, color = "FF0000")
                else:
                    ws.cell(row=j, column=s).font = Font(bold=True, color = "F1C40F")
        ws.cell(row=j, column=3+nStores).value = str(int(comparison[-1])) + "%"

    ws.insert_rows(1)
    for i, h in enumerate(header):
        ws.cell(row=1, column=i+1).value = h
    for col in ws.columns:
        ws.column_dimensions[get_column_letter(col[0].column)].width = 10
    wb.save(comparison_file)
    return "Done"


print(create_file(productsPrices))

#?prds=scoring:p
#?prds=epd