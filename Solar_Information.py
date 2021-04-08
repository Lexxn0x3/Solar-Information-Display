#Projekt:           Solar information Display
#Authoer:           Robin Rosner
#Compyright:        Robin Rosner
#E-Mail:            robinrosner@outlook.de

#Solar-Information-Display  2021 by Robin Rosner is licensed under CC BY-NC-SA 4.0

import pandas as pd                         #Import pandas for data analysis
import os                                   #Import OS for operating system interfaces
import glob                                 #Import glob for Unix style pathname pattern matching
import dash                                 #Import Dash as a framework for building web applications
import dash_core_components as dcc          #Import core components for the core set of interactive dash components
import dash_html_components as html         #Import Html components for python abstraction around HTML, CSS, and JavaScript
from dash.dependencies import Input, Output #Import Input and Output from Dash dependencies for callbacks
import plotly.express as px                 #Import plotly for creating figures
import datetime                             #Import datetime for time operations
import socket                               #Import socket for low-level networking interface operations
from pathlib import Path                    #Import pathlib for filesystem operations

if os.name == "nt":                         #if statement to check if the operating system is nt (nt for Windows-based operating systems)
                                            #os.name returns the name and it has to equal "nt" to set the variable linux to False otherwise the os has to be Linux
    linux = False                           #in which case the variable is set to True
else:
    linux = True

weekGraphLastShownAmount = 14               #creates a variable for how many of the last days should be visible in the week bar graph
                                            #here the value 14 is assigned

dir_path = os.path.dirname(os.path.realpath(__file__))                              #specify main datapath for .csv files. Currently automatically at the path of the executable
                                                                                    #creates variable dir_path and assigns the returned value from function os.path.dirname which is provided with
                                                                                    #the current path of the .py file by os.path.realpath(___file___) which is then converted to just the folder where the file is in
                                                                                    #e.g: D:\GithubRepos\\Solar-Information-Display\\Solar_Information.py --> D:\GithubRepos\\Solar-Information-Display

def getCurrentDataframe():                                                          #definition of function which automatically creates and returns an up to date data frame from current days data
    list_of_files = glob.glob(dir_path + "/*.csv")                                  #defines the variable list_of_files and assigns the return of the function glob
                                                                                    #glob takes a path to a folder (here put together from variable dir_path and the ending /*.csv to select all .csv files)
                                                                                    #and then returns a list of all files with that path
    latest_file = max(list_of_files, key=os.path.getctime)                          #gets the file with the maximum timestamp = most current file     
                                                                                    #max uses here two arguments: the list of files where the latest file should be selected
                                                                                    #and a key which defines the search parameter in this the metadata change time of the files

    df = pd.read_csv(latest_file, skiprows=2, delimiter=";", index_col=False)       #reads the selected file and skips the first two rows due to header information. The delimiter character is set to ";" and it doesn't create an index for references
                                                                                    #defines a new variable that is assigned with the output of read_csv. The function takes multiple arguments in this case
                                                                                    #at first the file it should read from, 2. a variable of rows it should skip while reading (here first two because they are the header of the file
                                                                                    #3. the delimiter by which the function should begin a new column and last but not least index_col which defines if the created data frame should have indexes

    return(df)                                                                      #returns the newly read df

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]               #sets the external stylesheet for cascade stylization on the front-end = web page
                                                                                    #creates a new variable and sets the value to the given link
                                                                                    #brackets are used to identify as link
                                                                                    #the stylesheets are used for the visible appearance of the website which is handled through Cascading Style Sheets

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)                #creates a new dash app with the previously defined CSS file

                                                                                    #definition of the Html layout:
                                                                                    #as previously mentioned dash provides a full python abstraction around HTML, CSS, and JavaScript
                                                                                    #and thus there is no Html writing required
                                                                                    #there is a Python representation for each Html element

app.layout = html.Div(                                                              #defining an Html Div container which includes:
    html.Div([                                                                      #another div
       # html.H2("PV-Anlage Produktion"),                                           #a Headline (H2) -> disabled due to waste of space on the website
        html.H5(id='E-Day'),                                                        #a smaller headline (H5)  -> being modified by callbacks to display energy yield of current day
        html.H5(id='E-Total'),                                                      #a smaller headline (H5)  -> being modified by callbacks to display total energy yield
        dcc.Graph(id='todayPowerGraph', config={'displayModeBar': False}),          #a graph for power over day -> being modified by callbacks
        dcc.Graph(id='weekPowerGraph', config={'displayModeBar': False}),           #a graph for power over last days -> being modified by callbacks
        dcc.Interval(                                                               #an interval component that automatically refreshes the content of the page after 1000 milliseconds
            id='interval-component',                                                    
            interval=10*1000,                                                           #interval: This component will increment the counter n_intervals every interval milliseconds
            n_intervals=0                                                               #n_intervals: Number of times the interval has passed   
                                                                                        #the config displayModeBar is set to false to hide the graphical control panels above graphs
        )
    ])                                                                                  # => id: The ID of components, is used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.
)

@app.callback(Output('todayPowerGraph', 'figure'),                                  #defining a callback for the daily power graph which is called every time the graphs refreshes -> interval component as the trigger
              Input('interval-component', 'n_intervals'))                           #Output defines which Html element the returned data is for (here todayPowerGraph) and what the data is (here a figure)
                                                                                    #Input defines which Html element acts as the trigger (here interval-component) and which variable is the trigger (here n_intervals)
                                                                                    #triggers every time n_intervals incremented
def update_graph_live(n):                                                           #defines the function that is called when the callback is triggered

    df = getCurrentDataframe()                                                      #calls the previous function to get the newest data frame
                                                                                    #defines variable df (short for data frame) and stores the returned df from getCurrentDataframe() in it

    df2 = pd.DataFrame({'Time' : [], 'Power' : []})                                 #creates a new df and assigns is a variable of type DataFrame where 2 columns are defined: Time and Power
                                                                                    
    for i in range(len(df.index)):                                                  #the for loop loops through every element from df and increments i every time
                                                                                    #in range() defines that the loop should go on for the number of elements given in brackets
                                                                                    #df.index returns the indexes of df and len returns the length of that list thus providing the number of times the loop shall lo
        power = (                                                                   #defines a new variable and assigns it the total amount of power over all 4 photovoltaic strings
                                                                                    #df.at[i,"..."] selects a specific cell in data table
                  df.at[i,"Upv1"]*df.at[i,"Ipv1"]                                   #i thereby defines the row which is equal to the current row the loop is at the moment
                 +df.at[i,"Upv2"]*df.at[i,"Ipv2"]                                   #and the second argument defines the Column which can be referenced by heading
                 +df.at[i,"Upv3"]*df.at[i,"Ipv3"]                                   #to current power output the function multiplies the current-voltage Upv of a string with the current current of the same string Ipv
                 +df.at[i,"Upv4"]*df.at[i,"Ipv4"]                                   #this has to be done for all strings a added together to get the total amount of power
                 )

        time = df.at[i,"#Time"]                                                     #selects with the same method the date from the current row
        time = time[11:]                                                            #stores a modified version of the same variable in itself
                                                                                    #time[11:] cuts off the first 11 characters of the time string which equals in that case the date
                                                                                    #because df.at[i,"#Time"] returns something like: 30/03/2021  17:55:00
                                                                                    #but only the time is needed
        time = time[:-3]                                                            #time[:-3] cuts off the last three characters which correspond to the seconds which are unnecessary because the update interval
                                                                                    #off most Loggers is way larger than minutes
        df2 = df2.append({"Power": power, "Time": time}, ignore_index=True)         #appends the new data to df2
                                                                                    #the append() function takes at first multiple arguments in brackets as data input
                                                                                    #first, the header has to be defined and then the data to append ('Power': power)
                                                                                    #once again the index is ignored (ignore_index=True)

    df2 = df2.iloc[::-1]                                                            #to flip the data frame around -> first entry as last entry and vise verse because latest data point should be on right side
                                                                                    #overwrites df2 with a flipped version of itself
                                                                                    #iloc[] is a function for integer-location based indexing but can also be used with a slice object -> ::-1 for inversion

    fig = px.line(df2, x="Time", y="Power", line_shape="spline")                    #creates a new fig in the form of lines that are connected through splines (smoother graph)
                                                                                    #defines new variable fig where the output of the line function from plotly is assigned
                                                                                    #the line() function returns a figure object
                                                                                    #line() takes multiple arguments -> 1. the data frame to get the necessary data 2./3. the names of the columns which contain to be used data
                                                                                    #4. the line shape (here type spline to give a smoother graph; could also be linear for e.g.)


    return fig                                                                      #returns the figure

@app.callback(Output('weekPowerGraph', 'figure'),                                   #defining a callback for the weekly power graph which is called every time the graphs refreshes -> interval component as the trigger
              Input('interval-component', 'n_intervals'))                           #Output defines which Html element the returned data is for (here weekPowerGraph) and what the data is (here a figure)
                                                                                    #Input defines which Html element acts as the trigger (here interval-component) and which variable is the trigger (here n_intervals)
                                                                                    #triggers every time n_intervals incremented
def update_graph_live(n):                                                           #defines the function that is called when the callback is triggered

    df = getCurrentDataframe()                                                      #calls the previous function to get the newest data frame
                                                                                    #defines variable df (short for data frame) and stores the returned df from getCurrentDataframe() in it

    eDay = df.at[0, 'E-Day']                                                        #gets the untill now produced energy from row: 0, Column: E-Day
    time =  df.at[0, "#Time"]                                                       #gets the current daytime from row: 0, Column: E-Day 
                                                                                    #.at[i, ...] and[:-i] work as previously shown
    time = time[:-9]                                                                #cuts off time and year (last 9 chars): 30/03/2021  17:55:00 -> 30/03/2021

    if linux:                                                                       #if statement is true when variable linux is True
        outdir = dir_path + "/internal/"                                            #defines the output directory variable and stores in it the dir_path and appends "/internal/" to it to write the daily-e.csv in a separate folder
                                                                                    #to avoid conflicts with the previous search function for .csv files
        if not os.path.exists(dir_path + "/internal/"):                             #os.path.exists checks if provided path exists and returns a boolean accordingly
            os.mkdir(dir_path + "/internal")                                        #if the path is not yet existing os.mkdir (mkdr = make directory) creates the directory

    try:                                                                            #a try statement tries to execute the following code but continues with the code in case of failure
        df2 = pd.read_csv(dir_path + "/internal/daily-e.csv", index_col=False)      #it tries to read the daily-e.csv file into a variable which could fail due to corruption or the fact that the file does not exist yet
        os.remove(dir_path + "/internal/daily-e.csv")                               #after that it ryes to delete the old file so a new file can be written more easily in a bit
    except:                                                                         #in case the upper code fails the body of the except statement is executed
        df2 = pd.DataFrame({'Time' : [], 'E-Day' : []},)                            #in a case of failure, the variable df2 is defined too but now without any data just with the necessary column titles
   
    if time in df2.values:                                                          #the statement checks if the previously read date from the current data frame is already existing in the daily-e file
        index = df2[df2["Time"]==time].index.values                                 #if so the index of the row the date was found in is assigned to a variable
        df2.at[index, "E-Day"] = eDay                                               #now the energy value in the data frame is overwritten with the previously received index
    else:               
        df2 = df2.append({'E-Day': eDay, 'Time' : time}, ignore_index=True)         #in case the date did not exist till now, it will simply append the data to the current data frame
                                                                                            #=> new day begun
        
    df2 = df2.tail(weekGraphLastShownAmount)                                        #to save memory, screenspace and decrease the possibility of reading errors df2 is shortened to the last few days (14)
                                                                                    #the function tail returns in brackets specified amount of last data entries of a data frame

    df2.to_csv(dir_path + "/internal/daily-e.csv")                                  #after all that the new and up to date df2 is saved as daily-e.csv again to get overwritten with the next update again

    fig = px.bar(df2, x="Time", y="E-Day")                                          #creates a new fig in the form of bars
                                                                                    #defines new variable fig where the output of the line function from plotly is assigned
                                                                                    #the bar() function returns a figure object
                                                                                    #bar() takes multiple arguments -> 1. the data frame to get the necessary data 2./3. the names of the columns which contain to be used data
   
    return fig                                                                      #returns the figure


@app.callback(Output('E-Day', 'children'),                                          #defining a callback for the produces energy for the day
              Input('interval-component', 'n_intervals'))
def update_text_live(n):                                                            #called Funktion from callback
    
    df = getCurrentDataframe()                                                      #calls the previous function to get the newest data frame

    return ("Today: " + str(df["E-Day"][0]) + "kWh")                                #returns the amount of energy with the prefix Today: and suffix: kWh

@app.callback(Output('E-Total', 'children'),                                        #defining a callback for the produces energy for day
              Input('interval-component', 'n_intervals'))
def update_text_live(n):                                                            #called funktion from callback
    
    df = getCurrentDataframe()                                                      #calls the previous function to get the newest data frame

    return ("Total: " + str(round(df["E-Total"][0]/1000, 2)) + "MWh")               #returns the Total amount of energy with the prefix Today: and suffix: kWh


if linux:                                                                           #cheks if the os is Linux due to other IP assignment
    app.run_server(                                                                 #calls Funktion to start webserver
        port="8050",                                                                #defines the web port as 8050.  Standard HTTP port  = 8080
        host="10.18.40.200"                                                         #manually sets IP address for Linux production environment
        )
else:
    app.run_server(                                                                 #calls function to start webserver
        port="8050",                                                                #defines the web port as 8050.  Standard HTTP port  = 8080
        host=str(socket.gethostbyname(socket.gethostname()))                        #sets the IP address for win machines by getting the current IP address of the machine
        )