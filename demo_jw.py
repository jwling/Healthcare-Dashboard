import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go
from dash import Dash
from dash.dependencies import Input, Output, State
import dash_daq as daq
import random

external_css = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "https://codepen.io/bcd/pen/KQrXdb.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

app = dash.Dash(__name__, external_stylesheets=external_css)

for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
               "https://codepen.io/bcd/pen/YaXojL.js"]

for js in external_js:
    app.scripts.append_script({"external_url": js})



# Bootstrap CSS:
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})

# Reading in data into variable df
df = pd.read_csv('./Dummy.csv')

#Retrieving Prediction data
dp = pd.read_csv('./Prediction_Dummy.csv')

#Naming
procedure_code = df['Procedure.Code'].unique()
surgeon_id = df['First.Surgeon.Staff.Id'].unique()
case_id = df['Case.No'].unique()


# Selecting only required columns
dummy_data = df[["Actual.Duration", "Listing.Duration", "Start.Time","Date"]].dropna()

#Data for Table
table_data = df[['Procedure.Code','First.Surgeon.Staff.Id','Actual.Duration','Listing.Duration']].dropna()

# Convert to date
dummy_data["Date"] = pd.to_datetime(dummy_data["Date"])
dummy_data["Start.Time"] = pd.to_datetime(dummy_data["Start.Time"]) #date is not unique
dummy_data = dummy_data.sort_values(by="Start.Time")

#(Qn: Why limit by date?)
dummy_data = dummy_data[dummy_data["Date"] > '01/02/2018']

# Add index to surgeries to number them
dummy_data['Index'] = np.arange(len(dummy_data))
dummy_data = dummy_data[dummy_data["Index"] < 80]

# Create Moving Average
mean_duration = dummy_data["Actual.Duration"].mean()
#(Qn: Why random choices?)
dummy_data["Moving.Average"] = random.choices([mean_duration-3, mean_duration, mean_duration+3], k=len(dummy_data))
dummy_data["Moving.Average.Upper"] = dummy_data["Moving.Average"]*1.1
dummy_data["Moving.Average.Lower"] = dummy_data["Moving.Average"]*0.9

################### COPY HERE for DURATION SLIDER COMPONENT ###################
#remember to CHANGE dummy_data variable to whatever you are using
#for slider component
dummy_data_min = int(dummy_data["Actual.Duration"].min())
dummy_data_max = int(dummy_data["Actual.Duration"].max())
#creating linear range of slider values, from min to max, integer, stepsize of 1
dummy_data_slider_values = np.arange(dummy_data_min,dummy_data_max+1,1).tolist()
#creating 5 marks/ ticks for the slider
dummy_data_slider_mark_values = np.linspace(dummy_data_min,dummy_data_max,5,dtype = int, endpoint=True).tolist()
d_marks={dummy_data_slider_mark_values[0]: {'label': 'min: {}'.format(str(dummy_data_slider_mark_values[0])), 'style': {'color': '#f50'}},
         dummy_data_slider_mark_values[1]: {'label': '{}'.format(str(dummy_data_slider_mark_values[1]))},
         dummy_data_slider_mark_values[2]: {'label': '{}'.format(str(dummy_data_slider_mark_values[2]))},
         dummy_data_slider_mark_values[3]: {'label': '{}'.format(str(dummy_data_slider_mark_values[3]))},
         dummy_data_slider_mark_values[4]: {'label': 'max: {}'.format(str(dummy_data_slider_mark_values[4])), 'style': {'color': '#77b0b1'}}
         }
#for slider description
dummy_data_length = len(dummy_data["Actual.Duration"])


################### COPY HERE for DURATION SLIDER COMPONENT ###################


actual_duration = go.Scatter(
    x=dummy_data['Start.Time'],
    y=dummy_data['Actual.Duration'],
    name='Actual',
    # text = 'Actual: ',
    mode='lines+markers',  # 'lines+markers','markers','lines'
    marker=dict(size=5,
                # line= dict(width=1),
                color=('rgb(205, 12, 24)'),
                # opacity= 0.3
                )
)

listing_duration = go.Scatter(
    x=dummy_data['Start.Time'],
    y=dummy_data['Listing.Duration'],
    name='Listing',
    mode='lines+markers',  # 'lines+markers','markers','lines'
    marker=dict(size=5,
                # line= dict(width=1),
                color=('rgb(22, 96, 167)'),
                # opacity= 0.3
                )
)

ma_duration = go.Scatter(
    x=dummy_data['Start.Time'],
    y=dummy_data['Moving.Average'],
    name='Moving Avg',
    mode='lines+markers',  # 'lines+markers','markers','lines'
    marker=dict(size=5,
                # line= dict(width=1),
                color=('green'),
                # opacity= 0.3
                )
)

ma_duration_upper = go.Scatter(
    x=dummy_data['Start.Time'],
    y=dummy_data['Moving.Average.Upper'],
    name='M.A. (80%)',
    # legendgroup = 'Moving Average',
    line=dict(
        color=('green'),
        width=0.5,
        dash='dot')
)

ma_duration_lower = go.Scatter(
    x=dummy_data['Start.Time'],
    y=dummy_data['Moving.Average.Lower'],
    name='M.A. (120%)',
    # legendgroup = 'Moving Average',
    line=dict(
        color=('green'),
        width=0.5,
        dash='dot')
)

data_dummy = [actual_duration, listing_duration, ma_duration, ma_duration_upper, ma_duration_lower]


# title = '<b>Historical Surgeries</b>',
layout_line = dict(
    # titlefont = {"size": 16},
    xaxis=dict(showticklabels=False,  # True
               autorange=True,
               rangeslider={"autorange": True},
               rangeselector=dict(
                   buttons=list([
                       dict(label='3M',
                            count=1,
                            step='month',
                            stepmode='backward'),
                       dict(label='6M',
                            count=2,
                            step='month',
                            stepmode='backward'),
                       dict(step='all')
                   ])
               ),
               type="date"),
    yaxis=dict(title='Surgical Duration (min)',
               anchor="x",
               autorange=True,
               linecolor="#1e1f26",
               showline=True,
               tickfont=dict(color="#3c2f2f"),
               tickmode="auto",
               ticks="",
               titlefont={"color": "#4a4e4d"},  # "family": 'Courier New, monospace',"size": 18,
               type="linear",
               zeroline=False),
    legend=dict(orientation="h", y=-0.25, x=0),  # y=1.135, x=0.25
    height=400,
    margin={'l': 50, 'b': 20, 't': 0, 'r': 5}
)



app.layout = html.Div(
    html.Div([
        html.Div([

            html.P(children='SingHealth Dashboard',
                   className="nine columns",
                   style={
                       'textAlign': 'left',
                       'fontWeight': 600,
                       'fontSize': 30,
                       'marginLeft': '1%',
                       'margin-Bottom': '10px',
                       'margin-Top': '10px',
                   }
                   ),

            # html.Img(
            #     src="/Users/jason/Documents/Singhealth-logo.png",
            #     className='three columns',
            #     style={
            #         'height': '10%',
            #         'width': '10%',
            #         'float': 'right',
            #         #'position': 'relative',
            #     },
            # ),

        ], className="row"),

        html.Div([
            # user input 1
            html.Div([
                html.P('Procedure Code',
                       className="gs-header gs-table-header padded",
                       style={
                           'textAlign': 'center',
                           'fontWeight': 600,
                           'fontSize': 15,
                           'marginLeft': '5px',
                       }),
                dcc.Dropdown(
                    id='Procedure Code',
                    options=[{'label': i, 'value': i} for i in procedure_code],
                    value='',
                    style={'fontSize': 10,
                           'marginLeft': '5px',
                           'marginRight': '5px',
                           }
                )
            ],
                className='two columns',
                style={'margin-bottom': '1%'}
            ),

            # user input 2
            html.Div([
                html.P('Surgeon-In-Charge ID',
                       className="gs-header gs-table-header padded",
                       style={
                           'textAlign': 'center',
                           'fontWeight': 600,
                           'fontSize': 15,
                           'marginLeft': '10px',
                       }),
                dcc.Dropdown(
                    id='First Surgeon ID',
                    options=[{'label': i, 'value': i} for i in surgeon_id],
                    value='',
                    style={'fontSize': 10,
                           'marginLeft': '5px',
                           'marginRight': '5px',
                           }
                ),
            ],
                className='two columns',
                style={'margin-bottom': '1%'}
            ),

            # user input 3
            html.Div([
                html.P('Case Number',
                       className="gs-header gs-table-header padded",
                       style={
                           'textAlign': 'center',
                           'fontWeight': 600,
                           'fontSize': 15,
                           'marginLeft': '5px',
                       }),
                dcc.Dropdown(
                    id='Case Number',
                    options=[{'label': i, 'value': i} for i in case_id],
                    value='',
                    style={'fontSize': 10,
                           'marginLeft': '3px',
                           'marginRight': '5px',
                           }
                ),
            ],
                className='two columns',
                style={'margin-bottom': '1%'}
            ),


            html.Div([
                html.Div([
                    html.P('Description of procedure:',
                           className="gs-header gs-table-header padded",
                           style={
                               #'marginLeft': '5px',
                               'marginRight': '5px',
                               'textAlign': 'center',
                               'fontWeight': 600,
                               'fontSize': 15
                           }),

                    html.Div(
                        id='result',
                        style={'fontSize': 15,
                               'marginLeft': '50px',
                               'marginRight': '10px',
                               'margin-Top': '45px'
                               }
                    ),
                ]),

            ],
                className='six columns',
                style={'margin-bottom': '1%'}
            ),

        ], className="row"),


        html.Div([

            # Descriptive info (Patient, Surgeon, Anaesthetist)
            html.Div([

                # Left Chunk
                html.Div([

                    #Patient
                    html.Div([
                        html.P('Patient',
                               className="gs-header gs-table-header padded",
                               style={
                                   #'textAlign': 'center',
                                   'textAlign': 'center',
                                   'fontWeight': 600,
                                   'fontSize': 15
                               }
                               ),

                        html.Div([
                            html.P('Age',
                                   style={
                                       'display': 'inline-block',
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600
                                   }
                                   ),

                            html.Div(
                                id='result_pa_1',
                                style={'fontSize': 10,
                                       #'marginLeft': '3px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),

                            html.Br(),

                            html.P('Gender',
                                   style={
                                       'display': 'inline-block',
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600
                                   }),

                            html.Div(
                                id='result_pa_2',
                                style={'fontSize': 10,
                                       #'marginLeft': '3px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),

                            html.Br(),

                            html.P('Race',
                                   style={
                                       'display': 'inline-block',
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600
                                   }),

                            html.Div(
                                id='result_pa_3',
                                style={'fontSize': 10,
                                       #'marginLeft': '3px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),

                            html.Br(),

                        ],
                            className='four columns',
                        ),

                        #html.Br(),


                        html.Div([
                            html.P('ASA Status',
                                   style={
                                       'display': 'inline-block',
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600
                                   }),

                            html.Div(
                                id='result_pa_4',
                                style={'fontSize': 10,
                                       #'marginLeft': '8px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),

                            html.Br(),

                            html.P('Op History',
                                   style={
                                       'display': 'inline-block',
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600
                                   }),

                            html.Div(
                                id='result_pa_5',
                                style={'fontSize': 10,
                                       #'marginLeft': '8px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),

                            html.Br(),

                            html.P('Type',
                                   style={
                                       'display': 'inline-block',
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600
                                   }),

                            html.Div(
                                id='result_pa_6',
                                style={'fontSize': 10,
                                       #'marginLeft': '8px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),
                            html.Br(),

                        ],
                            className='four columns',
                        ),

                        #html.Br(),

                        html.Div([
                            html.P('Priority',
                                   style={
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'display': 'inline-block'
                                   }),


                            html.Div(
                                id='result_pa_7',
                                style={'fontSize': 10,
                                       #'marginLeft': '8px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),
                            html.Br(),

                            html.P('Method',
                                   style={
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'display': 'inline-block'
                                   }),

                            html.Div(
                                id='result_pa_8',
                                style={'fontSize': 10,
                                       #'marginLeft': '8px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),
                            html.Br(),

                            html.P('Op Risk',
                                   style={
                                       'width': 120,
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'display': 'inline-block'
                                   }),

                            html.Div(
                                id='result_pa_9',
                                style={'fontSize': 10,
                                       #'marginLeft': '8px',
                                       #'marginRight': '5px',
                                       #'margin-Bottom': '10px'
                                       }
                            ),
                            html.Br(),

                        ],
                            className='three columns',
                        ),

                        #html.Br(),
                    ],
                        className='six columns',
                        style={'fontSize': 10,
                               'marginLeft': '5px',
                               'marginRight': '2%'
                               }
                    ),

                    # Surgeon
                    html.Div([
                        html.P('Surgeon',
                               className="gs-header gs-table-header padded",
                               style={
                                   'textAlign': 'center',
                                   'fontWeight': 600,
                                   'fontSize': 15,
                                   'marginLeft': '5px'
                               }
                               ),


                        html.Div([
                            html.P('Title',
                                   style={
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'marginLeft': '8px'
                                   }
                                   ),

                            html.Div(
                                id='result_su_1',
                                style={'fontSize': 10,
                                       'marginLeft': '8px',
                                       'marginRight': '5px',
                                       'margin-Bottom': '10px'
                                       }
                            ),

                        ],
                        ),

                        html.Br(),

                        html.Div([
                            html.P('Department',
                                   style={
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'marginLeft': '8px'
                                   }),

                            html.Div(
                                id='result_su_2',
                                style={'fontSize': 10,
                                       'marginLeft': '8px',
                                       'marginRight': '5px',
                                       'margin-Bottom': '10px'
                                       }
                            ),

                        ],
                        ),

                        html.Br(),

                        html.Div([
                            html.P('Staff ID', #Gender
                                   style={
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'marginLeft': '8px'
                                   }),

                            html.Div(
                                id='result_su_3',
                                style={'fontSize': 10,
                                       'marginLeft': '8px',
                                       'marginRight': '5px',
                                       'margin-Bottom': '10px'
                                       }
                            ),

                        ],
                        ),

                        html.Br(),

                    ],
                        className='three columns',
                        style={'fontSize': 10,
                               'marginRight': '2%'
                               #'marginLeft': '15px',
                               }
                    ),

                    # Anaesthetist
                    html.Div([
                        html.P('Anaesthetist',
                               className="gs-header gs-table-header padded",
                               style={
                                   'textAlign': 'center',
                                   'fontWeight': 600,
                                   'fontSize': 15,
                                   'marginLeft': '5px'}
                               ),

                        html.Div([
                            html.P('Title',
                                   style={
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'marginLeft': '8px',
                                       'margin-Bottom': '10px'
                                   }),


                        ],
                        ),
                        html.Div(
                            id='result_an_1',
                            style={'fontSize': 10,
                                   'marginLeft': '8px',
                                   'marginRight': '5px',
                                   'margin-Bottom': '10px'
                                   }
                        ),

                        html.Br(),

                        html.Div([
                            html.P('Staff ID',
                                   style={
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'marginLeft': '8px',
                                       'margin-Bottom': '10px'
                                   }),
                        ],
                        ),
                        html.Div(
                            id='result_an_2',
                            style={'fontSize': 10,
                                   'marginLeft': '8px',
                                   'marginRight': '5px',
                                   'margin-Bottom': '10px'
                                   }
                        ),


                        html.Br(),

                        html.Div([
                            html.P('Primary', #Anaesthetist
                                   style={
                                       'textAlign': 'Left',
                                       'fontSize': 12,
                                       'fontWeight': 600,
                                       'marginLeft': '8px'
                                   }),
                        ],
                        ),
                        html.Div(
                            id='result_an_3',
                            style={'fontSize': 10,
                                   'marginLeft': '8px',
                                   'marginRight': '5px',

                                   }
                        ),

                    ],
                        className='three columns',
                        style={'fontSize': 10,
                               #'marginLeft': '15px',
                               }
                    ),

                ], className='six columns',
                    # style={
                    #    'marginLeft': '5px',
                    #    'textAlign': 'center',
                    #    'fontWeight': 600,
                    #    'fontSize': 15}
                ),

                # Right Chunk
                html.Div([

                    html.P('Duration Visualisation',
                           className="gs-header gs-table-header padded",
                           style={
                               'marginRight': '5px',
                               'marginBottom': '60px',
                               'textAlign': 'center',
                               'fontWeight': 600,
                               'fontSize': 15,
                           }),

                    html.Div([

                        html.Div(daq.Slider(
                            min=dummy_data_min,
                            max=dummy_data_max,
                            value=135,  # model prediction
                            marks={'90': '10th Pct: {}'.format(str(90)),
                                   '140': 'MA Pred: {}'.format(str(140)),
                                   '190': '90th Pct: {}'.format(str(190))},
                            handleLabel={"showCurrentValue": True, "label": "Prediction"},
                            disabled=True,  # prevent movement
                            # vertical=True,
                        ), style={
                            'fontSize': 10,
                            'marginLeft': '20px',
                        }),
                    ],
                        className='seven columns'
                    ),

                    html.Div([
                        html.P('Place Holder for component',
                               style={
                                   'textAlign': 'center',
                                   'fontWeight': 600,
                                   'fontSize': 15,
                               }),
                    ],
                        className='five columns'
                    ),

                ],
                    className='six columns',
                    # style={
                    #     'fontSize': 10,
                    #     'marginLeft': '5px',
                    #     'marginRight': '5px',
                    # }
                ),

            ]),
        ], className="row"),

        # html.Div([
        #
        #     html.P('Duration Meter',
        #            className="gs-header gs-table-header padded",
        #            style={
        #                # 'width': 620,
        #                # marginLeft': '5px',
        #                'marginRight': '5px',
        #                'textAlign': 'center',
        #                'fontWeight': 600,
        #                'fontSize': 15}
        #            ),
        # ], className="six columns"),

        # Prediction Summary output
        html.Div([
            html.Div([
                html.P('Prediction Summary',
                       className="gs-header gs-table-header padded",
                       style={
                           'marginLeft': '5px',
                           'textAlign': 'center',
                           'fontWeight': 600,
                           'fontSize': 15}
                       ),
                html.Div([
                    html.P('Case Number',
                           style={
                               #'width': 120,
                               'textAlign': 'Left',
                               'fontSize': 12,
                               'fontWeight': 600,
                           }),

                    # html.Div(
                    #     id='result_ps_1',
                    #     style={'fontSize': 10,
                    #            }
                    # ),
                    html.Br(),
                ],
                    className='three columns',
                ),

                html.Div([
                    html.P('Procedure Code',
                           style={
                               #'width': 120,
                               'textAlign': 'Left',
                               'fontSize': 12,
                               'fontWeight': 600,
                           }),

                    # html.Div(
                    #     id='result_ps_1',
                    #     style={'fontSize': 10,
                    #            }
                    # ),
                    html.Br(),
                ],
                    className='three columns',
                ),

                html.Div([
                    html.P('Predicted Duration',
                           style={
                               #'width': 120,
                               'textAlign': 'Left',
                               'fontSize': 12,
                               'fontWeight': 600,
                           }),

                    # html.Div(
                    #     id='result_ps_1',
                    #     style={'fontSize': 10,
                    #            }
                    # ),
                    html.Br(),
                ],
                    className='three columns',
                ),

                html.Div([
                    html.P('Actual Duration',
                           style={
                               #'width': 120,
                               'textAlign': 'Left',
                               'fontSize': 12,
                               'fontWeight': 600,
                           }),

                    # html.Div(
                    #     id='result_ps_1',
                    #     style={'fontSize': 10,
                    #            }
                    # ),
                    html.Br(),
                ],
                    className='three columns',
                ),

                # html.Div([
                #     html.Table(
                #         [html.Tr([html.Th(col) for col in dp.columns[1:5]])] +
                #         # Body
                #         [html.Tr([
                #             html.Td(dp.iloc[i][col]) for col in dp.columns[1:5]
                #         ]) for i in range(0, 1)])
                #
                # ], style={
                #     'fontSize': 12,
                #     'marginLeft': '5px',
                # }
                # ),

            ], className="six columns",
                style={
                    'fontSize': 12,
                    'margin-bottom': '10px'
                }
            ),

            html.Div([

                html.P('Duration Slider',
                       className="gs-header gs-table-header padded",
                       style={
                           'marginRight': '5px',
                           'textAlign': 'center',
                           'fontWeight': 600,
                           'fontSize': 15}
                       ),

                # Duration Slider
                html.Div(dcc.RangeSlider(
                    id='duration-range-slider',
                    min=dummy_data_min,  # minimum of slider range
                    max=dummy_data_max,  # maximum of slider range
                    value=[dummy_data_min, dummy_data_max],  # initialized selected range
                    marks=d_marks,
                    step=1,
                    dots=False,  # dot for each value
                    allowCross=False,  # prevent selection "dots" from "crossing"
                    # updatemode='drag', #to update values AS you are dragging, i.e. even without releasing
                ),
                    style={
                        'margin-top': "15px",
                        'marginLeft': "20px",
                        'marginRight': "30px",
                    }
                ),
                # Duration Slider Description
                html.Div(id='output-duration-range-slider',
                         style={'margin-top': "20px"}),

            ], className="six columns")
        ], className="row"),

        html.Div([

            # Historical Records Dash Table
            html.Div([

                #header
                html.P('Historical Surgeries',
                       className="gs-header gs-table-header padded",
                       style={
                           'marginLeft': '5px',
                           'textAlign': 'center',
                           'fontWeight': 600,
                           'fontSize': 15}
                       ),

                #table
                dash_table.DataTable(
                    data=table_data.to_dict('rows'),
                    sorting=True,
                    columns=[{'name': i, 'id': i} for i in table_data.columns],

                    style_cell_conditional=[
                                               {
                                                   'if': {'row_index': 'odd'},
                                                   'backgroundColor': 'rgb(248, 248, 248)'
                                               }
                                           ] + [
                                               {
                                                   'if': {'column_id': c},
                                                   'textAlign': 'left'
                                               } for c in ['Date', 'Region']
                                           ],
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    },
                    style_table={
                        'maxHeight': '380',
                        'overflowY': 'scroll'
                    }
                ),
            ],
                className='six columns',
            ),

            html.Div([

                html.P('Historical Duration',
                       className="gs-header gs-table-header padded",
                       style={
                           'marginRight': '5px',
                           'textAlign': 'center',
                           'fontWeight': 600,
                           'fontSize': 15
                       }),

                dcc.Graph(
                    id='line_graph',
                    figure={
                        'data': data_dummy,
                        'layout': layout_line,
                    }
                ),
            ], className='six columns',
                style={
                    'marginLeft': '5px',
                }

            ),
        ], className="row")

    ])
)

@app.callback(
    Output('output-duration-range-slider', 'children'),
    [Input('duration-range-slider', 'value')])

def update_output(value):
    return '{}/{} historical surgeries\' durations fall within your selected range of {} to {} minutes'.format(
        str(count(dummy_data["Actual.Duration"].tolist(), value[0], value[1])),
        str(dummy_data_length),
        str(value[0]),
        str(value[1]),
    )

def count(duration_list, l, r):
    # the if condition checks for the number of numbers in the range l to r
    # the return is stored in a list whose length is the answer
    return len(list(x for x in duration_list if l <= x <= r))

@app.callback(
    Output('result', 'children'),
    [Input('Procedure Code', 'value')])

def update_result(x):
    description = df.loc[df['Procedure.Code'] == x]['Procedure.Description'].unique()[0]
    return "Procedure Description: " + description

############################Anaesthetist##################################

@app.callback(
    Output('result_an_1', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Principal.Anaesthetist.Title'].unique()[0]
    return "Anaesthetist Title: " + description

@app.callback(
    Output('result_an_2', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Principal.Anaesthetist.Staff.Id'].unique()[0]
    return "Anaesthetist ID: " + str(description)

@app.callback(
    Output('result_an_3', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Primary.Anae'].unique()[0]
    return "Primary Anaesthetist: " + description

############################Surgeon##################################

@app.callback(
    Output('result_su_1', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['First.Surgeon.Title'].unique()[0]
    return "Surgeon Title: " + description

@app.callback(
    Output('result_su_2', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['First.Surgeon.Department.Code'].unique()[0]
    return "Department Code: " + description

@app.callback(
    Output('result_su_3', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['First.Surgeon.Staff.Id'].unique()[0]
    return "Staff Id: " + str(description)

############################Patient##################################

@app.callback(
    Output('result_pa_1', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Age'].unique()[0]
    return "Age: " + str(description)

@app.callback(
    Output('result_pa_2', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Gender'].unique()[0]
    return "Gender: " + description

@app.callback(
    Output('result_pa_3', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Race'].unique()[0]
    return "Race: " + description

@app.callback(
    Output('result_pa_4', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['ASA.Status'].unique()[0]
    return "ASA Status: " + str(description)

@app.callback(
    Output('result_pa_5', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Op.History'].unique()[0]
    return "Operations History: " + description

@app.callback(
    Output('result_pa_6', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Type'].unique()[0]
    return "Patient Type: " + str(description)

@app.callback(
    Output('result_pa_7', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Priority.of.Operation'].unique()[0]
    return "Status: " + description

@app.callback(
    Output('result_pa_8', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Method.of.Operation'].unique()[0]
    return "Method: " + description

@app.callback(
    Output('result_pa_9', 'children'),
    [Input('Case Number', 'value')])

def update_result(x):
    description = df.loc[df['Case.No'] == x]['Op.Risk'].unique()[0]
    return "Op Risk: " + description

# @app.callback(
#     dash.dependencies.Output('Procedure Description', 'children'),
#     [dash.dependencies.Input('Procedure Code', 'value')])
#
# def update_num(key):
#     description = df.loc[df['Procedure.Code'] == key]['Procedure.Description'].unique()[0]
#     return "Procedure Description: " + description



if __name__ == '__main__':
    app.run_server(debug=True)

    #set a row limit and add a scroll bar
    #adding a page clicker or a scoll bar
    #add call backs on dash

#Predication summary and Details will be swapped
# align with left
# Duration Slider
# Prediction Visualisation

#update dash table like mock-up
