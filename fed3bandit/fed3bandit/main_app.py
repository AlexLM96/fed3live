import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True,
           suppress_callback_exceptions=True)

pages = list(dash.page_registry.values())

app.layout = html.Div([
    html.H1("FED3Bandit Analysis", style = {"textAlign": 'center'}),
    dbc.Row(dcc.Link(dbc.Button(f"{pages[0]['name']}", size="lg"), href=pages[0]["relative_path"])),
    html.Br(),
    dbc.Row(dcc.Link(dbc.Button(f"{pages[1]['name']}", size="lg"), href=pages[1]["relative_path"])),
    html.Br(),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)

def start_gui():
    app.run_server(debug=True)