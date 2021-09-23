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
from dash.dependencies import Input, Output
import boto3
from skimage import io
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Instantiating the Dashboard Application
app = dash.Dash(__name__)

s3 = boto3.resource('s3')
BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'
# Outputs image file to current directory
# s3.Bucket(BUCKET_NAME).download_file(KEY, 'current_satellite_image.jpg')





title = 'The date this image was captured: xx/xx/xx'
img = io.imread('data\\current_satellite_image.jpg')
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
    value='VI',
    id= 'vi--radio'
    )  

map = dcc.Graph(
    id = 'map-chart', 
    figure = map_fig, 
    style = {'height':'100%', 'width':'100%'},
    config={'displayModeBar': False}
    )

chart = dcc.Graph(
    id = 'vi-chart', 
    #figure = vi_fig, 
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
            dcc.Graph(
                    id = 'vi-chart', 
                
            )]),
])

#Callback
@app.callback(
    Output('vi-chart', 'figure'),
    Input('vi--radio','value')
)
def update_graph(VI):
    bandwidth_vi_data = pd.read_feather('C:\\Users\\Gladiator\\Documents\\Good_Crop_Bad_Crop\\dashboardv3\\data\\result-7680x-10240y')
    print(bandwidth_vi_data.head(3))
    # Create time_series figures
    # TODO: Currently, just creates plot for NVDI, expand to all VIs
    #labels ={"value": "Average", "variable": 'Statistic'}
    #VI_dict = create_VI_dict()
    #NDVI = VI_dict['NDVI']
    #VI_metric = str(list(VI_dict.keys())[0])
    bandwidth_vi_data = bandwidth_vi_data[VI]
    #vi_fig = px.line(bandwidth_vi_data, x='date', y=bandwidth_vi_data[['NDVI', 'SAVI', "GNDVI"]].columns, title="Time Series of selected region")
    vi_fig = px.line(bandwidth_vi_data, x='date', y=bandwidth_vi_data.columns, title="Time Series of selected region")
    vi_fig.add_trace(go.Scatter(mode="markers", x=bandwidth_vi_data["date"], y=bandwidth_vi_data["NDVI"], name = "NDVI", marker=dict(color='blue')))
    vi_fig.update_layout(autosize=True) 

    
    return vi_fig

'''
https://plotly.com/python/shapes/
This page for masking the fields
'''

#Main
if __name__ == '__main__':
    app.run_server(debug=True)