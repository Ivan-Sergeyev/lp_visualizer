import dash
import logging
import plotly.graph_objects as go

from model.constraint import Constraint
from algorithms.geometry import Line2D, Point2D, Vector2D
from model.objective import Objective, ObjectiveSense


logger = logging.getLogger(__name__)


# --- Objective ---

def max_unit_vector(objective: Objective) -> Vector2D:
    match objective.sense:
        case ObjectiveSense.MAX:
            return Vector2D(objective.coeff_x, objective.coeff_y).unit()
        case ObjectiveSense.MIN:
            return Vector2D(-objective.coeff_x, -objective.coeff_y).unit()
        case _:
            raise ValueError(f'Unrecognized objective sense: {objective.sense}')


def objective_arrow(
    figure: go.Figure,
    objective: Objective,
    arrowhead: int = 3,
    arrowwidth: float = 1.5,
    color: str = 'rgb(255,51,0)',
) -> go.layout.Annotation:
    objective_arrow_start = (0., 0.)
    objective_arrow_end = max_unit_vector(objective)

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
        x=objective_arrow_end.x,
        y=objective_arrow_end.y,
    ))


def figure_init_objective(figure: go.Figure, objective: Objective):
    logger.debug(f'Calling {figure_init_objective.__name__}({objective})')
    figure['layout']['annotations'] = [objective_arrow(figure, objective)]


def figure_update_objective(figure: go.Figure, objective: Objective) -> dash.Patch:
    logger.debug(f'Calling {figure_update_objective.__name__}({objective})')
    patch = dash.Patch()
    patch['layout']['annotations'][0] = objective_arrow(figure, objective)
    return patch


# --- Constraints ---

def figure_get_bounding_box(figure: go.Figure) -> tuple[Point2D, Point2D]:
    x_range: tuple[float, float] = figure['layout']['xaxis']['range']
    y_range: tuple[float, float] = figure['layout']['yaxis']['range']
    return Point2D(x_range[0], y_range[0]), Point2D(x_range[1], y_range[1])


def constraint_get_boxed_endpoints(constraint: Constraint, bottom_left: Point2D, top_right: Point2D) -> tuple[Point2D, Point2D]:
    line = Line2D(constraint.coeff_x, constraint.coeff_y, constraint.rhs)
    return line.boxed_endpoints(bottom_left, top_right)


def constraint_get_index_in_figure_shapes(figure: go.Figure, constraint_name: str) -> int:
    occurrences = [
        pos for pos, shape in enumerate(figure.get('layout', {}).get('shapes', []))
        if shape.get('name', '') == constraint_name
    ]

    if len(occurrences) < 1:
        raise ValueError(f'Constraint {constraint_name} not found in figure shapes.')

    if len(occurrences) > 1:
        raise ValueError(f'Constraint {constraint_name} found in figure shapes at more than one index: {occurrences}')

    return occurrences[0]


def constraint_line(
    figure: go.Figure,
    constraint_name: str,
    constraint: Constraint,
    color: str = 'blue',
    width: float = 2.
) -> dict[str, str | float | dict]:
    bottom_left, top_right = figure_get_bounding_box(figure)
    point_1, point_2 = constraint_get_boxed_endpoints(constraint, bottom_left, top_right)

    return dict(
        type='line',
        xref='x',
        yref='y',
        line=dict(color=color, width=width),
        name=constraint_name,
        x0=point_1.x,
        y0=point_1.y,
        x1=point_2.x,
        y1=point_2.y,
    )


def figure_init_constraint(figure: go.Figure, constraint_name: str, constraint: Constraint):
    logger.debug(f'Calling {figure_init_constraint.__name__}({constraint})')
    figure['layout']['shapes'] += (constraint_line(figure, constraint_name, constraint),)


def figure_add_constraint(figure: go.Figure, constraint_name: str, constraint: Constraint) -> dash.Patch:
    logger.debug(f'Calling {figure_add_constraint.__name__}({constraint})')
    patch = dash.Patch()
    patch['layout']['shapes'].append(constraint_line(figure, constraint_name, constraint))
    return patch


def figure_update_constraint(figure: go.Figure, constraint_name: str, constraint: Constraint) -> dash.Patch:
    logger.debug(f'Calling {figure_update_constraint.__name__}({constraint})')

    index = constraint_get_index_in_figure_shapes(figure, constraint_name)
    bottom_left, top_right = figure_get_bounding_box(figure)
    point_1, point_2 = constraint_get_boxed_endpoints(constraint, bottom_left, top_right)

    patch = dash.Patch()
    patch['layout']['shapes'][index].update(x0=point_1.x, y0=point_1.y, x1=point_2.x, y1=point_2.y)
    return patch


def figure_remove_constraint(figure: go.Figure, constraint_name: str) -> dash.Patch:
    logger.debug(f'Calling {figure_remove_constraint.__name__}({constraint_name})')

    index = constraint_get_index_in_figure_shapes(figure, constraint_name)

    patch = dash.Patch()
    del patch['layout']['shapes'][index]
    return patch


# --- Result ---

def update_result(result: str) -> dash.Patch:
    logger.debug(f'Calling {update_result.__name__}({result})')
    patch = dash.Patch()
    patch[0] = result
    return patch
