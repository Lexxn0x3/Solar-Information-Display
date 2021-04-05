#Projekt:           Solar information Display
#Authoer:           Robin Rosner
#Compyright:        Robin Rosner
#E-Mail:            robinrosner@outlook.de

#Solar-Information-Display  2021 by Robin Rosner is licensed under CC BY-NC-SA 4.0

import pandas as pd                         #Import panda library for dataframe operations
import os                                   #Import OS for os spcific operations e.g. IO
import glob                                 #Import glob for directory and file opterations 
#import matplotlib.pyplot as plt             #Import matplotlib for graphical visulizations
import dash                                 #Import Dash. Main component for providing web services and generation Html file and server
import dash_core_components as dcc          #Dash core essentials
import dash_html_components as html         #Dash HTML elements
import plotly.express as px                 
import datetime                             #Import datetime for time operations
from datetime import date
import socket
from pathlib import Path

if os.name == 'nt':
    linux = False
else:
    linux = True

weekGraphLastShownAmount = 14

from dash.dependencies import Input, Output

dir_path = os.path.dirname(os.path.realpath(__file__))                              #specify main datapath for .csv files. Currently automaticly at path of the executable

def getCurrentDataframe():                                                          #definition of funcition wich automaticly creates and returnes an uptodate dataframe from current days data
    #If windows
    list_of_files = glob.glob(dir_path + "/*.csv")
    #If linux
    #list_of_files = glob.glob(dir_path + "/*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)                          #gets the fille with tha maximum time stamp = most current file
    #print(latest_file + "intervals: " + str(n))

    df = pd.read_csv(latest_file, skiprows=2, delimiter=";", index_col=False)       #reads the selected file and skips the first two rows due to header information. The delimiterchar is set to ; and it doesnt create an index for references

    return(df)                                                                      #returns the newly read df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']               #sets the external stylsheet for cascade stylization on the front-end = web page

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)                #creates a new dash app
                                                                                    #Definition of the Html lyout
app.layout = html.Div(                                                              #defining a Html Div container wich includes:
    html.Div([                                                                      #another div
       # html.H2("PV-Anlage Produktion"),                                            #a Headline (H2)
        html.H5(id='E-Day'),                                                        #a smaller headline (H4)
        html.H5(id='E-Total'),                                                      #a smaller headline (H4)
        dcc.Graph(id='todayPowerGraph'),                                            #a graph for power over day
        dcc.Graph(id='weekPowerGraph'),                                             #a graph for power over last days
        dcc.Interval(                                                               #a intervall component wich automaicly refreshes content of the page after 1000 miliseconds
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('todayPowerGraph', 'figure'),                                  #defining a callback for the daly powergraph wich is called everytime the graphs refreshes = intervall component as trigger
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):                                                           #called funktion from callback

    df = getCurrentDataframe()                                                      #calls previous funktion to get newest dataframe

    df2 = pd.DataFrame({'Time' : [], 'Power' : []})                                 #creates a new df with coloums Time and Power
    for i in range(len(df.index)):                                                  #loops trough every element of df
        power = df.at[i,"Upv1"]*df.at[i,"Ipv1"]+df.at[i,"Upv2"]*df.at[i,"Ipv2"]+df.at[i,"Upv3"]*df.at[i,"Ipv3"]+df.at[i,"Upv4"]*df.at[i,"Ipv4"]  # calculates the poweroutput for given row from loop
        time = df.at[i,"#Time"]                                                     #gets time from current row
        time = time[11:]                                                            #get rid of unnecassary information
        time = time[:-3]
        df2 = df2.append({'Power': power, 'Time': time}, ignore_index=True)         #appends new data (power, time) to df2

    df2 = df2.iloc[::-1]                                                            #i dunno

    fig = px.line(df2, x="Time", y="Power", line_shape="spline")                    #creates a new fig in the form of lines wich are connected trough splines (smoother graph)


    return fig                                                                      #returnes the fig

@app.callback(Output('weekPowerGraph', 'figure'),                                   #defining a callback for the wekly powergraph wich is called everytime the graphs refreshes = intervall component as trigger
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):                                                           #called funktion from callback

    df = getCurrentDataframe()                                                      #calls previous funktion to get newest dataframe

    eDay = df.at[0, 'E-Day']                                                        #gets the untill now produced energy from row: 0, Column: E-Day 
    time =  df.at[0, "#Time"]                                                       #gets the current daytime from row: 0, Column: E-Day 
    time = time[:-9]                                                                #cuts off time and year -> dd/mm

    if linux:
        outdir = dir_path + "/internal/"
        if not os.path.exists(dir_path + "/internal/"):
            os.mkdir(dir_path + "/internal")

    if Path(dir_path + "/internal/daily-e.csv").is_file():
        df2 = pd.read_csv(dir_path + "/internal/daily-e.csv", index_col=False)
    else:
        df2 = pd.DataFrame({'Time' : [], 'E-Day' : []},)

    #try:                                                                            #trys the following due to the possiblity that file my not exsist
    #    df2 = pd.read_csv("internal\daily-e.csv", index_col=False)                  #trys to read daily-e.csv and converting it to df
    #except IOError:                                                                 #if an IOError is thrown code will continue and
    #    df2 = pd.DataFrame({'Time' : [], 'E-Day' : []})                             #and create a new empty df with Tiem and E-Day colums

    ##df2["Date"][df2.size] = df["E-Day"][0]

    ##fig = px.bar(df2)

    #fig = px.bar()
   
    if time in df2.values:                                  #will overwrite after on year              and doesnt work :(
        index = df2[df2["Time"]==time].index.values
        df2.at[index, "E-Day"] = eDay          #I dunno stupid              needs to replace previous value                maybe set time as index
        df2.to_csv(dir_path + "/internal/daily-e.csv")
    else:
        df2 = df2.append({'E-Day': eDay, 'Time' : time}, ignore_index=True)
        df2.to_csv(dir_path + "/internal/daily-e.csv")
    
    df2 = df2.tail(weekGraphLastShownAmount)

    fig = px.bar(df2, x="Time", y="E-Day")
   
    return fig


@app.callback(Output('E-Day', 'children'),                                          #defining a callback for the produces energy for day
              Input('interval-component', 'n_intervals'))
def update_text_live(n):                                                            #called funktion from callback
    
    df = getCurrentDataframe()                                                      #calls previous funktion to get newest dataframe
    #print(df["E-Day"][0])

    return ("Today: " + str(df["E-Day"][0]) + "kWh")                                #returns the amount of energy with the prefix Today: and suffix: kWh

@app.callback(Output('E-Total', 'children'),                                        #defining a callback for the produces energy for day
              Input('interval-component', 'n_intervals'))
def update_text_live(n):                                                            #called funktion from callback
    
    df = getCurrentDataframe()                                                      #calls previous funktion to get newest dataframe
    #print(df["E-Day"][0])

    return ("Total: " + str(round(df["E-Total"][0]/1000, 2)) + "MWh")               #returns the Total amount of energy with the prefix Today: and suffix: kWh


if __name__ == '__main__':                                                          #check if name = name
    if linux:
        app.run_server(                                                                 #calls funktion to start werbserver
            port="8050",                                                                #defines the web port to 8050.  Standart http port  = 8080
            host="10.18.40.200"                                                         #manually sets ip addr for linux production enviroment
            )
    else:
        app.run_server(                                                                 #calls funktion to start werbserver
            port="8050",                                                                #defines the web port to 8050.  Standart http port  = 8080
            host=str(socket.gethostbyname(socket.gethostname()))                        #sets the ipaddr for win machines by getting curr ipaddr of machiiine
            )