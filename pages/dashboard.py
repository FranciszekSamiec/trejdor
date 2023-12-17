import dash
from dash import html

dash.register_page(__name__)

layout = html.Div([
    html.H1('This is our dashboard page'),
    html.Div('This is our dashboard page content.'),
])