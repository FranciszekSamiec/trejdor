from libraries import *
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML



def createLayout(fig, options, frequency_options, selected_option, equity_chart_fig, info):
    app_layout = html.Div(
        style={'background-color': '#323738', 'margin': '0'},
        children = [
            # html.Button('Click Me', id='button'),
                
            html.Div([
                dcc.Graph(
                    id='candlestick-chart' ,
                    figure=fig,
                    # animate=True,
                    config={'displaylogo': False,'editable': True,'edits': {'annotationPosition': False} , 'responsive': True,  'scrollZoom': False}, # scroll in dash is fucked up 
                    style={'displayModeBar': False, 'height': '62vh', 'position': 'relative'}  # Set the chart height as 90% of the viewport height
                ),
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id='chart-title-dropdown',
                            options=[{'label': option, 'value': option} for option in options],
                            value=selected_option,
                            className='my-dropdown',
                            searchable=False,
                            style={'width': '155px', 'margin-right': '10px'},
                        ),
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

            ], style={'padding': '5px'}),
            html.Div([
                html.Div([
                    html.Div(
                        id='error',
                        style={'color':'#42c8f5'},
                        children=dash_dangerously_set_inner_html.DangerouslySetInnerHTML(),
                        # children=info,
                    ),
                    # html.Div(id='error', style={'color':'green'}, children="Default Text"),
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
                    html.Div(
                        [
                            html.Label('Percent to risk', htmlFor='text-input'),
                            # <input type="number" min="0" max="1" step="0.01" id="myPercent"/>
                            dcc.Input(id='options-percent-to-risk', placeholder = '%', type='number', min=0, max=100, step=0.1, className='options__percent-to-risk-input',style={'cursor': 'pointer', 'color': 'white'}),
                            # dcc.Input(id='text-input', type='text', value=''),
                        ],
                        className="options__percent-to-risk"
                    ),
                    html.Button('Reset', id='refresh-button', className='options__reset-button', n_clicks=0, style={'cursor': 'pointer'}),
                    html.Div([
                        html.P(id='click-output', hidden=True),
                        html.P(id='relayout-data', hidden=True),
                        html.P(id='dummyOut', hidden=True),
                        html.P(id='dummyOutNewPos', hidden=True),
                        html.P(id='dummyOutNewPair', hidden=True),
                        html.P(id='dummyOutAnnotation', hidden=True),
                    ], style={'display': 'none'}),

                ],
                className='options',
            ),

            html.Div([
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
            ], style={
                    'width': '80%',
                    'height': '100%',
                    'display': 'inline-block',
                    # 'border': '1px solid black'
                    'flexGrow': 1,

                }
            ),   # Adjust the width and alignment
            ], style={
                    'display': 'flex',
                    'height': 'calc(38vh - 15px)',
                    'background-color': '#323738',
                    'padding': '0 5px 5px'
                }
            ),
            # html.Script(
            #     """
            #     document.addEventListener('DOMContentLoaded', function() {
            #         // Get the annotation element by its class name
            #         var annotationElement = document.querySelector('.annotation-text');

            #         // Add a click event listener to the annotation
            #         annotationElement.addEventListener('click', function() {
            #             console.log('Annotation clicked');
            #         });
            #     });
            #     """
            # )
            # html.Script(src='C:/Users/fsami/Desktop/trejdor/app.js'),
        ]
    )

    return app_layout
