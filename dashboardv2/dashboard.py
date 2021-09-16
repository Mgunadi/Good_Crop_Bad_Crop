import dash
from dash import dcc
from dash import html
from skimage import io
import plotly.express as px
import random

# Instantiating the Dashboard Application
app = dash.Dash(__name__)

# Data
time_range = [x for x in range(48)]
vi = [random.randint(1, 10) for x in range(48)]
vi_fig = px.line(
    x=time_range,
    y=vi
)
vi_fig.update_layout(autosize=True)

title = 'The date this image was captured: xx/xx/xx'
img = io.imread('current_satellite_image.jpg')
map_fig = px.imshow(img)
map_fig.update_xaxes(showticklabels=False)
map_fig.update_yaxes(showticklabels=False)
map_fig.update_layout(autosize=True, margin=dict(l=0, r=0, b=0, t=0))

# HTML Components
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