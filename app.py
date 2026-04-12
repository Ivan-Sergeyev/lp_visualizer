import dash
import dash_iconify
import dash_latex as dl
import plotly.graph_objects as go

from callbacks.model_state import ConstraintDict, ModelState, ObjectiveDict


initial_objective = ObjectiveDict(x_coeff=6.0, y_coeff=9.0, sense='max')

initial_constraints = [
    ConstraintDict(name='0', x_coeff=2.0, y_coeff=3.0, sense='<=', rhs=12.0),
    ConstraintDict(name='1', x_coeff=1.0, y_coeff=1.0, sense='<=', rhs=5.0),
    ConstraintDict(name='2', x_coeff=1.0, y_coeff=0.0, sense='>=', rhs=0.0),
    ConstraintDict(name='3', x_coeff=0.0, y_coeff=1.0, sense='>=', rhs=0.0),
]

model_state = ModelState(initial_objective, initial_constraints)

objective_row_component = dash.html.Div(
    id='objective-row',
    children=[
        dash.dcc.Dropdown(
            id='objective-sense',
            options=['max', 'min'],
            value=initial_objective.sense,
            clearable=False,
            searchable=False,
            placeholder='Objective sense',
        ),
        dash.dcc.Input(
            id='objective-x-coeff',
            className='coeff-input',
            type='number',
            inputMode='numeric',
            value=initial_objective.x_coeff,
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
            value=initial_objective.y_coeff,
            debounce=True,
            placeholder='Coefficient for y',
        ),
        dash.html.Div(
            dl.DashLatex(r'$y$'),
            className='variable-label'
        ),
    ],
)

def constraint_component_builder(constraint: ConstraintDict) -> dash.html.Div:
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
                options={
                    '<=' : '≤',
                    '>=' : '≥',
                    '=' : '=',
                },
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

app = dash.Dash(__name__)

# note: there's an alternative way to render math in dash by using mathjax.
# it's done by changing app initialization to:
# ```python
# app = dash.Dash(__name__, external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'] # unfortunately, external)
# ```
# then formulas are rendered by writing, for example, '\\(x\\)' or r'\(x\)' instead of dl.DashLatex(r'$x$')
# however, the mathjax approach is unfortunately unstable---math rendering breaks after a few page reloads

app.layout = dash.html.Div(
    children=[
        dash.html.Div(
            id='model-container',
            children=[
                objective_row_component,
                dash.html.Div(
                    id='constraints-container',
                    children=[
                        dash.html.Div(
                            's.t.',
                            className='st-label',
                        ),
                        dash.html.Div(
                            id='constraints-list',
                            children=[
                                constraint_component_builder(constraint) for constraint in initial_constraints
                            ] + [
                                dash.html.Button(
                                    id='add-constraint-button',
                                    className='add-constraint-button',
                                    title='Add constraint',
                                    children=[
                                        'Add constraint',
                                        # dash_iconify.DashIconify(icon='mdi:plus')
                                    ],
                                    n_clicks=len(initial_constraints) - 1,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        dash.html.Div(
            id='visualization-container',
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


def prase_trigger(trigger: dict[str, str]) -> tuple[str, str]:
    return trigger['prop_id'].split(':')[1].split(',')[0].strip("\""), trigger['value']


@dash.callback(
    dash.Input('objective-sense', 'value'),
    prevent_initial_call=True,
)
def update_objective_sense(selected_sense):
    print(f' --- In update_objective_sense({selected_sense})')
    if selected_sense:
        print(f'Updating model sense with {selected_sense}')
        return model_state.update_objective_sense(selected_sense)


@dash.callback(
    dash.Input('objective-x-coeff', 'value'),
    dash.Input('objective-y-coeff', 'value'),
    prevent_initial_call=True,
)
def update_objective(x_coeff, y_coeff):
    print(f' --- In update_objective({x_coeff}, {y_coeff})')
    if x_coeff is not None and y_coeff is not None:
        return model_state.update_objective(x_coeff, y_coeff)


@dash.callback(
    dash.Input({'type': 'constraint-x-coeff', 'name': dash.ALL}, 'value'),
    prevent_initial_call=True,
)
def update_constraint_x_coefficient(_x_coeffs):
    print(f' --- In update_constraint_x_coefficient({_x_coeffs})')
    for trigger in dash.callback_context.triggered:
        constraint_name, x_coeff = prase_trigger(trigger)
        print(f'Triggered by {constraint_name} with value {x_coeff}')
        return model_state.update_constraint_x_coeff(constraint_name, float(x_coeff))


@dash.callback(
    dash.Input({'type': 'constraint-y-coeff', 'name': dash.ALL}, 'value'),
    prevent_initial_call=True,
)
def update_constraint_y_coefficient(_y_coeffs):
    print(f' --- In update_constraint_y_coefficient ({_y_coeffs})')
    for trigger in dash.callback_context.triggered:
        constraint_name, y_coeff = prase_trigger(trigger)
        print(f'Triggered by {constraint_name} with value {y_coeff}')
        return model_state.update_constraint_y_coeff(constraint_name, float(y_coeff))


@dash.callback(
    dash.Input({'type': 'constraint-sense', 'name': dash.ALL}, 'value'),
    prevent_initial_call=True,
)
def update_constraint_sense(_senses):
    print(f' --- In update_constraint_sense({_senses})')
    for trigger in dash.callback_context.triggered:
        constraint_name, sense = prase_trigger(trigger)
        print(f'Triggered by {constraint_name} with value {sense}')

        if sense is None:
            continue

        return model_state.update_constraint_sense(constraint_name, sense)


@dash.callback(
    dash.Input({'type': 'constraint-rhs', 'name': dash.ALL}, 'value'),
    prevent_initial_call=True,
)
def update_constraint_rhs(_rhs_values):
    print(f' --- In update_constraint_rhs({_rhs_values})')
    for trigger in dash.callback_context.triggered:
        constraint_name, rhs_value = prase_trigger(trigger)
        print(f'Triggered by {constraint_name} with value {rhs_value}')

        if rhs_value is None:
            continue

        return model_state.update_constraint_rhs(constraint_name, float(rhs_value))


def _add_constraint(add_n_clicks: int) -> dash.Patch:
    new_constraint = ConstraintDict(
        name=str(add_n_clicks),
        x_coeff=0.0,
        y_coeff=0.0,
        sense='<=',
        rhs=0.0,
    )

    model_state.add_constraint(new_constraint)
    # todo: propagate graph update

    patch = dash.Patch()
    patch.insert(-1, constraint_component_builder(new_constraint))
    return patch


def _remove_constraint(constraints_container: list, constraint_name: str) -> dash.Patch:
    patch = dash.Patch()
    constraint_found = False

    for pos, elem in enumerate(constraints_container[1]['props']['children']):
        elem_id = elem['props']['id']
        if not isinstance(elem_id, dict):
            continue

        if elem_id['type'] != 'constraint-row' or elem_id['name'] != constraint_name:
            continue

        constraint_found = True
        model_state.remove_constraint(constraint_name)
        # todo: propagate graph update
        del patch[pos]

    if not constraint_found:
        raise ValueError(f'Constraint with name {constraint_name} not found in constraints container list')

    return patch


@dash.callback(
    dash.Output('constraints-list', 'children', True),
    dash.Input('add-constraint-button', 'n_clicks'),
    dash.Input({'type': 'remove-constraint-button', 'name': dash.ALL}, 'n_clicks'),
    dash.State('constraints-container', 'children'),
    prevent_initial_call=True,
    running=[
        (dash.Output('add-constraint-button', 'disabled'), True, False),
        (dash.Output({'type': 'remove-constraint-button', 'name': dash.ALL}, 'disabled'), True, False),
    ],
)
def add_or_remove_constraint(add_n_clicks: int, _remove_ns_clicks: list[int], constraints_container: list):
    print(f' --- In add_constraint({add_n_clicks})')

    for trigger in dash.callback_context.triggered:
        trigger_prop_id = dash.callback_context.triggered_prop_ids[trigger['prop_id']]
        value = trigger['value']
        print(f'trigger_prop_id: {trigger_prop_id}, value: {value}')

        if trigger_prop_id == 'add-constraint-button':
            return _add_constraint(add_n_clicks)

        if trigger_prop_id['type'] == 'remove-constraint-button':
            constraint_name = trigger_prop_id['name']
            if value is None or value == 0:
                continue
            return _remove_constraint(constraints_container, constraint_name)


# todo: add graph drawing callbacks

# todo: add functionality for toggling constraints on/off (buttons, callbacks, greying out)

# note for later: if we want to horizontally align bottom edge of 's.t.' label with bottom edge of first constraint row,
# we need to wrap 's.t.' label and first constraint row in a flex container together; this will require additional logic
# for dynamically adding/removing constraint rows while keeping 's.t.' label properly positioned.

# note for later: how to disable a button while a callback is running
# running=[(dash.Output('submit-button', 'disabled'), True, False)]

# note for later: list of useful links
# very important for implementing callbacks!!! https://dash.plotly.com/pattern-matching-callbacks
# https://dash.plotly.com/dash-core-components
# https://dash.plotly.com/advanced-callbacks
# https://dash.plotly.com/clientside-callbacks
# https://dash.plotly.com/flexible-callback-signatures
# https://dash.plotly.com/callback-gotchas

# note: python-mip documentation https://docs.python-mip.com/en/latest/name.dash.html

# note: can make it look pretty
# - add nicer components with Dash Mantine Components (DMC) https://www.dash-mantine-components.com/
# - add icons with dash-iconify https://pypi.org/project/dash-iconify/ https://github.com/snehilvj/dash-iconify

# known issues:
# - reload browser page => UI refreshes, but not LP model => stale constraint IDs in UI => errors when changing constraints
# - with debug=True, model is optimized twice at startup

if __name__ == '__main__':
    app.run(debug=True)
