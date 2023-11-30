#!/usr/bin/env python3
import sqlite3
import dash
import csv
from dash import dcc, html
#import dash_core_components as dcc
#import dash_html_components as html
from subprocess import check_output 
import numpy
from dash.dependencies import Input, Output, State
import random
import time
import pandas as pd
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import numpy as np
import plotly.express as px
import json
from dash_iconify import DashIconify
import datetime
import json
import requests
import socket
import threading
import subprocess
import schedule
import Styles as styles
dtypes = {'data1':str, 'data2':str, 
          'cabinet_L1':float, 'cabinet_L2':float, 'cabinet_L3':float, 
          'motor_L1':float, 'motor_L2':float, 'motor_L3':float, 
          'temp_1':float, 'temp_2':float, 
          'input_1':bool, 'input_2':bool, 'input_3':bool, 
          'output_1': bool, 'output_2':bool, 'output_3': bool, 
          'kWh':float, 'OnOff': int}


thresholds ={
    'temp': 40,
    'asymetry': 0.080,
}
__sensors_path = "PmB_SensorsValues.json"
__relay_path = "PmB_RelayValues.json"
__plot_path = "plot_data.csv"

hostname = socket.gethostname()
ip_adress = socket.gethostbyname(hostname)
print('ip= ',ip_adress )

global SensorsValues
global RelayValues
relays = {}



password = "chuj"
# Flaga wskazująca, czy pole hasła jest widoczne
password_visible = False

web_hook_url = 'https://hooks.slack.com/services/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'
def slack_MSG(text):
    slack_msg = {'text': text}
    return requests.post(web_hook_url, data=json.dumps(slack_msg))




style_graph = {}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
value = 10.0

x = np.arange(10)
x2 = np.arange(10)*2
x3 = np.arange(10)*3

conn = sqlite3.connect('sensor_new.db')
query = 'SELECT * FROM data_center ORDER BY update_time DESC LIMIT 10000'
SensValuesDB = pd.read_sql_query(query, conn)

time.sleep(1)
conn.close()


SensValuesDB['update_time'] = SensValuesDB['update_time'].apply(lambda x: datetime.datetime.strptime(x, '%d/%m/%Y, %H:%M:%S.%f'))

#SensValuesDB['update_time'] = SensValuesDB['update_time'].apply()
#for i in range(len(SensValuesDB['update_time'])):
#    SensValuesDB['update_time'].iloc[i] = datetime.datetime.strptime(SensValuesDB['update_time'].iloc[i], '%d/%m/%Y, %H:%M:%S.%f') 

print(type(SensValuesDB['update_time'][0]))
#print('yoooooooooooooooooooooloooooooooooooooooooooooooo', len(SensValuesDB[0]))
temp1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['temperature_sensor_1'], 
            #fill='tozeroy', fillcolor='rgba(133, 203, 204, 0.2)',
            line=dict(color="rgba(10, 203, 204, 1)"))

temp2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['temperature_sensor_2'], 
            #fill='tozeroy', fillcolor='rgba(168, 222, 224, 0.2)',
            line=dict(color="rgba(10, 203, 204, 1)"))

cabinetL1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['cabinet_L1'], 
                #fill='tozeroy', fillcolor='rgba(133, 203, 204, 0.2)',
            line=dict(
            color="brown"#"rgba(10, 203, 204, 1)"
            ))

cabinetL2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['cabinet_L2'], 
                #fill='tozeroy', fillcolor='rgba(133, 203, 204, 0.2)',
                line=dict(
                color="black"#"rgba(10, 203, 204, 1)"
                ))

cabinetL3 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['cabinet_L3'], #fill='tozeroy',
                #fillcolor='rgba(133, 203, 204, 0.2)',
                line=dict(
                color="grey"#"rgba(10, 203, 204, 1)"
                ))

motorL1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['motor_L1'], #fill='tozeroy',
                #fillcolor='rgba(133, 203, 204, 0.2)',
                line=dict(
                color="brown"#"rgba(10, 203, 204, 1)"
                ))
motorL2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['motor_L2'], #fill='tozeroy',
                #fillcolor='rgba(133, 203, 204, 0.2)',
                line=dict(
                color="black"#"rgba(10, 203, 204, 1)"
                ))
motorL3 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['motor_L3'], #fill='tozeroy',
                #fillcolor='rgba(133, 203, 204, 0.2)',
                line=dict(
                color="grey"#"rgba(10, 203, 204, 1)"
                ))

OEE1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['kW'], #fill='tozeroy',
                #fillcolor='rgba(133, 203, 204, 0.2)',
                line=dict(
                color="rgba(10, 203, 204, 1)"
                ),
            line_shape='hv'
            )

OEE2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['kW'], #fill='tozeroy',
                line=dict(
                color="rgba(10, 203, 204, 1)"
                ),
            #line_shape='hv'
            )

layout = go.Layout(
paper_bgcolor="rgba(1, 1, 1, 0.0)",
plot_bgcolor='rgba(1, 1, 1, 0.0)',
font=dict(color='black'),
xaxis=dict(showgrid=False,
        gridcolor='black',
        tickformat='%H %M %S'),
yaxis=dict(showgrid=True,
        gridcolor='#d7d7d7'), showlegend=False,
margin=dict(l=10, r=10, t=10, b=10),

)

fig_temp = go.Figure(data=[temp1, temp2], layout=layout)
fig_oee = go.Figure(data=[OEE1], layout=layout)
fig_amp_cabinet = go.Figure(data=[cabinetL1, cabinetL2, cabinetL3], layout=layout)
fig_amp_motor = go.Figure(data=[motorL1, motorL2, motorL3], layout=layout)
'''

fig_temp = go.Figure(data=[temp1, temp2], layout=go.Layout(
    paper_bgcolor="rgba(1, 1, 1, 0.0)",
    plot_bgcolor='rgba(1, 1, 1, 0.0)',
    font=dict(color='black'),
    xaxis=dict(showgrid=False,
               gridcolor='black'),
    yaxis=dict(showgrid=True,
               gridcolor='#d7d7d7'), showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
))

fig_amp = go.Figure(data=[amp1, amp2, amp3], layout=go.Layout(
    paper_bgcolor="rgba(1, 1, 1, 0.0)",
    plot_bgcolor='rgba(1, 1, 1, 0.0)',
    font=dict(color='black'),
    xaxis=dict(showgrid=False,
               gridcolor='black'),
    yaxis=dict(showgrid=True,
               gridcolor='#d7d7d7'), showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
))
'''

temperature_tile = html.Div([
    dbc.Row([
        dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="fluent:temperature-16-regular", style={'color':'#405189'}, width=32), className='iconse'),
        html.Div([
            html.Div("0",id='temperatura_1_indicator', className='proba'),
            html.Div("Temperature T1", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(C)"),
], id='indi-T1', className='keymat d-flex justify-content-between align-items-center')], sm=6),
        dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="fluent:temperature-16-regular", style={'color':'#405189'}, width=32), className='iconse'),
        html.Div([
            html.Div("0", id='temperatura_2_indicator', className='proba'),
            html.Div("Temperatura T2", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(C)"),
], id='indi-T2', className='keymat d-flex justify-content-between align-items-center')], sm=6, style={})
    ]),
    dbc.Row([
        dbc.Col([html.Div([html.Div(['Temperatury Korbowodu [C]'], className='title-temp-korbowod'),dcc.Graph(figure=fig_temp,  style={'height':'20vh'}, id='graph-temperature')], className='keymat px-2')])
    ]),
], style={})


OEE_tile = html.Div([
    dbc.Row([
        dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="material-symbols:mode-off-on", style={'color':'#198754'}, width=32), className='iconse2'),
        html.Div([
            html.Div("0",id='OEE_1_indicator', className='ontoh'),
            html.Div("",id='OEE_indi_2', className='ontoh'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
], className='keymat d-flex align-items-center')], sm=6),
        dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="mdi:fuse", style={'color':'#198754'}, width=32), className='iconse2'),
        html.Div([
            html.Div("0",id='OEE_2_indicator', className='proba'),
            html.Div("Aktualne zużycie", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(kW)"),
], className='keymat d-flex justify-content-between align-items-center')], sm=6),
    ]),
    dbc.Row([
        dbc.Col([html.Div([html.Div(['Moc [kW]'], className='title-temp-korbowod'),dcc.Graph(figure=fig_oee, style={'height':'20vh'}, id='graph-OEE')], className='keymat px-2')])
    ]),
], style={})

OEE_tile_2 = html.Div([
    dbc.Row([
dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="mdi:fuse", style={'color':'#198754'}, width=32), className='iconse2'),
        html.Div([
            html.Div("0",id='cabinet_amperage', className='proba'),
            html.Div("Aktualne zużycie szafy", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(A)"),
], className='keymat d-flex justify-content-between align-items-center')], sm=2),
dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="mdi:fuse", style={'color':'#198754'}, width=32), className='iconse2'),
        html.Div([
            html.Div("0",id='motor_amperage', className='proba'),
            html.Div("Aktualne zużycie suwaka", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(A)"),
], className='keymat d-flex justify-content-between align-items-center')], sm=3),
dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="mdi:fuse", style={'color':'#198754'}, width=32), className='iconse2'),
        html.Div([
            html.Div("0",id='day_kWh', className='proba'),
            html.Div("Godzinowy pobór mocy", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(kWh)"),
], className='keymat d-flex justify-content-between align-items-center')], sm=2),

dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="mdi:fuse", style={'color':'#198754'}, width=32), className='iconse2'),
        html.Div([
            html.Div("0",id='biggest_day_kWh', className='proba'),
            html.Div("Największa chwilowa moc ostatniej godziny", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(kW)"),
], className='keymat d-flex justify-content-between align-items-center')], sm=3),

dbc.Col([
html.Div([
    html.Div([
        html.Div(DashIconify(icon="mdi:fuse", style={'color':'#198754'}, width=32), className='iconse2'),
        html.Div([
            html.Div("0",id='average_day_kWh', className='proba'),
            html.Div("Średni pobór ostatniej godziny", className='sctitle'),
        ], className='text-start'),
    ], className='d-flex align-items-center'),
    html.Div("(kW)"),
], className='keymat d-flex justify-content-between align-items-center')], sm=2),])])


amperage_tile1 = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:thunder", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Cabinet_1_indicator', className='proba ndsam'),
                        html.Div("Szafa L1", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(A)"),
                        html.Div('',style=styles.amper_cabinet_color_style_brown),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='indi-CL1', className='keymat')], md=4),
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:thunder", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Cabinet_2_indicator', className='proba ndsam'),
                        html.Div("Szafa L2", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(A)"),
                        html.Div('',style=styles.amper_cabinet_color_style_black),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='indi-CL2', className='keymat')], md=4),
dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:thunder", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Cabinet_3_indicator', className='proba ndsam'),
                        html.Div("Szafa L3", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(A)"),
                        html.Div('',style=styles.amper_cabinet_color_style_grey),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='indi-CL3', className='keymat')], md=4),
    ]),
    dbc.Row([
        dbc.Col([html.Div([html.Div(['Natężenie prądu szafy sterowniczej [A]'], className='title-temp-korbowod'),dcc.Graph(figure=fig_amp_cabinet, style={'height':'20vh'}, id='graph-cabinet')], className='keymat px-2')])
    ]),
], style={})

amperage_tile2 = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:thunder", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Motor_1_indicator', className='proba ndsam'),
                        html.Div("Suwak L1", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(A)"),
                        html.Div('',style=styles.amper_cabinet_color_style_brown),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='indi-ML1', className='keymat')], md=4),
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:thunder", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Motor_2_indicator', className='proba ndsam'),
                        html.Div("Suwak L2", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(A)"),
                        html.Div('',style=styles.amper_cabinet_color_style_black),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='indi-ML2', className='keymat')], md=4),
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:thunder", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Motor_3_indicator', className='proba ndsam'),
                        html.Div("Suwak L3", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(A)"),
                        html.Div('',style=styles.amper_cabinet_color_style_grey),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='indi-ML3', className='keymat')], md=4),
    ]),
    dbc.Row([
        dbc.Col([html.Div([html.Div(['Natęzenie prądu suwaka [A]'], className='title-temp-korbowod'),dcc.Graph(figure=fig_amp_motor, style={'height':'20vh'}, id='graph-motor')], className='keymat px-2')])
    ]),
], style={})

panel_IO = html.Div([
        dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("", id='Input_1_indicator', className='sctitle2'),
                html.Div("Input 1", className='sctitle'),
            ], id='indi-INPUT1', className='keymat')], sm=4),
        dbc.Col([
            html.Div([
                html.Div("", id='Input_2_indicator', className='sctitle2'),
                html.Div("Input 2", className='sctitle'),
            ], id='indi-INPUT2', className='keymat')], sm=4, style={}),
        dbc.Col([
            html.Div([
                html.Div("", id='Input_3_indicator', className='sctitle2'),
                html.Div("Input 3", className='sctitle'),
            ], id='indi-INPUT3', className='keymat')], sm=4),
    ]),
])

asymetri_indicators = html.Div([
        dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:current-ac", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Cabinet_asymetrii_L1', className='proba ndsam'),
                        html.Div("Asymetria szafy L1", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(%)"),
                        #html.Div('',style=styles.amper_cabinet_color_style_brown),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='', className='keymat')], md=2),
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:current-ac", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Cabinet_asymetrii_L2', className='proba ndsam'),
                        html.Div("Asymetria szafy L2", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(%)"),
                        #html.Div('',style=styles.amper_cabinet_color_style_black),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='', className='keymat')], md=2),
dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:current-ac", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Cabinet_asymetrii_L3', className='proba ndsam'),
                        html.Div("Asymetria szafy L3", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(%)"),
                        #html.Div('',style=styles.amper_cabinet_color_style_grey),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='', className='keymat')], md=2),
            dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:current-ac", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Motor_asymetrii_L1', className='proba ndsam'),
                        html.Div("Asymetria suwaka L1", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(%)"),
                        #html.Div('',style=styles.amper_cabinet_color_style_brown),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='', className='keymat')], md=2),
            dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:current-ac", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Motor_asymetrii_L2', className='proba ndsam'),
                        html.Div("Asymetria suwaka L2", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(%)"),
                        #html.Div('',style=styles.amper_cabinet_color_style_brown),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='', className='keymat')], md=2),
            dbc.Col([
            html.Div([
                html.Div([
                    html.Div(DashIconify(icon="mdi:current-ac", color="gold", width=32), className='iconse3'),
                    html.Div([
                        html.Div("0", id='Motor_asymetrii_L3', className='proba ndsam'),
                        html.Div("Asymetria suwaka L3", className='sctitle'),
                    ], className='text-start'),
                    html.Div([
                        html.Div("(%)"),
                        #html.Div('',style=styles.amper_cabinet_color_style_brown),
                    ], className='oresk'),
                ], className='d-flex align-items-center'),
            ], id='', className='keymat')], md=2),
    ]),

])


row6 = dbc.Row([OEE_tile_2])


hostname_start = check_output("hostname", encoding="utf8")
print('hostname', hostname_start)
row0 = html.Div([
    html.Div([
        html.Div(['UR monitor' + str(hostname_start)

        ], className='app-header-title', id='Main-title')
    ], className='app-header')
])
row1 = dbc.Row([
        dbc.Col([temperature_tile], width=6, sm=12, md=12, lg=6, style={}, xs=12),
dbc.Col([OEE_tile], width=6, sm=12, md=12, lg=6, xs=12)
    ], className='dueos')

row2 = dbc.Row([
dbc.Col([amperage_tile1], width=6, sm=12, md=12, lg=6, xs=12),
dbc.Col([amperage_tile2], width=6, sm=12, md=12, lg=6, xs=12)
    ])
'''
row3 = dbc.Row([
    dbc.Col([drop1], style={'padding':'10px'}, width=2, sm=4, md=4, lg=2, xs=12),
dbc.Col([drop2], style={'padding':'10px'}, width=2, sm=4, md=4, lg=2, xs=12),
dbc.Col([drop3], style={'padding':'10px'}, width=2, sm=4, md=4, lg=2, xs=12),
dbc.Col([
html.Div([
html.Button("Dowlad text", id="download-button"),
dcc.Download(id="download-text"),
dcc.Input(id="password-input", type="password", value=""),
])
],className="download-button-title",  style={'padding':'10px'}, width=2, sm=4, md=4, lg=1, xs=12),
dbc.Col([html.Div([''], id='emergency-state')], id='emergency', className='emergencyOFF', style={}, width=6, sm=12, md=12, lg=5, xs=12),
])'''

row5 = dbc.Row([asymetri_indicators])

row3 = dbc.Row([
    dbc.Col([
        panel_IO
    ], xl=7),

    dbc.Col([
        html.Div([
            html.Div([''], id='emergency-state')
        ], id='emergency', className='emergencyOFF'),
    ], xl=5),
])


row4 = dbc.Row([
    dbc.Col([
        html.Div([
            html.Div([
                dcc.Input(id='ip-input', type='text', className='form-control', placeholder='Wprowadź adres IP'),
            ], className='off_led'),
            html.Div([
                html.Button('Ustaw Nowe IP', id='button-set-ip', className='btn btn-primary', n_clicks=0),
            ])
        ], className='led_cont'),
    ], lg=4),
    dbc.Col([
        html.Div([
             html.Div([
                    dcc.Input(id='hostname-input', type='text', className='form-control', placeholder='Wprowadź nazwe urzadzenia'),], className='off_led'),
                html.Div([
                html.Button('Ustaw Nowa Nazwe Urzadzenia', id='button-set-hostname', className='btn btn-primary nowrap', n_clicks=0,)
            ])
        ], className='led_cont'),
    ], lg=5),
dbc.Col([
    html.Div([
html.Button("Download data", id="download-button", className="btn btn-success w-100"),
dcc.Download(id="download-text"),], className='led_cont')
], lg=3)
])


timers =html.Div([
dcc.Interval(
    ##TIMER LAMPEK LED
       id='interval-component', # indicators i style
       interval=1 * 1000,  # in milliseconds
       n_intervals=0
   ),
html.Div(id='hidden-div', style={'display': 'none'}),
html.Div(id='hidden-div-relays', style={'display': 'none'}),
dcc.Store(id='data', clear_data=True),
dcc.Store(id='oee', clear_data=True),
dcc.Store(id='temp1', clear_data=True),
dcc.Store(id='warning temp1', clear_data=True),
dcc.Store(id='temp2', clear_data=True),
dcc.Store(id='warning temp2', clear_data=True),
dcc.Store(id='cabinet1', clear_data=True),
dcc.Store(id='warning cabinet1', clear_data=True),
dcc.Store(id='cabinet2', clear_data=True),
dcc.Store(id='warning cabinet2', clear_data=True),
dcc.Store(id='cabinet3', clear_data=True),
dcc.Store(id='warning cabinet3', clear_data=True),
dcc.Store(id='mot1', clear_data=True),
dcc.Store(id='warning mot1', clear_data=True),
dcc.Store(id='mot2', clear_data=True),
dcc.Store(id='warning mot2', clear_data=True),
dcc.Store(id='mot3', clear_data=True),
dcc.Store(id='warning mot3', clear_data=True),
dcc.Store(id='input1', clear_data=True),
dcc.Store(id='input2', clear_data=True),
dcc.Store(id='input3', clear_data=True),
dcc.Store(id='warning input1', clear_data=True),
dcc.Store(id='warning input2', clear_data=True),
dcc.Store(id='warning input3', clear_data=True),
dcc.Store(id='relays', clear_data=True),
dcc.Store(id='kW', clear_data=True),
dcc.Store(id='cabinet amperage', clear_data=True),
dcc.Store(id='motor amperage', clear_data=True),
dcc.Store(id='day kWh', clear_data=True),
dcc.Store(id='biggest day kWh', clear_data=True),
dcc.Store(id='average day kWh', clear_data=True),
dcc.Store(id='cabinet asymetrii L1', clear_data=True),
dcc.Store(id='cabinet asymetrii L2', clear_data=True),
dcc.Store(id='cabinet asymetrii L3', clear_data=True),
dcc.Store(id='motor asymetrii L1', clear_data=True),
dcc.Store(id='motor asymetrii L2', clear_data=True),
dcc.Store(id='motor asymetrii L3', clear_data=True),
dcc.Interval(
       id='interval-component1',
       interval=1 * 3000,  # in milliseconds
       n_intervals=0
   ),
    dcc.Interval(
        id='interval-component2', # Wyświetlanie wykresow
        interval=2*60 * 1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Interval(
        id='interval-component3',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    )
])


app.layout = dbc.Container(html.Div([
    row0,
    row1,
    row2,
    row5,
    row6,
    row3,
    row4,
    timers

], style={'backgroundColor':'transparent',
         }), fluid=True)

SensorsValues_table = []
RelayValues_table = []

#print('chuj wi o oc o chodzi')
@app.callback(
        Output('motor asymetrii L1', 'data'),
        Output('motor asymetrii L2', 'data'),
        Output('motor asymetrii L3', 'data'),
        Output('cabinet amperage', 'data'),
        Output('motor amperage', 'data'),
        Output('day kWh', 'data'),
        Output('cabinet asymetrii L1', 'data'),
        Output('cabinet asymetrii L2', 'data'),
        Output('cabinet asymetrii L3', 'data'),
#Output('average day kWh', 'data'),
        #Output('biggest day kWh', 'data'),
        
        
        Input('interval-component', 'n_intervals')
)

def motor_asymetrii(n_intervals):
    conn = sqlite3.connect('/home/pi/venv/raspberry2/sensor_new.db')
    query = 'SELECT motor_asymetrii_L1, motor_asymetrii_L2, motor_asymetrii_L3, cabinet_amperage, motor_amperage, day_kWh, cabinet_asymetrii_L1, cabinet_asymetrii_L2, cabinet_asymetrii_L3  FROM data_center ORDER BY update_time DESC LIMIT 1'
    readData = pd.read_sql_query(query, conn)
    
    conn.close()
    return  readData['motor_asymetrii_L1'], readData['motor_asymetrii_L1'], readData['motor_asymetrii_L3'],\
            readData['cabinet_amperage'], readData['motor_amperage'], readData['day_kWh'],\
            readData['cabinet_asymetrii_L1'], readData['cabinet_asymetrii_L2'], readData['cabinet_asymetrii_L3']


#print('chuj wi o oc o chodzi')
@app.callback(
        #Output('motor asymetrii L1', 'data'),
        #Output('motor asymetrii L2', 'data'),
        #Output('motor asymetrii L3', 'data'),
        Output('biggest day kWh', 'data'),
        Output('average day kWh', 'data'),
        
        
        Input('interval-component', 'n_intervals')
)

def chuj(n_intervals):
    conn = sqlite3.connect('sensor_new.db')
    #print('cccccccccccccccccccccccccccccc')
    query = 'SELECT biggest_kWh_of_day, average_kWh_if_day FROM data_center ORDER BY update_time DESC LIMIT 1'
    readData = pd.read_sql_query(query, conn)
    #print('ciekawa data biggest i average: ', readData)
    conn.close()
    #print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP \n', readData['biggest_kWh_of_day'])
    return  readData['biggest_kWh_of_day'], readData['average_kWh_if_day'], 



@app.callback(
        Output('data', 'data'),
        Output('oee', 'data'),
        Output('temp1', 'data'),
        Output('temp2', 'data'),
        Output('warning temp1', 'data'),
        Output('warning temp2', 'data'),
        Output('mot1', 'data'),
        Output('mot2', 'data'),
        Output('mot3', 'data'),
        Output('warning mot1', 'data'),
        Output('warning mot2', 'data'),
        Output('warning mot3', 'data'),
        Output('cabinet1', 'data'),
        Output('cabinet2', 'data'),
        Output('cabinet3', 'data'),
        Output('warning cabinet1', 'data'),
        Output('warning cabinet2', 'data'),
        Output('warning cabinet3', 'data'),
        Output('input1', 'data'),
        Output('input2', 'data'),
        Output('input3', 'data'),
        Output('warning input1', 'data'),
        Output('warning input2', 'data'),
        Output('warning input3', 'data'),
        #Output('cabinet amperage', 'data'),
        #Output('motor amperage', 'data'),
        #Output('day kWh', 'data'),
        #Output('cabinet asymetrii L1', 'data'),
        #Output('cabinet asymetrii L2', 'data'),
        #Output('cabinet asymetrii L3', 'data'),
        #Output('motor asymetrii L1', 'data'),
        #Output('motor asymetrii L2', 'data'),
        #Output('motor asymetrii L3', 'data'),
        
        Input('interval-component', 'n_intervals')
)

def chuj(n_intervals):
    conn = sqlite3.connect('/home/pi/venv/raspberry2/sensor_new.db')
    query = 'SELECT update_time, kW, temperature_sensor_1, temperature_sensor_2, motor_L1, motor_L2, motor_L3, warning_current_sensor_4, warning_current_sensor_5, warning_current_sensor_6, cabinet_L1, cabinet_L2, cabinet_L3, warning_current_sensor_1, warning_current_sensor_2, warning_current_sensor_3, input_1, input_2, input_3, warning_input_1, warning_input_2, warning_input_3 FROM data_center ORDER BY update_time DESC LIMIT 1'
    readData = pd.read_sql_query(query, conn)
    
    conn.close()
    #print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP \n', readData['motor_asymetrii_L1'])
    return  readData['update_time'], readData['kW'],\
            readData['temperature_sensor_1'], readData['temperature_sensor_2'],\
            readData['warning_temperature_1'], readData['warning_temperature_2'],\
            readData['motor_L1'], readData['motor_L2'], readData['motor_L3'],\
            readData['warning_current_sensor_4'], readData['warning_current_sensor_5'], readData['warning_current_sensor_6'],\
            readData['cabinet_L1'], readData['cabinet_L2'], readData['cabinet_L3'],\
            readData['warning_current_sensor_1'], readData['warning_current_sensor_2'], readData['warning_current_sensor_3'],\
            readData['input_1'], readData['input_2'], readData['input_3'],\
            readData['warning_input_1'], readData['warning_input_2'], readData['warning_input_3'],\
            #readData['cabinet_amperage'], readData['motor_amperage'], readData['day_kWh'],\
            #readData['cabinet_asymetrii_L1'], readData['cabinet_asymetrii_L2'], readData['cabinet_asymetrii_L3'],\
            #readData['motor_asymetrii_L1'], #readData['motor_asymetrii_L2'], readData['motor_asymetrii_L3']

'''@app.callback(
        [#Output('data', 'data'),
         ,], 
         Input('interval-component', 'n_intervals')
)

def store_data(n_intervals, chuj):
    
    print('chuj wi o oc o chodzi1111111', conn)
    #try:
    conn = sqlite3.connect('sensor_new.db')
    query = 'SELECT * FROM data_center ORDER BY update_time DESC LIMIT 1'
    readData = pd.read_sql_query(query, conn)
    print('ciota')
    print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa',(readData))
    print('readdasdasssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss, ', readData['cabinet_L1'])

    conn.close()
    #return  readData['update_time'], readData['kW'],\
    #return  readData['temperature_sensor_1'], readData['temperature_sensor_2'],\
    #        readData['warning_temperature_1'], readData['warning_temperature_2'],\
    #        readData['motor_L1'], readData['motor_L2'], readData['motor_L3'],\
    return  readData['warning_current_sensor_4'], readData['warning_current_sensor_5'], readData['warning_current_sensor_6'],\
            readData['cabinet_L1'], readData['cabinet_L2'], readData['cabinet_L3'],\
            readData['warning_current_sensor_1'], readData['warning_current_sensor_2'], readData['warning_current_sensor_3'],\
            readData['input_1'], readData['input_2'], readData['input_3'],\
            readData['warning_input_1'], readData['warning_input_2'], readData['warning_input_3'],\
            readData['cabinet_amperage'], readData['motor_amperage'], readData['day_kWh'],\
            readData['cabinet_asymetrii_L1'], readData['cabinet_asymetrii_L2'], readData['cabinet_asymetrii_L3'],\
            readData['motor_asymetrii_L1'], readData['motor_asymetrii_L2'], readData['motor_asymetrii_L3']
#except:
    #    print("Plik Indicators.json nie został znaleziony.")
'''

emergency_information = {
                   '5' : 'Asymetria fazy L1 suwaka jest wieksza niz 80%!',
                '6' : 'Asymetria fazy L2 suwaka jest wieksza niz 80%!',
                '7' : 'Asymetria fazy L3 suwaka jest wieksza niz 80%!',
                '2' : 'Asymetria fazy L1 szafy sterowniczej jest wieksza niz 80%!',
                '3' : 'Asymetria fazy L2 szafy sterowniczej jest wieksza niz 80%!',
                '4' : 'Asymetria fazy L3 szafy sterowniczej jest wieksza niz 80%!',
                '0' : 'Temperatura czujnika 1 przekracza dozwolony limit!',
                '1' : 'Temperatura czujnika 2 przekracza dozwolony limit!',
                '8' : 'Wejscie 1 jest aktywne!',
                '9' : 'Wejscie 2 jest aktywne!',
                '10' : 'Wejscie 3 jest aktywne!',
         }

@app.callback(
    [Output('temperatura_1_indicator', 'children'),
     Output('temperatura_2_indicator', 'children'),
     Output('OEE_1_indicator', 'children'),
     Output('OEE_2_indicator', 'children'),
     Output('Cabinet_1_indicator', 'children'),
     Output('Cabinet_2_indicator', 'children'),
     Output('Cabinet_3_indicator', 'children'),
     Output('Motor_1_indicator', 'children'),
     Output('Motor_2_indicator', 'children'),
     Output('Motor_3_indicator', 'children'),
     Output('Input_1_indicator', 'children'),
     Output('Input_2_indicator', 'children'),
     Output('Input_3_indicator', 'children'),
     Output('indi-T1', 'style'),
     Output('indi-T2', 'style'),
     Output('indi-CL1', 'style'),
     Output('indi-CL2', 'style'),
     Output('indi-CL3', 'style'),
     Output('indi-ML1', 'style'),
     Output('indi-ML2', 'style'),
     Output('indi-ML3', 'style'),
     Output('indi-INPUT1', 'style'),
     Output('indi-INPUT2', 'style'),
     Output('indi-INPUT3', 'style'),
     Output('emergency-state', 'children'),
     Output('emergency', 'className'),
     Output('Motor_asymetrii_L1', 'children'), 
     Output('Motor_asymetrii_L2', 'children'), 
     Output('Motor_asymetrii_L3', 'children'), 
     Output('Cabinet_asymetrii_L1', 'children'), 
     Output('Cabinet_asymetrii_L2', 'children'), 
     Output('Cabinet_asymetrii_L3', 'children'), 
     Output('cabinet_amperage', 'children'), 
     Output('motor_amperage', 'children'), 
     Output('day_kWh', 'children'),
     Output('biggest_day_kWh', 'children'),
     Output('average_day_kWh', 'children'),
     ],
     [
        Input('data', 'data'),
        Input('oee', 'data'),
        Input('temp1', 'data'),
        Input('temp2', 'data'),
        Input('warning temp1', 'data'),
        Input('warning temp2', 'data'),
        Input('mot1', 'data'),
        Input('mot2', 'data'),
        Input('mot3', 'data'),
        Input('warning mot1', 'data'),
        Input('warning mot2', 'data'),
        Input('warning mot3', 'data'),
        Input('cabinet1', 'data'),
        Input('cabinet2', 'data'),
        Input('cabinet3', 'data'),
        Input('warning cabinet1', 'data'),
        Input('warning cabinet2', 'data'),
        Input('warning cabinet3', 'data'),
        Input('input1', 'data'),
        Input('input2', 'data'),
        Input('input3', 'data'),
        Input('warning input1', 'data'),
        Input('warning input2', 'data'),
        Input('warning input3', 'data'),
        Input('motor asymetrii L1', 'data'),
        Input('motor asymetrii L2', 'data'),
        Input('motor asymetrii L3', 'data'),
        Input('cabinet asymetrii L1', 'data'),
        Input('cabinet asymetrii L2', 'data'),
        Input('cabinet asymetrii L3', 'data'),
        Input('cabinet amperage', 'data'),
        Input('motor amperage', 'data'),
        Input('day kWh', 'data'),
        Input('biggest day kWh', 'data'),
        Input('average day kWh', 'data'),
     Input('interval-component', 'n_intervals')]
)

def Indicators(date, oee,
               temp1, temp2, warning_temp1, warning_temp2,
               mot1, mot2, mot3, warning_mot1, warning_mot2, warning_mot3,
               cab1, cab2, cab3, warning_cab1, warning_cab2, warning_cab3,
               input1, input2, input3, warning_input1, warning_input2, warning_input3,
               motor_asym_L1, motor_asym_L2, motor_asym_L3, 
               cabinet_asym_L1, cabinet_asym_L2, cabinet_asym_L3, 
               cabinet_amperage, motor_amperage, day_kWh,
               biggest_kWh, average_kWh,
                n_intervals):

    global temperature_sensor_1
    global temperature_sensor_2
    global Motor_L1
    global Motor_L2
    global Motor_L3
    global Cabinet_L1
    global Cabinet_L2
    global Cabinet_L3
    global Motor_L1_Asymetrii
    global Motor_L2_Asymetrii
    global Motor_L3_Asymetrii
    global Cabinet_L1_Asymetrii
    global Cabinet_L2_Asymetrii
    global Cabinet_L3_Asymetrii
    global Watts


    Motor_L1_Asymetrii = warning_mot1
    Motor_L2_Asymetrii = warning_mot2
    Motor_L3_Asymetrii = warning_mot3
    Cabinet_L1_Asymetrii = warning_cab1
    Cabinet_L2_Asymetrii = warning_cab2
    Cabinet_L3_Asymetrii = warning_cab3
    
    Watts = oee
    print('warning _temp', temp1, temp2, warning_temp1, warning_temp2,
               mot1, mot2, mot3, warning_mot1, warning_mot2, warning_mot3,
               cab1, cab2, cab3, warning_cab1, warning_cab2, warning_cab3,)
    print('')
    content1 = str(round(temp1[0], 3))
    content2 = str(round(temp2[0], 3))
    content3 = str(date[0])
    content4 = str(round(Watts[0], 2))
    content5 = str(round(cab1[0], 3))
    content6 = str(round(cab2[0], 3)) 
    content7 = str(round(cab3[0], 3))
    content8 = str(round(mot1[0], 3))
    content9 = str(round(mot2[0], 3))
    content10 = str(round(mot3[0], 3))
    content11 = str(input1[0])
    content12 = str(input2[0])
    content13 = str(input3[0])
    content14 = str(round(motor_asym_L1[0], 3))
    content15 = str(round(motor_asym_L2[0], 3))
    content16 = str(round(motor_asym_L3[0], 3))
    content17 = str(round(cabinet_asym_L1[0], 3))
    content18 = str(round(cabinet_asym_L2[0], 3))
    content19 = str(round(cabinet_asym_L3[0], 3))
    content20 = str(round(cabinet_amperage[0], 3))
    content21 = str(round(motor_amperage[0], 3))
    content22 = str(round(day_kWh[0], 3))
    content23 = str(round(biggest_kWh[0], 3))
    content24 = str(round(average_kWh[0], 3))


    if warning_temp1[0]==1:
        temp_indicator_div_style1 = {
            # 'width': '300px',
            'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer1 = 1
        emer_info = 'temp1'
        
    else:
        temp_indicator_div_style1 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }

        emer1 = 0

    if warning_temp2[0]==1:
        temp_indicator_div_style2 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }

        emer2 = 1
        emer_info = 'temp2'
    else:
        temp_indicator_div_style2 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer2 = 0

    if warning_cab1[0]==1:
        amper_indicator_div_style1 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer3 = 1
        emer_info = 'Cabinet L1'
    else:
        amper_indicator_div_style1 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer3 = 0

    if warning_cab2[0]==1:
        amper_indicator_div_style2 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer4 = 1
        emer_info = 'Cabinet L2'
    else:
        amper_indicator_div_style2 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer4 = 0

    if warning_cab3[0]==1:
        amper_indicator_div_style3 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer5 = 1
        emer_info = 'Cabinet L3'
    else:
        amper_indicator_div_style3 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer5 = 0
    if warning_mot1[0]==1:
        amper_indicator_div_style4 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer6 = 1
        emer_info = 'MotorL1'
    else:
        amper_indicator_div_style4 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer6 = 0

    if warning_mot2[0]==1:
        amper_indicator_div_style5 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer7 = 1
        emer_info = 'MotorL2'
    else:
        amper_indicator_div_style5 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer7 = 0
    if warning_mot3[0]==1:
        amper_indicator_div_style6 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer8 = 1
        emer_info = 'MotorL3'
    else:
        amper_indicator_div_style6 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer8 = 0
    if warning_input1[0]==1:
        input_indicator_div_style1 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer9 = 1
        emer_info = 'warning input1'
    else:
        input_indicator_div_style1 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer9 = 0
    if warning_input2[0]==1:
        input_indicator_div_style2 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer10 = 1
        emer_info = 'warning input2'
    else:
        input_indicator_div_style2 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer10 = 0
    if warning_input3[0]==1:
        input_indicator_div_style3 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': 'red',
            # 'margin': '10px 10px 10px 10px'
        }
        emer9 = 1
        emer_info = 'warning input1'
    else:
        input_indicator_div_style3 = {
            # 'width': '300px',
            # 'height': '100px',
            'border-radius': '10px',
            'position': 'relative',
            'border': 'solid 1px',

            # 'background': 'linear-gradient(45deg, #e7e7e7, #d1d1d1)',
            'background': '#ffffff',
            # 'margin': '10px 10px 10px 10px'
        }
        emer9 = 0


        
    text = ''
    emer=[emer1, emer2, emer3, emer4, emer5, emer6, emer7, emer8, emer9]
    if emer1 == 1 or emer2 == 1 or emer3 == 1 or emer4 == 1 or emer5 == 1 or emer6 == 1 or emer7 == 1 or emer8 == 1 or emer9 == 1 :
        #emergency_text = pd.read_csv('emergency_information.csv',delimiter="    ", header= None, engine='python')
        #print('emergency                      ', emergency_text[0])
        print(emer)
        for i in range(len(emer)):
            if emer[i] == 1:  
                print(i)  
                print(emergency_information['6'])
                text = text + emergency_information[str(i)] + '\n'
                print('emeri', emer[i])
        emergency_className = 'emergencyON'
    else:
        text = 'EMERGENCY OUTPUTS OFF'
        emergency_className = 'emergencyOFF'

    return content1, content2, content3, content4, content5, content6, content7, content8, content9, content10, content11, content12, content13,\
        temp_indicator_div_style1, temp_indicator_div_style2, \
        amper_indicator_div_style1, amper_indicator_div_style2, amper_indicator_div_style3,\
        amper_indicator_div_style4, amper_indicator_div_style5, amper_indicator_div_style6,\
        input_indicator_div_style1, input_indicator_div_style2, input_indicator_div_style3,\
        text, emergency_className,\
        content14, content15, content16, content17, content18, content19, \
        content20, content21, content22,\
        content23, content24,
cName1 = ''
cName2 = ''
cName3 = ''

bufor = []
columns = ['data1', 'data2',  'cabinet_L1', 'cabinet_L2', 'cabinet_L3', 'motor_L1', 'motor_L2', 'motor_L3','temp_1', 'temp_2', 'input_1', 'input_2', 'input_3', 'output_1', 'output_2', 'output_3', 'kWh', 'OnOff']

@app.callback(
    [Output('graph-temperature', 'figure'),
    Output('graph-OEE', 'figure'),
    Output('graph-cabinet', 'figure'),
    Output('graph-motor', 'figure'),
     ],
    Input('interval-component2', 'n_intervals')
)

def Figures(n_intervals):
    global relays
    #SensValues = pd.read_csv(__plot_path,delimiter="\s+", names=columns, dtype=dtypes, engine='python')
    #SensValues = SensValues.iloc[-5:]


    conn = sqlite3.connect('/home/pi/venv/raspberry2/sensor_new.db')
    query = 'SELECT update_time, temperature_sensor_1, temperature_sensor_2, cabinet_L1, cabinet_L2, cabinet_L3, motor_L1, motor_L2, motor_L3, kW FROM data_center ORDER BY update_time DESC LIMIT 10000'
    SensValuesDB = pd.read_sql_query(query, conn)
    #print('leeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeen', len(SensValuesDB))
    conn.close()
    #pizda = SensValuesDB['current_sensor_1']
    #print(type(SensValuesDB['update_time'][0]))
    
    
    #print('sensvalue', SensValues['temp_1'][:1]q)
    #jebana_data = f"{str(SensValues['data1'].iloc[0])} {str(SensValues['data2'].iloc[0])}"
    #godziny = SensValues['data1'] + ' ' +SensValues['data2']
    
    #jebana_data = f"{str(SensValues['data1'].iloc[0])} {str(SensValues['data2'].iloc[0])}"
    #godziny = SensValues['data1'] + ' ' +SensValues['data2']
    
    #for i in range(len(godziny)):
    #    godziny[i] = datetime.datetime.strptime(godziny[i], '%d/%m/%Y, %H:%M:%S.%f') 

    #def convert_to_datetime(string_time):
    #    return datetime.strptime(string_time, '%d%m%Y, %H:%M:%S.%f')

    # Przetworzenie kolumny 'update_time' w DataFrame na typ datetime
    #data['update_time'] = data['update_time'].apply(convert_to_datetime)

    SensValuesDB['update_time'] = SensValuesDB['update_time'].apply(lambda x: datetime.datetime.strptime(x, '%d/%m/%Y, %H:%M:%S.%f'))

    #SensValuesDB['update_time'] = SensValuesDB['update_time'].apply()
    #for i in range(len(SensValuesDB['update_time'])):
    #    SensValuesDB['update_time'].iloc[i] = datetime.datetime.strptime(SensValuesDB['update_time'].iloc[i], '%d/%m/%Y, %H:%M:%S.%f') 

    print(type(SensValuesDB['update_time'][0]))
    temp1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['temperature_sensor_1'], 
                       #fill='tozeroy', fillcolor='rgba(133, 203, 204, 0.2)',
                       line=dict(color="rgba(10, 203, 204, 1)"))

    temp2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['temperature_sensor_2'], 
                       #fill='tozeroy', fillcolor='rgba(168, 222, 224, 0.2)',
                      line=dict(color="rgba(10, 203, 204, 1)"))

    cabinetL1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['cabinet_L1'], 
                           #fill='tozeroy', fillcolor='rgba(133, 203, 204, 0.2)',
                       line=dict(
                        color="brown"#"rgba(10, 203, 204, 1)"
                        ))

    cabinetL2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['cabinet_L2'], 
                           #fill='tozeroy', fillcolor='rgba(133, 203, 204, 0.2)',
                           line=dict(
                            color="black"#"rgba(10, 203, 204, 1)"
                            ))

    cabinetL3 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['cabinet_L3'], #fill='tozeroy',
                           #fillcolor='rgba(133, 203, 204, 0.2)',
                           line=dict(
                            color="grey"#"rgba(10, 203, 204, 1)"
                            ))

    motorL1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['motor_L1'], #fill='tozeroy',
                           #fillcolor='rgba(133, 203, 204, 0.2)',
                           line=dict(
                            color="brown"#"rgba(10, 203, 204, 1)"
                            ))
    motorL2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['motor_L2'], #fill='tozeroy',
                           #fillcolor='rgba(133, 203, 204, 0.2)',
                           line=dict(
                            color="black"#"rgba(10, 203, 204, 1)"
                            ))
    motorL3 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['motor_L3'], #fill='tozeroy',
                           #fillcolor='rgba(133, 203, 204, 0.2)',
                           line=dict(
                            color="grey"#"rgba(10, 203, 204, 1)"
                            ))

    OEE1 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['kW'], #fill='tozeroy',
                           #fillcolor='rgba(133, 203, 204, 0.2)',
                           line=dict(
                            color="rgba(10, 203, 204, 1)"
                            ),
                      line_shape='hv'
                      )

    OEE2 = go.Scatter(x=SensValuesDB['update_time'], y=SensValuesDB['kW'], #fill='tozeroy',
                           line=dict(
                            color="rgba(10, 203, 204, 1)"
                            ),
                      #line_shape='hv'
                      )

    layout = go.Layout(
        paper_bgcolor="rgba(1, 1, 1, 0.0)",
        plot_bgcolor='rgba(1, 1, 1, 0.0)',
        font=dict(color='black'),
        xaxis=dict(showgrid=False,
                   gridcolor='black',
                   tickformat='%H %M %S'),
        yaxis=dict(showgrid=True,
                   gridcolor='#d7d7d7'), showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        
    )
    
    return [go.Figure(data=[temp1, temp2], layout=layout),
            go.Figure(data=[OEE1], layout=layout),
            go.Figure(data=[cabinetL1, cabinetL2, cabinetL3], layout=layout),
            go.Figure(data=[motorL1, motorL2, motorL3], layout=layout),]
    
@app.callback(
    Output("download-text", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True,
    )
def func(n_clicks):
    conn = sqlite3.connect('sensor_new.db')
    cursor = conn.cursor()
    cursor.execute("select * from data_center;")
    with open(__plot_path, 'w',newline='') as csv_file: 
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description]) 
        csv_writer.writerows(cursor)
    conn.close()
    return dcc.send_file(__plot_path)

# Funkcja callback do zapisywania adresu IP do pliku po naciśnięciu przycisku
@app.callback(Output('ip-input', 'value'),
              Input('button-set-ip', 'n_clicks'),
              State('ip-input', 'value'))
def set_ip_value(n_clicks, ip_value):
    try:
        # Zmień adres IP interfejsu eth0
        subprocess.run(['sudo', 'ifconfig', 'eth0', ip_value, 'netmask', '255.255.255.0'])
        
        # Wyświetlenie potwierdzenia
        print(f'Adres IP interfejsu Ethernet zmieniony na: {ip_value}')
    except Exception as e:
        print(f'Wystąpił błąd: {e}')

# Użyj tej funkcji, podając nowy adres IP jako argument
#nowy_adres_ip_ethernet = '192.168.1.212'  # Podaj nowy adres IP interfejsu Ethernet
    # Zwróć aktualną wartość adresu IP
    return ip_value

# Funkcja callback do zapisywania adresu IP do pliku po naciśnięciu przycisku
@app.callback(Output('hostname-input', 'value'),
              Output('Main-title', 'children'),
              Input('button-set-hostname', 'n_clicks'),
              State('hostname-input', 'value'))
def set_ip_value(n_clicks, hostname):
    # Sprawdź, czy przycisk został naciśnięty
    if n_clicks > 0 and hostname:
        # Zapisz adres IP do pliku 'IP.csv'
        try:
            # Zmiana nazwy w pliku /etc/hostname
                        
            subprocess.run(['sudo', 'hostnamectl', 'set-hostname', hostname])

            # Modyfikacja nazwy w pliku /etc/hosts
            with open('/etc/hosts', 'r') as file:
                lines = file.readlines()
            
            with open('/etc/hosts', 'w') as file:
                for line in lines:
                    if '127.0.1.1' in line:
                        file.write(f'127.0.1.1\t{hostname}\n')
                    else:
                        file.write(line)
            
            print(f"Pomyślnie zmieniono hostname na {hostname}")
        except Exception as e:
            print(f"Wystąpił błąd podczas zmiany hostname: {e}")

        # Zresetuj licznik kliknięć przycisku
        n_clicks = 0

    # Zwróć aktualną wartość adresu IP
    return hostname, "STAN PRASY " + str(hostname_start)



if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True, port=8050)
    #app.run(host= '192.168.1.88', debug=True, port=8050)