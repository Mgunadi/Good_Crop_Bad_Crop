
import requests
from bs4 import BeautifulSoup
from ftplib import FTP
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
import os
import re
import json

# This is the example url for rainfall, max temp, min temp.
# http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=122&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num=033255
# http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num=033268
# http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num=033268
BASE_URL = 'http://www.bom.gov.au'

# Don't remove this header it's to bypass!!
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
    "Dnt": "1", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
}
AREA_CODE = '033'

def get_url(temp: int, number: str):
    code = 0 
    if temp == 0:
        code = 122 # Maximum temp
    elif temp == 1:
        code = 123 # Minimum temp
    else:
        code = 136 # Rainfall
    return f'{BASE_URL}/jsp/ncc/cdio/weatherData/av?p_nccObsCode={code}&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num=033{number}'


def get_file(ID: str):
    url = get_url(2, ID)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

    latitude = soup.find("div", {"id": "latitude"})
    longitude = soup.find("div", {"id": "longitude"})
    ID = soup.find("div", {"id": "id"})
    if latitude != None and longitude != None:
        pattern = "^Lat: +(\d+.\d+).*$"
        match = re.match(pattern,latitude.text)
        latitude = match.group(1)
        pattern = "^Lon: +(\d+.\d+).*$"
        match = re.match(pattern,longitude.text)
        longitude = match.group(1)

        pattern = "^Number: +(\d+).*$"
        match = re.match(pattern,ID.text)
        ID = '0'+match.group(1)
        # print(latitude)
        # print(longitude)
        # print(ID)
        
        data = {}
        data['statiod_id'] = ID
        data['latitude'] = latitude
        data['longitude'] = longitude

        # Download url is in the 2nd <li>
        # <ul class="downloads">
        #   <li>
        #   <!--Data:--> 
        #       <a href="/tmp/cdio/IDCJAC0011_033327_2021.zip" title="Data file for selected year of daily minimum temperature">1 year of data</a>
        #   </li>
        #   <li>
        #       <a href="/jsp/ncc/cdio/weatherData/av?p_display_type=dailyZippedDataFile&amp;p_stn_num=033327&amp;p_c=-222227429&amp;p_nccObsCode=123&amp;p_startYear=2021" title="Data file for daily minimum temperature data for all years">All years of data</a></li>
        #   <li>
        #       <a href="/tmp/cdio/IDCJAC0011_033327_2021.pdf"><abbr title="Portable Document Format file of selected year">PDF</abbr></a><
        #   /li>
        # </ul>

        # Download Rainfall File

        # Filter to get url for donwload
        ul = soup.find("ul", class_= "downloads")
        if ul != None:
            a = ul.select('ul > li')[1].select('li > a')[0]
            download_url = a['href']
            # print(download_url)
            download_url = BASE_URL+download_url

            # Download the file
            req = requests.get(download_url, headers=headers)
            zip_file = ZipFile(BytesIO(req.content))
            files = zip_file.namelist()
            zip_file.extractall()

            # READ THE FILE & FIlTER
            with open(files[0], 'r') as csvfile:
                df = pd.read_csv(csvfile)
                filter_data = df[df['Year'] >= 2016] 

            

            # REMOVE THE FILE
            for file in files:
                os.remove(file)


            # Check whether the data has year 0ver 2016
            if len(filter_data.index) > 0:
                # This chunk code for Download Max Temp FILE
                
                url = get_url(0, ID)

                r = requests.get(url, headers=headers)
                soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

                latitude = soup.find("div", {"id": "latitude"})
                if latitude != None:
                # Filter to get url for donwload
                    ul = soup.find("ul", class_= "downloads")
                    if ul != None:
                        a = ul.select('ul > li')[1].select('li > a')[0]
                        download_url = a['href']
                        # print(download_url)
                        download_url = BASE_URL+download_url

                        # Download the file
                        req = requests.get(download_url, headers=headers)
                        zip_file = ZipFile(BytesIO(req.content))
                        files = zip_file.namelist()
                        zip_file.extractall()

                        # READ THE FILE & FIlTER
                        with open(files[0], 'r') as csvfile:
                            df2 = pd.read_csv(csvfile)
                            filter_data2 = df2[df2['Year'] >= 2016] 
                            
                        if len(filter_data2.index) > 0:
                            # print(filter_data2.head())
                            filter_data = filter_data.merge(filter_data2, how='inner', on=['Bureau of Meteorology station number', 'Year', 'Month', 'Day'])
                        # REMOVE THE FILE
                        for file in files:
                            os.remove(file)



                url = get_url(1, ID)

                r = requests.get(url, headers=headers)
                soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

                latitude = soup.find("div", {"id": "latitude"})
                if latitude != None:
                # Filter to get url for donwload
                    ul = soup.find("ul", class_= "downloads")
                    if ul != None:
                        a = ul.select('ul > li')[1].select('li > a')[0]
                        download_url = a['href']
                        # print(download_url)
                        download_url = BASE_URL+download_url

                        # Download the file
                        req = requests.get(download_url, headers=headers)
                        zip_file = ZipFile(BytesIO(req.content))
                        files = zip_file.namelist()
                        zip_file.extractall()

                        # READ THE FILE & FIlTER
                        with open(files[0], 'r') as csvfile:
                            df3 = pd.read_csv(csvfile)
                            filter_data3 = df3[df3['Year'] >= 2016] 
                            
                        if len(filter_data3.index) > 0:
                            # print(filter_data3.head())
                            filter_data = filter_data.merge(filter_data3, how='inner', on=['Bureau of Meteorology station number', 'Year', 'Month', 'Day'])
                        # REMOVE THE FILE
                        for file in files:
                            os.remove(file)

                # Save the dataframe to file
                data['col'] = [col for col in filter_data.columns]
                data['data'] = filter_data.to_dict()
                path = 'data/'+ID+'.json'
                with open(path, 'w') as fp:
                    json.dump(data, fp)



for i in range(1,1000):
    number = f"{i:03}"
    print(i)
    get_file(number)

    
# <html>
#  <head>
#  </head>
#  <body>
#   <p>
#    Your access is blocked due to the detection of a potential automated access request. The Bureau of Meteorology website does not support web scraping and if you are trying to access Bureau data through automated means, you may like to consider the following options:
#   </p>
#   <ul>
#    <li>
#     An anonymous FTP channel:
#     <a href="http://reg.bom.gov.au/catalogue/data-feeds.shtml">
#      http://reg.bom.gov.au/catalogue/data-feeds.shtml
#     </a>
#     -  this is free to access, but use is subject to the default terms of the Bureau's copyright notice:
#     <a href="http://www.bom.gov.au/other/copyright.shtml">
#      http://www.bom.gov.au/other/copyright.shtml
#     </a>
#    </li>
#    <li>
#     A Registered User service for continued use of Bureau data if your activity does not respect the default terms:
#     <a href="http://reg.bom.gov.au/other/charges.shtml">
#      http://reg.bom.gov.au/other/charges.shtml
#     </a>
#     noting charges apply to some data products. Please contact webreg@bom.gov.au  to discuss your requirements.
#    </li>
#   </ul>
#   <p>
#    If you still need assistance in accessing our website, please contact us by filling in your details at
#    <a href="http://reg.bom.gov.au/screenscraper/screenscraper_enquiry_form/">
#     http://reg.bom.gov.au/screenscraper/screenscraper_enquiry_form/
#    </a>
#    and we will get in touch with you. Thank you.
#   </p>
#   True Client IP: 118.99.81.198
#   <br/>
#   Reference Error: 0.6d283417.1629361100.edc7582b
#  </body>
# </html>
