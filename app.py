import logging

import dash
# import os
import plotly.graph_objects as go

from callbacks import user
from callbacks.graph import figure_init_constraint, figure_init_objective
from components.app_layout import app_wrapper
from components.common import STORAGE_TYPE
from model.constraint import Constraint, ConstraintSense
from model.objective import Objective, ObjectiveSense
from algorithms.simplex import SimplexSolver


logging.basicConfig(level=logging.DEBUG)

objective = Objective(sense=ObjectiveSense.MAX, coeff_x=6., coeff_y=9.)
constraints = {
    '0': Constraint(coeff_x=2., coeff_y=3., sense=ConstraintSense.LE, rhs=12.),
    '1': Constraint(coeff_x=1., coeff_y=1., sense=ConstraintSense.LE, rhs=5.),
    '2': Constraint(coeff_x=1., coeff_y=0., sense=ConstraintSense.GE, rhs=0.),
    '3': Constraint(coeff_x=0., coeff_y=1., sense=ConstraintSense.GE, rhs=0.),
}

figure = go.Figure(layout=dict(
    xaxis=dict(range=(-1, 6)),
    yaxis=dict(range=(-1, 4)),
))
figure_init_objective(figure, objective)
for name in constraints:
    figure_init_constraint(figure, name, constraints[name])

solver = SimplexSolver.solve(objective, list(constraints.values()))
result = solver.get_result()

app = dash.Dash(__name__)
app.title = 'LP Visualizer'
# app._favicon = (os.path.join('assets', 'icon.ico'))
app.layout = app_wrapper(
    objective=objective,
    constraints=constraints,
    add_constraint_button_n_clicks=3,
    figure=figure,
    result=str(result),
    storage_type=STORAGE_TYPE
)

user.register(app)


if __name__ == '__main__':
    app.run(debug=False)
