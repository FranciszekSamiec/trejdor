from libraries import *
from init import custom_theme

def createDashBoard(pieChart):
    # labels = ['Long maxouts', 'long < max', 'short maxouts', 'short < max']
    # values = [30, 40, 30, 10]
    categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4']
    bar_values = [50, 20, 30, 40]

    page_1_layout = html.Div(
        [
            dcc.Graph(
                id='pie-chart',
                figure = pieChart,
                # figure=go.Figure(
                #     data=[go.Pie(labels=labels, values=values)],
                #     layout=go.Layout(title='Pie Chart', template=custom_theme)
                # ),
                style={
                    'display': 'inline-block',
                    'height': '100%',
                    'width': '50%'
                }  # Set the chart height as 30% of the viewport height
            ),

            dcc.Graph(
                id='bar-chart',
                figure=px.bar(x=categories, y=bar_values, title='Bar Chart', template=custom_theme),
                style={
                    'display': 'inline-block',
                    'height': '100%',
                    'width': '50%',
                }  # Adjust width and height as needed
            ),
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






    # page_1_layout = html.Div([
    #     html.H1("Page 1"),
    #     html.P("This is the content of page 1."),
    # ])

    return page_1_layout