import dash
from dash import ALL, MATCH, State, dcc, html, callback, Input, Output, Patch

import plotly.graph_objects as go

from callbacks.model_state import ConstraintDict, ModelState, ObjectiveDict, constraint_id_to_name


initial_objective = ObjectiveDict(x_coeff=6.0, y_coeff=9.0, sense='max')

initial_constraints = [
    ConstraintDict(id=0, name=constraint_id_to_name(0), x_coeff=2.0, y_coeff=3.0, sense='<=', rhs=12.0),
    ConstraintDict(id=1, name=constraint_id_to_name(1), x_coeff=1.0, y_coeff=1.0, sense='<=', rhs=5.0),
    ConstraintDict(id=2, name=constraint_id_to_name(2), x_coeff=1.0, y_coeff=0.0, sense='>=', rhs=0.0),
    ConstraintDict(id=3, name=constraint_id_to_name(3), x_coeff=0.0, y_coeff=1.0, sense='>=', rhs=0.0),
]

model_state = ModelState(initial_objective, initial_constraints)

objective_row_component = html.Div(
    id='objective-row',
    children=[
        dcc.Dropdown(
            id='objective-sense',
            options=['max', 'min'],
            value=initial_objective.sense,
            clearable=False,
            searchable=False,
            placeholder='Objective sense',
        ),
        dcc.Input(
            id='objective-x-coeff',
            className='coeff-input',
            type='number',
            inputMode='numeric',
            value=initial_objective.x_coeff,
            debounce=True,
            placeholder='Coefficient for x',
        ),
        html.Div(
            'x',
            className='variable-label',
        ),
        html.Div(
            '+',
            id='objective-sign-label',
            className='sign-label',
        ),
        dcc.Input(
            id='objective-y-coeff',
            className='coeff-input',
            type='number',
            inputMode='numeric',
            value=initial_objective.y_coeff,
            debounce=True,
            placeholder='Coefficient for y',
        ),
        html.Div(
            'y',
            className='variable-label'
        ),
    ],
)

def constraint_component_builder(constraint: ConstraintDict) -> html.Div:
    return html.Div(
        id={'type': 'constraint-row', 'index': constraint.id},
        className='constraint-row',
        children=[
            dcc.Input(
                id={'type': 'constraint-x-coeff', 'index': constraint.id},
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.x_coeff,
                debounce=True,
                placeholder='Coefficient for x',
            ),
            html.Div(
                'x',
                className='variable-label',
            ),
            html.Div(
                '+',
                id={'type': 'constraint-sign-label', 'index': constraint.id},
                className='sign-label',
            ),
            dcc.Input(
                id={'type': 'constraint-y-coeff', 'index': constraint.id},
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.y_coeff,
                debounce=True,
                placeholder='Coefficient for y',
            ),
            html.Div(
                'y',
                className='variable-label',
            ),
            dcc.Dropdown(
                id={'type': 'constraint-sense', 'index': constraint.id},
                className='constraint-sense',
                options=['<=', '>=', '='],
                value=constraint.sense,
                clearable=False,
                searchable=False,
                placeholder='Constraint sense',
            ),
            dcc.Input(
                id={'type': 'constraint-rhs', 'index': constraint.id},
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.rhs,
                debounce=True,
                placeholder='Right hand side',
            )
        ],
    )

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(
            id='model-container',
            children=[
                objective_row_component,
                html.Div(
                    id='constraints-container',
                    children=[
                        html.Div(
                            's.t.',
                            className='st-label',
                        ),
                        html.Div(
                            id='constraints-list',
                            children=[
                                constraint_component_builder(constraint) for constraint in initial_constraints
                            ],
                        ),
                    ]
                )
            ],
        ),
        html.Div(
            id='visualization-container',
            children=[
                dcc.Graph(
                    id='graph',
                    figure=go.Figure(),
                ),
                html.Div(
                    'Optimal value: ',
                    id='solution-value',
                )
            ],
        ),
    ],
)

@callback(
    Input('objective-sense', 'value')
)
def update_objective_sense(selected_sense):
    print(f'Received objective sense change to {selected_sense} in callback.')
    if selected_sense:
        return model_state.update_objective_sense(selected_sense)

@callback(
    Input('objective-x-coeff', 'value'),
    Input('objective-y-coeff', 'value')
)
def update_objective(x_coeff, y_coeff):
    print(f'Received objective coefficient change to x: {x_coeff}, y: {y_coeff} in callback.')
    if x_coeff is not None and y_coeff is not None:
        return model_state.update_objective(x_coeff, y_coeff)

@callback(
    # Output({'type': 'constraint-line', 'index': MATCH}, 'value'),
    Input({'type': 'constraint-x-coeff', 'index': ALL}, 'value'),
    # State({'type': 'constraint-x-coeff', 'index': MATCH}, 'id'),
)
def update_constraint_x_coefficient(_x_coeffs):
    for trigger in dash.callback_context.triggered:
        constraint_id = int(trigger['prop_id'].split(':')[1].split(',')[0])
        x_coeff = float(trigger['value'])
        print(f'Triggered by {constraint_id} with value {x_coeff}')
        return model_state.update_constraint_x_coeff(constraint_id_to_name(constraint_id), x_coeff)

@callback(
    Input({'type': 'constraint-y-coeff', 'index': ALL}, 'value'),
)
def update_constraint_y_coefficient(_y_coeffs):
    for trigger in dash.callback_context.triggered:
        constraint_id = int(trigger['prop_id'].split(':')[1].split(',')[0])
        y_coeff = float(trigger['value'])
        print(f'Triggered by {constraint_id} with value {y_coeff}')
        return model_state.update_constraint_y_coeff(constraint_id_to_name(constraint_id), y_coeff)

@callback(
    Input({'type': 'constraint-sense', 'index': ALL}, 'value'),
)
def update_constraint_sense(_senses):
    for trigger in dash.callback_context.triggered:
        constraint_id = int(trigger['prop_id'].split(':')[1].split(',')[0])
        sense = trigger['value']
        print(f'Triggered by {constraint_id} with value {sense}')
        return model_state.update_constraint_sense(constraint_id_to_name(constraint_id), sense)

@callback(
    Input({'type': 'constraint-rhs', 'index': ALL}, 'value'),
)
def update_constraint_rhs(_rhs_values):
    for trigger in dash.callback_context.triggered:
        constraint_id = int(trigger['prop_id'].split(':')[1].split(',')[0])
        rhs_value = float(trigger['value'])
        print(f'Triggered by {constraint_id} with value {rhs_value}')
        return model_state.update_constraint_rhs(constraint_id_to_name(constraint_id), rhs_value)

# todo: add graph drawing callbacks

# todo: add functionality for adding new constraint (button, callback)
# todo: add functionality for removing existing constraint (button, callback)
# todo: add functionality for toggling constraints on/off (buttons, callbacks, greying out)

# note for later: if we want to horizontally align bottom edge of 's.t.' label with bottom edge of first constraint row,
# we need to wrap 's.t.' label and first constraint row in a flex container together; this will require additional logic
# for dynamically adding/removing constraint rows while keeping 's.t.' label properly positioned.

# note for later: how to disable a button while a callback is running
# running=[(Output('submit-button', 'disabled'), True, False)]

# note for later: list of useful links
# very important for implementing callbacks!!! https://dash.plotly.com/pattern-matching-callbacks
# https://dash.plotly.com/dash-core-components
# https://dash.plotly.com/advanced-callbacks
# https://dash.plotly.com/clientside-callbacks
# https://dash.plotly.com/flexible-callback-signatures
# https://dash.plotly.com/callback-gotchas

# note: python-mip documentation https://docs.python-mip.com/en/latest/index.html

if __name__ == '__main__':
    app.run(debug=True)
