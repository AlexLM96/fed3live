from dash import Dash, dcc, html, Input, Output, State, ctx, callback
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
data_analyses = ["Overview", "Performance", "Accuracy", "Win-stay/Lose-shift", "Reversal peh", "Logistic wins", "Logistic losses"]
#data_analyses = ["Overview", "Performance"]
c_analysis = []

dash.register_page(__name__)

layout = html.Div([
    html.H1('This is our Archive page'),
    html.Div('This is our Archive page content.'),
])

#%%

"""
layout = dbc.Container([
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
            dbc.Row(html.H4("Date Selection", style = {"textAlign": 'center','padding': 10})),
            dcc.DatePickerRange(id="date_range", start_date=datetime.datetime.today(), end_date=datetime.datetime.today(), disabled=True),
            dbc.Row(html.H4("Time Selection", style = {"textAlign": 'center','padding': 10})),
            dbc.Row(html.H5("From:",style = {"textAlign": 'center','padding': 5})),
            dcc.Dropdown(id="start_time", disabled=True),
            dbc.Row(html.H5("To:",style = {"textAlign": 'center','padding': 5})),
            dcc.Dropdown(id="end_time", disabled=True)
        ],width=2),
        dbc.Col([
            dbc.Row([dcc.Graph(id="s_actions")])
        ]),
        dbc.Col([
            dbc.Row(dbc.Button("Download Graph Data", id="download_button", outline=True, color="primary", size="lg", className="me-1")),
            dcc.Download(id="download_data"),
            html.Br(),
            dbc.Row(html.H4("Individual Analysis", style = {"textAlign": 'center'})),
            dbc.Row(dbc.Button('Run', outline=False, color="primary", className="me-1", id="individual_run")),
            html.Br(),
            dbc.Row(html.H4("Group Analysis", style = {"textAlign": 'center'})),
            dcc.Checklist([" Group Analysis"], id="group_analysis", value=[]),
            dbc.Row(html.H5("Group 1", style = {"textAlign": 'center','padding': 10})),
            dcc.Dropdown([], id="group 1", disabled=True, multi=True),
            dbc.Row(html.H5("Group 2", style = {"textAlign": 'center','padding': 15})),
            dcc.Dropdown([], id="group 2", disabled=True, multi=True),
            html.Br(),
            dbc.Row(dbc.Button('Run', outline=False, color="primary", className="me-1", disabled=True, id="group_run")),
            html.Br(),
            dbc.Row(dbc.Button("Download File Summary", id="summary_button", outline=True, color="primary", size="lg", className="me-1")),
            dcc.Download(id="download_summary")
        ],width=2)
    ])

])

@callback(
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

@callback(
        Output("group 1", "options"),
        Output("group 2", "options"),
        Input("my_files", "options"),
        prevent_initial_call=True
)

def update_group_options(filenames):
    return filenames, filenames

@callback(
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
    

@callback(
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
            if latest_start > earliest_end:
                start_date = (datetime.datetime.today() + datetime.timedelta(days=1)).date()
                end_date = (datetime.datetime.today() + datetime.timedelta(days=1)).date()
                return start_date, end_date, start_date, end_date, True

            return latest_start, earliest_end, latest_start, earliest_end, False

        else:
            start_date = datetime.datetime.today()
            end_date = datetime.datetime.today()

            return start_date, end_date, start_date, end_date, True
        
    
@callback(
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
        
    elif group_check == [' Group Analysis']:
        if (group1 != None) and (group2 != None):
            
            dt_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            dt_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

            if (dt_start_date > datetime.datetime.today().date()) or (dt_end_date > datetime.datetime.today().date()):
                return [0],[0], True, True, 0, 0

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
            return [0],[0], True, True, 0, 0



@callback(
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
        State("group_analysis", "value"),
        prevent_initial_call = True
)
def update_graph(i_clicks, g_clicks, analysis_type, start_date, end_date, start_time, end_time, file, group1, group2, group_check):
    global c_analysis
    
    start_datetime = datetime.datetime.strptime(start_date+" "+str(start_time), "%Y-%m-%d %H")
    end_datetime = datetime.datetime.strptime(end_date+" "+str(end_time), "%Y-%m-%d %H")
    if g_clicks and group_check == [' Group Analysis']:
        #print("Group click")
        figure_g = go.Figure()
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
                    all_ws_g1 = {mouse: f3b.win_stay(g1_slices[mouse]) for mouse in g1_slices}
                    all_ws_g2 = {mouse: f3b.win_stay(g2_slices[mouse]) for mouse in g2_slices}
                    all_ls_g1 = {mouse: f3b.lose_shift(g1_slices[mouse]) for mouse in g1_slices}
                    all_ls_g2 = {mouse: f3b.lose_shift(g1_slices[mouse]) for mouse in g1_slices}
                    
                    x_ws = ["win-stay"]
                    x_ls = ["lose-shift"]

                    figure_g.add_trace(go.Box(x=x_ws*len(list(all_ws_g1.keys())), y= list(all_ws_g1.values()), name="Group 1"))
                    figure_g.add_trace(go.Box(x=x_ws*len(list(all_ws_g2.keys())), y= list(all_ws_g2.values()), name="Group 2"))
                    figure_g.add_trace(go.Box(x=x_ls*len(list(all_ls_g1.keys())), y= list(all_ls_g2.values()), name="Group 1"))
                    figure_g.add_trace(go.Box(x=x_ls*len(list(all_ls_g1.keys())), y= list(all_ls_g2.values()), name="Group 2"))
                    figure_g.update_layout(title = {'text': "Mouse Win-Stay/Lose-Shift ", 'x': 0.5}, boxmode="group", yaxis_title = "Proportion", font = dict(size = 16), yaxis_range = [0,1],xaxis= dict(tickvals = [0,1], ticktext = ["Win-Stay", "Lose-Shift"]), transition_duration=200)

                
                elif analysis_type == "Reversal peh":
                    rpeh_g1 = {mouse: f3b.reversal_peh(g1_slices[mouse], (-10,11)).mean(axis=0) for mouse in g1_slices}
                    rpeh_g2 = {mouse: f3b.reversal_peh(g2_slices[mouse], (-10,11)).mean(axis=0) for mouse in g2_slices}

                    a_rpeh_g1 = np.vstack(list(rpeh_g1.values()))
                    g1_mean = a_rpeh_g1.mean(axis=0)
                    g1_std = a_rpeh_g1.std(axis=0)
                    g1_upper = g1_mean + g1_std
                    g1_lower = g1_mean - g1_std

                    a_rpeh_g2 = np.vstack(list(rpeh_g2.values()))
                    g2_mean = a_rpeh_g2.mean(axis=0)
                    g2_std = a_rpeh_g2.std(axis=0)
                    g2_upper = g2_mean + g2_std
                    g2_lower = g2_mean - g2_std

                    c_analysis.append(pd.DataFrame({"Trial from reversal": np.arange(-10,11), 
                                                    "Group1 mean": g1_mean,
                                                    "Group1 std": g1_std,
                                                    "Group2 mean": g2_mean,
                                                    "Group2 std": g2_std}))
                    
                    figure_g.add_trace(go.Scatter(x=np.arange(-10,11),y=g1_mean, mode='lines'))
                    figure_g.add_trace(go.Scatter(x=np.arange(-10,11),y=g2_mean, mode='lines'))
                    figure_g.update_layout(title = {'text': "Reversal PEH", 'x': 0.5}, xaxis_title = "Trial", yaxis_title = "P(High)", yaxis_range=[0,1], font = dict(size = 16), transition_duration=200)

                elif analysis_type == "Logistic wins":
                    g1_sidep_rew = {mouse: f3b.side_prewards(g1_slices[mouse]) for mouse in g1_slices}
                    g1_preX = {mouse: f3b.create_X(g1_slices[mouse], g1_sidep_rew[mouse],5) for mouse in g1_slices}
                    g1_plogreg = {mouse: f3b.logit_regr(g1_preX[mouse]) for mouse in g1_sidep_rew}
                    g1_params = {mouse: g1_plogreg[mouse].params for mouse in g1_plogreg}
                    
                    a_g1_params = np.vstack(list(g1_params.values()))
                    g1_params_mean = a_g1_params.mean(axis=0)
                    g1_params_std = a_g1_params.std(axis=0)

                    g2_sidep_rew = {mouse: f3b.side_prewards(g2_slices[mouse]) for mouse in g2_slices}
                    g2_preX = {mouse: f3b.create_X(g2_slices[mouse], g2_sidep_rew[mouse],5) for mouse in g2_slices}
                    g2_plogreg = {mouse: f3b.logit_regr(g2_preX[mouse]) for mouse in g2_sidep_rew}
                    g2_params = {mouse: g2_plogreg[mouse].params for mouse in g2_plogreg}
                    
                    a_g2_params = np.vstack(list(g2_params.values()))
                    g2_params_mean = a_g2_params.mean(axis=0)
                    g2_params_std = a_g2_params.std(axis=0)

                    c_analysis.append(pd.DataFrame({"Trial in past": np.arange(-5,0), 
                                "Group1 mean": g1_params_mean,
                                "Group1 std": g1_params_std,
                                "Group2 mean": g2_params_mean,
                                "Group2 std": g2_params_std}))

                    figure_g.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=g1_params_mean))
                    figure_g.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=g2_params_mean))
                    figure_g.update_layout(title = {'text': "Logistic wins", 'x': 0.5}, xaxis={"title": "Trial in past", "tickvals": np.flip(np.arange(-5,0))}, yaxis_title = "Regr. Coeff", font = dict(size = 16), transition_duration=200)

                elif analysis_type == "Logistic losses":
                    g1_siden_rew = {mouse: f3b.side_nrewards(g1_slices[mouse]) for mouse in g1_slices}
                    g1_npreX = {mouse: f3b.create_X(g1_slices[mouse], g1_siden_rew[mouse], 5) for mouse in g1_slices}
                    g1_nlogreg = {mouse: f3b.logit_regr(g1_npreX[mouse]) for mouse in g1_siden_rew}
                    g1_nparams = {mouse: g1_nlogreg[mouse].params for mouse in g1_nlogreg}
                    
                    a_g1_nparams = np.vstack(list(g1_nparams.values()))
                    g1_nparams_mean = a_g1_nparams.mean(axis=0)
                    g1_nparams_std = a_g1_nparams.std(axis=0)

                    g2_siden_rew = {mouse: f3b.side_nrewards(g2_slices[mouse]) for mouse in g2_slices}
                    g2_npreX = {mouse: f3b.create_X(g2_slices[mouse], g2_siden_rew[mouse], 5) for mouse in g2_slices}
                    g2_nlogreg = {mouse: f3b.logit_regr(g2_npreX[mouse]) for mouse in g2_siden_rew}
                    g2_nparams = {mouse: g2_nlogreg[mouse].params for mouse in g2_nlogreg}
                    
                    a_g2_nparams = np.vstack(list(g2_nparams.values()))
                    g2_nparams_mean = a_g2_nparams.mean(axis=0)
                    g2_nparams_std = a_g2_nparams.std(axis=0)

                    c_analysis.append(pd.DataFrame({"Trial in past": np.arange(-5,0), 
                                "Group1 mean": g1_nparams_mean,
                                "Group1 std": g1_nparams_std,
                                "Group2 mean": g2_nparams_mean,
                                "Group2 std": g2_nparams_std}))

                    figure_g.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=g1_nparams_mean))
                    figure_g.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=g2_nparams_mean))
                    figure_g.update_layout(title = {'text': "Logistic wins", 'x': 0.5}, xaxis={"title": "Trial in past", "tickvals": np.flip(np.arange(-5,0))}, yaxis_title = "Regr. Coeff", font = dict(size = 16), transition_duration=200)

                elif analysis_type == "Accuracy":
                    accuracy_g1 = {mouse: f3b.accuracy(g1_slices[mouse]) for mouse in g1_slices}
                    accuracy_g2 = {mouse: f3b.accuracy(g2_slices[mouse]) for mouse in g2_slices}
                    
                    x_ws = [""]

                    figure_g.add_trace(go.Box(x=[0]*len(list(accuracy_g1.keys())), y= list(accuracy_g1.values()), name="Group 1", width=0.4))
                    figure_g.add_trace(go.Box(x=[0.6]*len(list(accuracy_g2.keys())), y= list(accuracy_g2.values()), name="Group 2", width=0.4))
                    figure_g.update_layout(title = {'text': "Accuracy ", 'x': 0.5}, boxmode="group", yaxis_title = "Proportion", font = dict(size = 16), yaxis_range = [0,1],xaxis= dict(tickvals = [0,1], ticktext = ["", ""]), transition_duration=200)                    
                    pass


        return figure_g

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

                
            elif analysis_type == "Win-stay/Lose-shift":
                
                c_ws = f3b.win_stay(c_slice)
                c_ls = f3b.lose_shift(c_slice)
                c_analysis.append(pd.DataFrame({"Win-stay": [c_ws], "Lose-shift": [c_ls]}))

                figure_i.add_trace(go.Bar(x=[0,1], y= [c_ws, c_ls]))
                figure_i.update_layout(title = {'text': "Mouse Win-Stay/Lose-Shift ", 'x': 0.5}, yaxis_title = "Proportion", font = dict(size = 16), yaxis_range = [0,1],
                                xaxis= dict(tickvals = [0,1], ticktext = ["Win-Stay", "Lose-Shift"]), transition_duration=200)
            
            elif analysis_type == "Reversal peh":
                c_rev_peh = f3b.reversal_peh(c_slice, (-10,11)).mean(axis=0)
                c_analysis.append(pd.DataFrame({"Trial from reversal": np.arange(-10,11), "P(High)": c_rev_peh}))

                figure_i.add_trace(go.Scatter(x=np.arange(-10,11),y=c_rev_peh, mode='lines', showlegend = False))
                figure_i.update_layout(title = {'text': "Reversal PEH", 'x': 0.5}, xaxis_title = "Trial", yaxis_title = "P(High)", yaxis_range=[0,1], font = dict(size = 16), transition_duration=200)
            
            elif analysis_type == "Logistic wins":
                c_sidep_rew = f3b.side_prewards(c_slice)
                c_preX = f3b.create_X(c_slice, c_sidep_rew, 5)
                c_plogreg = f3b.logit_regr(c_preX)
                c_pcoeffs = c_plogreg.params
                c_analysis.append(pd.DataFrame({"Trial in past": np.flip(np.arange(-5,0)), "Regr. Coeffs.": c_pcoeffs}))
                y_min = np.min(c_pcoeffs)
                y_max = np.max(c_pcoeffs)

                figure_i.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_pcoeffs))
                figure_i.update_layout(title = {'text': "Logistic wins", 'x': 0.5}, xaxis={"title": "Trial in past", "tickvals": np.flip(np.arange(-5,0))}, yaxis_title = "Regr. Coeff", yaxis_range=[y_min-0.5,y_max+0.5], font = dict(size = 16), transition_duration=200)

            elif analysis_type == "Logistic losses":
                c_siden_rew = f3b.side_nrewards(c_slice)
                c_npreX = f3b.create_X(c_slice, c_siden_rew, 5)
                c_nlogreg = f3b.logit_regr(c_npreX)
                c_ncoeffs = c_nlogreg.params
                c_analysis.append(pd.DataFrame({"Trial in past": np.flip(np.arange(-5,0)), "Regr. Coeffs.": c_ncoeffs}))
                y_min = np.min(c_ncoeffs)
                y_max = np.max(c_ncoeffs)

                figure_i.add_trace(go.Scatter(x=np.flip(np.arange(-5,0)),y=c_ncoeffs))
                figure_i.update_layout(title = {'text': "Logistic losses", 'x': 0.5}, xaxis={"title": "Trial in past", "tickvals": np.flip(np.arange(-5,0))}, yaxis_title = "Regr. Coeff", yaxis_range=[y_min-0.5,y_max+0.5], font = dict(size = 16), transition_duration=200)

            elif analysis_type == "Accuracy":
                c_accuracy = f3b.accuracy(c_slice)
                figure_i.add_trace(go.Bar(x=[0], y= [c_accuracy], width=0.4))
                figure_i.update_layout(title = {'text': "Accuracy ", 'x': 0.5}, yaxis_title = "Accuracy", font = dict(size = 16), yaxis_range = [0,1],
                xaxis= dict(tickvals = [0], ticktext = [""]), transition_duration=200)

        return figure_i



@callback(
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

@callback(
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

"""