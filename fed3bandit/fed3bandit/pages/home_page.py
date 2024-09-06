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
    dbc.Row([
        dbc.Col([
            dbc.Row(dcc.Upload(children=dbc.Button('Upload File', outline=True, color="primary", size="lg", className="me-1"), multiple=False, id="upload_csv")),
            html.Br(),
            dbc.Row([
                dbc.Col(html.H4("Files", style = {"textAlign": 'left','padding': 5})),
                dbc.Col(dbc.Button('Clear', id="clear_button", outline=True, color="link", size="sm", className="me-1", style ={'padding': 10}))
            ]),
            dcc.Dropdown(id="my_files", options = file_names),
            html.Br(),
            dbc.Row(dbc.Button('Run', outline=False, color="primary", className="me-1", id="individual_run", disabled=True)),
            html.Br(),
            dbc.Row(dbc.Button("Download File Summary", id="summary_button", outline=True, color="primary", size="lg", className="me-1", disabled=True)),
            dcc.Download(id="download_summary")
        ],width=2),
        dbc.Col([
            dbc.Row(html.H4("Overview", style = {"textAlign": 'center'})),
            dbc.Row([dcc.Graph(id="s_actions", figure={"layout": go.Layout(margin={"t": 0})})])
        ], width=6),
        dbc.Col([
            html.H4("Summary (Average)", style = {"textAlign": 'center'}),
            dbc.Row([dash_table.DataTable([{"BLANK": "TABLE"}], id="summary_table")])
        ], width=2),
        dbc.Col([
            dbc.Row(html.H4("Start", style = {"textAlign": 'left','padding': 10})),
            dcc.Checklist(options=["Beginning of file"], value=["Beginning of file"], id="beg_check"),
            dcc.DatePickerSingle(id="start_date", date=datetime.datetime.today(), disabled=True),
            html.Br(),
            dcc.Dropdown(id="start_time", disabled=True),
            dbc.Row(html.H4("End", style = {"textAlign": 'left','padding': 10})),
            dcc.Checklist(options=["End of file"], value=["End of file"], id="end_check"),
            dcc.DatePickerSingle(id="end_date", date=datetime.datetime.today(), disabled=True),
            dcc.Dropdown(id="end_time", disabled=True),

        ],width=2)
    ])
])


@callback(
        Output("my_files", "options"),
        Output("my_files", "value"),
        Input("upload_csv", "contents"),
        Input("clear_button", "n_clicks"),
        State("upload_csv", "filename"),
        
        prevent_initial_call=True
)
def update_output(list_of_contents, clear_press, filenames):
    global file_data
    global file_names
    
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        file_data[filenames[:-4]]=df
        file_names.append(filenames[:-4])

    if "clear_button" == ctx.triggered_id:
        file_data = {}
        file_names = []
        
    return file_names, None

@callback(
        Output("start_date", "date"),
        Output("start_date", "min_date_allowed"),
        Output("start_date", "max_date_allowed"),
        Output("start_date", "disabled"),
        Input("my_files", "value"),
        Input("beg_check", "value"),
        prevent_initial_call=True
)
def update_dates(file, beg_check):
    if file != None:
        if beg_check != ["Beginning of file"]:
            print(file_data)
            c_df = file_data[file]
            c_dates = pd.to_datetime(c_df.iloc[:,0]).dt.date
            start_date = c_dates.iloc[0]
            end_date = c_dates.iloc[-1]

            return start_date, start_date, end_date, False
        else:
            start_date = datetime.datetime.today()
            end_date = datetime.datetime.today()

            return start_date, start_date, end_date, True     
    else:
        start_date = datetime.datetime.today()
        end_date = datetime.datetime.today()

        return start_date, start_date, end_date, True
    
@callback(
        Output("start_time", "disabled"),
        Output("start_time", "options"),
        Output("start_time", "value"),
        Output("end_time", "disabled"),
        Output("analysis_hours", "options"),
        Output("analysis_hours", "value"),
        Input("beg_check", "value"),
        Input("my_files", "value"),
        Input("start_date", "date"),
        Input("clear_button", "n_clicks"),
        prevent_initial_call=True
)
def update_time(beg_check, file, start_date, clear_click):
    if file != None:
        if beg_check != ["Beginning of file"]:
            c_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            
            c_df = file_data[file]
            c_datetimes = pd.to_datetime(c_df.iloc[:,0])
            c_start_datetimes = c_datetimes[c_datetimes.dt.date == c_start_date]

            first_event_time = c_start_datetimes.dt.time.iloc[0]
            first_event_str = str(first_event_time)[:2]

            times = [str(i) for i in range(int(first_event_str), 24)]
            hours = [str(i+1) for i in range(100)]

            return False, times, str(times[0]), False
        
        else:
            return True, [0], 0, True
    else:
        return True, [0], 0, True


@callback(
        Output("s_actions", "figure"),
        Input("individual_run", "n_clicks"),
        State("start_date", "date"),
        State("start_time", "value"),
        State("analysis_hours", "value"),
        State("my_files", "value"),
        prevent_initial_call = True
)
def update_graph(i_clicks, start_date, start_time, hours, file):
    
    c_df = file_data[file]
    c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])
    start_datetime = datetime.datetime.strptime(start_date+" "+str(start_time), "%Y-%m-%d %H")
    end_datetime = start_datetime + datetime.timedelta(hours=int(hours))

    figure_i = go.Figure()
    if file != None:
        c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]
    
        figure_i = make_subplots(
            rows=3, cols=3,
            specs=[
                [{"colspan":3},None, None],
                [{"colspan":2}, None, {"colspan":1}],
                [{"colspan":2}, None, {"colspan":1}]
            ],
            #subplot_titles=("Overview", "Pellets", "Pokes"),
            horizontal_spacing=0.15
        )
            
        cb_actions = f3b.binned_paction(c_slice, 5)
        c_prob = f3b.true_probs(c_slice)[0]
        c_trials = np.arange(len(cb_actions)) 

        figure_i.add_trace(go.Scatter(x=c_trials, y = cb_actions, showlegend=False),row=1,col=1)
        figure_i.add_trace(go.Scatter(x=c_trials, y = c_prob, showlegend=False),row=1,col=1)
        figure_i.update_xaxes(title_text="Trial", row=1, col=1)
        figure_i.update_yaxes(title_text="P(left)", row=1, col=1)

        try:
            c_rev_peh = f3b.reversal_peh(c_slice, (-10,11)).mean(axis=0)
            figure_i.add_trace(go.Scatter(x=np.arange(-10,11),y=c_rev_peh, mode='lines'), row=2, col=1)
            figure_i.update_xaxes(title_text="Trial from reversal", tickvals=np.arange(-10,11,5), row=2, col=1)
            figure_i.update_yaxes(title_text="P(High)", row=2, col=1)
        except:
            figure_i.add_annotation(text="Not Enough Data", x=0, y=0.5, row=2, col=1)

        c_ws = f3b.win_stay(c_slice)
        c_ls = f3b.lose_shift(c_slice)
        figure_i.add_trace(go.Bar(x=[0,1], y= [c_ws, c_ls]), row=2, col=3)
        figure_i.update_xaxes(tickvals=[0,1], ticktext=["Win-Stay", "Lose-Shift"], row=2, col=3)
        figure_i.update_yaxes(title_text="Proportion", row=2, col=3, range=[0,1])

        try:
            c_psides = f3b.side_prewards(c_slice)
            c_pX = f3b.create_X(c_slice, c_psides, 5)
            c_plogreg = f3b.logit_regr(c_pX)
            c_pcoeffs = c_plogreg.params
            c_pauc = c_pcoeffs.sum()

            c_nsides = f3b.side_nrewards(c_slice)
            c_nX = f3b.create_X(c_slice, c_nsides, 5)
            c_nlogreg = f3b.logit_regr(c_nX)
            c_ncoeffs = c_nlogreg.params
            c_nauc = c_ncoeffs.sum()

            figure_i.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_pcoeffs), row=3, col=1)
            figure_i.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_ncoeffs), row=3, col=1)
            figure_i.update_xaxes(title_text="Trial in past", tickvals=np.arange(-5,0), row=3, col=1)
            figure_i.update_yaxes(title_text="Regr. Coeff.", row=3, col=1)
            
            figure_i.add_trace(go.Bar(x=[0,1], y=[c_pauc, c_nauc]), row=3, col=3)
            figure_i.update_xaxes(tickvals=[0,1], ticktext=["Wins", "Losses"], row=3, col=3)
            figure_i.update_yaxes(title_text="AUC", row=3, col=3)
        
        except:
            figure_i.add_annotation(text="Not Enough Data", x=0, y=0.5, row=3, col=1)
            figure_i.add_annotation(text="Not Enough Data", x=0, y=0.5, row=3, col=3)

        figure_i.update_layout(showlegend=False, height=600, margin={"t": 10})
            
    return figure_i

@callback(
    Output("summary_table", "data"),
    Input("individual_run", "n_clicks"),
    State("start_date", "date"),
    State("start_time", "value"),
    State("analysis_hours", "value"),
    State("my_files", "value"),
    prevent_initial_call = True
)

def update_table(i_clicks, start_date, start_time, hours, file):
    
    c_df = file_data[file]
    start_datetime = datetime.datetime.strptime(start_date+" "+str(start_time), "%Y-%m-%d %H")
    end_datetime = start_datetime + datetime.timedelta(hours=int(hours))
    c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]

    c_pellets = f3b.count_pellets(c_slice)
    c_all_pokes = f3b.count_pokes(c_slice)
    c_left_pokes = f3b.count_left_pokes(c_slice)
    c_right_pokes = f3b.count_right_pokes(c_slice)
    c_invalid_pokes = f3b.count_invalid_pokes(c_slice)
    
    c_accuracy = f3b.accuracy(c_slice)
    c_ppp = f3b.pokes_per_pellet(c_slice)
    c_ws = f3b.win_stay(c_slice)
    c_ls = f3b.lose_shift(c_slice)

    c_table = [
        {"Metric": "Total Pokes", "Value": c_all_pokes},
        {"Metric": "Left Pokes", "Value": c_left_pokes},
        {"Metric": "Right Pokes", "Value": c_right_pokes},
        {"Metric": "Invalid Pokes", "Value": c_invalid_pokes},
        {"Metric": "Pellets", "Value": c_pellets},
        {"Metric": "Accuracy", "Value": round(c_accuracy, 2)},
        {"Metric": "Pokes/Pellet", "Value": round(c_ppp, 2)},
        {"Metric": "Win-Stay", "Value": round(c_ws, 2)},
        {"Metric": "Lose-Shift", "Value": round(c_ls, 2)}
        ]

    return c_table


@callback(
    Output("download_summary", "data"),
    Input("summary_button", "n_clicks"),
    State("my_files", "value"),
    State("start_date", "date"),
    State("start_time", "value"),
    State("analysis_hours", "value"),
    prevent_initial_call=True
)

def summary(n_clicks, file, start_date, start_time, hours):
    c_df = file_data[file]
    c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])
    start_datetime = datetime.datetime.strptime(start_date+" "+str(start_time), "%Y-%m-%d %H")
    end_datetime = start_datetime + datetime.timedelta(hours=int(hours))

    c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]

    c_summary = {
        "Start date": [start_datetime.date()],
        "Start time": [start_datetime.time()],
        "Analysis duration": [f"{hours} hours"],
        "Accuracy": [f3b.accuracy(c_slice)],
        "Win-Stay": [f3b.win_stay(c_slice)],
        "Lose-Shift": [f3b.lose_shift(c_slice)],
        "Reg Wins AUC": [0],
        "Reg Losses AUC": [0],
        "Pellets": [f3b.count_pellets(c_slice)],
        "Left Pokes": [f3b.count_left_pokes(c_slice)],
        "Right Pokes": [f3b.count_right_pokes(c_slice)],
        "Total Pokes": [f3b.count_pokes(c_slice)],
        "Iti after win": f3b.iti_after_win(c_slice).median(),
        "Iti after loss": np.median(f3b.iti_after_loss(c_slice)),
        "Timeout pokes": [f3b.count_invalid_pokes(c_slice, reason=["timeout"])],
        "Vigor": [f3b.filter_data(c_slice)["Poke_Time"].mean()]
    }

    try:
        c_pside = f3b.side_prewards(c_slice)
        c_preX = f3b.create_X(c_slice, c_pside, 5)
        c_preg = f3b.logit_regr(c_preX)
        c_preg_auc = np.sum(c_preg.params)
        c_summary["Reg Wins AUC"] = [c_preg_auc]
    except:
        c_summary["Reg Wins AUC"] = ["Not enough data"]

    try:
        c_nside = f3b.side_nrewards(c_slice)
        c_npreX = f3b.create_X(c_slice, c_nside, 5)
        c_nreg = f3b.logit_regr(c_npreX)
        c_nreg_auc = np.sum(c_nreg.params)
        c_summary["Reg Losses AUC"] = [c_nreg_auc]
    except:
        c_summary["Reg Losses AUC"] = ["Not enough data"]


    print(c_summary)
    c_summary_df = pd.DataFrame(c_summary)
    c_summary_df.index = [file]
    print(c_summary_df)
    outname = f"{file}_summary.csv"

    return dcc.send_data_frame(c_summary_df.to_csv, outname)

@callback(
    Output('individual_run', 'disabled'),
    Output('summary_button', 'disabled'),
    Input('my_files', 'value'),
    Input("clear_button", "n_clicks"),
)

def enable_analysis(c_file, clear_click):
    if c_file == None:
        return True, True
    else:
        return False, False


# %%
