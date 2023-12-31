from libraries import *
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

def createEqChartLayout(fig):
    eqLayout = html.Div(
        [
            dcc.Graph(
                id='equity-chart',
                figure=fig,
                config={'displaylogo': False,'editable': True, 'responsive': True, 'scrollZoom': False},
                style={
                    'transparent' : 'false',
                    'height': '100%',
                    'width': '100%'
                }  # Set the chart height as 30% of the viewport height
            )
        ],
        style={
            'width': '100%',
            'height': '100%',
            'display': 'inline-block',
            # 'border': '1px solid black'
            'flexGrow': 1,
        },
        id='trading-eval',

    )

    return eqLayout

def createLayout(fig, options, frequency_options, selected_option, equity_chart_fig, info, pairInfo, histData):

    histogram = px.histogram(histData, 
                    title='Histogram of bills',
                    # template=custom_theme,
                    )

    histogram.update_traces(textfont=dict(color='white'))

    histogram.update_traces(marker=dict(opacity = 0.4, color='purple'))
    histogram.update_layout(bargap=0.2)

    app_layout = html.Div(
        style={'background-color': '#323738', 'margin': '0'},
        # id='page-content',

        children = [
            # html.Button('Click Me', id='button'),
            dcc.Location(id='url', refresh=False),


            html.Div([

                # dcc.Graph(
                #     # title='Histogram',
                #     config={'displayModeBar': False},
                #     id='histogram',
                #     figure=histogram,
                #     style={
                #         'display': 'inline-block',
                #         'height': '100%',
                #         'width': '33.33%',
                #     }  # Adjust width and height as needed
                # ),

                dcc.Graph(
                    id='candlestick-chart' ,
                    figure=fig,
                    clear_on_unhover=True,    
                    # animate=True,
                    config={'doubleClick': 'autosize', 'modeBarButtonsToRemove': ['resetScale2d'], 'displaylogo': False,'editable': True,
                            'edits': {'annotationPosition': False} , 'responsive': True,  'scrollZoom': True}, # scroll in dash is fucked up 
                    style={ 'height': '62vh', 'position': 'relative'}  # Set the chart height as 90% of the viewport height
                ),
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id='chart-title-dropdown',
                            options=[{'label': option, 'value': option} for option in options],
                            value=selected_option,
                            # placeholder='symbol',
                            className='my-dropdown',
                            searchable=True, 
                            style={'width': '155px', 'margin-right': '5px'},
                        ),

                        html.Div([
                            dcc.Input(
                                id='new-pair',
                                type='text',
                                className="new-pair",
                                placeholder='add new symbol',
                            ),
                            html.Div(
                                id='new-pair-info',
                                # children=dash_dangerously_set_inner_html.DangerouslySetInnerHTML(pairInfo),
                            ),
                        ], style={'display': 'flex', 'flexDirection': 'column'}),  # This will arrange them vertically

                        html.Div([
                            html.Button("+", id="plus-button", n_clicks=0, className="plus-button"),
                            html.Button("-", id="minus-button", n_clicks=0, className="minus-button"),
                        ]),
                        dcc.Dropdown(
                            id='frequency-dropdown',
                            options=[{'label': label, 'value': value} for value, label in frequency_options.items()],
                            value='1h',  # Default value
                            className='my-dropdown',
                            searchable=False,
                            style={'width': '70px'},
                        ),

                    ], style={'display': 'flex', 'flexDirection': 'row'}),
                ], style={'padding': '10px', 'position': 'absolute', 'top': '10px', 'left': '10px'}),
                html.Div(
                    children=[
                        html.Div(
                            "T  r  e  y  d  o  r (Alpha)",
                            className='text-center',  # Apply the CSS class
                            style={
                                'color': '#e384c3',
                                'font-size': '16px',
                                'font-family': 'Courier New',
                                'font-weight': 'normal',
                                'font-style': 'italic',
                                'display': 'flex',  # Use Flexbox
                                'justify-content': 'center',  # Center horizontally
                                'align-items': 'center',  # Center vertically
                                'height': '20px',  # Match the height of the parent div
                            }
                        ),
                    ],
                    id='text-frame',
                    style={'padding': '10px', 'position': 'absolute', 'top': '18px', 'right': '18px', 'border': '1px solid blue', 'border-radius': '5px'}
                    # style={'background-color': '#323738', 'padding-left': '10px', 'padding-right': '10px' ,'border-radius': '5px', 'margin-left': '10px',
                    #     'border': '1px solid blue'},
                ),
            ], style={'padding': '5px'}),
            html.Div([
                html.Div([

                    html.Div(
                        [   
                            html.Div("Mode:"),
                            html.Img(id = 'equityMode', src='/assets/equity.jpeg', style={'width': '22px', 'height': '22px', 'cursor': 'pointer'}),
                            html.Img(id = 'dashboardMode', src='/assets/pieChart.png', style={'width': '20px', 'height': '20px', 'cursor': 'pointer'}),
                        ],
                        className='options__mode',
                    ),

                    # html.Div(
                    #     id='control-panel',
                    #     style={'color': '#42c8f5', 'text-align': 'center'},
                    #     children=dash_dangerously_set_inner_html.DangerouslySetInnerHTML("control panel"),
                    # ),

                    html.Div(className='horizontal-line'),
                    html.Div(
                        [
                            dcc.DatePickerSingle(
                                id = 'dateStart',
                                className="options__date-from",
                                day_size=20,
                                placeholder='Start date'
                            ),
                            dcc.DatePickerSingle(
                                id = 'dateEnd',
                                className="options__date-to",
                                day_size=20,
                                placeholder='End date'
                            ),
                        ],
                        className='options__dates'
                    ),
                    html.Div(className='horizontal-line'),
                    dcc.RadioItems(
                        [
                            {
                                "label": ["long position", html.Span(className="checkmark")],
                                "value": "long position",
                            },
                            {
                                "label": ["short position", html.Span(className="checkmark")],
                                "value": "short position",
                            },
                        ],
                        'long position',
                        id = 'position',
                        inline=False,
                        className='options__position-radio',
                    ),
                    html.Div(className='horizontal-line'),

                    html.Div(
                        [
                            html.Label('Percent to risk: ', htmlFor='text-input'),
                            # <input type="number" min="0" max="1" step="0.01" id="myPercent"/>
                            dcc.Input(id='options-percent-to-risk', placeholder = '2%', type='number', min=0, max=100, step=0.1, className='options__percent-to-risk-input',style={'cursor': 'pointer', 'color': 'white'}),
                            # dcc.Input(id='text-input', type='text', value=''),
                        ],
                        className="options__percent-to-risk"
                    ),
                    html.Div(className='horizontal-line'),

                    html.Div(
                        [
                            html.Label('Start Capital: ', htmlFor='text-input'),
                            # <input type="number" min="0" max="1" step="0.01" id="myPercent"/>
                            dcc.Input(id='start-capital', placeholder = '100 000', type='number', min=0, max=100, step=0.1, className='options__percent-to-risk-input',style={'cursor': 'pointer', 'color': 'white'}),
                            # dcc.Input(id='text-input', type='text', value=''),
                        ],
                        className="options__start-capital"
                    ),
                    html.Div(className='horizontal-line'),

                    html.Button('Reset', id='refresh-button', className='options__reset-button', n_clicks=0, style={'cursor': 'pointer'}),
                    html.Div([
                        html.P(id='click-output', hidden=True),
                        html.P(id='relayout-data', hidden=True),
                        html.P(id='dummyOut', hidden=True),
                        html.P(id='dummyOutNewPos', hidden=True),
                        html.P(id='dummyOutNewPair', hidden=True),
                        html.P(id='dummyOutAnnotation', hidden=True),
                        html.P(id='plusMinusButton', hidden=True),
                        html.P(id='dummyOutNewPairSearch', hidden=True),
                        html.P(id='dummyOutHover', hidden=True),
                        html.P(id='dummyTriggerDashboard', hidden=True, children = 0),
                        # html.Div(id='dummyTriggerDashboard', hidden=True, children = 0),
                    ], style={'display': 'none'}),

                ],
                className='options',
            ),

            html.Div(
                [
                    dcc.Graph(
                        id='equity-chart',
                        figure=equity_chart_fig,
                        config={'displaylogo': False,'editable': True, 'responsive': True, 'scrollZoom': False},
                        style={
                            'transparent' : 'false',
                            'height': '100%',
                            'width': '100%'
                        }  # Set the chart height as 30% of the viewport height
                    )
                ],
                style={
                    'width': '100%',
                    'height': '100%',
                    'display': 'inline-block',
                    # 'border': '1px solid black'
                    'flexGrow': 1,
                },
                id='trading-eval',

            ),   # Adjust the width and alignment
            ],
            style={
                    'display': 'flex',
                    'height': 'calc(38vh - 15px)',
                    'background-color': '#323738',
                    'padding': '0 5px 5px'
                }
            ),


            # html.Div([
            #     html.Div(
            #         dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
            #     ) for page in dash.page_registry.values()
            # ]),
            # dash.page_container
            # html.Script(src='./assets/app.js'),
        ]
    )

    return app_layout
