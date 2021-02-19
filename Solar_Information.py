
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import datetime

from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Atomkraftwerk Produktion'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    list_of_files = glob.glob(r"E:\Desktop\*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file + "intervals: " + str(n))

    df = pd.read_csv(latest_file, skiprows=2, delimiter=";", index_col=False)

    df2 = pd.DataFrame({'Time' : [], 'Power' : []})
    for i in range(len(df.index)):
        power = df.at[i,"Upv1"]*df.at[i,"Ipv1"]+df.at[i,"Upv2"]*df.at[i,"Ipv2"]+df.at[i,"Upv3"]*df.at[i,"Ipv3"]+df.at[i,"Upv4"]*df.at[i,"Ipv4"]
        time = df.at[i,"#Time"]
        time = time[11:]
        time = time[:-3]
        df2 = df2.append({'Power': power, 'Time': time}, ignore_index=True)

    df2 = df2.iloc[::-1]

    fig = px.line(df2, x="Time", y="Power")

    return fig

if __name__ == '__main__':
    app.run_server(debug=False)