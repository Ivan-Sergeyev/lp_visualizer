from typing import TypedDict

import dash
import dash_iconify
import plotly.graph_objects as go

from components.common import StorageType
from components.constraint import constraint_layout, constraint_store
from components.objective import objective_layout, objective_store
from model.constraint import Constraint
from model.objective import Objective


PageIDs = TypedDict('PageIDs', {
    'constraints_list': str,
    'add_constraint_button': str,
    'graph': str,
    'result': str,
})


PAGE_IDS: PageIDs = {
    'constraints_list': 'constraints-list',
    'add_constraint_button': 'add-constraint-button',
    'graph': 'graph',
    'result': 'result',
}


def app_left_panel(objective: Objective, constraints: dict[str, Constraint], add_constraint_button_n_clicks: int) -> dash.html.Div:
    return dash.html.Div(
        id='left-panel',
        children=[
            dash.html.Div(
                id='model-wrapper',
                children = [
                    objective_layout(objective),
                    dash.html.Div(
                        id='constraints-wrapper',
                        children=[
                            dash.html.Div(
                                's.t.',
                                id='st-label',
                            ),
                            dash.html.Div(
                                id=PAGE_IDS['constraints_list'],
                                children=[
                                    constraint_layout(name, constraints[name]) for name in constraints
                                ] + [
                                    dash.html.Button(
                                        id=PAGE_IDS['add_constraint_button'],
                                        className='button add-constraint-button',
                                        title='Add constraint',
                                        children=[
                                            dash_iconify.DashIconify(icon='mdi:plus'),
                                            'Add constraint',
                                        ],
                                        n_clicks=add_constraint_button_n_clicks,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def app_right_panel(figure: go.Figure, result: str) -> dash.html.Div:
    return dash.html.Div(
        id='right-panel',
        children=[
            dash.dcc.Graph(
                id=PAGE_IDS['graph'],
                figure=figure,
            ),
            dash.html.Div(
                id=PAGE_IDS['result'],
                children=[result],
            ),
        ],
    )


def app_wrapper(
    objective: Objective,
    constraints: dict[str, Constraint],
    add_constraint_button_n_clicks: int,
    figure: go.Figure,
    result: str,
    storage_type: StorageType,
) -> dash.html.Div:
    return dash.html.Div(
        id='app-wrapper',
        children=[
            app_left_panel(objective, constraints, add_constraint_button_n_clicks),
            app_right_panel(figure, result),
            objective_store(objective, storage_type),
            dash.html.Div(
                id='constraints-store',
                children=[constraint_store(name, constraints[name], storage_type) for name in constraints],
            ),
        ],
    )
