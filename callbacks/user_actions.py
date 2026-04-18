import dash
import plotly.graph_objects as go

from callbacks import graph_updates
from model.domain_transfer_objects import Constraint
from model.linear_program import linear_program
from components.components import constraint_row_component


def register(app):
    @app.callback(
        dash.Output('graph', 'figure', allow_duplicate=True),
        dash.Output('optimization-result', 'children', allow_duplicate=True),
        dash.Input('objective-sense', 'value'),
        dash.State('graph', 'figure'),
        prevent_initial_call=True,
    )
    def set_objective_sense(selected_sense: str, figure: go.Figure) -> tuple[dash.Patch, dash.Patch]:
        print(f' --- in {set_objective_sense.__name__}({selected_sense})')

        if not selected_sense:
            return dash.Patch(), dash.Patch()

        linear_program.set_objective_sense(selected_sense)
        linear_program.optimize()

        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        figure_patch = graph_updates.figure_update_objective(figure, linear_program.get_objective())
        return figure_patch, result_patch

    @app.callback(
        dash.Output('graph', 'figure', allow_duplicate=True),
        dash.Output('optimization-result', 'children', allow_duplicate=True),
        dash.Input('objective-x-coeff', 'value'),
        dash.Input('objective-y-coeff', 'value'),
        dash.State('graph', 'figure'),
        prevent_initial_call=True,
    )
    def set_objective_coeffs(x_coeff: float, y_coeff: float, figure: go.Figure) -> tuple[dash.Patch, dash.Patch]:
        print(f' --- in {set_objective_coeffs.__name__}({x_coeff}, {y_coeff})')

        if x_coeff is None or y_coeff is None:
            return dash.Patch(), dash.Patch()

        linear_program.set_objective_coeffs(x_coeff, y_coeff)
        linear_program.optimize()

        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        figure_patch = graph_updates.figure_update_objective(figure, linear_program.get_objective())
        return figure_patch, result_patch

    def add_constraint(constraint: Constraint, figure: go.Figure) -> tuple[dash.Patch, dash.Patch, dash.Patch]:
        print(f' --- in {add_constraint.__name__}({constraint})')

        linear_program.add_constraint(constraint)
        linear_program.optimize()

        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        figure_patch = graph_updates.figure_add_constraint(figure, constraint)
        constraints_patch = dash.Patch()
        constraints_patch.insert(-1, constraint_row_component(constraint))

        return constraints_patch, figure_patch, result_patch

    def set_constraint_x_coefficient(constraint_name: str, x_coeff: float, figure: go.Figure) -> tuple[dash.Patch, dash.Patch, dash.Patch]:
        print(f' --- in {set_constraint_x_coefficient.__name__}({constraint_name}, {x_coeff})')

        linear_program.set_constraint_x_coeff(constraint_name, x_coeff)
        linear_program.optimize()

        figure_patch = graph_updates.figure_update_constraint(figure, linear_program.get_constraint_by_name(constraint_name))
        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        constraints_patch = dash.Patch()

        return constraints_patch, figure_patch, result_patch

    def set_constraint_y_coefficient(constraint_name: str, y_coeff: float, figure: go.Figure) -> tuple[dash.Patch, dash.Patch, dash.Patch]:
        print(f' --- in {set_constraint_y_coefficient.__name__}({constraint_name}, {y_coeff})')

        linear_program.set_constraint_y_coeff(constraint_name, y_coeff)
        linear_program.optimize()

        figure_patch = graph_updates.figure_update_constraint(figure, linear_program.get_constraint_by_name(constraint_name))
        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        constraints_patch = dash.Patch()

        return constraints_patch, figure_patch, result_patch

    def set_constraint_sense(constraint_name: str, sense: str) -> tuple[dash.Patch, dash.Patch, dash.Patch]:
        print(f' --- in {set_constraint_sense.__name__}({constraint_name}, {sense})')

        linear_program.set_constraint_sense(constraint_name, sense)
        linear_program.optimize()

        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        figure_patch = dash.Patch()
        constraints_patch = dash.Patch()

        return constraints_patch, figure_patch, result_patch

    def set_constraint_rhs(constraint_name: str, rhs: float, figure: go.Figure) -> tuple[dash.Patch, dash.Patch, dash.Patch]:
        print(f' --- in {set_constraint_rhs.__name__}({constraint_name}, {rhs})')

        linear_program.set_constraint_rhs(constraint_name, rhs)
        linear_program.optimize()

        figure_patch = graph_updates.figure_update_constraint(figure, linear_program.get_constraint_by_name(constraint_name))
        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        constraints_patch = dash.Patch()

        return constraints_patch, figure_patch, result_patch

    def remove_constraint(constraint_name: str, constraints_list: list, figure: go.Figure) -> tuple[dash.Patch, dash.Patch, dash.Patch]:
        print(f' --- in {remove_constraint.__name__}({constraint_name})')

        occurrences = [
            pos for pos, prop in enumerate(constraints_list)
            if isinstance(prop['props']['id'], dict)
               and prop['props']['id'].get('type') == 'constraint-row'
               and prop['props']['id'].get('name') == constraint_name
        ]

        if len(occurrences) < 1:
            raise ValueError(f'Constraint {constraint_name} not found in constraints list')

        if len(occurrences) > 1:
            raise ValueError(f'Constraint {constraint_name} found in constraints list at more than one index: {occurrences}')

        remaining_constraints = [
            prop for prop in constraints_list
            if isinstance(prop['props']['id'], dict)
                and prop['props']['id'].get('type') == 'constraint-row'
        ]
        if len(remaining_constraints) == 1:
            # reset last constraint instead of removing it to prevent master_constraint_callback() from breaking when no constraints remain
            default_constraint = Constraint(constraint_name)

            linear_program.remove_constraint(constraint_name)
            linear_program.add_constraint(default_constraint)
            linear_program.optimize()

            constraints_patch = dash.Patch()
            constraints_patch[occurrences[0]] = constraint_row_component(default_constraint)
            figure_patch = graph_updates.figure_update_constraint(figure, default_constraint)
            result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
            return constraints_patch, figure_patch, result_patch

        linear_program.remove_constraint(constraint_name)
        linear_program.optimize()

        constraints_patch = dash.Patch()
        del constraints_patch[occurrences[0]]
        result_patch = graph_updates.optimization_result_update(linear_program.get_optimization_result())
        figure_patch = graph_updates.figure_remove_constraint(figure, constraint_name)
        return constraints_patch, figure_patch, result_patch

    @app.callback(
        dash.Output('constraints-list', 'children', allow_duplicate=True),
        dash.Output('graph', 'figure', allow_duplicate=True),
        dash.Output('optimization-result', 'children', allow_duplicate=True),

        dash.Input('add-constraint-button', 'n_clicks'),

        dash.Input({'type': 'constraint-x-coeff', 'name': dash.ALL}, 'value'),
        dash.Input({'type': 'constraint-y-coeff', 'name': dash.ALL}, 'value'),
        dash.Input({'type': 'constraint-sense', 'name': dash.ALL}, 'value'),
        dash.Input({'type': 'constraint-rhs', 'name': dash.ALL}, 'value'),
        dash.Input({'type': 'remove-constraint-button', 'name': dash.ALL}, 'n_clicks'),

        dash.State('constraints-list', 'children'),
        dash.State('graph', 'figure'),

        prevent_initial_call=True,
        running=[
            (dash.Output('add-constraint-button', 'disabled'), True, False),
            (dash.Output({'type': 'remove-constraint-button', 'name': dash.ALL}, 'disabled'), True, False),
        ],
    )
    def master_constraint_callback(
        add_n_clicks: int,

        _x_coeffs: list[float],
        _y_coeffs: list[float],
        _senses: list[str],
        _rhss: list[float],
        _remove_ns_clicks: tuple[int],

        constraints_list: list,
        figure: go.Figure,
    ) -> tuple[dash.Patch, dash.Patch, dash.Patch]:
        print(f' --- in { tuple.__name__}({add_n_clicks})')

        for trigger in dash.callback_context.triggered:
            trigger_prop_id = dash.callback_context.triggered_prop_ids.get(trigger.get('prop_id'))
            trigger_value = trigger.get('value')
            print(f'trigger_prop_id: {trigger_prop_id}, value: {trigger_value}')

            if trigger_prop_id is None:
                continue

            if trigger_prop_id == 'add-constraint-button':
                return add_constraint(Constraint(name=str(add_n_clicks)), figure)

            trigger_type, trigger_name = trigger_prop_id.get('type'), trigger_prop_id.get('name')

            match trigger_type:
                case 'remove-constraint-button':
                    if trigger_value is None or trigger_value == 0:
                        continue
                    return remove_constraint(trigger_name, constraints_list, figure)
                case 'constraint-x-coeff':
                    return set_constraint_x_coefficient(trigger_name, float(trigger_value), figure)
                case 'constraint-y-coeff':
                    return set_constraint_y_coefficient(trigger_name, float(trigger_value), figure)
                case 'constraint-sense':
                    return set_constraint_sense(trigger_name, trigger_value)
                case 'constraint-rhs':
                    return set_constraint_rhs(trigger_name, float(trigger_value), figure)
                case _:
                    raise ValueError(f'Unhandled trigger type {trigger_type} for trigger name {trigger_name} with value {trigger_value}')

        return dash.Patch(), dash.Patch(), dash.Patch()
