from dash import Dash, dcc, html, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import statsmodels.api as sm
import fed3live as f3l
import base64
import io

#%%

file_names = []
file_data = {}
data_analyses = ["Overview", "Win-stay/Lose-shift", "Reversal peh", "Logistic wins", "Logistic losses"]
c_analysis = []
group_clicks = 0

#%%

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(html.H1("Bandit Task Analysis", style = {"textAlign": 'center'})),
    dbc.Row([
        dbc.Col([
            dbc.Row(dcc.Upload(children=dbc.Button('Upload File', outline=True, color="primary", size="lg", className="me-1"), multiple=False, id="upload_csv")),
            dbc.Row([
                dbc.Col(html.H3("Files", style = {"textAlign": 'center','padding': 10})),
                dbc.Col(dbc.Button('Clear', outline=True, color="link", size="sm", className="me-1", style ={'padding': 10}))
            ]),
            dcc.Dropdown(id="my_files", options = file_names),
            dbc.Row(html.H3("Analysis", style = {"textAlign": 'center','padding': 10})),
            dcc.Dropdown(id="analyses", options = data_analyses),
            dbc.Row(html.H3("Date Selection", style = {"textAlign": 'center','padding': 10})),
            dcc.DatePickerRange(id="date_range", start_date=datetime.datetime.today(), end_date=datetime.datetime.today(), disabled=True),
            dbc.Row(html.H3("Time Selection", style = {"textAlign": 'center','padding': 10})),
            dbc.Row(html.H5("From:",style = {"textAlign": 'center','padding': 5})),
            dcc.Dropdown(id="start_time", disabled=True),
            dbc.Row(html.H5("To:",style = {"textAlign": 'center','padding': 5})),
            dcc.Dropdown(id="end_time", disabled=True)
        ],width=2),
        dbc.Col([
            dbc.Row(html.H3("Current data", style = {"textAlign": 'center'})),
            dbc.Row([dcc.Graph(id="s_actions")])
        ]),
        dbc.Col([
            dbc.Row(dbc.Button("Download Data", id="download_button", outline=True, color="primary", size="lg", className="me-1")),
            dcc.Download(id="download_data"),
            dbc.Row(html.H3("Individual Analysis", style = {"textAlign": 'center'})),
            dbc.Row(dbc.Button('Run', outline=False, color="primary", className="me-1", id="individual_run")),
            html.Br(),
            dbc.Row(html.H3("Group Analysis", style = {"textAlign": 'center'})),
            dcc.Checklist([" Group Analysis"], id="group_analysis", value=[]),
            dbc.Row(html.H5("Group 1", style = {"textAlign": 'center','padding': 10})),
            dcc.Dropdown([], id="group 1", disabled=True, multi=True),
            dbc.Row(html.H5("Group 2", style = {"textAlign": 'center','padding': 15})),
            dcc.Dropdown([], id="group 2", disabled=True, multi=True),
            html.Br(),
            dbc.Row(dbc.Button('Run', outline=False, color="primary", className="me-1", disabled=True, id="group_run"))
            
        ],width=2)
    ])

])

@app.callback(
        Output("my_files", "options"),
        Input("upload_csv", "contents"),
        State("upload_csv", "filename"),
        prevent_initial_call=True
)
def update_output(list_of_contents, filenames):
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        file_data[filenames[:12]]=f3l.filter_data(df)
        file_names.append(filenames[:12])
        
    return file_names

@app.callback(
        Output("group 1", "options"),
        Output("group 2", "options"),
        Input("my_files", "options"),
        prevent_initial_call=True
)

def update_group_options(filenames):
    return filenames, filenames

@app.callback(
        Output("my_files", "disabled"),
        Output("individual_run", "disabled"),
        Output("group 1", "disabled"),
        Output("group 2", "disabled"),
        Output("group_run", "disabled"),
        Input("group_analysis", "value"),
        prevent_initial_call=True
)

def setup_group_analysis(group_check):
    if group_check == [' Group Analysis']:
        return True, True, False, False, False
    elif group_check == []:
        return False, False, True, True, True
    

@app.callback(
        Output("date_range", "start_date"),
        Output("date_range", "end_date"),
        Output("date_range", "min_date_allowed"),
        Output("date_range", "max_date_allowed"),
        Output("date_range", "disabled"),
        Input("group_analysis", "value"),
        Input("my_files", "value"),
        Input("group 1", "value"),
        Input("group 2", "value"),
        prevent_initial_call=True
)
def update_date_range(group_check, file, group1, group2):
    if group_check == []:
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

    elif group_check == [' Group Analysis']:
        if (group1 != None) and (group2 != None):
            all_start_dates = []
            all_end_dates = []
            for mouse in (group1+group2):
                c_df = file_data[mouse]
                c_dates = pd.to_datetime(c_df.iloc[:,0]).dt.date
                start_date = c_dates.iloc[0]
                end_date = c_dates.iloc[-1]
                all_start_dates.append(start_date)
                all_end_dates.append(end_date)
            
            latest_start = max(all_start_dates)
            
            earliest_end = min(all_end_dates)

            return latest_start, earliest_end, latest_start, earliest_end, False

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
        Input("group_analysis", "value"),
        State("my_files", "value"),
        State("group 1", "value"),
        State("group 2", "value"),
        prevent_initial_call=True
)
def update_time_range(end_date, start_date, group_check, file, group1, group2,):
    if group_check == []:
        if file != None:
            dt_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            dt_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            
            c_df = file_data[file]
            c_dates = pd.to_datetime(c_df.iloc[:,0]).dt.date

            start_slice = c_df[c_dates == dt_start_date]
            start_time = pd.to_datetime(start_slice.iloc[:,0]).dt.time.iloc[0]
            start_options = np.arange(int(str(start_time)[:2]),24)

            end_slice = c_df[c_dates == dt_end_date]
            end_time = pd.to_datetime(end_slice.iloc[:,0]).dt.time.iloc[-1]
            last_option = int(str(end_time)[:2])
            end_options = np.arange(0,last_option+1)
            print(end_options)


            return list(start_options), list(end_options), False, False, str(start_time)[:2], str(last_option)
        
        else:
            return [0],[0], True, True, 0, 0
        
    elif group_check == [' Group Analysis']:
        if (group1 != None) and (group2 != None):
            dt_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            dt_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            all_start_times = []
            all_end_times = []
            for mouse in (group1+group2):
                c_df = file_data[mouse]
                c_dates = pd.to_datetime(c_df.iloc[:,0]).dt.date
                
                c_start_slice = c_df[c_dates == dt_start_date]
                c_start_times = pd.to_datetime(c_start_slice.iloc[:,0]).dt.time
                all_start_times.append(c_start_times.iloc[0])

                c_end_slice = c_df[c_dates == dt_end_date]
                c_end_times = pd.to_datetime(c_end_slice.iloc[:,0]).dt.time
                all_end_times.append(c_end_times.iloc[-1])

            latest_start = max(all_start_times)
            latest_str = str(latest_start)[:2]
            start_options = np.arange(int(latest_str), 24)

            earliest_end = min(all_end_times)
            earliest_str = str(earliest_end)[:2]
            end_options = np.arange(0, int(earliest_str)+1)

            return list(start_options), list(end_options), False, False, latest_str, earliest_str
    
        else:
            return [],[], True, True, 0, 0



@app.callback(
        Output("s_actions", "figure"),
        Input("individual_run", "n_clicks"),
        Input("group_run", "n_clicks"),
        State("analyses", "value"),
        State("date_range", "start_date"),
        State("date_range", "end_date"),
        State("start_time", "value"),
        State("end_time", "value"),
        State("my_files", "value"),
        State("group 1", "value"),
        State("group 2", "value"),
        prevent_initial_call = True
)
def update_graph(i_clicks, g_clicks, analysis_type, start_date, end_date, start_time, end_time, file, group1, group2):
    global c_analysis
    global group_clicks
    global single_clicks
    figure = go.Figure()
    start_datetime = datetime.datetime.strptime(start_date+" "+str(start_time), "%Y-%m-%d %H")
    end_datetime = datetime.datetime.strptime(end_date+" "+str(end_time), "%Y-%m-%d %H")
    if g_clicks:
        group_clicks = g_clicks
        if (len(group1)>0) and (len(group2)>0):
            g1_slices = {}
            g2_slices = {}
            for mouse in group1:
                c_df = file_data[mouse]
                c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])
                c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]
                g1_slices[mouse] = c_slice

            for mouse in group2:
                c_df = file_data[mouse]
                c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])
                c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]
                g2_slices[mouse] = c_slice

            if analysis_type != None:
                if analysis_type == "Overview":
                    #Find a way to trigger warning that it is not possible
                    pass
                    

                elif analysis_type == "Win-stay/Lose-shift":
                    all_ws_g1 = {mouse: f3l.win_stay(g1_slices[mouse]) for mouse in g1_slices}
                    all_ws_g2 = {mouse: f3l.win_stay(g2_slices[mouse]) for mouse in g2_slices}
                    all_ls_g1 = {mouse: f3l.lose_shift(g1_slices[mouse]) for mouse in g1_slices}
                    all_ls_g2 = {mouse: f3l.lose_shift(g1_slices[mouse]) for mouse in g1_slices}
                    
                    x_ws = ["win-stay"]
                    x_ls = ["lose-shift"]


                    figure.add_trace(go.Box(x=x_ws*len(list(all_ws_g1.keys())), y= list(all_ws_g1.values()), name="Group 1"))
                    figure.add_trace(go.Box(x=x_ws*len(list(all_ws_g2.keys())), y= list(all_ws_g2.values()), name="Group 2"))
                    figure.add_trace(go.Box(x=x_ls*len(list(all_ls_g1.keys())), y= list(all_ls_g2.values()), name="Group 1"))
                    figure.add_trace(go.Box(x=x_ls*len(list(all_ls_g1.keys())), y= list(all_ls_g2.values()), name="Group 2"))
                    figure.update_layout(title = {'text': "Mouse Win-Stay/Lose-Shift ", 'x': 0.5}, boxmode="group", yaxis_title = "Proportion", font = dict(size = 16), yaxis_range = [0,1],xaxis= dict(tickvals = [0,1], ticktext = ["Win-Stay", "Lose-Shift"]), transition_duration=200)

                    return figure

    elif i_clicks:
        if file != None:
            c_df = file_data[file]
            c_df.iloc[:,0] = pd.to_datetime(c_df.iloc[:,0])

            c_slice = c_df[np.logical_and(c_df.iloc[:,0] >= start_datetime, c_df.iloc[:,0] <= end_datetime)]

        if analysis_type != None:
            if analysis_type == "Overview":
                cb_actions = f3l.binned_paction(c_slice, 5)
                c_prob = f3l.filter_data(c_slice)["Session_type"].iloc[5:] / 100
                c_trials = np.arange(len(cb_actions)) 
                c_analysis.append(pd.DataFrame({"Trial": c_trials, "True P(left)": c_prob, "Mouse P(left)": cb_actions}))

                figure.add_trace(go.Scatter(x=c_trials, y = cb_actions, showlegend=False))
                figure.add_trace(go.Scatter(x=c_trials, y = c_prob, showlegend=False))
                figure.update_layout(title = {'text': "Actions", 'x': 0.5}, xaxis_title = "Trial", yaxis_title = "P(left)", 
                                font = dict(size = 16), transition_duration=200)
            
            elif analysis_type == "Win-stay/Lose-shift":
                c_ws = f3l.win_stay(c_slice)
                c_ls = f3l.lose_shift(c_slice)
                c_analysis.append(pd.DataFrame({"Win-stay": [c_ws], "Lose-shift": [c_ls]}))

                figure.add_trace(go.Bar(x=[0,1], y= [c_ws, c_ls]))
                figure.update_layout(title = {'text': "Mouse Win-Stay/Lose-Shift ", 'x': 0.5}, yaxis_title = "Proportion", font = dict(size = 16), yaxis_range = [0,1],
                                xaxis= dict(tickvals = [0,1], ticktext = ["Win-Stay", "Lose-Shift"]), transition_duration=200)
                
            elif analysis_type == "Reversal peh":
                c_rev_peh = f3l.reversal_peh(c_slice, (-10,11)).mean(axis=0)
                c_analysis.append(pd.DataFrame({"Trial from reversal": np.arange(-10,11), "P(High)": c_rev_peh}))

                figure.add_trace(go.Scatter(x=np.arange(-10,11),y=c_rev_peh, mode='lines', showlegend = False))
                figure.update_layout(title = {'text': "Reversal PEH", 'x': 0.5}, xaxis_title = "Trial", yaxis_title = "P(High)", yaxis_range=[0,1], font = dict(size = 16), transition_duration=200)
            
            elif analysis_type == "Logistic wins":
                c_sidep_rew = f3l.side_prewards(c_slice)
                c_preX = f3l.create_X(c_slice, c_sidep_rew[0], c_sidep_rew[1],5)
                c_plogreg = f3l.logit_regr(c_preX)
                c_pcoeffs = c_plogreg.params
                c_analysis.append(pd.DataFrame({"Trial in past": np.flip(np.arange(-5,0)), "Regr. Coeffs.": c_pcoeffs}))

                figure.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_pcoeffs))
                figure.update_layout(title = {'text': "Logistic wins", 'x': 0.5}, xaxis={"title": "Trial in past", "tickvals": np.flip(np.arange(-5,0))}, yaxis_title = "Regr. Coeff", yaxis_range=[-0.5,2.5], font = dict(size = 16), transition_duration=200)

            elif analysis_type == "Logistic losses":
                c_siden_rew = f3l.side_nrewards(c_slice)
                c_npreX = f3l.create_X(c_slice, c_siden_rew[0], c_siden_rew[1],5)
                c_nlogreg = f3l.logit_regr(c_npreX)
                c_ncoeffs = c_nlogreg.params
                c_analysis.append(pd.DataFrame({"Trial in past": np.flip(np.arange(-5,0)), "Regr. Coeffs.": c_ncoeffs}))

                figure.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_ncoeffs))
                figure.update_layout(title = {'text': "Logistic losses", 'x': 0.5}, xaxis={"title": "Trial in past", "tickvals": np.flip(np.arange(-5,0))}, yaxis_title = "Regr. Coeff", yaxis_range=[-0.5,2.5], font = dict(size = 16), transition_duration=200)

        return figure



@app.callback(
    Output("download_data", "data"),
    Input("download_button", "n_clicks"),
    State("my_files", "value"),
    State("analyses", "value"),
    prevent_initial_call=True
)
def func(n_clicks, filename, analysis_type):
    if c_analysis != None:
        outname = f"{filename}_{analysis_type}.csv"
        return dcc.send_data_frame(c_analysis[-1].to_csv, outname)
    else:
        print("Detecting none")
        return None


#if __name__ == '__main__':
    #app.run_server(debug=True)

def start_gui():
    app.run_server(debug=True)
