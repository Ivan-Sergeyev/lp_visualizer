import dash
from dash import dcc, html
from dash.dependencies import Output, Input

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Hello, Dash!'),
    dcc.Graph(id='example-graph', figure={})
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)
