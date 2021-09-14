from dash.development.base_component import Component
import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import dash_table
from os import listdir
from os.path import isfile, join

# Connect to your app pages
#from apps import cumulative, split
from app import app

# ---------- Importing Inputs and Results


mypath = r'C:\Users\alvin\Desktop\University\Year 4 Term 2\Thesis\Thesis B\Simulation\Actual\Results'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
filename_type = []
for y in onlyfiles:
    y = y.replace(' - Inputs.json', "")
    y = y.replace(' - Results.json', "")
    y = y.replace(' - Cost.json',"")
    filename_type.append(y)
filename_type = list(set(filename_type))
print(filename_type)
filename_type1 = filename_type[0]

simulation_type = filename_type1
input_filename_x = simulation_type + ' - Inputs.json'
input_filename = join(mypath,input_filename_x)
inputs = pd.read_json (input_filename)
inputs =inputs.T
inputs = inputs.reset_index()

# ------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col(html.H1('Energy Storage Simulation',
            className='text-center text-primary mb-4'),
            width = 12),
        dcc.Store(id='storage_df')    
    ]),
    dbc.Row(
        dbc.Col([dcc.Dropdown(
        id='simulation_select',
        options=[
            {'label': i, 'value': i} for i in filename_type],
            value = filename_type1)
        ],width = 6),justify = 'center'),

    html.Br(),

    # dbc.Row([
    #     dash_table.DataTable(
    #         id = 'stor_info',
    #         columns=[{"name": i, "id": i} for i in inputs.columns],
    #         data=inputs.to_dict('records')
    #         )
    # ], justify = 'center'),

    # dbc.Row([
    #     dcc.Location(id='url', refresh=False),
    #     html.Div([
    #         dcc.Link('Cumulative Graphs|', href='/apps/cumulative'),
    #         dcc.Link('Split Graphs', href='/apps/split'),
    #     ], className="row"),
    #     dbc.Col(id='page-content', children=[], width = 12)
    # ], justify = 'center'),  
    
    #New South Wales
    dbc.Card([
        dbc.Row([html.H2('New South Wales',className='text-center text-light my-4 mb-4')], justify = 'center'),

        dbc.Row([
            #--------------------------------------NSW LCOE--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('LCOE',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'lcoe_nsw',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------NSW Storage Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Storage Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'storcost_nsw',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------NSW Generation Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Generation Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'generation_nsw',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------NSW RE Factor--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Renewable Factor',className='text-center text-dark my-4 mb-4'),
                        html.H1(id = 'nsw_re',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------NSW Unused Energy--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Unused Energy',className='text-center text-dark my-4 mb-4'),
                        html.H1(id = 'nsw_unused',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------NSW Power Capacity--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Power Capacity (MW)',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Flywheels:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5(id = 'nsw_fly',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Batteries:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'nsw_batt',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Pumped Hydro:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'nsw_phes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Compressed Air:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'nsw_caes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Hydrogen:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'nsw_hyd',className='text-center text-dark my-2 mb-2', )])
                        ]),
                ], color="light")
            ],width = 2),
        ], justify = 'center'),
        html.Br(),
        dbc.Row([
            #--------------------------------------NSW Storage Cumulative Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([ html.H4('Storage Cumulative',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'NSW_cumulative')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 7),
            #--------------------------------------NSW Storage Capacity Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Storage Capacity (MWh)',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'NSW_stor_cap')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 3),
        ],justify = 'center'),
        html.Br(),
    ], color = 'dark'),
    html.Br(),
    #Queensland
    dbc.Card([
        dbc.Row([html.H2('Queensland',className='text-center text-light my-4 mb-4')], justify = 'center'),

        dbc.Row([
            #--------------------------------------QLD LCOE--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('LCOE',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'lcoe_qld',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------QLD Storage Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Storage Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'storcost_qld',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------QLD Generation Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Generation Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'generation_qld',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------QLD Reneawble Factor--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Renewable Factor',className='text-center text-dark my-4 mb-4 vertical-align: middle'),
                        html.H1(id = 'qld_re',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),

            #--------------------------------------QLD Unused Energy--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Unused Energy',className='text-center text-dark my-4 mb-4'),
                        html.H1(id = 'qld_unused',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------QLD Power Capacity--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Power Capacity (MW)',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Flywheels:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5(id = 'qld_fly',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Batteries:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'qld_batt',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Pumped Hydro:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'qld_phes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Compressed Air:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'qld_caes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Hydrogen:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'qld_hyd',className='text-center text-dark my-2 mb-2', )])
                        ]),
                ], color="light")
            ],width = 2),
        ], justify = 'center'),
        html.Br(),
        dbc.Row([
            #--------------------------------------QLD Storage Cumulative Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([ html.H4('Storage Cumulative',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'QLD_cumulative')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 7),
            #--------------------------------------QLD Storage Capacity Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Storage Capacity (MWh)',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'QLD_stor_cap')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 3),
        ],justify = 'center'), 
    ], color = 'dark'),
    html.Br(),
     #Victoria
    dbc.Card([
        dbc.Row([html.H2('Victoria',className='text-center text-light my-4 mb-4')], justify = 'center'),

        dbc.Row([
            #--------------------------------------VIC LCOE--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('LCOE',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'lcoe_vic',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------VIC Storage Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Storage Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'storcost_vic',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------VIC Generation Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Generation Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'generation_vic',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------VIC Reneawble Factor--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Renewable Factor',className='text-center text-dark my-4 mb-4 vertical-align: middle'),
                        html.H1(id = 'vic_re',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------VIC Unused Energy--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Unused Energy',className='text-center text-dark my-4 mb-4'),
                        html.H1(id = 'vic_unused',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------VIC Power Capacity--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Power Capacity (MW)',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Flywheels:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5(id = 'vic_fly',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Batteries:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'vic_batt',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Pumped Hydro:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'vic_phes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Compressed Air:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'vic_caes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Hydrogen:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'vic_hyd',className='text-center text-dark my-2 mb-2', )])
                        ]),
                ], color="light")
            ],width = 2),
        ], justify = 'center'),
        html.Br(),
        dbc.Row([
            #--------------------------------------VIC Storage Cumulative Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([ html.H4('Storage Cumulative',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'VIC_cumulative')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 7),
            #--------------------------------------VIC Storage Capacity Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Storage Capacity (MWh)',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'VIC_stor_cap')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 3),
        ],justify = 'center'), 
    ], color = 'dark'),
    html.Br(),
     #Tasmania
   dbc.Card([
        dbc.Row([html.H2('Tasmania',className='text-center text-light my-4 mb-4')], justify = 'center'),

        dbc.Row([
            #--------------------------------------TAS LCOE--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('LCOE',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'lcoe_tas',className='text-center text-dark my-5 mb-5')])
                            ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------TAS Storage Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Storage Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'storcost_tas',className='text-center text-dark my-5 mb-5')])
                    ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------TAS Generation Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Generation Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'generation_tas',className='text-center text-dark my-5 mb-5')])
                    ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------TAS Reneawble Factor--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Renewable Factor',className='text-center text-dark my-4 mb-4 vertical-align: middle'),
                        html.H1(id = 'tas_re',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------TAS Unused Energy--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Unused Energy',className='text-center text-dark my-4 mb-4'),
                        html.H1(id = 'tas_unused',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------TAS Power Capacity--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Power Capacity (MW)',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Flywheels:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5(id = 'tas_fly',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Batteries:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'tas_batt',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Pumped Hydro:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'tas_phes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Compressed Air:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'tas_caes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Hydrogen:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'tas_hyd',className='text-center text-dark my-2 mb-2', )])
                        ]),
                ], color="light")
            ],width = 2),
        ], justify = 'center'),
        html.Br(),
        dbc.Row([
            #--------------------------------------TAS Storage Cumulative Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([ html.H4('Storage Cumulative',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'TAS_cumulative')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 7),
            #--------------------------------------TAS Storage Capacity Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Storage Capacity (MWh)',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'TAS_stor_cap')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 3),
        ],justify = 'center'), 
    ], color = 'dark'),
    html.Br(),


     #South Australia
    dbc.Card([
        dbc.Row([html.H2('South Australia',className='text-center text-light my-4 mb-4')], justify = 'center'),

        dbc.Row([
            #--------------------------------------SA LCOE--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('LCOE',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'lcoe_sa',className='text-center text-dark my-5 mb-5')])
                        ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------SA Storage Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Storage Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'storcost_sa',className='text-center text-dark my-5 mb-5')])
                        ]),  
                ], color="light")
            ],width = 2),
            #--------------------------------------SA Generation Cost--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Total Generation Cost',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H1(id = 'generation_sa',className='text-center text-dark my-5 mb-5')])
                            ]),
                ], color="light")
            ],width = 2),
            #--------------------------------------SA Reneawble Factor--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Renewable Factor',className='text-center text-dark my-4 mb-4 vertical-align: middle'),
                        html.H1(id = 'sa_re',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------SA Unused Energy--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Unused Energy',className='text-center text-dark my-4 mb-4'),
                        html.H1(id = 'sa_unused',className='text-center text-dark my-5 mb-5')
                ], color="light")
            ],width = 2),
            #--------------------------------------SA Power Capacity--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Power Capacity (MW)',className='text-center text-dark my-4 mb-4'),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Flywheels:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5(id = 'sa_fly',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Batteries:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'sa_batt',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Pumped Hydro:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'sa_phes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Compressed Air:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'sa_caes',className='text-center text-dark my-2 mb-2')])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5('Hydrogen:',className='text-center text-dark my-2 mb-2')]),
                            dbc.Col([
                                html.H5('',id = 'sa_hyd',className='text-center text-dark my-2 mb-2', )])
                        ]),
                ], color="light")
            ],width = 2),
        ], justify = 'center'),
        html.Br(),
        dbc.Row([
            #--------------------------------------SA Storage Cumulative Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([ html.H4('Storage Cumulative',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'SA_cumulative')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 7),
            #--------------------------------------SA Storage Capacity Graph--------------------------------------------------------------
            dbc.Col([
                dbc.Card([html.H4('Storage Capacity (MWh)',className='text-center text-dark my-4 mb-4'),
                    dcc.Graph(id = 'SA_stor_cap')
                ], color = 'light', style = {'height':'55vh'})
            ],width = 3),
        ],justify = 'center'), 
    ], color = 'dark'),
    html.Br(),   
], fluid = True)

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# @app.callback(Output(component_id='storage_df', component_property = 'data'),
#             Input('results', 'data'))


@app.callback([#Output('page-content', 'children'),
                #Output(component_id='storage_df', component_property = 'data'),
                #Output(component_id='stor_info', component_property = 'data'),
                Output(component_id = 'nsw_re',component_property = 'children'),
                Output(component_id = 'qld_re',component_property = 'children'),
                Output(component_id = 'vic_re',component_property = 'children'),
                Output(component_id = 'tas_re',component_property = 'children'),
                Output(component_id = 'sa_re',component_property = 'children'),
                Output(component_id = 'nsw_fly',component_property = 'children'),
                Output(component_id = 'nsw_batt',component_property = 'children'),
                Output(component_id = 'nsw_phes',component_property = 'children'),
                Output(component_id = 'nsw_caes',component_property = 'children'),
                Output(component_id = 'nsw_hyd',component_property = 'children'),
                Output(component_id = 'lcoe_nsw',component_property = 'children'),
                Output(component_id = 'storcost_nsw',component_property = 'children'),
                Output(component_id = 'generation_nsw',component_property = 'children'),
                Output(component_id = 'qld_fly',component_property = 'children'),
                Output(component_id = 'qld_batt',component_property = 'children'),
                Output(component_id = 'qld_phes',component_property = 'children'),
                Output(component_id = 'qld_caes',component_property = 'children'),
                Output(component_id = 'qld_hyd',component_property = 'children'),
                Output(component_id = 'lcoe_qld',component_property = 'children'),
                Output(component_id = 'storcost_qld',component_property = 'children'),
                Output(component_id = 'generation_qld',component_property = 'children'),
                Output(component_id = 'vic_fly',component_property = 'children'),
                Output(component_id = 'vic_batt',component_property = 'children'),
                Output(component_id = 'vic_phes',component_property = 'children'),
                Output(component_id = 'vic_caes',component_property = 'children'),
                Output(component_id = 'vic_hyd',component_property = 'children'),
                Output(component_id = 'lcoe_vic',component_property = 'children'),
                Output(component_id = 'storcost_vic',component_property = 'children'),
                Output(component_id = 'generation_vic',component_property = 'children'),
                Output(component_id = 'tas_fly',component_property = 'children'),
                Output(component_id = 'tas_batt',component_property = 'children'),
                Output(component_id = 'tas_phes',component_property = 'children'),
                Output(component_id = 'tas_caes',component_property = 'children'),
                Output(component_id = 'tas_hyd',component_property = 'children'),
                Output(component_id = 'lcoe_tas',component_property = 'children'),
                Output(component_id = 'storcost_tas',component_property = 'children'),
                Output(component_id = 'generation_tas',component_property = 'children'),
                Output(component_id = 'sa_fly',component_property = 'children'),
                Output(component_id = 'sa_batt',component_property = 'children'),
                Output(component_id = 'sa_phes',component_property = 'children'),
                Output(component_id = 'sa_caes',component_property = 'children'),
                Output(component_id = 'sa_hyd',component_property = 'children'),
                Output(component_id = 'lcoe_sa',component_property = 'children'),
                Output(component_id = 'storcost_sa',component_property = 'children'),
                Output(component_id = 'generation_sa',component_property = 'children'),
                Output(component_id = 'NSW_cumulative', component_property = 'figure'),
                Output(component_id = 'QLD_cumulative', component_property = 'figure'),
                Output(component_id = 'VIC_cumulative', component_property = 'figure'),
                Output(component_id = 'TAS_cumulative', component_property = 'figure'),
                Output(component_id = 'SA_cumulative', component_property = 'figure'),
                Output(component_id = 'NSW_stor_cap', component_property = 'figure'),
                Output(component_id = 'QLD_stor_cap', component_property = 'figure'),
                Output(component_id = 'VIC_stor_cap', component_property = 'figure'),
                Output(component_id = 'TAS_stor_cap', component_property = 'figure'),
                Output(component_id = 'SA_stor_cap', component_property = 'figure')
                ],
              [Input('simulation_select','value'),
              #Input('url', 'pathname')
              ])

def display_page(simulation_type):

    if simulation_type != None:

        result_filename_x = simulation_type + ' - Results.json'
        input_filename_x = simulation_type + ' - Inputs.json'
        cost_filename_x = simulation_type + ' - Cost.json'
        result_filename = join(mypath, result_filename_x)
        input_filename = join(mypath,input_filename_x)
        cost_filename = join(mypath,cost_filename_x)
        inputs = pd.read_json (input_filename)
        inputs =inputs.T
        #inputs = inputs.reset_index()
        results = pd.read_json (result_filename)
        cost = pd.read_json(cost_filename)
    print(str(simulation_type))

    storage = results.copy()
    stor_cap = inputs['Storage Capacity (MWh)']

    #NSW
    #Power Capacity 
    nsw_fly = inputs.loc['NSW Flywheels']['Power Capacity (MW)']
    nsw_batt = inputs.loc['NSW Batt']['Power Capacity (MW)']
    nsw_phes = inputs.loc['NSW PHES']['Power Capacity (MW)']
    nsw_caes = inputs.loc['NSW CAES']['Power Capacity (MW)']
    nsw_hyd = inputs.loc['NSW Hydrogen']['Power Capacity (MW)']
    nsw_re = inputs.loc['NSW Renewable Factor']['Renewable Factor']
    #Storage Capacity
    target_row = [row for row in stor_cap.index if 'NSW' in row and 'Renewable Factor' not in row]
    NSW_stor_df = stor_cap[target_row]
    NSW_stor_cap = px.pie(labels=target_row, values=NSW_stor_df.values, names = target_row)

    #Cost
    nsw_lcoe = cost.loc['NSW']['LCOE ($AUD/MWh)']
    nsw_storcost = cost.loc['NSW']['Storage Cost ($ Billion AUD)']
    nsw_gencost = cost.loc['NSW']['Generation Cost ($ Billion AUD)']

    #Cumulative Storage
    NSW_storage = storage.iloc[:,0:5]
    NSW_storage = NSW_storage.iloc[:, ::-1]

    NSW_cumulative = px.area(NSW_storage)
    
    #QLD
    #Power Capacity
    qld_fly = inputs.loc['QLD Flywheels']['Power Capacity (MW)']
    qld_batt = inputs.loc['QLD Batt']['Power Capacity (MW)']
    qld_phes = inputs.loc['QLD PHES']['Power Capacity (MW)']
    qld_caes = inputs.loc['QLD CAES']['Power Capacity (MW)']
    qld_hyd = inputs.loc['QLD Hydrogen']['Power Capacity (MW)']
    qld_re = inputs.loc['QLD Renewable Factor']['Renewable Factor']

    #Storage Capacity
    target_row = [row for row in stor_cap.index if 'QLD' in row and 'Renewable Factor' not in row]
    QLD_stor_df = stor_cap[target_row]
    QLD_stor_cap = px.pie(labels=target_row, values=QLD_stor_df.values, names = target_row)

    #Cost
    qld_lcoe = cost.loc['QLD']['LCOE ($AUD/MWh)']
    qld_storcost = cost.loc['QLD']['Storage Cost ($ Billion AUD)']
    qld_gencost = cost.loc['QLD']['Generation Cost ($ Billion AUD)']

    #Cumulative Storage
    QLD_storage = storage.iloc[:,6:11]
    QLD_storage = QLD_storage.iloc[:, ::-1]
    QLD_cumulative = px.area(QLD_storage)

    #VIC
    #Power Capacity
    vic_fly = inputs.loc['VIC Flywheels']['Power Capacity (MW)']
    vic_batt = inputs.loc['VIC Batt']['Power Capacity (MW)']
    vic_phes = inputs.loc['VIC PHES']['Power Capacity (MW)']
    vic_caes = inputs.loc['VIC CAES']['Power Capacity (MW)']
    vic_hyd = inputs.loc['VIC Hydrogen']['Power Capacity (MW)']
    vic_re = inputs.loc['VIC Renewable Factor']['Renewable Factor']

    #Storage Capacity
    target_row = [row for row in stor_cap.index if 'VIC' in row and 'Renewable Factor' not in row]
    VIC_stor_df = stor_cap[target_row]
    VIC_stor_cap = px.pie(labels=target_row, values=VIC_stor_df.values, names = target_row)

    #Cost
    vic_lcoe = cost.loc['VIC']['LCOE ($AUD/MWh)']
    vic_storcost = cost.loc['VIC']['Storage Cost ($ Billion AUD)']
    vic_gencost = cost.loc['VIC']['Generation Cost ($ Billion AUD)']

    #Cumulative Storage
    VIC_storage = storage.iloc[:,12:17]
    VIC_storage = VIC_storage.iloc[:, ::-1]
    VIC_cumulative = px.area(VIC_storage)

    #TAS
    #Power Capacity
    tas_fly = inputs.loc['TAS Flywheels']['Power Capacity (MW)']
    tas_batt = inputs.loc['TAS Batt']['Power Capacity (MW)']
    tas_phes = inputs.loc['TAS PHES']['Power Capacity (MW)']
    tas_caes = inputs.loc['TAS CAES']['Power Capacity (MW)']
    tas_hyd = inputs.loc['TAS Hydrogen']['Power Capacity (MW)']
    tas_re = inputs.loc['TAS Renewable Factor']['Renewable Factor']

    #Storage Capacity
    target_row = [row for row in stor_cap.index if 'TAS' in row and 'Renewable Factor' not in row]
    TAS_stor_df = stor_cap[target_row]
    TAS_stor_cap = px.pie(labels=target_row, values=TAS_stor_df.values, names = target_row)

    #Cost
    tas_lcoe = cost.loc['TAS']['LCOE ($AUD/MWh)']
    tas_storcost = cost.loc['TAS']['Storage Cost ($ Billion AUD)']
    tas_gencost = cost.loc['TAS']['Generation Cost ($ Billion AUD)']

    #Cumulative Storage
    TAS_storage = storage.iloc[:,18:23]
    TAS_storage = TAS_storage.iloc[:, ::-1]
    TAS_cumulative = px.area(TAS_storage)

    #SA
    #Power Capacity
    sa_fly = inputs.loc['SA Flywheels']['Power Capacity (MW)']
    sa_batt = inputs.loc['SA Batt']['Power Capacity (MW)']
    sa_phes = inputs.loc['SA PHES']['Power Capacity (MW)']
    sa_caes = inputs.loc['SA CAES']['Power Capacity (MW)']
    sa_hyd = inputs.loc['SA Hydrogen']['Power Capacity (MW)']
    sa_re = inputs.loc['SA Renewable Factor']['Renewable Factor']

    #Storage Capacity
    target_row = [row for row in stor_cap.index if 'SA' in row and 'Renewable Factor' not in row]
    SA_stor_df = stor_cap[target_row]
    SA_stor_cap = px.pie(labels=target_row, values=SA_stor_df.values, names = target_row)

    #Cost
    sa_lcoe = cost.loc['SA']['LCOE ($AUD/MWh)']
    sa_storcost = cost.loc['SA']['Storage Cost ($ Billion AUD)']
    sa_gencost = cost.loc['SA']['Generation Cost ($ Billion AUD)']

    #Cumulative Storage
    SA_storage = storage.iloc[:,24:29]
    SA_storage = SA_storage.iloc[:, ::-1]
    SA_cumulative = px.area(SA_storage)


    #input_col = [{"name": i, "id": i} for i in inputs.columns]
    data = inputs.to_dict('records')
    # if pathname == '/apps/cumulative':
    #     x = cumulative.layout
    # # elif pathname == '/apps/split':
    # #     x= split.layout
    # else:
    #     x= "404 Page Error! Please choose a link"   
    
    return (nsw_re, vic_re, vic_re, tas_re, sa_re, 
            nsw_fly, nsw_batt, nsw_phes, nsw_caes, nsw_hyd, nsw_lcoe, nsw_storcost, nsw_gencost,
            qld_fly, qld_batt, qld_phes, qld_caes, qld_hyd, qld_lcoe, nsw_storcost, nsw_gencost,
            vic_fly, vic_batt, vic_phes, vic_caes, vic_hyd, vic_lcoe, vic_storcost, vic_gencost,
            tas_fly, tas_batt, tas_phes, tas_caes, tas_hyd, tas_lcoe, tas_storcost, tas_gencost,
            sa_fly, sa_batt, sa_phes, sa_caes, sa_hyd, sa_lcoe, sa_storcost, sa_gencost,
            NSW_cumulative, QLD_cumulative, VIC_cumulative, TAS_cumulative, SA_cumulative,
            NSW_stor_cap, QLD_stor_cap, VIC_stor_cap, TAS_stor_cap, SA_stor_cap)#, input_col)
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port = 3000)

1
