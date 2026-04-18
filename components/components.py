import dash
import dash_iconify
import dash_latex as dl
import plotly.graph_objects as go

from model.domain_transfer_objects import Constraint, Objective


def objective_row_component(objective: Objective) -> dash.html.Div:
    return dash.html.Div(
        id='objective-row',
        children=[
            dash.dcc.Dropdown(
                id='objective-sense',
                options=['max', 'min'],
                value=objective.sense,
                clearable=False,
                searchable=False,
                placeholder='Objective sense',
            ),
            dash.dcc.Input(
                id='objective-x-coeff',
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
                id='objective-sign-label',
                className='sign-label',
            ),
            dash.dcc.Input(
                id='objective-y-coeff',
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
        id={'type': 'constraint-row', 'name': constraint.name},
        className='constraint-row',
        children=[
            dash.dcc.Input(
                id={'type': 'constraint-x-coeff', 'name': constraint.name},
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
                id={'type': 'constraint-sign-label', 'name': constraint.name},
                className='sign-label',
            ),
            dash.dcc.Input(
                id={'type': 'constraint-y-coeff', 'name': constraint.name},
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
                id={'type': 'constraint-sense', 'name': constraint.name},
                className='constraint-sense',
                options=[
                    '≤',
                    '≥',
                    '=',
                ],
                value=constraint.sense,
                clearable=False,
                searchable=False,
                placeholder='Constraint sense',
            ),
            dash.dcc.Input(
                id={'type': 'constraint-rhs', 'name': constraint.name},
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.rhs,
                debounce=True,
                placeholder='Right hand side',
            ),
            dash.dcc.Button(
                id={'type': 'remove-constraint-button', 'name': constraint.name},
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
    initial_objective: Objective,
    initial_constraints: list[Constraint],
    initial_add_constraint_button_n_clicks: int,
    initial_figure: go.Figure,
    initial_optimization_result: str,
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
                            objective_row_component(initial_objective),
                            dash.html.Div(
                                id='constraints-wrapper',
                                children=[
                                    dash.html.Div(
                                        's.t.',
                                        className='st-label',
                                    ),
                                    dash.html.Div(
                                        id='constraints-list',
                                        children=[
                                            constraint_row_component(constraint) for constraint in initial_constraints
                                        ] + [
                                            dash.html.Button(
                                                id='add-constraint-button',
                                                className='button add-constraint-button',
                                                title='Add constraint',
                                                children=[
                                                    'Add constraint',
                                                    # todo: plus icon dash_iconify.DashIconify(icon='mdi:plus')
                                                ],
                                                n_clicks=initial_add_constraint_button_n_clicks,
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
                        id='graph',
                        figure=initial_figure,
                    ),
                    dash.html.Div(
                        id='optimization-result',
                        children=[initial_optimization_result],
                    )
                ],
            ),
        ],
    )
