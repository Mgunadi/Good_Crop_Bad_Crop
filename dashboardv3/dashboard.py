import dash
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import image
import glob
import os
#from dash import dcc
#from dash import html
import dash_core_components as dcc
import dash_html_components as html
import boto3
from skimage import io
import plotly.express as px
import random

# Instantiating the Dashboard Application
app = dash.Dash(__name__)

s3 = boto3.resource('s3')

BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'

# Outputs image file to current directory
s3.Bucket(BUCKET_NAME).download_file(KEY, 'current_satellite_image.jpg')

def get_tile_path(x, y, band, date):
    path = f'C:\\Users\\Gladiator\\Documents\\Good_Crop_Bad_Crop\\model\\satelite_data\\phase-01\\data\\sentinel-2a-tile-{x}x-{y}y\\timeseries\\{x}-{y}-{band}-{date}.png'
    return path

def get_image(x, y, band, date):
    path = get_tile_path(x,y,band,date)
    im = image.imread(path)
    return im

paths = glob.glob(get_tile_path('7680','10240','B01','*'))
dates = []
for path in paths:
    x = len(path)
    dates.append(path[x-14:x-4])

# sort the list of dates  
dates.sort(key= lambda x: int(''.join(x.split('-'))))

# Code the colour bands
BLUE = 'B02'
GREEN = 'B03'
RED = 'B04'
NIR = 'B08'

# NVDI calculation
def calulcate_NVDI(NIR, RED):
    return (NIR - RED) / (NIR + RED)

# ENVDI calcuation
def calculate_ENVDI(NIR, GREEN, BLUE):
    return ((NIR+GREEN) - (2*BLUE)) / ((NIR+GREEN) + (2*BLUE)) 

# GNDVI calcuation
def calulcate_GNDVI(NIR, GREEN):
    return (NIR - GREEN) / (NIR + GREEN)

def get_wavelength(x, y, band, date):
    im = Image.open(get_tile_path(x,y,band,date))
    arr = np.array(im.getdata()).reshape(512,512)
    return arr

def get_partition(image, xStart, yStart, mask):
    result = [] 
    for y in range(0, len(mask)):
        for x in range(0, len(mask[0])):
            # check if the mask pixel is selected then add the img pixel to list
            if mask[y,x]==1:
                result.append(image[yStart+y, xStart+x])
    return np.array(result)


def get_avg_vegetation_index(vi, X, Y, xStart, yStart, mask, date_range):
    date_range = []
    result = []
    avg = []
    upper = []
    lower = []
    for date in dates[0:12]:
        red = get_wavelength(X,Y,RED,date)
        blue = get_wavelength(X,Y,BLUE,date)
        green = get_wavelength(X,Y,GREEN,date)
        nir = get_wavelength(X,Y,NIR,date)
        
        if vi == 'NVDI':
            nvdi = calulcate_NVDI(nir, red)
            res = get_partition(nvdi, xStart, yStart, mask)
            average = np.average(res)
            sd = np.std(res)

            avg.append(average)
            upper.append(average+(2*sd))
            lower.append(average-(2*sd))
            result.append(res)
    dict = {}
    dict['result'] = result
    dict['avg'] = avg
    dict['upper'] = upper
    dict['lower'] = lower
    return dict

# Data
xlabels = [] 
result = []
xlabel2 = []
X = '7680'
Y = '10240'
xStart = 0
yStart = 0
mask = np.ones((20,20))
temp = get_avg_vegetation_index('NVDI', X, Y, xStart, yStart, mask, 2)
for i in range(0, len(temp['result'])):
    xlabel2.append(i)
    for res in temp['result'][i]:
        result.append(res)
        xlabels.append(i)
df = pd.DataFrame({'Stage': xlabel2, 'Average': temp['avg'], 'Upper': temp['upper'], 'Lower': temp['lower']})

labels={"value": "Average", "variable": 'Statistic'}
vi_fig = px.line(df, x='Stage', y=df.columns, labels=labels)
#fig.add_scatter()
vi_fig.update_layout(autosize=True)




title = 'The date this image was captured: xx/xx/xx'
img = io.imread('current_satellite_image.jpg')
map_fig = px.imshow(img)
map_fig.update_xaxes(showticklabels=False)
map_fig.update_yaxes(showticklabels=False)
map_fig.update_layout(autosize=True, margin=dict(l=0, r=0, b=0, t=0))




#components
vi_radio = dcc.RadioItems(
    options=[
        {'label': 'Phenological Stage', 'value': 'NDVI'},
        {'label': 'Maturity', 'value': 'GNDVI'},
        {'label': 'Plantation', 'value': 'SAVI'}
    ],
    labelStyle={'display': 'flex'},
    value='NDVI'
    )  

map = dcc.Graph(
    id = 'map-chart', 
    figure = map_fig, 
    style = {'height':'100%', 'width':'100%'},
    config={'displayModeBar': False}
    )

chart = dcc.Graph(
    id = 'vi-chart', 
    figure = vi_fig, 
    style = {'height':'90%', 'width':'80%'},
    config={'displayModeBar': False}
    )

# HTML Layout
app.layout = html.Div(id='container', children = [
    html.Div(id = 'header', children = [
        html.H1('Good Crop, Bad Crop'),
        html.P('Predicting sugarcane health near Prosperine, Queensland')]),
    html.Div(id = 'sidebar', children =[
        html.H2('Field Info'),
        html.P('Select health metric:'),
        vi_radio]),
    html.Div(id = 'map', children = [
        map]),
    html.Div(id = 'chart', children = [
        chart]),
])

#Callback

'''
https://plotly.com/python/shapes/
This page for masking the fields
'''

#Main
if __name__ == '__main__':
    app.run_server(debug=True)