from dash import Dash, dcc, html, Input, Output, State, ctx, dash_table, callback
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
import fed3

#%%

app = dash.Dash(__name__, external_stylesheets= [dbc.themes.BOOTSTRAP])

#app.config.suppress_callback_exceptions = True

df = pd.DataFrame({
    "Name": [],
    "Mode": [],
    "# Events": [],
    "Start Time": [],
    "End Time": [],
    "Duration": [],
    "Group": []
})

analyses_dict = {
    "Pellets": [
        "Single Pellet",
        "Multi Pellet",
        "Interpellet Interval",
        "Group Interpellet Interval",
        "Meal Size Histogram",
        "Group Meal Size Histogram",
        "Retrieval Time Plot",
        "Multi Retrieval Time Plot",
        "Average Retrieval Time Plot"
    ],
    "Pokes": [
        "Single Poke",
        "Average Poke (Correct)",
        "Average Poke (Error)",
        "Average Poke (Left)",
        "Average Poke (Right)",
        "Poke Bias",
        "Average Poke Bias Plot (Correct %)",
        "Average Poke Bias Plot (Left %)",
        "Poke Time"
    ],
    "Progressive Ratio": [
        "Breakpoint",
        "Group Breakpoint"
    ],
    "Circadian": [
        "Day/Night",
        "Day/Night Interpellet interval",
        "Chronogram (Line)",
        "Chronogram (Circle)",
        "Chronogram (Heatmap)",
        "Chronogram (Spiny)"
    ],
    "Bandit": [
        "Win-Stay",
        "Lose-Shift",
        "Win Regression",
        "Loss Regression",
        "Pokes/pellet",
        "Accuracy",
        "Reversal PEH",
    ],
    "Diagnostic": [
        "Battery Life",
        "Motor Turns"
    ]
}

files = {}

group = 0

#%%

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H4("Home", style = {"textAlign": 'center'})),
        dbc.Col(html.H4("Plots", style = {"textAlign": 'center'})),
        dbc.Col(html.H4("Settings", style = {"textAlign": 'center'}))
    ]),
    dbc.Row([
        dbc.Col([
            html.Br(),
            dbc.Row(dcc.Upload(id="load_file", multiple=True, children=dbc.Button('Load files', outline=True, color="primary", size="lg", className="me-2"))),
            dbc.Row(dbc.Button('Load folder', id="load_folder", outline=True, color="primary", size="lg", className="me-2")),
            dbc.Row(dbc.Button('Delete files', id="delete_file", outline=True, color="primary", size="lg", className="me-2")),
            html.Br(),
            dbc.Row(dbc.Button('Add group', id="add_group", outline=True, color="primary", size="lg", className="me-2")),
            dbc.Row(dbc.Button('Remove group', id="remove_group", outline=True, color="primary", size="lg", className="me-2")),
            dbc.Row(dbc.Button('Edit group', id="edit_group", outline=True, color="primary", size="lg", className="me-2")),
        ], width=2),
        dbc.Col([
            html.Br(),
            dash.dash_table.DataTable(
                id = "files_table",
                data = df.to_dict('records'), 
                columns = [{"name": i, "id": i} for i in df.columns],
                style_cell_conditional = [
                    {"if": {"column_id": "Name"},
                     "width": "30%"},
                    {"if": {"column_id": "Mode"},
                     "width": "10%"},
                    {"if": {"column_id": "# Events"},
                     "width": "5%"},
                    {"if": {"column_id": "Start Time"},
                     "width": "15%"},
                    {"if": {"column_id": "End Time"},
                     "width": "15%"},
                    {"if": {"column_id": "Duration"},
                     "width": "10%"},
                    {"if": {"column_id": "Group"},
                     "width": "10%"},
                ],
                row_selectable = "multi",
                style_cell = {"fontSize": 12}
            )
        ],width=8),
        dbc.Col([
            html.Br(),
            dbc.Row(html.H4("Mode")),
            dbc.Row(dcc.Dropdown(id="analysis_mode", options=["Pellets", "Pokes", "Progressive Ratio", "Circadian", "Diagnostic", "Bandit"])),
            dbc.Row(html.H4("Analysis")),
            dbc.Row(dcc.RadioItems(id="analysis_type", options=[])),
            html.Br(),
            dbc.Row(dbc.Button('Plot', outline=True, color="primary", size="lg", className="me-2", disabled=True))
        ], width=2),
    ])
])

#%%

@app.callback(
        Output("files_table", "data"),
        Input("load_file", "contents"),
        #Input("load_folder", "n_clicks"),
        Input("delete_file", "n_clicks"),
        Input("add_group", "n_clicks"),
        #Input("edit_group", "n_clicks"),
        #Input("remove_group", "n_clicks"),
        State("files_table", "selected_rows"),
        State("load_file", "filename"),

        prevent_initial_call=True
)

def update_files(list_of_contents, delete_click, group_click, s_rows, filename):

    global files
    global df
    global group

    button_clicked = ctx.triggered_id
    print(button_clicked)

    if button_clicked == "load_file":
        if list_of_contents is not None:
            for c_filename, content in zip(filename, list_of_contents):
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                c_file = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                c_file2 = fed3.FEDFrame(c_file)
                c_file2._load_init()
                c_file2 = c_file2.set_index(c_file2.columns[0])
                #c_file2 = fed3.load(io.StringIO(decoded.decode('utf-8')))
                files[c_filename] = c_file

        for file in files:
            c_file = files[file]
            
            if file not in list(df["Name"]):            
                new_row = pd.DataFrame({
                    "Name": [file], 
                    "Mode": [str(c_file2.fedmode)], 
                    "# Events": [str(c_file2["Event"].shape[0])], 
                    "Start Time": [str(c_file2.start_time)], 
                    "End Time": [str(c_file2.end_time)], 
                    "Duration": [str(c_file2.duration)],
                    "Groups": [""]
                })

                df = pd.concat([df, new_row]).reset_index(drop=True)

            else:
                print("File already loaded")
        
        new_data = df.to_dict('records')

    
    elif button_clicked == "delete_file":
        
        if s_rows != None:
            file_names = df["Name"].iloc[s_rows]
            print(file_names)
            for name in file_names:
                files.pop(name)

            df = df.drop(index=s_rows).reset_index(drop=True)
        else:
            print("Must select a row first")
            pass

        new_data = df.to_dict('records')

    elif button_clicked == "add_group":

        if s_rows != None:
            df.loc[s_rows, "Group"] = str(int(group))
            group += 1
        else:
            print("Must select a row first")
            pass

        new_data = df.to_dict('records')

    return new_data

@app.callback(
        Output("analysis_type", "options"),
        Input("analysis_mode", "value"),
        prevent_initial_call=True
)
def update_output(mode):
    #global analyses_dict
    c_options = analyses_dict[mode]
        
    return c_options

#%%

if __name__ == '__main__':
    app.run_server(debug=True)

def start_gui():
    app.run_server(debug=True)