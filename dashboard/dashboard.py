import dash
#from dash import dcc
#from dash import html
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import boto3
from skimage import io
import pandas as pd
import random

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID])

# Using Amazon S3 for file storage - need to rememeber to move the ~/.aws/credential and config files to the hosting service
s3 = boto3.resource('s3')

BUCKET_NAME = 'goodcropbadcrop'
KEY = 'satellite-data/phase-01/data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-TCI-2019-08-09.png'

# Outputs image file to current directory
s3.Bucket(BUCKET_NAME).download_file(KEY, 'current_satellite_image.jpg')

time_range = [x for x in range(48)]

gndvi = [random.randint(1, 10) for x in range(48)]

vi_fig = px.line(
    x=time_range,
    y=gndvi
)

vi_fig.update_layout(autosize=False, height= 300)

img = io.imread('current_satellite_image.jpg')
title = 'The date this image was captured: xx/xx/xx' # To show somewhere in the UI to indicate the date that this image comes from
map_fig = px.imshow(img)
map_fig.update_xaxes(showticklabels=False)
map_fig.update_yaxes(showticklabels=False)
map_fig.update_layout(autosize=False, margin=dict(l=0, r=0, b=0, t=0))

# HTML App layout
app.layout = html.Div(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1('Good Crop, Bad Crop'), width = 12),
            dbc.Col(html.P('Predicting sugarcane health in Prosperine, Queensland'), width = 12)]),
        dbc.Row([
            dbc.Col(html.H2('Sidebar'), width=4, style={'height': '100%'}),
            html.Div([
                dbc.Col(
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            dcc.Graph(
                            id='map',
                            figure=map_fig,
                            config={
                                'displayModeBar': False
                            })), width=8))
                ),
                dbc.Col(
                    html.Div(id='chart-container', 
                    children =
                        dcc.Graph(
                            id='vi-graph',
                            className='vi_graphs',
                            figure=vi_fig,
                            config={
                                'displayModeBar': False
                            })), width = 8
                    
                )])
            ])
        ])
    )

dbc.Row([dbc.Col(html.Div(html.B('1'), style={'height': '190px'},
                className='bg-danger'), width=4),
    dbc.Col(html.Div([
        dbc.Row([dbc.Col(html.Div(html.B('2'), className='bg-success'))]),
        dbc.Row([dbc.Col(html.Div(html.B('3'), style={'height': '120px'},
                className='bg-info'), width=6),
            dbc.Col(html.Div([
                dbc.Row([dbc.Col(html.Div(html.B('4'), className='bg-dark badge-dark'))]),
                dbc.Row([dbc.Col(html.Div(html.B('5'), className='bg-warning'))],
                className="row mt-3")]), width=6)
        ], className="row mt-3")]), width=8)
])

if __name__ == '__main__':
    app.run_server(debug = True)

'''
    id='container',
    children=[
        html.Div(id='header',
            children=[
                html.H1('Good Crop, Bad Crop'),
                html.P("Predicting the health of sugarcane in the Prosperine region of Queensland")
                ]),

        html.Div(id='sidebar',
            children=[
                html.H2('Sidebar')]
            ),

        html.Div(id='chart-container',
            children = [
                html.H2('Map')
            ]),
    ])
'''

''',
        children = [
        dcc.Graph(
                id='map',
                figure=map_fig,
                config={
                    'displayModeBar': False
                }
            ),
            dcc.Graph(
            id='vi-graph',
            className='vi_graphs',
            figure=vi_fig,
            config={
                'displayModeBar': False
            }
        )]'''