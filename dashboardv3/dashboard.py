import dash
import pillow as PIL
from PIL import Image
#from dash import dcc
#from dash import html
import dash_core_components as dcc
import dash_html_components as html
import boto3
from skimage import io
import plotly.express as px
from create_VI_timeseries import create_VI_dict


# Instantiating the Dashboard Application
app = dash.Dash(__name__)

s3 = boto3.resource('s3')

BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'

# Outputs image file to current directory
s3.Bucket(BUCKET_NAME).download_file(KEY, 'current_satellite_image.jpg')

# Create VI timeseries graph
# TODO: Currently, just creates plot for NVDI, expand to all VIs
labels ={"value": "Average", "variable": 'Statistic'}
VI_dict = create_VI_dict()
NDVI = VI_dict['NDVI']
VI_metric = str(list(VI_dict.keys())[0])

vi_fig = px.line(NDVI, x='Stage', y=NDVI.columns, labels=labels, title=f"{VI_metric} Time Series of selected region")
#fig.add_scatter()
vi_fig.update_layout(autosize=True)

# Create Satellite image to display
title = 'The date this image was captured: xx/xx/xx'
img = io.imread('current_satellite_image.jpg')
map_fig = px.imshow(img)
overlay = io.imread('sugarcane-region-mask.png')
map_fig.add_trace(overlay)
map_fig.update_xaxes(showticklabels=False)
map_fig.update_yaxes(showticklabels=False)
map_fig.update_layout(autosize=True, margin=dict(l=0, r=0, b=0, t=0))

# Dashboard Components
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