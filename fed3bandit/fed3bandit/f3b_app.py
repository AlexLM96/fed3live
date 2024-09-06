
from dash import Dash, dcc, html, Input, Output, State, ctx, dash_table
from plotly.subplots import make_subplots
import dash
import dash_bootstrap_components as dbc
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import statsmodels.api as sm
import fed3bandit as f3b
import base64
import io


#%%

app = dash.Dash(__name__, external_stylesheets= [dbc.themes.BOOTSTRAP], use_pages=True)

app.config.suppress_callback_exceptions = True

#%%

navbar = dbc.Navbar(children=[
        dbc.Col(dcc.Link("Home", href="/home-page", id="home_link", style = {"fontSize": 24, "font-weight": "bold", "font": "Helvetica",
         "color": "black", "textDecoration": "None"})),
        dbc.Col(dcc.Link("Group Analysis", href="/group-analysis", id="group_link", style = {"fontSize": 24, "font-weight": "bold", "font": "Helvetica",
        "color": "black", "textDecoration": "None"})),
        dbc.Col(html.H4("Circadian Analysis"))
    ], color="light", style={"textAlign": 'center'})



#%%

app.layout = html.Div([
    navbar,
    dcc.Location(id="url"),
    html.Div(id="content")
])

@app.callback(
    Output('content', 'children'), 
    Input('url', 'pathname')
    )

def display_content(pathname):
    page_name = app.strip_relative_path(pathname)
    pages = dash.page_registry
    if not page_name:  # None or ''
        return pages['pages.home_page']['layout']
    elif page_name == 'home-page':
        return pages['pages.home_page']['layout']
    elif page_name == 'group-analysis':
        return pages['pages.group_analysis']['layout']
if __name__ == '__main__':
    app.run_server(debug=True)

def start_gui():
    app.run_server(debug=True)