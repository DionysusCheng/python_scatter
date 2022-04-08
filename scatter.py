import time
import os
import numpy
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
cwd = "/home/dionysus/python_cron/chromedriver"
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
    global os_is
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.headless = True
    if os_is == "windows":
        driver = webdriver.Chrome(chrome_options=options)
    else:
        driver = webdriver.Chrome(cwd,chrome_options=options)
    driver.get("https://www.tdcc.com.tw/smWeb/QryStock.jsp")

    times =10
    while times>0:
        try:
            select = driver.find_element_by_name("scaDates")
            select.click()
            break
        except:
            continue
        time.sleep(0.5)
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

def GetStockValue(no, date):
    import pandas_datareader as data
    stock_name = str(no) + ".TW"
    date = str(date)[:4] + "-" + str(date)[4:6] + "-" + str(date)[6:9]
    value = data.DataReader(stock_name, 'yahoo', date, date)

    str_split = str(value["Close"][0]).split('.')

    return str_split[0] +"."+ str_split[1][:3]

def ScatterTable(no,date):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    global os_is
    options = Options()
    options.headless = True
    if os_is == "windows":
        driver = webdriver.Chrome(chrome_options=options)
    else:
        driver = webdriver.Chrome(cwd,chrome_options=options)
    driver.get("https://www.tdcc.com.tw/smWeb/QryStock.jsp")
    #time.sleep(1)

    out_str = ""
    for d_i in date:
        try:
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

            elements = driver.find_elements_by_name("sub")
            for b in elements:
                if (b.get_attribute("type") == "button" and b.get_property("value") == "查詢"):
                    b.click()
            tables = driver.find_elements_by_class_name("mt")

            if len(tables)>1:
                #print(tables[1].text)
                table = tables[1].text.split("\n")
                # date, stock value
                try:
                    s_val =  GetStockValue(no,d_i)
                except:
                    s_val = ""
                out_str += d_i + "," + s_val
                for i in range(1,len(table)-1):
                    val = table[i].split(" ")
                    # cat person, percentage
                    out_str += "," + val[2].replace(",","") + " " + val[4]
                out_str +="\n"
        except:
            continue
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

def readScatterFile(no):
    import csv
    import pandas as pd
    try:
        file_path = "ScaterData/{0}.csv".format(no)
        f = open(file_path,"r")
    except:
        return None,None,None
    lines = csv.reader(f)
    delete_file = False
    value_table = []
    person_table = []
    percent_table = []
    i = 0
    #load file
    for line in lines:
        datas = str(line).split("\.")
        j = -1
        try:
            for a in datas:
                tmp_person = []
                tmp_percent = []
                for b in a.split(","):
                    if j >=1:
                        try:
                            tmp_person.append(int(b.split(" ")[1].replace("'","")))
                            tmp_percent.append(float(b.split(" ")[2].replace("'","").replace("]","")))
                        except:
                            continue
                    elif j== 0:
                        val = b.replace("'","").replace(" ","")
                        try:
                            float(val)
                            value_table.append(float(val))
                        except:
                            value_table.append("")
                    j += 1
                person_table.append(tmp_person)
                percent_table.append(tmp_percent)
        except:
            continue
        i += 1
    #fill the None data
    no_sction = False
    try:
        for i in range(len(value_table)):
            if value_table[i] != "" : continue
            if i == 0:
                j = i
                while (value_table[j] == ""):
                    j += 1
                value_table[i] = value_table[j]
                continue
            pre_val = value_table[i-1]
            j=i
            while(value_table[j]=="" and no_sction == False):
                j+=1
                if j>=len(value_table):
                    no_sction = True
                    break
            if no_sction == False:
                off=(float(value_table[j])-float(pre_val))/float(j-i+1)
                j=i
                while(value_table[j]==""):
                    tmp = str(float(value_table[j-1]) + off)
                    dot = tmp.find('.')
                    value_table[j] = tmp[:dot+4]
                    j+=1
            else:
                value_table[i] = pre_val
    except:
        delete_file = True
        value_table = None
    for i in range(1,len(person_table)):
        tmp_p0=person_table[i-1]
        tmp_p1 = None
        tmp_pc0 = percent_table[i-1]
        tmp_pc1 = None
        j = i
        if len(tmp_p0) == 0 or len(tmp_pc0) == 0:
            delete_file = True
            continue
        while j < len(person_table):
            if len(person_table[j])>0:
                tmp_p1 = person_table[j]
                tmp_pc1 = percent_table[j]
                break
            j += 1
        if tmp_pc1 != None:
            if len(tmp_p0) != len(tmp_p1):
                limit_no = len(tmp_p0)
                if len(tmp_p1) < limit_no:
                    limit_no = len(tmp_p1)
                if len(tmp_p0) != limit_no:
                    tmp_list=tmp_p0
                    tmp_p0 =[]
                    for i in range(limit_no):tmp_p0.append(tmp_list[i])
                if len(tmp_p1) != limit_no:
                    tmp_list=tmp_p1
                    tmp_p1 =[]
                    for i in range(limit_no): tmp_p1.append(tmp_list[i])
            div = j - i +1
            off_p = (numpy.subtract(tmp_p1,tmp_p0) / div).astype(int)
            off_pc = numpy.subtract(tmp_pc1,tmp_pc0) / div
            k=i
            while k < j:
                person_table[k] = numpy.add( person_table[k - 1] , off_p).tolist()
                percent_table[k] = numpy.add(percent_table[k - 1] ,off_pc).tolist()
                k += 1

    if delete_file:
        f.close()
        os.remove(file_path)
        return None,None,None

    return value_table, person_table, percent_table

def relationAnalyze(rp,rpc,rv):
    stocks = GetStockNO(None)
    sel = []
    for a in stocks:
        pi = []
        ana_i = []
        v,p,pc = readScatterFile(a)
        if v==None or p==None or pc==None: continue
        ##get reference index
        if rv != None and v[0]>rv: continue
        if rp != None:
            for i in range(len(p[0])):
                if p[0][i] < rp:
                    pi.append(i)
        if rpc !=None:
            if len(pi)>0:
                t_pc = 0.00
                for ai in pi:
                    t_pc += pc[0][ai]
                if t_pc < rpc: continue
                ana_i = pi
            else:
                t_pc = 0
                for i in range(len(pc[0])-1, 0, -1):
                    ana_i.append(i)
                    t_pc += pc[0][i]
                    if t_pc > rpc: break

        ##get all person/percentage using reference index
        if len(ana_i)>0:
            p_hist = []
            pc_hist = []
            for it in p:
                sum = 0
                try:
                    for i in ana_i:
                        sum += it[i]
                except:
                    continue
                p_hist.append(sum)
            for it in pc:
                sum = 0.00
                try:
                    for i in ana_i:
                        sum += it[i]
                except:
                    continue
                pc_hist.append(sum)
        if len(v)<10: continue
        #if positive/negative relation over 80%
        del_val = []
        del_p_ref = []
        del_pc_ref = []
        for i in range(len(v) - 1): del_val.append(float(v[i])-float(v[i-1]))
        for i in range(len(p_hist) - 1): del_p_ref.append(p_hist[i] - p_hist[i - 1])
        for i in range(len(pc_hist) - 1): del_pc_ref.append(pc_hist[i] - pc_hist[i - 1])

        weight = 0
        percent_change = 0
        #data lose
        if len(del_val) != len(del_pc_ref): continue
        for pi in del_pc_ref:
            if pi != 0: percent_change += 1
        for i in range(len(del_val)):
            if(del_val[i]*del_pc_ref[i])>0: weight +=1;
            if(del_val[i]*del_pc_ref[i])<0: weight -=1;

        ratio = float(weight)/float(percent_change)
        if ratio>=0.5:
            sel.append(a)
        elif ratio <= -0.5:
            sel.append("n" + a)
    return sel
if __name__ == '__main__':
    ScatterDataBase()
    rsl=relationAnalyze(500,60,None)
    print(rsl)