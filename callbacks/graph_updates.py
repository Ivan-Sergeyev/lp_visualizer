import dash
import math
import plotly.graph_objects as go

from model.domain_transfer_objects import Constraint, Objective, OptimizationResult
from model.geometry import get_constraint_line_endpoints, normal_objective_vector


def optimization_result_update(optimization_result: OptimizationResult) -> dash.Patch:
    print(f' --- in {optimization_result_update.__name__}({optimization_result})')
    patch = dash.Patch()
    patch[0] = str(optimization_result)
    return patch


def figure_update_objective(figure: go.Figure, objective: Objective) -> dash.Patch:
    print(f' --- in {figure_update_objective.__name__}({objective})')

    # todo: absolute positioning of objective arrow?
    objective_arrow_start = 0., 0.
    objective_arrow_end = normal_objective_vector(objective)
    # todo: add color picker?
    objective_arrow_color = 'rgb(255,51,0)'

    objective_arrow = go.layout.Annotation(dict(
        arrowcolor=objective_arrow_color,
        arrowhead=3,
        arrowwidth=1.5,
        showarrow=True,
        text='',
        axref='x', # todo: change '*ref' values to 'paper' for positioning relative to plot; same for bounding box if you want it
        ayref='y',
        xref='x',
        yref='y',
        ax=objective_arrow_start[0],
        ay=objective_arrow_start[1],
        x=objective_arrow_end[0],
        y=objective_arrow_end[1],
    ))

    patch = dash.Patch()

    if len(figure.get('layout', {}).get('annotations', [])) == 0:
        patch.layout.annotations.append(objective_arrow)
    else:
        patch.layout.annotations[0] = objective_arrow

    return patch


def figure_add_constraint(figure: go.Figure, constraint: Constraint) -> dash.Patch:
    print(f' --- in {figure_add_constraint.__name__}({constraint})')

    # todo: add color picker?
    constraint_color = 'blue'
    x_min, x_max = figure['layout']['xaxis']['range']
    y_min, y_max = figure['layout']['yaxis']['range']
    (x0, y0), (x1, y1) = get_constraint_line_endpoints(constraint, x_min, x_max, y_min, y_max)

    constraint_line = dict(
        type='line',
        xref='x',
        yref='y',
        line=dict(color=constraint_color, width=2), # todo: pass dash='dash' for disabled constraints
        name=constraint.name,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
    )

    patch = dash.Patch()
    patch.layout.shapes.append(constraint_line)
    return patch


def figure_update_constraint(figure: go.Figure, constraint: Constraint) -> dash.Patch:
    print(f' --- in {figure_add_constraint.__name__}({constraint})')

    occurrences = [pos for pos, shape in enumerate(figure['layout'].get('shapes', [])) if shape.get('name', '') == constraint.name]

    if len(occurrences) > 1:
        raise ValueError(f'Constraint {constraint.name} found in figure shapes at more than one index: {occurrences}')

    if len(occurrences) < 1:
        print(f'Constraint {constraint.name} not found in figure shapes')
        return figure_add_constraint(figure, constraint)

    x_min, x_max = figure['layout']['xaxis']['range']
    y_min, y_max = figure['layout']['yaxis']['range']
    (x0, y0), (x1, y1) = get_constraint_line_endpoints(constraint, x_min, x_max, y_min, y_max)

    patch = dash.Patch()
    patch.layout.shapes[occurrences[0]].update(x0=x0, y0=y0, x1=x1, y1=y1)
    return patch


# todo: draw feasible region via
# go.Scatter(
#         x=vertices_x_list, y=vertices_y_list,
#         fill="toself"
#     )
# need to compute convex hull (of constraints + bounding box) to get vertices_x_list, vertices_y_list
