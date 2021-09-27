import dash
import pandas as pd
import numpy as np
import os
from PIL import Image
from plotly.tools import mpl_to_plotly
import matplotlib.pyplot as plt
#from dash import dcc
#from dash import html
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import boto3
from skimage import io
import plotly.express as px
import plotly.graph_objects as go
from create_rasters import create_rasters
import imageio


# S3 import implementation for Satellite image
s3 = boto3.resource('s3')
BUCKET_NAME = 'goodcropbadcrop'
KEY = 'data/timeseries/7680-10240-TCI-2019-08-09.png'
# Outputs image file to current directory
# s3.Bucket(BUCKET_NAME).download_file(KEY, 'current_satellite_image.jpg')

data_path = os.path.join(os.getcwd(), 'data')
static_img_path = os.path.join(os.getcwd(), 'assets')
data_file_name = os.path.join(data_path, 'result-7680x-10240y')
img_file_name = os.path.join(data_path,'timeseries', '7680-10240-TCI-2019-08-09.png')

# Read the binary datafile
bandwidth_vi_data = pd.read_feather(data_file_name)



# Instantiating the Dashboard Application
app = dash.Dash(__name__)

# Draw the satellite background
def create_stl_img(VI_type):
    title = 'The date this image was captured: xx/xx/xx'
    if VI_type == 'NDVI':
        img = io.imread('NDVI.png')
        map_fig = px.imshow(img)
    elif VI_type == 'GNDVI':
        #img = create_rasters()
        # print("img 2")
        img = io.imread('GNDVI.png')
        #image2 = imageio.core.util.Array(img)
        map_fig = px.imshow(img)
        # print(type(image2))
        # print(image2)
        #map_fig = plt.figure()
        #map_fig = map_fig.add_subplot(img)
        #map_fig = mpl_to_plotly(map_fig)
        #map_fig.add_trace(px.imshow(img).img[0])
        # map_fig.update_xaxes(showticklabels=False)
        # map_fig.update_yaxes(showticklabels=False)
        # map_fig.update_layout(autosize=True, margin=dict(l=0, r=0, b=0, t=0))
    elif VI_type == 'SAVI':
        img = io.imread('ENDVI.png')
        map_fig = px.imshow(img)
    else:
        img = io.imread(img_file_name)
        print("img 1")
        print(type(img))
        print(img)
        map_fig = px.imshow(img)
        # map_fig.update_xaxes(showticklabels=False)
        # map_fig.update_yaxes(showticklabels=False)
        # map_fig.update_layout(autosize=True, margin=dict(l=0, r=0, b=0, t=0))
    return map_fig


# UI components
vi_radio = dcc.RadioItems(
    options=[
        {'label': 'Base map', 'value': 'None'},
        {'label': 'Normalized Difference Vegetation Index', 'value': 'NDVI'},
        {'label': 'Green Normalized Difference Vegetation Index', 'value': 'GNDVI'},
        {'label': 'Soil Adjusted Vegetation Index', 'value': 'SAVI'}
    ],
    labelStyle={'display': 'flex', 
                'color': 'white'},
    value='None',
    id='vi--radio'
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

time_scrub = dcc.Slider(
    id='date_slider',
    #min=bandwidth_vi_data['date'].min(),
    min=2021,
    #max=bandwidth_vi_data['date'].max(),
    max=2026,
    #value=bandwidth_vi_data['date'].min(),
    value=2021,
    marks={2021: {'label': '2021', 'style': {'color': 'yellow', 'font-weight': 'bold'}},  
            2022: {'label': '2022', 'style': {'color': 'yellow', 'font-weight': 'bold'}}, 
            2023: {'label': '2023', 'style': {'color': 'yellow', 'font-weight': 'bold'}}, 
            2024: {'label': '2024', 'style': {'color': 'yellow', 'font-weight': 'bold'}}, 
            2025: {'label': '2025', 'style': {'color': 'yellow', 'font-weight': 'bold'}}},
    step=1
)

map = dcc.Graph(
    id = 'map-chart', 
    figure = create_stl_img('Default'), 
    style = {'height':'100%', 'width':'100%'},
    config={'displayModeBar': False},
    )

chart = dcc.Graph(
    id = 'vi--chart', 
    #figure = vi_fig, 
    style = {'height':'90%', 'width':'80%', 'background-color': 'white'},
    config={'displayModeBar': False}
    )

# Function to get mask from basket (takes as inputs the Coordinates)
def get_mask(x, y):
    mask_path = f'satellite-data/phase-01/data/sentinel-2a-tile-{x}x-{y}y/masks/sugarcane-region-mask.png'
    pic_bytes = s3.Object(BUCKET_NAME, mask_path).get()['Body'].read()
    im = Image.open(io.BytesIO(pic_bytes))
    arr = np.array(im.getdata()).reshape(512,512,4)
    return arr

# HTML Layout
app.layout = html.Div(id='container', 
                    children = [
                                html.Div(id = 'header', 
                                        children = [
                                                    html.H1('Good Crop, Bad Crop'),
                                                    ]
                                        ),
                                html.Div(id= 'header2',
                                         children = [ 
                                                        html.Div(html.H2('Predicting sugarcane health near Proserpine, Queensland')),
                                                        html.Div(html.Img(src= os.path.join('assets','sugarcane.png'), style={'align': 'right'}))
                                                    ]
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
                                                    # Add blank line
                                                    html.Br(), 
                                                    html.P('Select the region of interest:',
                                                            style={'font-weight': 'bold'}),
                                                    field_selection,
                                                    html.Br(), 
                                                    html.P('Forecast into:',
                                                            style={'font-weight': 'bold'}),
                                                    time_scrub,  
                                                ],
                                        ),
                                html.Div(
                                    html.P('Crop health: Good',), style={'font-size': '200'}, className='Panel1'),
                                html.Div(id = 'map', 
                                        children = [map],
                                        style= {'background-color': 'rgb(5, 4, 37)'}
                                        ),
                                html.Div(id = 'chart', 
                                        children = [chart]
                                        )
                                ]
                    )

#Callback
@app.callback(
    Output(component_id='vi--chart', component_property='figure'),
    Output(component_id='map-chart', component_property='figure'),
    Input(component_id='vi--radio', component_property='value'),
)
def update_VI_type(VI):
    # Read and subset the dataframe
    if VI == "None":
        upper = 'NDVI_LOWER'
        lower = 'NDVI_UPPER'
        data_vi = bandwidth_vi_data[['date', 'NDVI', lower, upper]]
        VI = 'NDVI'
    else:
        upper = VI + '_LOWER'
        lower = VI + '_UPPER'
        data_vi = bandwidth_vi_data[['date', VI, lower, upper]]

    # Create time_series figures
    fig = go.Figure([
                        go.Scatter( 
                                    name=f'Average {VI} - all pixels',
                                    x=data_vi['date'],
                                    y=data_vi[VI],
                                    line=dict(color='rgb(0,100,80)'),
                                    mode='lines'
                                ),
                        go.Scatter(
                                    name='Upper Bound',
                                    x=data_vi['date'],
                                    y=data_vi[upper],
                                    mode='lines',
                                    marker=dict(color="#444"),
                                    line=dict(width=0),
                                    showlegend=False
                                ),
                        go.Scatter(
                                    name='Lower Bound',
                                    x=data_vi['date'],
                                    y=data_vi[lower],
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
    return fig, create_stl_img(VI)

# Callback
# @app.callback(
#     #Output(component_id='map-chart', component_property='figure'),
#     Input(component_id='field_selection', component_property='value')
# )

# def update_field(field): 
#     #return create_stl_img(field)

'''
https://plotly.com/python/shapes/
This page for masking the fields
'''

#Main
if __name__ == '__main__':
    app.run_server(debug=True)