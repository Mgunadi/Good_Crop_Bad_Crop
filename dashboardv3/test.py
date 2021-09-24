from PIL import Image
from matplotlib import image
import matplotlib.pyplot as plt
import os
import boto3
import glob
import io
import numpy as np
import pandas as pd
import statistics

# Set up import paths
BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'
DATES_KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-B01-'

# TYPE
BLUE = 'B02'
GREEN = 'B03'
RED = 'B04'
NIR = 'B08'

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)


def get_image(x, y, band, date):
    custom_key = get_s3_KEY(x,y, band, date)
    pic_bytes = s3.Object(BUCKET_NAME, custom_key).get()['Body'].read()
    im = Image.open(io.BytesIO(pic_bytes))
    arr = np.array(im.getdata()).reshape(512,512,3)
    return arr

# return custom key for s3
def get_s3_KEY(x,y, band, date):
    CUSTOM_KEY = f'satellite-data/phase-01/data/sentinel-2a-tile-{x}x-{y}y/timeseries/{x}-{y}-{band}-{date}.png'
    return CUSTOM_KEY

# This function return a list of sorted dates
def get_dates():
    dates = []
    for obj in bucket.objects.filter(Prefix=DATES_KEY):
        content = obj.key
        x = len(content)
        date = content[x-14:x-4]
        dates.append(date)
    dates.sort(key= lambda x: int(''.join(x.split('-'))))
    return dates

# This function get the mask
def get_mask(x, y):
    mask_path = f'satellite-data/phase-01/data/sentinel-2a-tile-{x}x-{y}y/masks/sugarcane-region-mask.png'
    pic_bytes = s3.Object(BUCKET_NAME, mask_path).get()['Body'].read()
    im = Image.open(io.BytesIO(pic_bytes))
    arr = np.array(im.getdata()).reshape(512,512,4)
    return arr


# function to an array of wavelength value
def get_wavelength(x, y, band, date):
    custom_key = get_s3_KEY(x,y, band, date)
    pic_bytes = s3.Object(BUCKET_NAME, custom_key).get()['Body'].read()
    im = Image.open(io.BytesIO(pic_bytes))
    arr = np.array(im.getdata()).reshape(512,512)
    return arr

# SAVI calculation
def calculate_SAVI(NIR, RED, L):
    return (NIR - RED) / (NIR + RED + L) * (1+L)

# NDVI calculation
def calculate_NDVI(NIR, RED):
    return (NIR - RED) / (NIR + RED) 

# ENDVI calcuation
def calculate_ENDVI(NIR, GREEN, BLUE):
    return ((NIR+GREEN) - (2*BLUE)) / ((NIR+GREEN) + (2*BLUE)) 

# GNDVI calcuation
def calculcate_GNDVI(NIR, GREEN):
    return (NIR - GREEN) / (NIR + GREEN)

def get_VI_DF(X,Y, path):
    dates = get_dates()

    result = {}
    # result['x'] = []
    # result['Y'] = []
    result['date'] = []
    # BLUE = 'B02'
    # GREEN = 'B03'
    # RED = 'B04'
    # NIR = 'B08'
    result['B02'] = []
    result['B03'] = []
    result['B04'] = []
    result['B08'] = []
    result['NDVI'] = []
    result['SAVI'] = []
    result['ENDVI'] = []
    result['GNDVI'] = []

    result['B02_UPPER'] = []
    result['B03_UPPER'] = []
    result['B04_UPPER'] = []
    result['B08_UPPER'] = []
    result['NDVI_UPPER'] = []
    result['SAVI_UPPER'] = []
    result['ENDVI_UPPER'] = []
    result['GNDVI_UPPER'] = []

    result['B02_LOWER'] = []
    result['B03_LOWER'] = []
    result['B04_LOWER'] = []
    result['B08_LOWER'] = []
    result['NDVI_LOWER'] = []
    result['SAVI_LOWER'] = []
    result['ENDVI_LOWER'] = []
    result['GNDVI_LOWER'] = []
    for date in dates:
        red = get_wavelength(X,Y,RED,date)
        blue = get_wavelength(X,Y,BLUE,date)
        green = get_wavelength(X,Y,GREEN,date)
        nir = get_wavelength(X,Y,NIR,date)
        img = get_image(X,Y,'TCI',date)
        mask = get_mask(X,Y)
        
        # FOR AVG
        count = 0 
        r_avg = []
        b_avg = []
        g_avg = []
        n_avg = []
        ndvi_avg = []
        endvi_avg = []
        gndvi_avg = []
        savi_avg = []


        for y in range(0,512):
            for x in range(0,512):
                # Check if the pixel is in mask
                if (mask[y,x,3] == 255):
                    # Check for cloud
                    RGB = img[y,x]
                    if RGB[0] <= 200 and RGB[1] <= 200 and RGB[2] <= 200:

                        r = red[y,x]
                        g = green[y,x]
                        b = blue[y,x]
                        n = nir[y,x]

                        ndvi = calculate_NDVI(n,r)
                        endvi = calculate_ENDVI(n, g, b)
                        gndvi = calculcate_GNDVI(n, g)
                        savi = calculate_SAVI(n, r, 0.5)

                        r_avg.append(r)
                        b_avg.append(b)
                        g_avg.append(g)
                        n_avg.append(n)
                        ndvi_avg.append(ndvi)
                        endvi_avg.append(endvi)
                        gndvi_avg.append(gndvi)
                        savi_avg.append(savi)
                        count +=1

                        # r_avg += r
                        # b_avg += b
                        # g_avg += g
                        # n_avg += n
                        # ndvi_avg += ndvi
                        # endvi_avg += endvi
                        # gndvi_avg += gndvi
                        # savi_avg += savi
                        # count +=1


                        # result['x'].append(x)
                        # result['Y'].append(y)

                        # result['date'].append(date)

                        # result['B04'].append(r)
                        # result['B02'].append(b)
                        # result['B03'].append(g)
                        # result['B08'].append(n)

                        # result['NDvI'].append(ndvi)
                        # result['SAVI'].append(savi)
                        # result['ENDVI'].append(endvi)
                        # result['GNDVI'].append(gndvi)
        # ADD AVERAGE
        if count !=0:

            a = sum(r_avg)/count
            b = sum(b_avg)/count
            c = sum(g_avg)/count
            d = sum(n_avg)/count
            e = sum(ndvi_avg)/count
            f = sum(savi_avg)/count
            g = sum(endvi_avg)/count
            h = sum(gndvi_avg)/count
            result['date'].append(date)
            result['B04'].append(a)
            result['B02'].append(b)
            result['B03'].append(c)
            result['B08'].append(d)

            result['NDVI'].append(e)
            result['SAVI'].append(f)
            result['ENDVI'].append(g)
            result['GNDVI'].append(h)

            r_std = statistics.stdev(r_avg)
            b_std = statistics.stdev(b_avg)
            g_std = statistics.stdev(g_avg)
            n_std = statistics.stdev(n_avg)
            ndvi_std = statistics.stdev(ndvi_avg)
            endvi_std = statistics.stdev(endvi_avg)
            gndvi_std = statistics.stdev(gndvi_avg)
            savi_std = statistics.stdev(savi_avg)


            result['B04_UPPER'].append(a+r_std)
            result['B02_UPPER'].append(b+b_std)
            result['B03_UPPER'].append(c+g_std)
            result['B08_UPPER'].append(d+n_std)

            result['NDVI_UPPER'].append(e+ndvi_std)
            result['SAVI_UPPER'].append(f+savi_std)
            result['ENDVI_UPPER'].append(g+endvi_std)
            result['GNDVI_UPPER'].append(h+gndvi_std)

            result['B04_LOWER'].append(a-r_std)
            result['B02_LOWER'].append(b-b_std)
            result['B03_LOWER'].append(c-g_std)
            result['B08_LOWER'].append(d-n_std)

            result['NDVI_LOWER'].append(e-ndvi_std)
            result['SAVI_LOWER'].append(f-savi_std)
            result['ENDVI_LOWER'].append(g-endvi_std)
            result['GNDVI_LOWER'].append(h-gndvi_std)
        df = pd.DataFrame(result)
    save_path = f'{path}result-{X}x-{Y}y'
    df.to_feather(save_path)
                        


# TO GENERATE DF
# get_VI_DF('7680', '10240','data/')
# df = pd.read_feather('data/result-7680x-10240y')
# print(df.head(10))


# DO NOT REMOVE BELOW FOR TESTING
# DO NOT REMOVE BELOW FOR TESTING

# for obj in bucket.objects.filter(Prefix='satellite-data/Phase02-DataDelivery/'):
#     print(obj.key)

# satellite-data/Phase02-DataDelivery/geometries/geo-x9728-y6144.geojson

# picture = io.BytesIO(cont)
# im = image.imread(picture)

# pic = Image.open(picture)
# temp = np.array(pic.getdata()).reshape(512,512)

# print(im)
# s3.Object(BUCKET_NAME, custom_key).get()['Body'].read()
# response = client.list_objects(
#     Bucket='string',
#     Delimiter='string',
#     EncodingType='url',
#     Marker='string',
#     MaxKeys=123,
#     Prefix='string',
#     RequestPayer='requester',
#     ExpectedBucketOwner='string'
# )
# 




