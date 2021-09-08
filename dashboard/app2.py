import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px

from dash.dependencies import Input, Output

app = dash.Dash(__name__)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#px.set_mapbox_access_token(open("map_token.txt").read())
df = px.data.carshare()

app.layout = html.Div([
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-example-content')
])

@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))

def render_content(tab):
    figure = ff.create_hexbin_mapbox(
    data_frame=df, lat="centroid_lat", lon="centroid_lon",
    nx_hexagon=10, opacity=0.5, labels={"color": "Point Count"},
    min_count=1, color_continuous_scale="Viridis",
    show_original_data=True,
    original_data_marker=dict(size=4, opacity=0.6, color="deeppink")
)

    figure.update_layout(mapbox_style="open-street-map")
    figure.update_layout(margin=dict(b=0, t=0, l=0, r=0))

    if tab == 'tab-1':
        html.Div(style={'backgroundColor': colors['background']}, 
                children=[
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
                            figure= figure
                        )
                        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])



if __name__ == '__main__':
    app.run_server(debug=True)


