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

@app.callback(Output('weekPowerGraph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    df = getCurrentDataframe()
    df2 = pd.DataFrame({'Date' : [], 'Power' : []})
    df2.astype({'Date': 'string'}).dtypes

    #df2["Date"][0] = df["#Time"][0][:-3] 
    #if df2["Date"][len(df2.index)] != df["#Time"][len(df2.index)-1]:
    if not df2['Date'].str.contains(str(date.today())).any():
        #df2["Date"][int(date.today())] = df["E-Day"][0]
        df2 = df2.append({'Date': df["#Time"][len(df2.index)][:-8], 'Power': df["E-Day"][0]}, ignore_index=True)            #neeeeds lot of work  !!!!!!!!!!! :(
        print("doesnt contain")
    print(df2.head())

    #df2["Date"][df2.size] = df["E-Day"][0]

    #fig = px.bar(df2)

    fig = px.bar()
   
    return()


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