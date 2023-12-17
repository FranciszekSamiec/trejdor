import dash
from dash import html, dcc, callback, Output, Input, State

app = dash.Dash(__name__)

# Assume you have some data or state in your app
initial_value = 42

app.layout = html.Div([
    html.A(
        href='/dashboard',
        children=[
            html.Img(
                id='clickable_image',  # Correct id here
                src='/assets/pieChart.png',
                style={'width': '200px', 'height': '200px'},
            ),
        ],
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='hidden-store', data=initial_value),
])

# Create callback to store data in a hidden store when the image is clicked
@app.callback(
    Output('hidden-store', 'data'),
    [Input('clickable_image', 'n_clicks')]
)
def store_data(n_clicks):
    return initial_value

# Create callback to display the stored data in the dashboard
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('hidden-store', 'data')]
)
def display_page(pathname, stored_data):
    if pathname == '/dashboard':
        return html.Div([
            html.H1('Dashboard'),
            html.Div(f'Data from clickable image: {stored_data}'),
            # Add other dashboard components here
        ])
    else:
        return html.Div([
            html.H1('Home Page'),
            # Add other home page components here
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
