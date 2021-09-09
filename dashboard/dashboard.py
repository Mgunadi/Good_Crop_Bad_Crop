import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import boto3
from skimage import io
import pandas as pd
import random

app = dash.Dash(__name__)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Using Amazon S3 for file storage - need to rememeber to move the ~/.aws/credential and config files to the hosting service
s3 = boto3.resource('s3')

BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'

# Outputs image file to current directory
s3.Bucket(BUCKET_NAME).download_file(KEY, 'current_satellite_image.jpg')

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
us_cities = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

time_range = [x for x in range(48)]
ndvi = [random.randint(1, 10) for x in range(48)]
gndvi = [random.randint(1, 10) for x in range(48)]
savi = [random.randint(1, 10) for x in range(48)]

ndvi_fig = px.line(
    x=time_range,
    y=ndvi)

gndvi_fig = px.line(
    x=time_range,
    y=gndvi
)

savi_fig = px.line(
    x=time_range,
    y=savi
)

img = io.imread('my_local_image.jpg')
title = 'The date this image was captured: xx/xx/xx'
map_fig = px.imshow(
    img,
    title=title
)

map_fig.update_xaxes(showticklabels=False)
map_fig.update_yaxes(showticklabels=False)
map_fig.update_layout(autosize=False, width=1024, height=1024)

# App layout in terms of HTML
app.layout = html.Div(
    className='container',
    children=[
        html.Div(id='header',
                 children=[
                     html.H1('Good Crop, Bad Crop'),
                     html.P("Predicting the health of sugarcane in the Prosperine region of Queensland"
                            )]),

        html.Div(id='left-sidebar',
                 children=[
                     html.Div(id='field-health',
                              children=[
                                  html.H2('Field Health'),
                                  html.P(
                                      'Lorem ipsum paragraph that says something interesting about the field, incuding maybe the \{params\}')
                              ]),
                     dcc.Dropdown(id='field-filter',
                                  options=[
                                      {'label': 'Field 1',
                                       'value': '1'},
                                      {'label': 'Field 2',
                                       'value': '2'},
                                      {'label': 'Field 3', 'value': '3'}],
                                  value='1'),

                     html.Div(id='ndvi-info',
                              children=[
                                  dcc.Graph(
                                      id='ndvi-graph',
                                      figure=ndvi_fig,
                                      config={
                                          'displayModeBar': False
                                      }),
                                  html.H3('NDVI'),
                                  html.P(
                                      'Details regarding the suggested advice')
                              ]),

                     html.Div(id='gndvi-info',
                              children=[
                                  dcc.Graph(
                                      id='gndvi-graph',
                                      figure=gndvi_fig,
                                      config={
                                          'displayModeBar': False
                                      }
                                  ),
                                  html.H3('GNDVI'),
                                  html.P(
                                      'Details regarding the suggested advice')
                              ]),

                     html.Div(id='savi-info',
                              children=[
                                  dcc.Graph(
                                      id='savi-graph',
                                      figure=savi_fig,
                                      config={
                                          'displayModeBar': False
                                      }
                                  ),
                                  html.H3('SAVI'),
                                  html.P(
                                      'Details regarding the suggested advice')
                              ]),

                     html.Div(id='time-filter',
                              children=[
                                  html.H3('Time Period'),
                                  dcc.RangeSlider(
                                      count=1,
                                      min=-5,
                                      max=10,
                                      step=1,
                                      value=[0, 48]
                                  )
                              ])
                 ]),

        html.Div(id='map', children=[
            dcc.Graph(
                figure=map_fig,
                config={
                    'displayModeBar': False
                }
            )]),

        html.Div(id='right-sidebar',
                 children='This will be for toggling filter values'),

                 html.Div(id='footer', 
                 children='This will show our names, any copyright details and the data sources for the project')
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
