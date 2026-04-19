from collections.abc import Callable

import dash
import dash_iconify
import dash_latex as dl
import plotly.graph_objects as go

from model.domain_transfer_objects import Constraint, ConstraintSense, Objective, ObjectiveSense, OptimizationResult


def type_name_id(type_str: str) -> Callable[[str], dict[str, str]]:
    return lambda name : {'type': type_str, 'name': name}


COMPONENT_IDS = {
    'objective': {
        'sense': 'objective-sense',
        'x_coeff': 'objective-x-coeff',
        'sign_label': 'objective-sign-label',
        'y_coeff': 'objective-y-coeff',
    },
    'constraints': {
        'list': 'constraints-list',
        'add_button': 'add-constraint-button',
        'row': type_name_id('constraint-row'),
        'x_coeff': type_name_id('constraint-x-coeff'),
        'sign_label': type_name_id('constraint-sign-label'),
        'y_coeff': type_name_id('constraint-y-coeff'),
        'sense': type_name_id('constraint-sense'),
        'rhs': type_name_id('constraint-rhs'),
        'remove_button': type_name_id('remove-constraint-button'),
    },
    'graph': 'graph',
    'optimization_result': 'optimization-result',
}

CONSTRAINT_SENSES = [str(ConstraintSense.LEQ), str(ConstraintSense.GEQ), str(ConstraintSense.EQ)]
OBJECTIVE_SENSES = [str(ObjectiveSense.MAX), str(ObjectiveSense.MIN)]


def objective_row_component(objective: Objective) -> dash.html.Div:
    return dash.html.Div(
        id='objective-row',
        children=[
            dash.dcc.Dropdown(
                id=COMPONENT_IDS['objective']['sense'],
                options=OBJECTIVE_SENSES,
                value=str(objective.sense),
                clearable=False,
                searchable=False,
                placeholder='Objective sense',
            ),
            dash.dcc.Input(
                id=COMPONENT_IDS['objective']['x_coeff'],
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=objective.x_coeff,
                debounce=True,
                placeholder='Coefficient for x',
            ),
            dash.html.Div(
                dl.DashLatex(r'$x$'),
                className='variable-label',
            ),
            dash.html.Div(
                dl.DashLatex(r'$+$'),
                id=COMPONENT_IDS['objective']['sign_label'],
                className='sign-label',
            ),
            dash.dcc.Input(
                id=COMPONENT_IDS['objective']['y_coeff'],
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=objective.y_coeff,
                debounce=True,
                placeholder='Coefficient for y',
            ),
            dash.html.Div(
                dl.DashLatex(r'$y$'),
                className='variable-label'
            ),
        ],
    )


def constraint_row_component(constraint: Constraint) -> dash.html.Div:
    return dash.html.Div(
        id=COMPONENT_IDS['constraints']['row'](constraint.name),
        className='constraint-row',
        children=[
            dash.dcc.Input(
                id=COMPONENT_IDS['constraints']['x_coeff'](constraint.name),
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.x_coeff,
                debounce=True,
                placeholder='Coefficient for x',
            ),
            dash.html.Div(
                dl.DashLatex(r'$x$'),
                className='variable-label',
            ),
            dash.html.Div(
                dl.DashLatex(r'$+$'),
                id=COMPONENT_IDS['constraints']['sign_label'](constraint.name),
                className='sign-label',
            ),
            dash.dcc.Input(
                id=COMPONENT_IDS['constraints']['y_coeff'](constraint.name),
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.y_coeff,
                debounce=True,
                placeholder='Coefficient for y',
            ),
            dash.html.Div(
                dl.DashLatex(r'$y$'),
                className='variable-label',
            ),
            dash.dcc.Dropdown(
                id=COMPONENT_IDS['constraints']['sense'](constraint.name),
                className='constraint-sense',
                options=CONSTRAINT_SENSES,
                value=str(constraint.sense),
                clearable=False,
                searchable=False,
                placeholder='Constraint sense',
            ),
            dash.dcc.Input(
                id=COMPONENT_IDS['constraints']['rhs'](constraint.name),
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.rhs,
                debounce=True,
                placeholder='Right hand side',
            ),
            dash.dcc.Button(
                id=COMPONENT_IDS['constraints']['remove_button'](constraint.name),
                name=constraint.name,
                className='button remove-constraint-button',
                title='Remove constraint',
                children=[
                    dash_iconify.DashIconify(icon='mdi:trash-can-outline')
                ],
                n_clicks=0,
            ),
        ],
    )


def app_layout(
    objective: Objective,
    constraints: list[Constraint],
    add_constraint_button_n_clicks: int,
    figure: go.Figure,
    optimization_result: OptimizationResult,
) -> dash.html.Div:
    return dash.html.Div(
        id='app-wrapper',
        children=[
            dash.html.Div(
                id='left-panel',
                children=[
                    dash.html.Div(
                        id='model-wrapper',
                        children = [
                            objective_row_component(objective),
                            dash.html.Div(
                                id='constraints-wrapper',
                                children=[
                                    dash.html.Div(
                                        's.t.',
                                        id='st-label',
                                    ),
                                    dash.html.Div(
                                        id=COMPONENT_IDS['constraints']['list'],
                                        children=[
                                            constraint_row_component(constraint) for constraint in constraints
                                        ] + [
                                            dash.html.Button(
                                                id=COMPONENT_IDS['constraints']['add_button'],
                                                className='button add-constraint-button',
                                                title='Add constraint',
                                                children=[
                                                    'Add constraint',
                                                    # todo: plus icon dash_iconify.DashIconify(icon='mdi:plus')
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
            ),
            dash.html.Div(
                id='right-panel',
                children=[
                    dash.dcc.Graph(
                        id=COMPONENT_IDS['graph'],
                        figure=figure,
                    ),
                    dash.html.Div(
                        id=COMPONENT_IDS['optimization_result'],
                        children=[str(optimization_result)],
                    )
                ],
            ),
        ],
    )
