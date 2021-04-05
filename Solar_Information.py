#Projekt:           Solar information Display
#Authoer:           Robin Rosner
#Compyright:        Robin Rosner
#E-Mail:            robinrosner@outlook.de

#Solar-Information-Display  2021 by Robin Rosner is licensed under CC BY-NC-SA 4.0

import pandas as pd                         #Import pandas for data analysis
import os                                   #Import OS for operating system interfaces
import glob                                 #Import glob for unix style pathname pattern matching
import dash                                 #Import Dash as framework for building web applications
import dash_core_components as dcc          #Import core components for core set of interactive dash components
import dash_html_components as html         #Import html components for python abstraction around HTML, CSS, and JavaScript
from dash.dependencies import Input, Output #Import Input and Output from Dash dependencies for callbacks
import plotly.express as px                 #Import plotly for creating figures
import datetime                             #Import datetime for time operations
import socket                               #Import socket for low-level networking interface operations
from pathlib import Path                    #Import pathlib for filesystem operations

if os.name == "nt":                         #if statement to check if operting system is nt (nt for Windows based operating systems)
                                            #os.name returnes the name and it has to equal "nt" to set the variable linux to False otherwise the os has to be Linux
    linux = False                           #in wich case the variable is set to True
else:
    linux = True

weekGraphLastShownAmount = 14               #creates a variable for how many of the last days should be visible in the week bar graph
                                            #here the value 14 is asigned

dir_path = os.path.dirname(os.path.realpath(__file__))                              #specify main datapath for .csv files. Currently automaticly at path of the executable
                                                                                    #creates variable dir_path and assignes the returned value from function os.path.dirname which is provided with with
                                                                                    #the current path of the .py file by os.path.realpath(___file___) which is then convertet to just the folder where the file is in
                                                                                    #e.g: D:\GithubRepos\\Solar-Information-Display\\Solar_Information.py --> D:\GithubRepos\\Solar-Information-Display

def getCurrentDataframe():                                                          #definition of funcition which automaticly creates and returnes an up to date dataframe from current days data
    list_of_files = glob.glob(dir_path + "/*.csv")                                  #defines the variable list_of_files and asignes the return of the function glob
                                                                                    #glob takes a path to a folder (here put togeter from variable dir_path and the ending /*.csv to select all .csv files)
                                                                                    #and then returnes a list of all files with that path
    latest_file = max(list_of_files, key=os.path.getctime)                          #gets the fille with tha maximum time stamp = most current file
                                                                                    #max uses here two arguments: the list of files where the latest file should be selected
                                                                                    #and a key which defines the search parameter in this the metadata change time of the files

    df = pd.read_csv(latest_file, skiprows=2, delimiter=";", index_col=False)       #reads the selected file and skips the first two rows due to header information. The delimiterchar is set to ; and it doesnt create an index for references
                                                                                    #defines a new variable which is asigned with the output of read_csv. The funcion takes multiple arguments in this
                                                                                    #case at first the file it should read from, 2. a variable of rows it should skip whil readin (here first two because they are the files header
                                                                                    #3. the delimiter by which the funcion should begin a new column and last but not least index_col which defines if the created dataframe should have indexes

    return(df)                                                                      #returns the newly read df

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]               #sets the external stylsheet for cascade stylization on the front-end = web page
                                                                                    #creates a new variable and sets the value to the given link
                                                                                    #brackets are used to identify as link
                                                                                    #the stylesheets are used for the visible appearence of the website wich is handelt through Cascading Style Sheets

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)                #creates a new dash app with the previously defined css file

                                                                                    #definition of the Html layout:
                                                                                    #as previously mentioned dash provides a full python abstraction around HTML, CSS, and JavaScript
                                                                                    #and thus there is no html writing required
                                                                                    #there is a pytho representation for each html element

app.layout = html.Div(                                                              #defining a Html Div container wich includes:
    html.Div([                                                                      #another div
       # html.H2("PV-Anlage Produktion"),                                           #a Headline (H2) -> disabled due to waste of space on website
        html.H5(id='E-Day'),                                                        #a smaller headline (H5)  -> beeing modifyed by callbacks to display energy yield of current day
        html.H5(id='E-Total'),                                                      #a smaller headline (H5)  -> beeing modifyed by callbacks to display total energy yield
        dcc.Graph(id='todayPowerGraph'),                                            #a graph for power over day -> beeing modifyed by callbacks
        dcc.Graph(id='weekPowerGraph'),                                             #a graph for power over last days -> beeing modifyed by callbacks
        dcc.Interval(                                                               #an intervall component which automaicly refreshes content of the page after 1000 miliseconds
            id='interval-component',                                                    
            interval=10*1000, # in milliseconds                                         interval: This component will increment the counter n_intervals every interval milliseconds
            n_intervals=0                                                               #n_intervals: Number of times the interval has passed                                                                             
        )
    ])                                                                              # => id: The ID of components, is used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.
)

@app.callback(Output('todayPowerGraph', 'figure'),                                  #defining a callback for the daily powergraph which is called everytime the graphs refreshes -> intervall component as trigger
              Input('interval-component', 'n_intervals'))                           #Output defines which html element the returned data is for (here todayPowerGraph) and what the data is (here a figure)
                                                                                    #Input defines which html element acts as trigger (here interval-component) and which variable actualy is the trigger (here n_intervals)
                                                                                    #triggers everytime n_intervals incremented
def update_graph_live(n):                                                           #defines the function that is called when callback is triggerd

    df = getCurrentDataframe()                                                      #calls previous funktion to get newest dataframe
                                                                                    #defines variable df (short for data frame) and stores the returnes df from getCurrentDataframe() in it

    df2 = pd.DataFrame({'Time' : [], 'Power' : []})                                 #creates a new df and assignes is a variable of type DataFrame where 2 colums are defined: Time and Power
                                                                                    
    for i in range(len(df.index)):                                                  #the for loop loops trough every element from df and increments i every time
                                                                                    #in range() defines that the loop should go on for the amount of elements given in brackets
                                                                                    #df.index returns the indexes of df and len returns the lengh of that list thus providing the amount of times the loop shall loop
        power = (                                                                   #defines a new variable and assignes it the total amount of power over all 4 photovoltaik strings
                                                                                    #df.at[i,"..."] selects a specific cell in data table
                  df.at[i,"Upv1"]*df.at[i,"Ipv1"]                                   #i therby defines the row which is equal to the current row the loop is at the moment
                 +df.at[i,"Upv2"]*df.at[i,"Ipv2"]                                   #and the second argument defines the Column which can be references by heading
                 +df.at[i,"Upv3"]*df.at[i,"Ipv3"]                                   #to calculate to current power output the function multyplies the current volltage Upv of a string with the current curent of the same string Ipv
                 +df.at[i,"Upv4"]*df.at[i,"Ipv4"]                                   #this has to be done for all strings a added together to get the total amount of power
                 )

        time = df.at[i,"#Time"]                                                     #selects with the same method the date from the current row
        time = time[11:]                                                            #stores a modified version of the same variable in it self
                                                                                    #time[11:] cuts off the first 11 characters of the time string which equals in that case the date
                                                                                    #because df.at[i,"#Time"] returns something like: 30/03/2021  17:55:00
                                                                                    #but only the time is needed
        time = time[:-3]                                                            #time[:-3] cuts off the last three character which correspond to the seconds which are unnecassary becaus the updateintervall
                                                                                    #off most Loggers is way larger than minutes
        df2 = df2.append({"Power": power, "Time": time}, ignore_index=True)         #appends the new data to df2
                                                                                    #the append() function takes at first multiple arguments in brackets as data input
                                                                                    #first the header has to be defined and then the data to append ('Power': power)
                                                                                    #once again the index is ignored (ignore_index=True)

    df2 = df2.iloc[::-1]                                                            #to flip the dataframe aroung -> first entry as last entry and vise verse because latest data point should be on right side
                                                                                    #overwrites df2 with a fliped version of itself
                                                                                    #iloc[] is a funcion for integer-location based indexing but can also be used with a slice object -> ::-1 for inversion

    fig = px.line(df2, x="Time", y="Power", line_shape="spline")                    #creates a new fig in the form of lines which are connected trough splines (smoother graph)
                                                                                    #defines new variable fig where the output of the line function from plotly is assigned
                                                                                    #the line() function returns a figure object
                                                                                    #line() takes muliple arguments -> 1. the dataframe to get the necassary data 2./3. the names of the coulums which contain to be used data
                                                                                    #4. the line shape (here type spline to give a smoother graph; could also be linear for e.g.)


    return fig                                                                      #returnes the figure

@app.callback(Output('weekPowerGraph', 'figure'),                                   #defining a callback for the weekly powergraph which is called everytime the graphs refreshes -> intervall component as trigger
              Input('interval-component', 'n_intervals'))                           #Output defines which html element the returned data is for (here weekPowerGraph) and what the data is (here a figure)
                                                                                    #Input defines which html element acts as trigger (here interval-component) and which variable actually is the trigger (here n_intervals)
                                                                                    #triggers everytime n_intervals incremented
def update_graph_live(n):                                                           #defines the function that is called when callback is triggerd

    df = getCurrentDataframe()                                                      #calls previous funktion to get newest dataframe
                                                                                    #defines variable df (short for data frame) and stores the returned df from getCurrentDataframe() in it

    eDay = df.at[0, 'E-Day']                                                        #gets the untill now produced energy from row: 0, Column: E-Day
    time =  df.at[0, "#Time"]                                                       #gets the current daytime from row: 0, Column: E-Day 
                                                                                        #.at[i, ...] and[:-i] work as previously shown
    time = time[:-9]                                                                #cuts off time and year (last 9 chars): 30/03/2021  17:55:00 -> 30/03/2021

    if linux:                                                                       #if statment: is true when variable linux is True
        outdir = dir_path + "/internal/"                                            #defines outdir variable and stores in it the dir_path and appends "/internal/" to it in order to write the daily-e.csv in seperate folder
                                                                                    #in order to avoid conflicts with the previous search function for .csv files
        if not os.path.exists(dir_path + "/internal/"):             
            os.mkdir(dir_path + "/internal")

    if Path(dir_path + "/internal/daily-e.csv").is_file():
        df2 = pd.read_csv(dir_path + "/internal/daily-e.csv", index_col=False)
    else:
        df2 = pd.DataFrame({'Time' : [], 'E-Day' : []},)
   
    if time in df2.values:                                 
        index = df2[df2["Time"]==time].index.values
        df2.at[index, "E-Day"] = eDay         
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

    return ("Today: " + str(df["E-Day"][0]) + "kWh")                                #returns the amount of energy with the prefix Today: and suffix: kWh

@app.callback(Output('E-Total', 'children'),                                        #defining a callback for the produces energy for day
              Input('interval-component', 'n_intervals'))
def update_text_live(n):                                                            #called funktion from callback
    
    df = getCurrentDataframe()                                                      #calls previous funktion to get newest dataframe

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