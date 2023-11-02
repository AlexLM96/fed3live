import dash
from dash import html

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

#%%

file_names = []
file_data = {}

#%%

dash.register_page(__name__)

layout = dbc.Container([
    dbc.Row(html.H1("FED3Bandit Analyis", style = {"textAlign": 'center'})),
    dbc.Row([
        dbc.Col([
            dbc.Row(dcc.Upload(children=dbc.Button('Upload Files', outline=True, color="primary", size="lg", className="me-1"), multiple=True, id="g_upload_csv")),
            dbc.Row(dbc.Button('Clear All', id="g_clear_button", outline=True, color="link", size="sm", className="me-1", style ={'textAlign': 'left'})),
            dbc.Row(html.H4("Group 1", style = {"textAlign": 'left','padding': 5})),
            dcc.Dropdown(id="g1_files", options = file_names, disabled=False, multi=True, clearable=True),
            html.Br(),
            dbc.Row(html.H4("Group 2", style = {"textAlign": 'left','padding': 5})),
            dcc.Dropdown(id="g2_files", options = file_names, disabled=False, multi=True, clearable=True),
            html.Br(),
            dbc.Row(dbc.Button('Run', outline=False, color="primary", className="me-1", id="g_run")),
            html.Br(),
            dbc.Row(dbc.Button("Download Summary", id="g_summary_button", outline=True, color="primary", size="lg", className="me-1")),
            dcc.Download(id="g_download_summary")
        ],width=2),
        dbc.Col([
            dbc.Row(html.H4("Performance", style = {"textAlign": 'center'})),
            dbc.Row([dcc.Graph(id="g_graphs", figure={"layout": go.Layout(margin={"t": 0})})])
        ], width=5),
        dbc.Col([
            html.H4("Summary (Average)", style = {"textAlign": 'center'}),
            dbc.Row([dash_table.DataTable([{"BLANK": "TABLE"}], id="g_summary_table")])
        ], width=3),
        dbc.Col([
            dbc.Row(html.H4("Start day: ", style = {"textAlign": 'left','padding': 10})),
            dcc.Dropdown(id="start_day", options=["Beginning of files"] + [f"Day {i+2}" for i in range(7)], value="Beginning of files", disabled=True),
            dbc.Row(html.H4("Start time: ", style = {"textAlign": 'left','padding': 10})),
            dcc.Dropdown(id="g_start_time", options=["Beginning of files"] + list(np.arange(0,24,1)), value="Beginning of files", disabled=True),
            dbc.Row(html.H4("Hours: ",style = {"textAlign": 'left','padding': 10})),
            dcc.Dropdown(id="g_analysis_hours", options=np.arange(1,100,1), disabled=True),
        ],width=2)
    ])
])





# %%

@callback(
        Output("g1_files", "options"),
        Output("g2_files", "options"),
        Input("g_upload_csv", "contents"),
        Input("g_clear_button", "n_clicks"),
        State("g_upload_csv", "filename"),
        prevent_initial_call=True
)
def update_files(list_of_contents, clear_clicks, filenames):
    global file_data
    global file_names
    
    if list_of_contents is not None:
        if isinstance(list_of_contents, list):
            for i, file in enumerate(list_of_contents):
                content_type, content_string = file.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                file_data[filenames[i][:-4]]=df
                file_names.append(filenames[i][:-4])
        
    if "g_clear_button" == ctx.triggered_id:
        file_data = {}
        file_names = []

    return file_names, file_names
        
@callback(
        Output("start_day", "disabled"),
        Output("g_start_time", "disabled"),
        Output("g_analysis_hours", "disabled"),
        Input("g1_files", "value"),
        prevent_initial_call=True
)
def enable_datetime(g1_files):
    if isinstance(g1_files, list):
        if len(g1_files) > 0:
            return False, False, False
        else:
            return True, True, True
    else:
        return True, True, True

@callback(
    Output("g_graphs", "figure"),
    Input("g_run", "n_clicks"),
    State("start_day", "value"),
    State("g_start_time", "value"),
    State("g_analysis_hours", "value"),
    State("g1_files", "value"),
    State("g2_files", "value"),
    prevent_initial_call = True
)

def udpate_g_graph(g_clicks, start_day, start_time, hours, g1_files, g2_files):

    g_figure = go.Figure()

    all_groups = [g1_files, g2_files]
    group_names = ["Group1", "Group2"]

    rev_peh = {}
    accuracy = {}
    win_stay = {}
    lose_shift = {}
    p_coeffs = {}
    p_auc = {}
    n_coeffs = {}
    n_auc = {}

    for i, group in enumerate(all_groups):
        if isinstance(group, list):
            if len(group) > 0:
                accuracy[group_names[i]] = []
                win_stay[group_names[i]] = []
                lose_shift[group_names[i]] = []
                p_auc[group_names[i]] = []
                n_auc[group_names[i]] = []
                
                g_rev_peh = []
                g_pcoeffs = []
                g_ncoeffs = []

                for mouse in group:
                    c_df = file_data[mouse]
                    c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])
                    if start_day == "Beginning of files":
                        start_date = c_df.iloc[0,0].date()
                    else:
                        days_offset = int(start_day[-1])
                        start_date = (c_df.iloc[0,0] + datetime.timedelta(days=days_offset)).date()

                    if start_time == "Beginning of files":
                        c_start_time = c_df.iloc[0,0].time()
                    else:
                        hours_offset = int(start_time)
                        c_start_time = (c_df.iloc[0,0] + datetime.timedelta(days=days_offset)).time()

                    start_datetime = datetime.datetime.combine(start_date, c_start_time)
                    end_datetime = start_datetime + datetime.timedelta(hours=int(hours))
                    c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]

                    try:
                        c_rev_peh = f3b.reversal_peh(c_slice, (-10,11)).mean(axis=0)
                        g_rev_peh.append(c_rev_peh)
                    except:
                        pass

                    c_accuracy = f3b.accuracy(c_slice)
                    accuracy[group_names[i]].append(c_accuracy)
                    c_ws = f3b.win_stay(c_slice)
                    win_stay[group_names[i]].append(c_ws)
                    c_ls = f3b.lose_shift(c_slice)
                    lose_shift[group_names[i]].append(c_ls)

                    try:
                        c_psides = f3b.side_prewards(c_slice)
                        c_pX = f3b.create_X(c_slice, c_psides, 5)
                        c_plogreg = f3b.logit_regr(c_pX)
                        c_pcoeffs = c_plogreg.params
                        c_pauc = c_pcoeffs.sum()
                        g_pcoeffs.append(c_pcoeffs)
                        p_auc[group_names[i]].append(c_pauc)

                        c_nsides = f3b.side_nrewards(c_slice)
                        c_nX = f3b.create_X(c_slice, c_nsides, 5)
                        c_nlogreg = f3b.logit_regr(c_nX)
                        c_ncoeffs = c_nlogreg.params
                        c_nauc = c_ncoeffs.sum()
                        g_ncoeffs.append(c_ncoeffs)
                        n_auc[group_names[i]].append(c_nauc)
                    except:
                        pass
                
                ag_rev_peh = np.vstack(g_rev_peh)
                rev_peh[group_names[i]] = ag_rev_peh.mean(axis=0)

                ag_pcoeffs = np.vstack(g_pcoeffs)
                p_coeffs[group_names[i]] = ag_pcoeffs.mean(axis=0)

                ag_ncoeffs = np.vstack(g_ncoeffs)
                n_coeffs[group_names[i]] = ag_ncoeffs.mean(axis=0)

            else:
                pass
        else:
            pass      

    g_figure = make_subplots(
        rows=4, cols=4,
        specs=[
            [{"colspan":2},None, {"colspan":2}, None],
            [{"colspan":2},None, {"colspan":2}, None],
            [{"colspan":2},None, {"colspan":2}, None],
            [{"colspan":2},None, {"colspan":2}, None]
        ],
        #subplot_titles=("Overview", "Pellets", "Pokes"),
        horizontal_spacing=0.2,
        vertical_spacing = 0.1
    )

    for group in rev_peh:
        g_figure.add_trace(go.Scatter(x=np.arange(-10,11),y=rev_peh[group], mode='lines'), row=1, col=1)
        
        
        g_figure.add_trace(go.Box(y=accuracy[group], boxpoints="all"), row=1, col=3)
        g_figure.add_trace(go.Box(y=win_stay[group], boxpoints="all"), row=2, col=1)
        g_figure.add_trace(go.Box(y=lose_shift[group], boxpoints="all"), row=2, col=3)

        g_figure.add_trace(go.Scatter(x=np.arange(-5,0),y=np.flip(p_coeffs[group]), mode='lines'), row=3, col=1)
        g_figure.add_trace(go.Box(y=p_auc[group], boxpoints="all"), row=3, col=3)

        g_figure.add_trace(go.Scatter(x=np.arange(-5,0),y=np.flip(n_coeffs[group]), mode='lines'), row=4, col=1)
        print(n_auc[group])
        g_figure.add_trace(go.Box(y=n_auc[group], boxpoints="all"), row=4, col=3)

    
    g_figure.update_xaxes(title_text="Trials", row=1, col=1)
    g_figure.update_xaxes(tickvals=np.arange(0, len(list(accuracy.keys()))), ticktext=list(accuracy.keys()), row=1, col=3)
    g_figure.update_xaxes(tickvals=np.arange(0, len(list(win_stay.keys()))), ticktext=list(win_stay.keys()), row=2, col=1)
    g_figure.update_xaxes(tickvals=np.arange(0, len(list(lose_shift.keys()))), ticktext=list(lose_shift.keys()), row=2, col=3)
    g_figure.update_xaxes(title_text="Trial in past", row=3, col=1)
    g_figure.update_xaxes(tickvals=np.arange(0, len(list(p_auc.keys()))), ticktext=list(p_auc.keys()), row=3, col=3)
    g_figure.update_xaxes(title_text="Trial in past", row=4, col=1)
    g_figure.update_xaxes(tickvals=np.arange(0, len(list(n_auc.keys()))), ticktext=list(n_auc.keys()), row=4, col=3)
    
    g_figure.update_yaxes(title_text="P(High)", range=[0,1], row=1, col=1)
    g_figure.update_yaxes(title_text="Accuracy", range=[0,1], row=1, col=3)
    g_figure.update_yaxes(title_text="Win Stay", range=[0,1], row=2, col=1)
    g_figure.update_yaxes(title_text="Lose Shift", range=[0,1], row=2, col=3)
    g_figure.update_yaxes(title_text="Win Coeffs.", range=[-0.7,2.5], row=3, col=1)
    g_figure.update_yaxes(title_text="Win AUC.", row=3, col=3)
    g_figure.update_yaxes(title_text="Loss Coeffs.", range=[-0.7,2.5], row=4, col=1)
    g_figure.update_yaxes(title_text="Loss AUC.", row=4, col=3)

    g_figure.update_layout(showlegend=False, height=600, margin={"t": 10})

    return g_figure

@callback(
    Output("g_summary_table", "data"),
    Input("g_run", "n_clicks"),
    State("start_day", "value"),
    State("g_start_time", "value"),
    State("g_analysis_hours", "value"),
    State("g1_files", "value"),
    State("g2_files", "value"),
    prevent_initial_call = True
)

def g_update_table(g_clicks, start_day, start_time, hours, g1_files, g2_files):

    all_groups = [g1_files, g2_files]
    group_names = ["Group1", "Group2"]

    table_data = [
        {"Metric": "Total Pokes"},
        {"Metric": "Left Pokes"},
        {"Metric": "Right Pokes"},
        {"Metric": "Invalid Pokes"},
        {"Metric": "Pellets"},
        {"Metric": "Pokes/Pellet"}
    ]

    for i, group in enumerate(all_groups):
        if isinstance(group, list):
            if len(group) > 0:
                for mouse in group:
                    c_df = file_data[mouse]
                    c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])
                    if start_day == "Beginning of files":
                        start_date = c_df.iloc[0,0].date()
                    else:
                        days_offset = int(start_day[-1])
                        start_date = (c_df.iloc[0,0] + datetime.timedelta(days=days_offset)).date()

                    if start_time == "Beginning of files":
                        c_start_time = c_df.iloc[0,0].time()
                    else:
                        hours_offset = int(start_time)
                        c_start_time = (c_df.iloc[0,0] + datetime.timedelta(days=days_offset)).time()

                    start_datetime = datetime.datetime.combine(start_date, c_start_time)
                    end_datetime = start_datetime + datetime.timedelta(hours=int(hours))
                    c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]

                    group_data = [
                        {group_names[i]: f3b.count_pokes(c_slice)},
                        {group_names[i]: f3b.count_left_pokes(c_slice)},
                        {group_names[i]: f3b.count_right_pokes(c_slice)},
                        {group_names[i]: f3b.count_invalid_pokes(c_slice)},
                        {group_names[i]: f3b.count_pellets(c_slice)},
                        {group_names[i]: round(f3b.pokes_per_pellet(c_slice),2)}
                    ]

                for j, metric in enumerate(table_data):
                    table_data[j] = table_data[j] | group_data[j]

    return table_data

@callback(
    Output("g_download_summary", "data"),
    Input("g_summary_button", "n_clicks"),
    State("g1_files", "value"),
    State("g2_files", "value"),
    State("start_day", "value"),
    State("g_start_time", "value"),
    State("g_analysis_hours", "value"),
    prevent_initial_call=True
)

def group_summary(n_clicks, g1_files, g2_files, start_day, start_time, hours):

    c_summary = {
        "File": [],
        "Group": [],
        "Start date": [],
        "Start time": [],
        "Analysis duration": [],
        "Accuracy": [],
        "Win-Stay": [],
        "Lose-Shift": [],
        "Reg Wins AUC": [],
        "Reg Losses AUC": [],
        "Pellets": [],
        "Left Pokes": [],
        "Right Pokes": [],
        "Total Pokes": [],
        "Iti after win": [],
        "Iti after loss": [],
        "Timeout pokes": [],
        "Vigor": []
    }

    all_groups = [g1_files, g2_files]
    group_names = ["Group 1", "Group 2"]

    for i, group in enumerate(all_groups):
        if isinstance(group, list):
            if len(group) > 0:
                for mouse in group:
                    c_df = file_data[mouse]
                    c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])
                    if start_day == "Beginning of files":
                        start_date = c_df.iloc[0,0].date()
                    else:
                        days_offset = int(start_day[-1])
                        start_date = (c_df.iloc[0,0] + datetime.timedelta(days=days_offset)).date()

                    if start_time == "Beginning of files":
                        c_start_time = c_df.iloc[0,0].time()
                    else:
                        hours_offset = int(start_time)
                        c_start_time = (c_df.iloc[0,0] + datetime.timedelta(days=days_offset)).time()

                    start_datetime = datetime.datetime.combine(start_date, c_start_time)
                    end_datetime = start_datetime + datetime.timedelta(hours=int(hours))
                    c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]

                    c_summary["File"].append(mouse)
                    c_summary["Group"].append(group_names[i])
                    c_summary["Start date"].append(start_date)
                    c_summary["Start time"].append(c_start_time)
                    c_summary["Analysis duration"].append(f"{hours} hours")
                    c_summary["Accuracy"].append(f3b.accuracy(c_slice))
                    c_summary["Win-Stay"].append(f3b.win_stay(c_slice))
                    c_summary["Lose-Shift"].append(f3b.lose_shift(c_slice))
                    
                    try:
                        c_pside = f3b.side_prewards(c_slice)
                        c_preX = f3b.create_X(c_slice, c_pside, 5)
                        c_preg = f3b.logit_regr(c_preX)
                        c_preg_auc = np.sum(c_preg.params)
                        c_summary["Reg Wins AUC"].append(c_preg_auc)
                    except:
                        c_summary["Reg Wins AUC"].append("Not enough data")

                    try:
                        c_nside = f3b.side_nrewards(c_slice)
                        c_npreX = f3b.create_X(c_slice, c_nside, 5)
                        c_nreg = f3b.logit_regr(c_npreX)
                        c_nreg_auc = np.sum(c_nreg.params)
                        c_summary["Reg Losses AUC"].append(c_nreg_auc)
                    except:
                        c_summary["Reg Losses AUC"].append("Not enough data")

                    c_summary["Pellets"].append(f3b.count_pellets(c_slice))
                    c_summary["Left Pokes"].append(f3b.count_left_pokes(c_slice))
                    c_summary["Right Pokes"].append(f3b.count_right_pokes(c_slice))
                    c_summary["Total Pokes"].append(f3b.count_pokes(c_slice))
                    c_summary["Iti after win"].append(f3b.iti_after_win(c_slice).median())
                    c_summary["Iti after loss"].append(np.median(f3b.iti_after_loss(c_slice)))
                    c_summary["Timeout pokes"].append(f3b.count_invalid_pokes(c_slice, reason=["timeout"]))
                    c_summary["Vigor"].append(f3b.filter_data(c_slice)["Poke_Time"].mean())

    print(c_summary)
    c_summary_df = pd.DataFrame(c_summary)
    print(c_summary_df.head())
    outname = f"group_summary.csv"

    return dcc.send_data_frame(c_summary_df.to_csv, outname)
