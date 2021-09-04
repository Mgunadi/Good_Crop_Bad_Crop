import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

app = dash.Dash(__name__)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

df = pd.read_csv('https://raw.githubusercontent.com/phillipsj/dashmap/main/Geothermals.csv')
df['text'] = df['Name'] + ', ' + df['State']

fig = go.Figure(data=go.Scattergeo(
    lon=df['Lon_84'],
    lat=df['Lat_84'],
    text=df['text'],
    mode='markers',
    marker_color=df['Temp_C_ML']
))

fig.update_layout(
    geo_scope='usa'
)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Good Crop, Bad Crop',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children='A tool for identifying where the unhealthy sugar cane fields are (in the Proserpine region)', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Graph(
        id='Graph1',
        figure= fig
    )
])



if __name__ == '__main__':
    app.run_server(debug=True)