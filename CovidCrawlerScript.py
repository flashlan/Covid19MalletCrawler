from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import urllib.request
import shutil
import re # for regular expressions, can be removed if no test is used
from tqdm import tqdm # to print progress bar
from urllib.parse import urljoin, urlparse
import requests
import os 
#teste
#html = urlopen("http://mallet.pr.gov.br/Site_mallet/materias/2020/03_marco/18_covid_oficio/18_covid_oficio.asp")
#res = BeautifulSoup(html.read(),"html5lib");    
#print(res.title)

# Functions
def is_valid(url): #Checks whether `url` is a valid URL.
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_images(url): # Returns all image URLs on a single `url`
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)
        # remove URLs like '/hsts-pixel.gif?c=3.2.5'
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)
    return urls

def download(url, pathname): # Downloads a file given an URL and puts it in the folder `pathname`
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))

            
def main(url, path):
    # get all images
    imgs = get_all_images(url)
    for img in imgs:
        # for each image, download it
        download(img, path)
        
main("http://mallet.pr.gov.br/Site_mallet/materias/2020/03_marco/18_covid_oficio/18_covid_oficio.asp", "covid19_mallet_scrappedImages")

#OCR
from pytesseract import Output # importing modules
import cv2
import pytesseract

# for windows only
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

import cv2
from pathlib import Path
import glob
import pandas as pd
import numbers

# empty dataframe
df1 = pd.DataFrame(columns=['dDescartados', 'dNotificados','dMonitorados','dSuspeitos','dPositivos', 'dRecuperados','dObitos','dAtuais','dData'])
df3 = df1
bNotifica = 0
bDesca = 0
bRecupera = 0
bObitos = 0

# load images in a loop
images = [cv2.imread(file) for file in glob.glob("covid19_mallet_scrappedImages/*.jpg")]
# print(images)
for pic in images:
    gray_image = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    custom_config = r'-c preserve_interword_spaces=1 makebox --oem 1 --psm 6' #configuring parameters for tesseract
    # now feeding image to tesseract
    details = pytesseract.image_to_data(threshold_img, output_type='data.frame', config=custom_config, lang='por')
    dt = details.text # select columm
    #create empty dataframe
    col_names = ['Notificados','Monitorados','Suspeitos','Positivos','Recuperados','Descartados','Obitos','Atuais','Data']
    coviddf = pd.DataFrame(columns = col_names)
    # select itens with regex
    des = dt[details["text"].str.contains("1|2|3|4|5|6|7|8|9|0|:",  na=False)]
    #apague
    # create a new dict(dataframe) to put extracted data 
    covidict = {"dDescartados": [], "dNotificados":[],"dMonitorados":[],"dSuspeitos":[],"dPositivos": [], "dRecuperados":[],"dObitos":[],"dAtuais":[],"dData":[] }
    #transform to dict
    enum=enumerate(des)
    enum
    d=dict((i,j) for i,j in enum)
    keyList=sorted(d.keys())
    for i,v in enumerate(keyList):# print values on the loop
        print(d[keyList[i]]) # get the value from the kay and print # for debug OCR
        if d[keyList[i]].find("Desca") == 0:
            if len(d[keyList[i]]) > 12: 
                bDesca = d[keyList[i]]
                bDesca = bDesca.replace("Descartados:", "")
                covidict["dDescartados"].append(int(bDesca))        
                #df1 = df1.append({'dDescartados': bDesca}, ignore_index=True)
                print(1)
            else:
                bDesca = d[keyList[i+1]]
                covidict["dDescartados"].append(bDesca)
                #df1 = df1.append({'dDescartados': bDesca}, ignore_index=True)
                print(2)
    
        if d[keyList[i]].find("Recupera") == 0:
            if len(d[keyList[i]]) > 12: 
                bRecupera = d[keyList[i]]
                bRecupera = bRecupera.replace("Recuperados:", "")
                covidict["dRecuperados"].append(int(bRecupera))
                #df1 = df1.append({'dRecuperados': bRecupera}, ignore_index=True)
            else:
                bRecupera = d[keyList[i+1]]
                covidict["dRecuperados"].append(int(bRecupera))
                #df1 = df1.append({'dRecuperados': bRecupera}, ignore_index=True)

        if d[keyList[i]].find("Notifica") == 0:
            if len(d[keyList[i]]) > 12: 
                bNotifica = d[keyList[i]]
                bNotifica = bNotifica.replace("Notificados:", "")
                covidict["dNotificados"].append(int(bNotifica))
                #df1 = df1.append({'dNotificados': bNotifica}, ignore_index=True)
            else:
                bNotifica = d[keyList[i+1]]
                if bNotifica.find("55O") == 0:
                    bNotifica = bNotifica.replace("55O", "550")
                    covidict["dNotificados"].append(int(bNotifica))
                if bNotifica.find("550, 550") == 0:
                    bNotifica = bNotifica.replace("550, 550", "550")
                    covidict["dNotificados"].append(int(bNotifica))
                    #df1 = df1.append({'dNotificados': bNotifica}, ignore_index=True)
                if bNotifica.find("5b6") == 0:
                    bNotifica = bNotifica.replace("b", "6")
                    covidict["dNotificados"].append(int(bNotifica))
                    #df1 = df1.append({'dNotificados': bNotifica}, ignore_index=True)
                else:
                    covidict["dNotificados"].append(int(bNotifica))
                    #df1 = df1.append({'dNotificados': bNotifica}, ignore_index=True)
 
        if d[keyList[i]].find("Monitora") == 0:
            if len(d[keyList[i]]) > 12: 
                bMonitora = d[keyList[i]]
                bMonitora = bMonitora.replace("Monitorados:", "")
                covidict["dMonitorados"].append(int(bMonitora))
            else:
                bMonitora = d[keyList[i+1]]
                if bMonitora.find("Suspeitos") == 0:
                    bMonitora = bMonitora.replace("Suspeitos:", "0")
                    covidict["dMonitorados"].append(int(bMonitora))
                else:
                    covidict["dMonitorados"].append(int(bMonitora))####substitui suspeitos
    
        if d[keyList[i]].find("Suspei") == 0:
            if len(d[keyList[i]]) > 10: 
                bSuspei = d[keyList[i]]
                bSuspei = bSuspei.replace("Suspeitos:", "")
                covidict["dSuspeitos"].append(int(bSuspei))
            else:
                bSuspei = d[keyList[i+1]]
                if bSuspei.find("Positivos") == 0:
                    bSuspei = bSuspei.replace("Positivos:", "0")
                    covidict["dSuspeitos"].append(int(bSuspei))
                else:
                    covidict["dSuspeitos"].append(int(bSuspei))
    
        if d[keyList[i]].find("Posit") == 0:
            if len(d[keyList[i]]) > 10: 
                bPosit = d[keyList[i]]
                bPosit = bPosit.replace("Positivos:", "")
                covidict["dPositivos"].append(int(bPosit))
            else:
                bPosit = d[keyList[i+1]]
                covidict["dPositivos"].append(int(bPosit))
 
        if d[keyList[i]].find("Óbit") == 0:
            if len(d[keyList[i]]) > 7: 
                bObitos = d[keyList[i]]
                bObitos = bObitos.replace("Óbitos:", "")
                covidict["dObitos"].append(bObitos)
            else:
                bObitos = d[keyList[i+1]]
                covidict["dObitos"].append(int(bObitos))
    
        # find  xx/xx/xx
        if len(d[keyList[i]]) == 8:
            bData = d[keyList[i]]
            covidict["dData"].append(bData)
        # Actual number of infecteds: function
        dAtuais = int(0)
        dAtuais = int(bNotifica) - int(bDesca) - int(bRecupera) - int(bObitos)
        if dAtuais > 0:
            covidict["dAtuais"] = []
            covidict["dAtuais"].append(dAtuais)
        
    df2 = pd.DataFrame([covidict])
    print(df2)
    
    df3 = df3.append(df2,ignore_index=True)
    #print(df3)


import re
import numpy as np
# Remove brackets and ´ from cells
df3['dMonitorados'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dMonitorados']])
df3['dNotificados'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dNotificados']])
df3['dDescartados'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dDescartados']])
df3['dSuspeitos'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dSuspeitos']])
df3['dPositivos'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dPositivos']])
df3['dRecuperados'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dRecuperados']])
df3['dObitos'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dObitos']])
df3['dAtuais'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dAtuais']])
df3['dData'] = pd.DataFrame([str(line).strip('[').strip(']').replace("'","") for line in df3['dData']])
df3['dNotificados'] = pd.DataFrame([str(line).strip('[').strip(']').replace("550, 550","550") for line in df3['dNotificados']])

# Full empy cells with 'None'
for i in df3.columns:
    df3[i][df3[i].apply(lambda i: True if re.search('^\s*$', str(i)) else False)]=None
# Delete cells wih None value
df3 = df3.replace(to_replace='None', value=np.nan).dropna()
df3 = df3.replace(to_replace='MILITAR', value=np.nan).dropna()

print(df3) # ver inteiro
df3.to_csv(r'CovidMalletDataFrame.csv', index = False) # exporta para csv
print("Terminado! arquivo CSV salvo cono: 'CovidMalletDataFrame.csv'")
#df3.head()
#df3.info()




