import dash
from dash import dcc, html, callback, Input, Output, Patch

import plotly.graph_objects as go


app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id="graph",
        figure={}
    )
])

# Obsolete
# - Initial graph
def make_figure(x_min, x_max):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=[0, 1, 2, 3], y=[0, 1, 2, 3], mode='markers'))

    fig.add_shape(
        type="line",
        x0=x_min, y0=(3 - x_min) / 2,
        x1=x_max, y1=(3 - x_max) / 2,
        xref="x", yref="y",
        line=dict(color="red", width=2)
    )

    fig.update_layout(xaxis=dict(range=[x_min, x_max]))
    return fig

# - how to use callbacks to update the graph on zooming and use dynamic range
@callback(
    Output("graph", "figure"),
    Input("graph", "relayoutData"),
    prevent_initial_call=True
)
def update_on_zoom(relayout_data):
    # print(relayout_data.get("xaxis.range[0]"))
    patched_fig = Patch()
    if relayout_data and "xaxis.range[0]" in relayout_data:
        x_min = relayout_data["xaxis.range[0]"]
        x_max = relayout_data["xaxis.range[1]"]
        patched_fig["layout"]["shapes"][0].update({
            "x0": x_min, "y0": (3 - x_min) / 2,
            "x1": x_max, "y1": (3 - x_max) / 2,
        })
    return patched_fig


if __name__ == "__main__":
    app.run(debug=True)
