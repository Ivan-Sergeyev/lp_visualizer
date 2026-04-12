import dash

from callbacks.model_state import model_state, ConstraintDict
from components.components import constraint_row_component


def get_trigger_prop_ids_and_values():
    return [
        (dash.callback_context.triggered_prop_ids[trigger['prop_id']], trigger['value'])
        for trigger in dash.callback_context.triggered
    ]


def register(app):
    @app.callback(
        dash.Input('objective-sense', 'value'),
        prevent_initial_call=True,
    )
    def update_objective_sense(selected_sense):
        print(f' --- In update_objective_sense({selected_sense})')
        if selected_sense:
            print(f'Updating model sense with {selected_sense}')
            return model_state.update_objective_sense(selected_sense)


    @app.callback(
        dash.Input('objective-x-coeff', 'value'),
        dash.Input('objective-y-coeff', 'value'),
        prevent_initial_call=True,
    )
    def update_objective(x_coeff, y_coeff):
        print(f' --- In update_objective({x_coeff}, {y_coeff})')
        if x_coeff is not None and y_coeff is not None:
            return model_state.update_objective(x_coeff, y_coeff)


    @app.callback(
        dash.Input({'type': 'constraint-x-coeff', 'name': dash.ALL}, 'value'),
        prevent_initial_call=True,
    )
    def update_constraint_x_coefficient(_x_coeffs):
        print(f' --- In update_constraint_x_coefficient({_x_coeffs})')
        for constraint_prop_id, x_coeff in get_trigger_prop_ids_and_values():
            print(f'Triggered by {constraint_prop_id} with value {x_coeff}')
            return model_state.update_constraint_x_coeff(constraint_prop_id['name'], float(x_coeff))


    @app.callback(
        dash.Input({'type': 'constraint-y-coeff', 'name': dash.ALL}, 'value'),
        prevent_initial_call=True,
    )
    def update_constraint_y_coefficient(_y_coeffs):
        print(f' --- In update_constraint_y_coefficient ({_y_coeffs})')
        for constraint_prop_id, y_coeff in get_trigger_prop_ids_and_values():
            print(f'Triggered by {constraint_prop_id} with value {y_coeff}')
            return model_state.update_constraint_y_coeff(constraint_prop_id['name'], float(y_coeff))


    @app.callback(
        dash.Input({'type': 'constraint-sense', 'name': dash.ALL}, 'value'),
        prevent_initial_call=True,
    )
    def update_constraint_sense(_senses):
        print(f' --- In update_constraint_sense({_senses})')
        for constraint_prop_id, sense in get_trigger_prop_ids_and_values():
            print(f'Triggered by {constraint_prop_id} with value {sense}')
            return model_state.update_constraint_sense(constraint_prop_id['name'], sense)


    @app.callback(
        dash.Input({'type': 'constraint-rhs', 'name': dash.ALL}, 'value'),
        prevent_initial_call=True,
    )
    def update_constraint_rhs(_rhs_values):
        print(f' --- In update_constraint_rhs({_rhs_values})')
        for constraint_prop_id, rhs_value in get_trigger_prop_ids_and_values():
            print(f'Triggered by {constraint_prop_id} with value {rhs_value}')
            return model_state.update_constraint_rhs(constraint_prop_id['name'], float(rhs_value))


    def _add_constraint(add_n_clicks: int) -> dash.Patch:
        new_constraint = ConstraintDict(name=str(add_n_clicks))

        model_state.add_constraint(new_constraint)
        # todo: propagate graph update

        patch = dash.Patch()
        patch.insert(-1, constraint_row_component(new_constraint))
        return patch


    def _remove_constraint(constraints_container: list, constraint_name: str) -> dash.Patch:
        patch = dash.Patch()
        constraint_found = False

        for pos, prop in enumerate(constraints_container[1]['props']['children']):
            elem_id = prop['props']['id']

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


    @app.callback(
        dash.Output('constraints-list', 'children', True),
        dash.Input('add-constraint-button', 'n_clicks'),
        dash.Input({'type': 'remove-constraint-button', 'name': dash.ALL}, 'n_clicks'),
        dash.State('constraints-wrapper', 'children'),
        prevent_initial_call=True,
        running=[
            (dash.Output('add-constraint-button', 'disabled'), True, False),
            (dash.Output({'type': 'remove-constraint-button', 'name': dash.ALL}, 'disabled'), True, False),
        ],
    )
    def add_or_remove_constraint(add_n_clicks: int, _remove_ns_clicks: list[int], constraints_container: list):
        print(f' --- In add_constraint({add_n_clicks})')

        for trigger_prop_id, value in get_trigger_prop_ids_and_values():
            print(f'trigger_prop_id: {trigger_prop_id}, value: {value}')

            if trigger_prop_id == 'add-constraint-button':
                return _add_constraint(add_n_clicks)

            if trigger_prop_id['type'] == 'remove-constraint-button':
                if value is None or value == 0:
                    continue
                constraint_name = trigger_prop_id['name']
                return _remove_constraint(constraints_container, constraint_name)
