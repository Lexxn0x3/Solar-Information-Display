import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import datetime
from datetime import date
import socket
from pathlib import Path

from dash.dependencies import Input, Output

dir_path = os.path.dirname(os.path.realpath(__file__))

def getCurrentDataframe():
    #If windows
    list_of_files = glob.glob(dir_path + "/*.csv")
    #If linux
    #list_of_files = glob.glob(dir_path + "/*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    #print(latest_file + "intervals: " + str(n))

    df = pd.read_csv(latest_file, skiprows=2, delimiter=";", index_col=False)

    return(df)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H2("PV-Anlage Produktion"),
        html.H4(id='E-Day'),
        html.H4(id='E-Total'),
        dcc.Graph(id='todayPowerGraph'),
        dcc.Graph(id='weekPowerGraph'),
        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('todayPowerGraph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    df = getCurrentDataframe()

    df2 = pd.DataFrame({'Time' : [], 'Power' : []})
    for i in range(len(df.index)):
        power = df.at[i,"Upv1"]*df.at[i,"Ipv1"]+df.at[i,"Upv2"]*df.at[i,"Ipv2"]+df.at[i,"Upv3"]*df.at[i,"Ipv3"]+df.at[i,"Upv4"]*df.at[i,"Ipv4"]
        time = df.at[i,"#Time"]
        time = time[11:]
        time = time[:-3]
        df2 = df2.append({'Power': power, 'Time': time}, ignore_index=True)

    df2 = df2.iloc[::-1]

    fig = px.line(df2, x="Time", y="Power", line_shape="spline")

    return fig

@app.callback(Output('weekPowerGraph', 'figure'),                   # week Powergraph
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    df = getCurrentDataframe()

    eDay = df.at[0, 'E-Day']
    time =  df.at[0, "#Time"]
    time = time[:-9]

    try:
        df2 = pd.read_csv("internal\daily-e.csv", index_col=False)
    except IOError:
        df2 = pd.DataFrame({'Time' : [], 'E-Day' : []})



    if time in df2.values:                                  #will overwrite after on year              and doesnt work :(
        index = df2[df2["Time"]==time].index.values
        df2.at[index, "E-Day"] = eDay          #I dunno stupid              needs to replace previous value                maybe set time as index
        df2.to_csv(r"internal\daily-e.csv")
    else:
        df2 = df2.append({'E-Day': eDay, 'Time' : time}, ignore_index=True)
        df2.to_csv(r"internal\daily-e.csv")
    
    fig = px.bar(df2, x="Time", y="E-Day")
   
    return fig


@app.callback(Output('E-Day', 'children'),
              Input('interval-component', 'n_intervals'))
def update_text_live(n):
    
    df = getCurrentDataframe()
    #print(df["E-Day"][0])

    return ("Today: " + str(df["E-Day"][0]) + "kWh")

@app.callback(Output('E-Total', 'children'),
              Input('interval-component', 'n_intervals'))
def update_text_live(n):
    
    df = getCurrentDataframe()
    #print(df["E-Day"][0])

    return ("Total: " + str(round(df["E-Total"][0]/1000, 2)) + "MWh")


if __name__ == '__main__':
    app.run_server(
        port="8050",
        host=str(socket.gethostbyname(socket.gethostname()))
        #host="10.18.40.200"
        )

#if __name__ == '__main__':
#    app.run_server(debug=True)