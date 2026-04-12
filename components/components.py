import dash
import dash_iconify
import dash_latex as dl
import plotly.graph_objects as go

from callbacks.model_state import ConstraintDict, ModelState, ObjectiveDict


def objective_row_component(objective: ObjectiveDict) -> dash.html.Div:
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


def constraint_row_component(constraint: ConstraintDict) -> dash.html.Div:
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
                className='remove-constraint-button',
                title='Remove constraint',
                children=[
                    dash_iconify.DashIconify(icon='mdi:trash-can-outline')
                ],
                n_clicks=0,
            ),
        ],
    )


def app_layout(model_state: ModelState) -> dash.html.Div:
    return dash.html.Div(
        id='app-wrapper',
        children=[
            dash.html.Div(
                id='left-panel',
                children=[
                    dash.html.Div(
                        id='model-wrapper',
                        children = [
                            objective_row_component(model_state.get_objective()),
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
                                            constraint_row_component(constraint) for constraint in model_state.get_constraints()
                                        ] + [
                                            dash.html.Button(
                                                id='add-constraint-button',
                                                className='add-constraint-button',
                                                title='Add constraint',
                                                children=[
                                                    'Add constraint',
                                                    # dash_iconify.DashIconify(icon='mdi:plus')
                                                ],
                                                n_clicks=model_state.last_numerical_name(),
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
                        figure=go.Figure(),
                    ),
                    dash.html.Div(
                        'Optimal value: ',
                        id='solution-value',
                    )
                ],
            ),
        ],
)
