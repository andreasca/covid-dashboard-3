#!/usr/bin/python

import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import os
import pathlib
import re
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px





# GLOBAL VARIABLES
clear_trigger = 0




# PATHS
rootdir = pathlib.Path('.')
output_dir = rootdir / 'data'  # directory where the csv files are

csv_fpath = output_dir / 'reg_table.csv'

try:
    csv_fullpath = csv_fpath.resolve(strict=True)
except FileNotFoundError:
    print(f'CSV file not found: {csv_fpath}')
    raise
else:
    df = pd.read_csv(csv_fpath)

#print(df.head())




locations = df['CountryName'].unique().tolist()
# 


age_bands = ['0_14', '15_64', '65_74', '75_84', '85p', '64m', '65p','Total']


all_options = { location: age_bands for location in locations}


# Create Dash/Flask app
app = dash.Dash(
    __name__,
    # external_stylesheets = [
    #     dbc.themes.SLATE,  # Bootswatch theme
    #     "https://use.fontawesome.com/releases/v5.9.0/css/all.css",],
    # meta_tags = [{
    #     "name": "description",
    #     "content": "Live coronavirus news, statistics, and visualizations tracking the number of cases and death toll due to COVID-19, with up-to-date testing center information by US states and counties. Also provides current SARS-COV-2 vaccine progress and treatment research across different countries. Sign up for SMS updates."},
    #     {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    # ]

) #(external_stylesheets = [dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions'] = True

final_table = html.Div([dash_table.DataTable(
                 id="final_table",
                 columns=[{"name": i, "id": i} for i in df.columns],
                 data=df.to_dict('records'),
         
                 style_cell={
                      'overflow': 'hidden',
                      'textOverflow': 'ellipsis',
                      'maxWidth': '50px'
                 },
       
                style_table={
                    'maxHeight': '700px',
                    'maxHeight': '400px',
                    'overflowY': 'scroll',
                    'border': 'thin lightgrey solid'
                },
          )
          ]) 

plot_display = html.Div([dcc.Graph(id='plot-excess')])

app.layout = html.Div(
                id = 'content',
                children=[
                    html.Div(
                        id="title",
                        children=[
                            html.H2(
                                'Excess Mortlaity Analysis by Levitt Lab ‪Stanford',
                                style={'color':  '#36393b', 
                                       'font-weight': 'bold',
                                       'font-size': '30px',
                                       'backgroundColor':'#EBF5FB',
                                       }
                            ),
                            html.P('METHODOLOGY:', style={'font-weight':'bold'}),
                            html.P(['We analize mortality data from https://www.mortality.org/Public/STMF/Outputs/stmf.csv. We calculate the weekly excess mortality since January 2020 by comparing the actual deaths to the expected number of deaths for a specific week. We use the weekly average values from 2017 to 2019 as a baseline. Normalized plots show mortality values per million population. ',html.Br(),'Age groups (years old) are defined as follows:',html.Br(),'0_14 - 0<=age<=14',html.Br(),'15_64 - 15<=age<=64',html.Br(),'65_74 - 65<=age<=74',html.Br(),'75_84 - 75<=age<=84',html.Br(),'85p - age>=85',html.Br(),'64m - 0<=age<=64',html.Br(),'65p - 65<=age',html.Br(),'Total - All ages combined']),

                
                        ],
                    ),
           #          dcc.Textarea(
        			# 	id='textarea-legend',
        			# 	value='We analize mortality data from https://www.mortality.org/Public/STMF/Outputs/stmf.csv.\nWe calculate the weekly excess mortality since January 2020 by comparing the actual deaths to the expected number of deaths for a specific week, using the average values from 2017 to 2019 as a baseline.\nAge groups (years old):\n     0_14 - 0<=age<=14\n     15_64 - 15<=age<=64\n     65_74 - 65<=age<=74\n     75_84 - 75<=age<=84\n     85p - age>=85\n     64m - 0<=age<=64\n     65p - 65<=age\n ',
        			# 	style={'width': '100%', 'height': 150},
        			# ),
                               
                    html.Div(
                        [ html.Label('Select a location'),
                            dcc.Dropdown(id='filter_loc_dropdown',
                                options=[{'label':loc, 'value':loc} for loc in locations],
                                placeholder="Select country",
                                value=locations[0],
                                multi=True,
                                style={"width": "50%"}),
                          html.Label('Select age group'),
                            dcc.Dropdown(id='filter_age_dropdown',
                                options=[{'label':age, 'value':age} for age in age_bands],
                                placeholder="Select age group",
                                value=age_bands[-1],
                                multi=True,
                            style={"width": "50%"}),
                    ]),    

                    html.Div(
                        dcc.RadioItems(
                        options=[
                            {'label': 'Non Normalized', 'value': 'vals'},
                            {'label': 'Normalized', 'value': 'normvals'},
                        ],
                        value='vals'
)  

                    ),

        
                    html.Div(id='display-selected-values'),
                    html.Div([plot_display]),
        #html.Div([final_table]),
 
     ]
 )

@app.callback(
    Output('filter_age_dropdown', 'options'),
    [Input('filter_loc_dropdown', 'value')])
def set_age_options(selected_country):
    print(selected_country, type(selected_country))
    
    if type(selected_country) == str:
        return [{'label': i, 'value': i} for i in all_options[selected_country]]
    else:
        return [{'label': i, 'value': i} for country in selected_country for i in all_options[country]]

@app.callback(Output('plot-excess', 'figure'),
    [Input('filter_loc_dropdown', 'value'),
    Input('filter_age_dropdown', 'value')])
def update_plot_excess(selected_location, selected_agegroup):
    print(selected_agegroup, type(selected_agegroup))
    
    if type(selected_location) == str:
        selected_location = [selected_location]
    if type(selected_agegroup) == str:
        selected_agegroup= [selected_agegroup]
    mask20 = df['Year']==2020
    mask21 = df['Year']==2021
    
    datatsets = ['']
    traces = ['']
    for loca in selected_location:
        maskc = df['CountryName'] == loca
        weeks20 = df[maskc & mask20]['Week'].values.tolist() 
        weeks21 = df[maskc & mask21]['Week'].values.tolist()
        year_week = [f'2020_{w}' for w in weeks20] + [f'2021_{w}' for w in weeks21]
        for age in selected_agegroup:
            colexp = 'ExpBaselineDeaths2020_' + age
            colext = 'ExtraDeathsOverBaseline_' + age
            cold = 'D_' + age
           # print(colexp, cold, colext)
            vals_ex = df[maskc & mask20][colexp].values.tolist() + list(df[maskc & mask21][colexp].values.tolist())
            vals20 = df[maskc & mask20][cold].values.tolist() + df[maskc & mask21][cold].values.tolist()
                
            l = [n for n, v in enumerate(vals20) if v > 0 ]
            last_week = l[-1] +  1
            ymax = max(vals20 + vals_ex)*1.1
            tot_extra= int(np.ceil(df[maskc & mask20][colext].sum())) + int(np.ceil(df[maskc & mask21][colext].sum()))
            
            traces.append(go.Scatter(
                                     {
                                        'x': year_week[:last_week],
                                        'y': vals20[:last_week],
                                        'mode': 'lines+markers',
                                        'name': f'{loca} {age} Weekly Deaths, Total excess = {tot_extra}',
                                     }
                                    )
                          )
            traces.append(go.Scatter(
                                     {
                                        'x': year_week[:last_week],
                                        'y': vals_ex[:last_week],
                                        'mode': 'lines+markers',
                                        'name': f'{loca} {age} Weekly Expected Deaths',
                                     }
                                    )
                          )
            
    traces.pop(0)
    layout = {'title': 'Weekly death counts vs expected death counts using a 2017-19 baseline'}
    fig = {'data': traces, 'layout': go.Layout(layout)}
    return go.Figure(fig)



if __name__ == '__main__':
    app.run_server(debug=False)
