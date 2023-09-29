from dash import Dash, dcc, html, Input, Output, State, ctx
from plotly.subplots import make_subplots
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
data_analyses = ["Overview", "Performance"]
c_analysis = []

#%%

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(html.H1("FED3Bandit Analyis", style = {"textAlign": 'center'})),
    dbc.Row([
        dbc.Col([
            dbc.Row(dcc.Upload(children=dbc.Button('Upload File', outline=True, color="primary", size="lg", className="me-1"), multiple=False, id="upload_csv")),
            dbc.Row([
                dbc.Col(html.H4("Files", style = {"textAlign": 'center','padding': 10})),
                dbc.Col(dbc.Button('Clear', id="clear_button", outline=True, color="link", size="sm", className="me-1", style ={'padding': 10}))
            ]),
            dcc.Dropdown(id="my_files", options = file_names),
            dbc.Row(html.H4("Analysis", style = {"textAlign": 'center','padding': 10})),
            dcc.Dropdown(id="analyses", options = data_analyses),
            html.Br(),
            dbc.Row(dbc.Button('Run', outline=False, color="primary", className="me-1", id="individual_run")),
            html.Br(),
            dbc.Row(dbc.Button("Download File Summary", id="summary_button", outline=True, color="primary", size="lg", className="me-1")),
            dcc.Download(id="download_summary")
        ],width=2),
        dbc.Col([
            dbc.Row([dcc.Graph(id="s_actions")])
        ]),
        dbc.Col([
            dbc.Row(html.H4("Date Selection", style = {"textAlign": 'center','padding': 10})),
            dcc.DatePickerRange(id="date_range", start_date=datetime.datetime.today(), end_date=datetime.datetime.today(), disabled=True),
            dbc.Row(html.H4("Time Selection", style = {"textAlign": 'center','padding': 10})),
            dbc.Row(html.H5("From:",style = {"textAlign": 'center','padding': 5})),
            dcc.Dropdown(id="start_time", disabled=True),
            dbc.Row(html.H5("To:",style = {"textAlign": 'center','padding': 5})),
            dcc.Dropdown(id="end_time", disabled=True),
        ],width=2)
    ])

])

@app.callback(
        Output("my_files", "options"),
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
        
    return file_names


@app.callback(
        Output("date_range", "start_date"),
        Output("date_range", "end_date"),
        Output("date_range", "min_date_allowed"),
        Output("date_range", "max_date_allowed"),
        Output("date_range", "disabled"),
        Input("my_files", "value"),
        prevent_initial_call=True
)
def update_date_range(file):
    if file != None:
        c_df = file_data[file]
        c_dates = pd.to_datetime(c_df.iloc[:,0]).dt.date
        start_date = c_dates.iloc[0]
        end_date = c_dates.iloc[-1]

        return start_date, end_date, start_date, end_date, False
    else:
        start_date = datetime.datetime.today()
        end_date = datetime.datetime.today()

        return start_date, end_date, start_date, end_date, True
    
@app.callback(
        Output("start_time", "options"),
        Output("end_time", "options"),
        Output("start_time", "disabled"),
        Output("end_time", "disabled"),
        Output("start_time", "value"),
        Output("end_time", "value"),
        Input("date_range", "end_date"),
        Input("date_range", "start_date"),
        State("my_files", "value"),
        prevent_initial_call=True
)
def update_time_range(end_date, start_date, file):
    if file != None:
        dt_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        dt_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        c_df = file_data[file]
        c_dates = pd.to_datetime(c_df.iloc[:,0]).dt.date

        start_slice = c_df[c_dates == dt_start_date]
        start_time = pd.to_datetime(start_slice.iloc[:,0]).dt.time.iloc[0]
        end_slice = c_df[c_dates == dt_end_date]
        end_time = pd.to_datetime(end_slice.iloc[:,0]).dt.time.iloc[-1]
        
        #print(dt_start_date, dt_end_date)
        #print(start_time, end_time)
        if dt_start_date == dt_end_date:
            start_options = np.arange(int(str(start_time)[:2]),int(str(end_time)[:2])+1)
            end_options = np.arange(int(str(start_time)[:2])+1, int(str(end_time)[:2])+2)
            #print(start_options, end_options)
        else:
            start_options = np.arange(int(str(start_time)[:2]),24)
            end_options = np.arange(0,int(str(end_time)[:2])+1)

        first_option = str(start_options[0])
        last_option = str(end_options[-1])


        return list(start_options), list(end_options), False, False, first_option, last_option
    
    else:
        return [0],[0], True, True, 0, 0
        

@app.callback(
        Output("s_actions", "figure"),
        Input("individual_run", "n_clicks"),
        State("analyses", "value"),
        State("date_range", "start_date"),
        State("date_range", "end_date"),
        State("start_time", "value"),
        State("end_time", "value"),
        State("my_files", "value"),
        prevent_initial_call = True
)
def update_graph(i_clicks, analysis_type, start_date, end_date, start_time, end_time, file):
    global c_analysis
    
    start_datetime = datetime.datetime.strptime(start_date+" "+str(start_time), "%Y-%m-%d %H")
    end_datetime = datetime.datetime.strptime(end_date+" "+str(end_time), "%Y-%m-%d %H")

    if i_clicks:
        figure_i = go.Figure()
        if file != None:
            c_df = file_data[file]
            c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])

            c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]

        if analysis_type != None:
            if analysis_type == "Overview":
                figure_i = make_subplots(
                    rows=2, cols=3,
                    specs=[
                        [{"colspan":3},None, None],
                        [{}, {"colspan":2}, None]
                    ],
                    subplot_titles=("Overview", "Pellets", "Pokes"),
                    horizontal_spacing=0.15
                )
                
                cb_actions = f3b.binned_paction(c_slice, 5)
                c_prob = f3b.filter_data(c_slice)["Prob_left"].iloc[5:] / 100
                c_trials = np.arange(len(cb_actions)) 
                c_analysis.append(pd.DataFrame({"Trial": c_trials, "True P(left)": c_prob, "Mouse P(left)": cb_actions}))

                figure_i.add_trace(go.Scatter(x=c_trials, y = cb_actions, showlegend=False),row=1,col=1)
                figure_i.add_trace(go.Scatter(x=c_trials, y = c_prob, showlegend=False),row=1,col=1)
                figure_i.update_xaxes(title_text="Trial", row=1, col=1)
                figure_i.update_yaxes(title_text="P(left)", row=1, col=1)

                c_pellets = f3b.count_pellets(c_slice)
                figure_i.add_trace(go.Bar(x=[0], y=[c_pellets]), row=2, col=1)
                figure_i.update_xaxes(tickvals=[0], ticktext=[""], row=2, col=1)
                figure_i.update_yaxes(title_text="Pellets", row=2, col=1)

                c_all_pokes = f3b.count_pokes(c_slice)
                c_left_pokes = f3b.count_left_pokes(c_slice)
                c_right_pokes = f3b.count_right_pokes(c_slice)

                figure_i.add_trace(go.Bar(x=[0,1,2], y=[c_all_pokes, c_left_pokes, c_right_pokes]), row=2, col=2)
                figure_i.update_xaxes(tickvals=[0,1,2], ticktext=["All", "Left", "Right"], row=2, col=2)
                figure_i.update_yaxes(title_text="Pokes", row=2, col=2)

                figure_i.update_layout(showlegend=False, height=600)
            
            elif analysis_type == "Performance":
                figure_i = make_subplots(
                    rows=2, cols=4,
                    specs=[
                        [{"colspan":2}, None, {}, {}],
                        [{}, {"colspan":2}, None, {}]
                    ],
                    #subplot_titles=("Reversal PEH", "PPP", "Accuracy"),
                    horizontal_spacing=0.125
                )
                
                c_rev_peh = f3b.reversal_peh(c_slice, (-10,11)).mean(axis=0)
                figure_i.add_trace(go.Scatter(x=np.arange(-10,11),y=c_rev_peh, mode='lines'), row=1, col=1)
                figure_i.update_xaxes(title_text="Trial from reversal", tickvals=np.arange(-10,11,5), row=1, col=1)
                figure_i.update_yaxes(title_text="P(High)", row=1, col=1)

                c_ppp = f3b.pokes_per_pellet(c_slice)
                figure_i.add_trace(go.Bar(x=[0], y=[c_ppp]), row=1, col=3)
                figure_i.update_xaxes(tickvals=[0], ticktext=[""], row=1, col=3)
                figure_i.update_yaxes(title_text="Pokes/Pellet", row=1, col=3)

                c_accuracy = f3b.accuracy(c_slice)
                figure_i.add_trace(go.Bar(x=[0], y=[c_accuracy]), row=1, col=4)
                figure_i.update_xaxes(tickvals=[0], ticktext=[""], row=1, col=4)
                figure_i.update_yaxes(title_text="Accuracy", row=1, col=4)
                
                c_ws = f3b.win_stay(c_slice)
                c_ls = f3b.lose_shift(c_slice)
                figure_i.add_trace(go.Bar(x=[0,1], y= [c_ws, c_ls]), row=2, col=1)
                figure_i.update_xaxes(tickvals=[0,1], ticktext=["Win-Stay", "Lose-Shift"], row=2, col=1)
                figure_i.update_yaxes(title_text="Proportion", row=2, col=1)

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

                figure_i.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_pcoeffs), row=2, col=2)
                figure_i.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_ncoeffs), row=2, col=2)
                figure_i.update_xaxes(title_text="Trial in past", tickvals=np.arange(-5,0), row=2, col=2)
                figure_i.update_yaxes(title_text="Regr. Coeff.", row=2, col=2)
                
                figure_i.add_trace(go.Bar(x=[0,1], y=[c_pauc, c_nauc]), row=2, col=4)
                figure_i.update_xaxes(tickvals=[0,1], ticktext=["Wins", "Losses"], row=2, col=4)
                figure_i.update_yaxes(title_text="AUC", row=2, col=4)

                figure_i.update_layout(showlegend=False, height=600)

        return figure_i


@app.callback(
    Output("download_summary", "data"),
    Input("summary_button", "n_clicks"),
    State("my_files", "value"),
    prevent_initial_call=True
)

def summary(n_clicks, file):
    c_df = file_data[file]
    print("Here")
    c_summary = {
        "Accuracy": [f3b.accuracy(c_df)],
        "Win-Stay": [f3b.win_stay(c_df)],
        "Lose-Shift": [f3b.lose_shift(c_df)],
        "Reg Wins AUC": [0],
        "Reg Losses AUC": [0],
        "Pellets": [f3b.count_pellets(c_df)],
        "Left Pokes": [f3b.count_left_pokes(c_df)],
        "Right Pokes": [f3b.count_right_pokes(c_df)],
        "Total Pokes": [f3b.count_pokes(c_df)],
        "Iti after win": f3b.iti_after_win(c_df).median(),
        "Vigor": [0]
    }

    c_pside = f3b.side_prewards(c_df)
    c_preX = f3b.create_X(c_df, c_pside, 5)
    c_preg = f3b.logit_regr(c_preX)
    c_preg_auc = np.sum(c_preg.params)
    c_summary["Reg Wins AUC"] = [c_preg_auc]

    c_nside = f3b.side_nrewards(c_df)
    c_npreX = f3b.create_X(c_df, c_nside, 5)
    c_nreg = f3b.logit_regr(c_npreX)
    c_nreg_auc = np.sum(c_nreg.params)
    c_summary["Reg Losses AUC"] = [c_nreg_auc]

    c_poke_times = f3b.filter_data(c_df)["Poke_Time"]
    c_summary["Vigor"] = [c_poke_times.mean()]

    print(c_summary)
    c_summary_df = pd.DataFrame(c_summary)
    c_summary_df.index = [file]
    print(c_summary_df)
    outname = f"{file}_summary.csv"

    return dcc.send_data_frame(c_summary_df.to_csv, outname)

if __name__ == '__main__':
    app.run_server(debug=True)

def start_gui():
    app.run_server(debug=True)
