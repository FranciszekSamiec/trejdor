from libraries import *
from init import custom_theme

def createDashBoard(pieChart, barChart, histogram):

    # data = np.random.randn(1000)

    # histogram_trace = go.Histogram(x=data, nbinsx=20, histnorm='probability')

    page_1_layout = html.Div(
        [
            dcc.Graph(
                config={'displayModeBar': False},
                id='pie-chart',
                figure = pieChart,
                # figure=go.Figure(
                #     data=[go.Pie(labels=labels, values=values)],
                #     layout=go.Layout(title='Pie Chart', template=custom_theme)
                # ),
                style={
                    'display': 'inline-block',
                    'height': '100%',
                    'width': '33.33%'
                }  # Set the chart height as 30% of the viewport height
            ),

            dcc.Graph(
                config={'displayModeBar': False},
                
                id='bar-chart',
                figure=barChart,
                style={
                    'display': 'inline-block',
                    'height': '100%',
                    'width': '33.33%',
                }  # Adjust width and height as needed
            ),
            dcc.Graph(
                # title='Histogram',
                config={'displayModeBar': False},
                id='histogram',
                figure=histogram,
                style={
                    'display': 'inline-block',
                    'height': '100%',
                    'width': '33.33%',
                }  # Adjust width and height as needed
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

    return page_1_layout