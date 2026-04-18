import dash
import plotly.graph_objects as go

from model.domain_transfer_objects import Constraint, Objective, OptimizationResult
from model.geometry import get_constraint_line_endpoints, normal_objective_vector


def objective_arrow(
    figure: go.Figure,
    objective: Objective,
    arrowhead: int = 3,
    arrowwidth: float = 1.5,
    color: str = 'rgb(255,51,0)',
) -> go.layout.Annotation:
    objective_arrow_start = 0., 0.
    objective_arrow_end = normal_objective_vector(objective)

    return go.layout.Annotation(dict(
        arrowcolor=color,
        arrowhead=arrowhead,
        arrowwidth=arrowwidth,
        showarrow=True,
        text='',
        axref='x',
        ayref='y',
        xref='x',
        yref='y',
        ax=objective_arrow_start[0],
        ay=objective_arrow_start[1],
        x=objective_arrow_end[0],
        y=objective_arrow_end[1],
    ))


def constraint_line(
    figure: go.Figure,
    constraint: Constraint,
    color: str = 'blue',
    width: float = 2.
) -> dict[str, str | float | dict]:
    x_min, x_max = figure['layout']['xaxis']['range']
    y_min, y_max = figure['layout']['yaxis']['range']
    (x0, y0), (x1, y1) = get_constraint_line_endpoints(constraint, x_min, x_max, y_min, y_max)
    print((x0, y0), (x1, y1))

    return dict(
        type='line',
        xref='x',
        yref='y',
        line=dict(color=color, width=width),
        name=constraint.name,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
    )


def figure_init_objective(figure: go.Figure, objective: Objective):
    print(f' --- in {figure_init_objective.__name__}({objective})')
    print(figure.layout)
    print(figure.layout.annotations)
    figure.layout.annotations = [objective_arrow(figure, objective)]


def figure_init_constraint(figure: go.Figure, constraint: Constraint):
    print(f' --- in {figure_init_constraint.__name__}({constraint})')
    figure.layout.shapes +=( constraint_line(figure, constraint),)


def figure_add_constraint(figure: go.Figure, constraint: Constraint) -> dash.Patch:
    print(f' --- in {figure_add_constraint.__name__}({constraint})')
    patch = dash.Patch()
    patch.layout.shapes.append(constraint_line(figure, constraint))
    return patch


def optimization_result_update(optimization_result: OptimizationResult) -> dash.Patch:
    print(f' --- in {optimization_result_update.__name__}({optimization_result})')
    patch = dash.Patch()
    patch[0] = str(optimization_result)
    return patch


def figure_update_objective(figure: go.Figure, objective: Objective) -> dash.Patch:
    print(f' --- in {figure_update_objective.__name__}({objective})')
    patch = dash.Patch()
    patch.layout.annotations[0] = objective_arrow(figure, objective)
    return patch


def get_constraint_index_in_figure_shapes_list(figure: go.Figure, constraint_name: str) -> int:
    occurrences = [
        pos for pos, shape in enumerate(figure['layout'].get('shapes', []))
        if shape.get('name', '') == constraint_name
    ]

    if len(occurrences) < 1:
        raise ValueError(f'Constraint {constraint_name} not found in figure shapes.')

    if len(occurrences) > 1:
        raise ValueError(f'Constraint {constraint_name} found in figure shapes at more than one index: {occurrences}')

    return occurrences[0]


def figure_update_constraint(figure: go.Figure, constraint: Constraint) -> dash.Patch:
    print(f' --- in {figure_add_constraint.__name__}({constraint})')

    index = get_constraint_index_in_figure_shapes_list(figure, constraint.name)
    x_min, x_max = figure['layout']['xaxis']['range']
    y_min, y_max = figure['layout']['yaxis']['range']
    (x0, y0), (x1, y1) = get_constraint_line_endpoints(constraint, x_min, x_max, y_min, y_max)

    patch = dash.Patch()
    patch.layout.shapes[index].update(x0=x0, y0=y0, x1=x1, y1=y1)
    return patch


def figure_remove_constraint(figure: go.Figure, constraint_name: str) -> dash.Patch:
    print(f' --- in {figure_remove_constraint.__name__}({constraint_name})')

    index = get_constraint_index_in_figure_shapes_list(figure, constraint_name)

    patch = dash.Patch()
    del patch.layout.shapes[index]
    return patch
