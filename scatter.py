import time

import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select

global os_is

def GetStockNO(l):
    date_add = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    response = requests.get(date_add)

    #print(response.text)
    df = pd.read_html(response.text)
    stock_no = []
    sel = l
    if l == None or l<4:
        sel = 4
    for a in df[0][0]:
        try:
            tmp = int(a[:4])
            tmp = a.split('\u3000')[0]
            if len(tmp) <= sel:
                stock_no.append(tmp)
        except:
            pass
    return stock_no

def ScatterCsv():
    import pandas as pd
    import csv
    csv_add = "https://smart.tdcc.com.tw/opendata/getOD.ashx?id=1-5"

    data = pd.read_csv(csv_add)

def ScatterWebGetDate():
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("https://www.tdcc.com.tw/smWeb/QryStock.jsp")

    times =10
    while times>0:
        try:
            select = driver.find_element_by_name("scaDates")
            select.click()
            break
        except:
            continue
        time.sleep(1)
        times-=1
    tables = driver.find_elements_by_class_name("mt")

    date = tables[0].text.split("\n")
    out_date = []
    for a in date:
        try:
            tmp = int(a)
            out_date.append(a)
        except:
            continue
    driver.close()
    return out_date

def ScatterTable(no,date):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("https://www.tdcc.com.tw/smWeb/QryStock.jsp")
    time.sleep(1)

    out_str = ""
    try:
        for d_i in date:
            # Get stock number element
            element = driver.find_elements_by_name("StockNo")
            for a in element:
                if a.get_attribute("type") == "text":
                    a.send_keys(no)
                    break
            # select date
            select = driver.find_element_by_name("scaDates")
            sel_date = Select(select)
            sel_date.select_by_visible_text(d_i)
            sel_date.select_by_value(d_i)
            #time.sleep(0.1)
            elements = driver.find_elements_by_name("sub")
            for b in elements:
                if (b.get_attribute("type") == "button" and b.get_property("value") == "查詢"):
                    b.click()

            tables = driver.find_elements_by_class_name("mt")

            if len(tables)>1:
                #print(tables[1].text)

                    table = tables[1].text.split("\n")
                    out_str += d_i
                    for i in range(1,len(table)-1):
                        val = table[i].split(" ")
                        out_str += "," + val[2].replace(",","") + " " + val[4]
                    out_str +="\n"
    except:
        pass
    driver.close()
    target_str = "ScaterData/" + str(no) + ".csv"
    if os_is == "windows":
        target_str = "ScaterData\\" + str(no) + ".csv"
    #save as csv
    if(out_str!=""):
        old_content =None
        try:
            fr = open(target_str, 'r')
            old_content = fr.readlines()
            fr.close()
        except:
            pass
        if old_content != None:
            for a in old_content:
                out_str += a

        f = open(target_str,'w+')
        f.write(out_str)
        f.close()

def ScatterDataBase():
    import os
    import shutil
    import sys
    global os_is
    if sys.platform == "linux" or sys.platform == "linux2":
        os_is = "linux"
    elif sys.platform == "win32":
        os_is = "windows"

    if os.path.exists("ScaterData") == False:
        os.mkdir("ScaterData")
    stock_no = GetStockNO(None)
    date = ScatterWebGetDate()
    for a in stock_no:
        target_str = "ScaterData/" + str(a) + ".csv"
        if os_is == "windows":
            target_str = "ScaterData\\" + str(a) + ".csv"
        # check file exist
        if os.path.exists(target_str):
            f = open(target_str, 'r')
            lens_1 = f.readline().split(",")
            last_date = lens_1[0]
            f.close()
            # head not complete
            if len(lens_1) < 2:
                update_date = date
                os.remove(target_str)
            else:
                update_date = []
                for b in date:
                    if b != last_date:
                        update_date.append(b)
                    else:
                        break
        else:
            update_date = date
        if len(update_date) > 0:
            ScatterTable(a, update_date)
            # if os.path.exists(str(a)+".csv"):
            #     shutil.move(str(a)+".csv", "ScaterData/"+ str(a)+".csv")

if __name__ == '__main__':
    ScatterDataBase()