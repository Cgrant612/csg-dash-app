import base64
import io
import plotly.graph_objects as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = {'background': 'gray', 'text': 'black'}
graph_label_styles = {'textAlign': 'center', 'color': colors['text'], 'padding-top': '25px'}
dropdown_styles = {'width': '50%', 'textAlign': 'center', 'margin-left': '25%'}
dropdown_label_styles = {'textAlign': 'center'}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def clean_df(df):
    df = df.dropna(subset=['Date'])
    df.columns = [c.replace(' ', '_') for c in df.columns]
    df = df.dropna(subset=['Agent_Name'])
    df = df[df.Agent_Name != 'Jacobs, Mark']
    df = df[df.Agent_Name != 'Jacobs, Mark Agent']
    df = df[df.Agent_Name != 'Wilson, Gail']
    df = df[df.Agent_Name != 'Grant, Connor']
    df = df[df.Agent_Name != 'Lawson, Alvin, J']
    final_df = df.fillna(0)
    return final_df


app.layout = html.Div([
    html.H1('CSG Data',
            style={'textAlign': 'center', 'color': colors['text'], 'padding-top': '25px'}),
    html.Label(
        'Files must be .csv and have the following fields: Agent Name, Disposition, Outbound Handled, Active Talk Time and have an interval of 60 minutes',
        style=dropdown_label_styles),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '75%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'margin-left': '12.5%'
        },
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    html.Label('Select Date', style=dropdown_label_styles),
    dcc.Dropdown(
        id='DateDropdown',
        style=dropdown_styles
    ),
    html.H2('Active Agents', style={'textAlign': 'center', 'padding-top': '25px'}),
    dcc.Textarea(id='ActiveLabel',
                 value='',
                 readOnly=True,
                 style={'margin-left': '45%',
                        'width': '10%',
                        'textAlign': 'center',
                        'font-size': '36px'},
                 disabled=True
                 ),
    html.H2('Outbound Contacts Handled', style=graph_label_styles),
    dcc.Graph(id='CallData'),
    html.H2('Average Active Talk Time (in Minutes)', style=graph_label_styles),
    dcc.Graph(
        id='TalkTimeData',
        style={'padding': '25px'}
    ),
    html.H2('Hourly Productivity', style=graph_label_styles),
    html.P(),
    html.Label('(Overall Contacts Handled per Hour)', style=graph_label_styles),
    dcc.Graph(
        id='HourlyData'
    ),

    html.Label('Select Agent', style=dropdown_label_styles),
    dcc.Dropdown(
        id='AgentDropdown',
        style=dropdown_styles
    ),
    html.H2('Dials Over Time by Agent', style=graph_label_styles),
    dcc.Graph(
        id='AgentDialsOverTime'
    ),
    html.H2('Average Talk Time', style=graph_label_styles),
    html.Label('Hourly by Agent (in Minutes)', style=graph_label_styles),
    dcc.Graph(
        id='AgentTalkOverTime'
    ),
    html.H2('Disposition Distribution by Agent', style=graph_label_styles),
    dcc.Graph(
        id='DispDist'
    )
])


def return_df(contents):
    content_type, content_string = contents[0].split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    df = clean_df(df)
    return df


def parse_contents(filename):
    return html.Div([
        html.Label(filename, style={'textAlign': 'center'}),
        html.Hr(),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            parse_contents(n) for n in zip(list_of_names)]
        return children


@app.callback(Output('DateDropdown', 'options'),
              [Input('upload-data', 'contents')])
def update_date_dropdown(list_of_contents):
    df = return_df(list_of_contents)
    return [{'label': i, 'value': i} for i in df['Date'].unique()] + [{'label': 'All', 'value': 'All'}]


@app.callback(Output('DateDropdown', 'value'),
              [Input('upload-data', 'contents')])
def update_date_dropdown(list_of_contents):
    df = return_df(list_of_contents)
    return [{'label': i, 'value': i} for i in df['Date']][0]['value']


@app.callback(Output('AgentDropdown', 'options'),
              [Input('upload-data', 'contents')])
def update_date_dropdown(list_of_contents):
    df = return_df(list_of_contents)
    return [{'label': i, 'value': i} for i in df['Agent_Name'].unique()]  # + [{'label': 'All', 'value': 'All'}]


@app.callback(Output('AgentDropdown', 'value'),
              [Input('upload-data', 'contents')])
def update_date_dropdown(list_of_contents):
    df = return_df(list_of_contents)
    return [{'label': i, 'value': i} for i in df['Agent_Name']][0]['value']


@app.callback(Output('CallData', 'figure'),
              [Input('DateDropdown', 'value'),
               Input('upload-data', 'contents')])
def change_graph(selected_date, list_of_contents):
    if list_of_contents is not None:
        if selected_date == 'All':
            df = return_df(list_of_contents)
            df = df.groupby('Date', sort=False)['Outbound_Handled'].sum().reset_index()
            x_data = df['Date']
            y_data = df['Outbound_Handled']
            bar_1_data = go.Scatter(x=x_data, y=y_data, mode='lines+markers')
        else:
            df = return_df(list_of_contents)
            df = df.loc[df['Date'] == selected_date]
            x_data = df['Agent_Name']
            y_data = df["Outbound_Handled"]
            bar_1_data = go.Histogram(x=x_data, y=y_data, histfunc='sum')
        return {'data': [bar_1_data]}


@app.callback(Output('TalkTimeData', 'figure'),
              [Input('DateDropdown', 'value'),
               Input('upload-data', 'contents')])
def change_graph(selected_date, list_of_contents):
    if list_of_contents is not None:
        if selected_date == 'All':
            df = return_df(list_of_contents)
            new_df = df.groupby('Date', sort=False)['Outbound_Handled', 'Active_Talk_Time'].sum().reset_index()
            new_df['Average_Talk_Time'] = new_df['Active_Talk_Time'] / new_df['Outbound_Handled']
            new_df = new_df.fillna(0)
            x_data = new_df['Date']
            y_data = new_df['Average_Talk_Time']
            bar_1_data = go.Scatter(x=x_data, y=y_data, mode='lines+markers')
        else:
            df = return_df(list_of_contents)
            df = df.loc[df['Date'] == selected_date]
            new_df = df.groupby('Agent_Name', sort=False)['Outbound_Handled', 'Active_Talk_Time'].sum().reset_index()
            new_df['Average_Talk_Time'] = new_df['Active_Talk_Time'] / new_df['Outbound_Handled']
            new_df = new_df.fillna(0)
            x_data = new_df['Agent_Name']
            y_data = new_df["Average_Talk_Time"]
            bar_1_data = go.Histogram(x=x_data, y=y_data, histfunc='sum')
        return {'data': [bar_1_data]}


@app.callback(Output('HourlyData', 'figure'),
              [Input('DateDropdown', 'value'),
               Input('upload-data', 'contents')])
def change_graph(selected_date, list_of_contents):
    if list_of_contents is not None:
        if selected_date == 'All':
            df = return_df(list_of_contents)
            df = df.groupby('Interval_60_Minutes', sort=True)['Outbound_Handled'].sum().reset_index()
            x_data = df['Interval_60_Minutes']
            y_data = df['Outbound_Handled']
            bar_1_data = go.Scatter(x=x_data, y=y_data, mode='lines+markers')
        else:
            df = return_df(list_of_contents)
            df = df.loc[df['Date'] == selected_date]
            df = df.groupby('Interval_60_Minutes', sort=False)['Outbound_Handled'].sum().reset_index()
            x_data = df['Interval_60_Minutes']
            y_data = df['Outbound_Handled']
            bar_1_data = go.Scatter(x=x_data, y=y_data, mode='lines+markers')
        return {'data': [bar_1_data]}


@app.callback(Output('AgentDialsOverTime', 'figure'),
              [Input('DateDropdown', 'value'),
                  Input('AgentDropdown', 'value'),
               Input('upload-data', 'contents')])
def change_dials_graph(selected_date, selected_agent, list_of_contents):
    if selected_date == 'All':
        df = return_df(list_of_contents)
        df = df.loc[df['Agent_Name'] == selected_agent]
        df = df.groupby('Date', sort=False)['Outbound_Handled'].sum().reset_index()
        x_data = df['Date']
        y_data = df['Outbound_Handled']
        bar_1_data = go.Scatter(x=x_data, y=y_data)
    else:
        df = return_df(list_of_contents)
        df = df.loc[df['Agent_Name'] == selected_agent]
        df = df.loc[df['Date'] == selected_date]
        df = df.groupby('Interval_60_Minutes', sort=False)['Outbound_Handled'].sum().reset_index()
        x_data = df['Interval_60_Minutes']
        y_data = df['Outbound_Handled']
        bar_1_data = go.Scatter(x=x_data, y=y_data)
    return {'data': [bar_1_data]}


@app.callback(Output('AgentTalkOverTime', 'figure'),
              [Input('DateDropdown', 'value'),
                  Input('AgentDropdown', 'value'),
               Input('upload-data', 'contents')])
def change_talk_time_graph(selected_date, selected_agent, list_of_contents):
    if selected_date == 'All':
        df = return_df(list_of_contents)
        df = df.loc[df['Agent_Name'] == selected_agent]
        new_df = df.groupby('Date', sort=False)['Outbound_Handled', 'Active_Talk_Time'].sum().reset_index()
        new_df['Average_Talk_Time'] = new_df['Active_Talk_Time'] / new_df['Outbound_Handled']
        new_df = new_df.fillna(0)
        x_data = new_df['Date']
        y_data = new_df['Average_Talk_Time']
        bar_1_data = go.Scatter(x=x_data, y=y_data)
    else:
        df = return_df(list_of_contents)
        df = df.loc[df['Agent_Name'] == selected_agent]
        df = df.loc[df['Date'] == selected_date]
        new_df = df.groupby('Interval_60_Minutes', sort=False)['Outbound_Handled', 'Active_Talk_Time'].sum().reset_index()
        new_df['Average_Talk_Time'] = new_df['Active_Talk_Time'] / new_df['Outbound_Handled']
        new_df = new_df.fillna(0)
        x_data = new_df['Interval_60_Minutes']
        y_data = new_df['Average_Talk_Time']
        bar_1_data = go.Scatter(x=x_data, y=y_data)
    return {'data': [bar_1_data]}


@app.callback(Output('DispDist', 'figure'),
              [Input('DateDropdown', 'value'),
               Input('AgentDropdown', 'value'),
               Input('upload-data', 'contents')])
def change_dist_graph(selected_date, selected_agent, list_of_contents):
    if selected_date == 'All':
        df = return_df(list_of_contents)
        df = df.loc[df['Agent_Name'] == selected_agent]
        x_data = df['Disposition']
        y_data = df['Outbound_Handled']
        bar_1_data = go.Histogram(x=x_data, y=y_data, histfunc='sum')
    else:
        df = return_df(list_of_contents)
        df = df.loc[df['Agent_Name'] == selected_agent]
        df = df.loc[df['Date'] == selected_date]
        x_data = df['Disposition']
        y_data = df['Outbound_Handled']
        bar_1_data = go.Histogram(x=x_data, y=y_data, histfunc='sum')
    return {'data': [bar_1_data]}


@app.callback(Output('ActiveLabel', 'value'),
              [Input('DateDropdown', 'value'),
               Input('upload-data', 'contents')])
def change_label(selected_date, list_of_contents):
    if selected_date is not 'All':
        df = return_df(list_of_contents)
        df = df.loc[df['Date'] == selected_date]
        agent_array = df['Agent_Name'].unique()
    else:
        agent_array = " "
    return str(len(agent_array))


server = app.server


if __name__ == '__main__':
    app.run_server(debug=True)
