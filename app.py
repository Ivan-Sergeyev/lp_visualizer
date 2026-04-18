import dash
# import os
import plotly.graph_objects as go

from callbacks import user_actions
from callbacks.graph_updates import figure_init_constraint, figure_init_objective
from components.components import app_layout
from model.domain_transfer_objects import Constraint
from model.linear_program import linear_program, initial_constraints, initial_objective


def get_max_numeric_name(constraint_list: list[Constraint]) -> int:
    return max(int(constraint.name) for constraint in constraint_list if constraint.name.isdigit())


initial_figure = go.Figure(layout=dict(
    xaxis=dict(range=(-1, 6)),
    yaxis=dict(range=(-1, 4)),
))

# todo: figure_init(figure, initial_objective, initial_constraints)
figure_init_objective(initial_figure, initial_objective)
for constraint in initial_constraints:
    figure_init_constraint(initial_figure, constraint)

app = dash.Dash(__name__)
app.title = 'LP Visualizer'
# app._favicon = (os.path.join('assets', 'icon.ico'))
app.layout = app_layout(
    objective=initial_objective,
    constraints=initial_constraints,
    add_constraint_button_n_clicks=get_max_numeric_name(initial_constraints),
    figure=initial_figure,
    optimization_result=linear_program.optimization_result(False),
)

user_actions.register(app)


if __name__ == '__main__':
    app.run(debug=True)
