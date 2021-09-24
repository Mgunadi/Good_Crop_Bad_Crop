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

# S3 import implementation for Satellite image
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


# UI components
vi_radio = dcc.RadioItems(
    options=[
        {'label': 'Phenological Stage', 'value': 'NDVI'},
        {'label': 'Maturity', 'value': 'GNDVI'},
        {'label': 'Plantation', 'value': 'SAVI'}
    ],
    labelStyle={'display': 'flex'},
    value='NDVI',
    id= 'vi--radio'
    )  

field_selection = dcc.Dropdown(
    id='field_selection',
    options=[
        {'label': 'Field 1', 'value': 'Field_1'},
        {'label': 'Field 2', 'value': 'Field_2'},
        {'label': 'Field 3', 'value': 'Field_3'}
            ],
    value='Field_1'
)

map = dcc.Graph(
    id = 'map-chart', 
    figure = map_fig, 
    style = {'height':'100%', 'width':'100%'},
    config={'displayModeBar': False}
    )

chart = dcc.Graph(
    id = 'vi--chart', 
    #figure = vi_fig, 
    style = {'height':'90%', 'width':'80%'},
    config={'displayModeBar': False}
    )

# HTML Layout
app.layout = html.Div(id='container', 
                    children = [
                                html.Div(id = 'header', 
                                        children = [
                                                    html.H1('Good Crop, Bad Crop'),
                                                    html.P('Predicting sugarcane health near Prosperine, Queensland')]
                                        ),
                                html.Div(id = 'sidebar', 
                                        children =[
                                                    html.H2('Field Information',
                                                            style={'text-align': 'center'}
                                                            ),
                                                    html.P('Select health metric:',
                                                            style={'font-weight': 'bold'}
                                                            ),
                                                    vi_radio,
                                                    html.P('Select the region of interest:',
                                                            style={'font-weight': 'bold'}),
                                                    field_selection
                                                ],
                                        ),
                                html.Div(id = 'map', 
                                        children = [map]
                                        ),
                                html.Div(id = 'chart', 
                                        children = [chart]
                                        )
                                ]
                    )

#Callback
@app.callback(
    Output(component_id='vi--chart', component_property='figure'),
    Input(component_id='vi--radio', component_property='value'),
)
def update_time_series(VI):
    # Read and subset the dataframe
    upper = VI + '_LOWER'
    lower = VI + '_UPPER'
    bandwidth_vi_data = pd.read_feather('C:\\Users\\Gladiator\\Documents\\Good_Crop_Bad_Crop\\dashboardv3\\data\\result-7680x-10240y')
    bandwidth_vi_data = bandwidth_vi_data[['date', VI, lower, upper]]
    #print(bandwidth_vi_data.head(3))

    # Create time_series figures
    fig = go.Figure([
                        go.Scatter( 
                                    name='VI_score',
                                    x=bandwidth_vi_data['date'],
                                    y=bandwidth_vi_data[VI],
                                    line=dict(color='rgb(0,100,80)'),
                                    mode='lines'
                                  ),
                        go.Scatter(
                                    name='Upper Bound',
                                    x=bandwidth_vi_data['date'],
                                    y=bandwidth_vi_data[upper],
                                    mode='lines',
                                    marker=dict(color="#444"),
                                    line=dict(width=0),
                                    showlegend=False
                                ),
                        go.Scatter(
                                    name='Lower Bound',
                                    x=bandwidth_vi_data['date'],
                                    y=bandwidth_vi_data[lower],
                                    marker=dict(color="#444"),
                                    line=dict(width=0),
                                    mode='lines',
                                    fillcolor='rgba(68, 68, 68, 0.3)',
                                    fill='tonexty',
                                    showlegend=False
                                )
                    ])
    fig.update_layout(  
                        title= f'<b>{VI} Time Series of selected region<b>',
                        title_x=0.5,
                        yaxis_title=VI,
                        xaxis_title= 'Date',
                        hovermode="x",
                        autosize=True) 
    return fig

#Callback
@app.callback(
    Output(component_id='map-chart', component_property='figure'),
    Input(component_id='field_selection', component_property='value')
)
def update_field(field): 
    if field == 'Field_1':
        img = io.imread('data\\current_satellite_image.jpg')
        #print(img)
    else:
        img = io.imread('data\\masked_region.png')
        #print(img)

    title = 'The date this image was captured: xx/xx/xx'
    map_fig = px.imshow(img)
    map_fig.update_xaxes(showticklabels=False)
    map_fig.update_yaxes(showticklabels=False)
    map_fig.update_layout(autosize=True, margin=dict(l=0, r=0, b=0, t=0))
    
    return map_fig

'''
https://plotly.com/python/shapes/
This page for masking the fields
'''

#Main
if __name__ == '__main__':
    app.run_server(debug=True)