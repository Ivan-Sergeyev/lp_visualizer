import dash
# import os
import plotly.graph_objects as go

from callbacks import user_actions
from callbacks.graph_updates import figure_init_constraint, figure_init_objective
from components.components import app_layout
from model.domain_transfer_objects import Constraint, Objective
from model.linear_program import linear_program


def get_max_numeric_name(constraint_list: list[Constraint]) -> int:
    return max(int(constraint.name) for constraint in constraint_list if constraint.name.isdigit())


initial_objective = Objective(sense='max', x_coeff=6., y_coeff=9.)
initial_constraints = [
    Constraint(name='0', x_coeff=2., y_coeff=3., sense='<=', rhs=12.),
    Constraint(name='1', x_coeff=1., y_coeff=1., sense='<=', rhs=5.),
    Constraint(name='2', x_coeff=1., y_coeff=0., sense='>=', rhs=0.),
    Constraint(name='3', x_coeff=0., y_coeff=1., sense='>=', rhs=0.),
]

linear_program.load(initial_objective, initial_constraints)
linear_program.optimize()

initial_figure = go.Figure(layout=dict(
    xaxis=dict(range=(-1, 6)),
    yaxis=dict(range=(-1, 4)),
))

app = dash.Dash(__name__)
app.title = 'LP Visualizer'
# app._favicon = (os.path.join('assets', 'icon.ico'))
app.layout = app_layout(
    initial_objective=initial_objective,
    initial_constraints=initial_constraints,
    initial_add_constraint_button_n_clicks=get_max_numeric_name(initial_constraints),
    initial_figure=initial_figure,
    initial_optimization_result=str(linear_program.get_optimization_result())
)

figure_init_objective(initial_figure, initial_objective)
for constraint in initial_constraints:
    figure_init_constraint(initial_figure, constraint)

user_actions.register(app)


if __name__ == '__main__':
    app.run(debug=True)


# todos:
# - nice to have: add functionality for toggling constraints on/off (buttons, callbacks, greying out)
# - make it look pretty:
#   - add custom favicon
#   - fiddle with css
#   - add nicer components with Dash Mantine Components (DMC) https://www.dash-mantine-components.com/
#   - add color picker for objective arrow, constraints lines colors, solution, feasible region etc.?
#   - add feasible region
#     - implement computation of convex hull (of constraints + bounding box) to get vertices_x_list, vertices_y_list
#     - add feasible region rendering on graph via go.Scatter(x=vertices_x_list, y=vertices_y_list, fill="toself")
#   - render objective vector in a box in a fixed position on the plot
#     - change '*ref' values to 'paper' for positioning relative to plot; same for bounding box if you want it
#     - add box rendering around objective
#   - implement toggling constraints on/off
#     - track in model
#     - pass dash='dash' to constraint dict renger for disabled constraints
#   - implement saving and loading of models
#   - implement resetting lp to default
#   - move documentation from app.py to readme
#   - generate readme/spec/... for github
#   - implement tests
# - fix known issues:
#   - reload browser page => UI refreshes, but not LP model => stale constraint IDs in UI => errors when changing constraints
#     - re-create initial model on reload?
#     - it might be the same problem as with multiple users on the same shared website
#     - switch to manual lp storage and optimization? only run with one server? reset on reload?
#   - with debug=True, model is optimized twice at startup
#     - randomly got fixed when model initialization was in linear_program.py, then re-added when model initialization got moved to app.py


# experimental findings, note for later: if we want to horizontally align bottom edge of 's.t.' label with bottom edge of first constraint row,
# we need to wrap 's.t.' label and first constraint row in a flex container together; this will require additional logic
# for dynamically adding/removing constraint rows while keeping 's.t.' label properly positioned.

# experimental findings: there's an alternative way to render math in dash by using mathjax.
# it's done by changing app initialization to:
# ```python
# app = dash.Dash(__name__, external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'] # unfortunately, external)
# ```
# then formulas are rendered by writing, for example, '\\(x\\)' or r'\(x\)' instead of dl.DashLatex(r'$x$')
# however, the mathjax approach is unfortunately unstable---math rendering breaks after a few page reloads

# experimental findings: dash handles inputs weirdly:
# - input is wrapped in div (toghether with buttons)
# - class of input inside div is only dash-input-element
# - stepper buttons are generated inside div even if min/max/step parameters are None
# - as a result, className is only applied to div wrapper, not input => text-align gets overridden
# - hence need for input[id*="-coeff"] to apply text-align: right
# - also input element is wider than div, hence need for width: 100% inside input[id*="-coeff"]

# docs: list of useful links about dash
# https://dash.plotly.com/pattern-matching-callbacks
# https://dash.plotly.com/advanced-callbacks
# https://dash.plotly.com/clientside-callbacks
# https://dash.plotly.com/flexible-callback-signatures
# https://dash.plotly.com/callback-gotchas
# https://dash.plotly.com/dash-core-components

# docs: python-mip documentation https://docs.python-mip.com/en/latest/name.dash.html

# docs:
# - how to use Patch https://dash.plotly.com/partial-properties
# - how to work with Graph (also internally) https://dash.plotly.com/dash-core-components/graph
# - how to add and control shapes https://plotly.com/python/shapes/
