from dash import Patch, Input, Output, State, ALL, callback_context
import logging
from plotly.graph_objects import Figure

from callbacks import graph_updates
from model.domain_transfer_objects import Constraint, Objective, OptimizationResult
from model.linear_program import linear_program
from components.components import COMPONENT_IDS, constraint_row_component


type PatchObjectiveChange = tuple[Patch, Patch]
type PatchConstraintChange = tuple[Patch, Patch, Patch]

logger = logging.getLogger(__name__)


def patch_objective(figure: Figure, objective: Objective, optimization_result: OptimizationResult) -> PatchObjectiveChange:
    figure_patch = graph_updates.figure_update_objective(figure, objective)
    result_patch = graph_updates.optimization_result_update(optimization_result)
    return figure_patch, result_patch


def patch_add_constraint(figure: Figure, constraint: Constraint, optimization_result: OptimizationResult) -> PatchConstraintChange:
    constraints_patch = Patch()
    constraints_patch.insert(-1, constraint_row_component(constraint))
    figure_patch = graph_updates.figure_add_constraint(figure, constraint)
    result_patch = graph_updates.optimization_result_update(optimization_result)
    return constraints_patch, figure_patch, result_patch


def patch_update_constraint(figure: Figure, constraint: Constraint, optimization_result: OptimizationResult) -> PatchConstraintChange:
    constraints_patch = Patch()
    figure_patch = graph_updates.figure_update_constraint(figure, constraint)
    result_patch = graph_updates.optimization_result_update(optimization_result)
    return constraints_patch, figure_patch, result_patch


def patch_update_feasible_region(figure: Figure, constraint: Constraint, optimization_result: OptimizationResult) -> PatchConstraintChange:
    constraints_patch = Patch()
    figure_patch = Patch()
    result_patch = graph_updates.optimization_result_update(optimization_result)
    return constraints_patch, figure_patch, result_patch


def patch_remove_constraint(figure: Figure, index: int, name: str, optimization_result: OptimizationResult) -> PatchConstraintChange:
    constraints_patch = Patch()
    del constraints_patch[index]
    figure_patch = graph_updates.figure_remove_constraint(figure, name)
    result_patch = graph_updates.optimization_result_update(optimization_result)
    return constraints_patch, figure_patch, result_patch


def set_objective_sense(sense: str, figure: Figure) -> PatchObjectiveChange:
    logger.debug(f'Calling {set_objective_sense.__name__}({sense})')
    linear_program.set_objective_sense(sense)
    return patch_objective(figure, linear_program.objective(), linear_program.optimization_result())


def set_objective_coeffs(x_coeff: float, y_coeff: float, figure: Figure) -> PatchObjectiveChange:
    logger.debug(f'Calling {set_objective_coeffs.__name__}({x_coeff}, {y_coeff})')
    linear_program.set_objective_coeffs(x_coeff, y_coeff)
    return patch_objective(figure, linear_program.objective(), linear_program.optimization_result())


def add_constraint(constraint: Constraint, figure: Figure) -> PatchConstraintChange:
    logger.debug(f'Calling {add_constraint.__name__}({constraint})')
    linear_program.add_constraint(constraint)
    return patch_add_constraint(figure, constraint, linear_program.optimization_result())


def set_constraint_x_coefficient(constraint_name: str, x_coeff: float, figure: Figure) -> PatchConstraintChange:
    logger.debug(f'Calling {set_constraint_x_coefficient.__name__}({constraint_name}, {x_coeff})')
    linear_program.set_constraint_x_coeff(constraint_name, x_coeff)
    return patch_update_constraint(figure, linear_program.constraint(constraint_name), linear_program.optimization_result())


def set_constraint_y_coefficient(constraint_name: str, y_coeff: float, figure: Figure) -> PatchConstraintChange:
    logger.debug(f'Calling {set_constraint_y_coefficient.__name__}({constraint_name}, {y_coeff})')
    linear_program.set_constraint_y_coeff(constraint_name, y_coeff)
    return patch_update_constraint(figure, linear_program.constraint(constraint_name), linear_program.optimization_result())


def set_constraint_sense(constraint_name: str, sense: str, figure: Figure) -> PatchConstraintChange:
    logger.debug(f'Calling {set_constraint_sense.__name__}({constraint_name}, {sense})')
    linear_program.set_constraint_sense(constraint_name, sense)
    return patch_update_feasible_region(figure, linear_program.constraint(constraint_name), linear_program.optimization_result())


def set_constraint_rhs(constraint_name: str, rhs: float, figure: Figure) -> PatchConstraintChange:
    logger.debug(f'Calling {set_constraint_rhs.__name__}({constraint_name}, {rhs})')
    linear_program.set_constraint_rhs(constraint_name, rhs)
    return patch_update_constraint(figure, linear_program.constraint(constraint_name), linear_program.optimization_result())


def remove_constraint(constraint_name: str, constraints_list: list, figure: Figure) -> PatchConstraintChange:
    logger.debug(f'Calling {remove_constraint.__name__}({constraint_name})')

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
        default_constraint = Constraint(constraint_name)

        linear_program.remove_constraint(constraint_name)
        linear_program.add_constraint(default_constraint)

        constraints_patch = Patch()
        constraints_patch[occurrences[0]] = constraint_row_component(default_constraint)
        figure_patch = graph_updates.figure_update_constraint(figure, default_constraint)
        result_patch = graph_updates.optimization_result_update(linear_program.optimization_result())
        return constraints_patch, figure_patch, result_patch

    linear_program.remove_constraint(constraint_name)
    return patch_remove_constraint(figure, occurrences[0], constraint_name, linear_program.optimization_result())


def register(app):
    @app.callback(
        Output(COMPONENT_IDS['graph'], 'figure', allow_duplicate=True),
        Output(COMPONENT_IDS['optimization_result'], 'children', allow_duplicate=True),
        Input(COMPONENT_IDS['objective']['sense'], 'value'),
        State(COMPONENT_IDS['graph'], 'figure'),
        prevent_initial_call=True,
    )
    def objective_sense_callback(sense: str, figure: Figure) -> PatchObjectiveChange:
        logger.debug(f'Calling {objective_sense_callback.__name__}({sense})')

        if not sense:
            return Patch(), Patch()

        return set_objective_sense(sense, figure)

    @app.callback(
        Output(COMPONENT_IDS['graph'], 'figure', allow_duplicate=True),
        Output(COMPONENT_IDS['optimization_result'], 'children', allow_duplicate=True),
        Input(COMPONENT_IDS['objective']['x_coeff'], 'value'),
        Input(COMPONENT_IDS['objective']['y_coeff'], 'value'),
        State(COMPONENT_IDS['graph'], 'figure'),
        prevent_initial_call=True,
    )
    def objective_coeffs_callback(x_coeff: float, y_coeff: float, figure: Figure) -> PatchObjectiveChange:
        logger.debug(f'Calling {objective_coeffs_callback.__name__}({x_coeff}, {y_coeff})')

        if x_coeff is None or y_coeff is None:
            return Patch(), Patch()

        return set_objective_coeffs(x_coeff, y_coeff, figure)

    @app.callback(
        Output(COMPONENT_IDS['constraints']['list'], 'children', allow_duplicate=True),
        Output(COMPONENT_IDS['graph'], 'figure', allow_duplicate=True),
        Output(COMPONENT_IDS['optimization_result'], 'children', allow_duplicate=True),

        Input(COMPONENT_IDS['constraints']['add_button'], 'n_clicks'),

        Input(COMPONENT_IDS['constraints']['x_coeff'](ALL), 'value'),
        Input(COMPONENT_IDS['constraints']['y_coeff'](ALL), 'value'),
        Input(COMPONENT_IDS['constraints']['sense'](ALL), 'value'),
        Input(COMPONENT_IDS['constraints']['rhs'](ALL), 'value'),
        Input(COMPONENT_IDS['constraints']['remove_button'](ALL), 'n_clicks'),

        State(COMPONENT_IDS['constraints']['list'], 'children'),
        State(COMPONENT_IDS['graph'], 'figure'),

        prevent_initial_call=True,
        running=[
            (Output(COMPONENT_IDS['constraints']['add_button'], 'disabled'), True, False),
            (Output(COMPONENT_IDS['constraints']['remove_button'](ALL), 'disabled'), True, False),
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
        figure: Figure,
    ) -> PatchConstraintChange:
        logger.debug(f'Calling {master_constraint_callback.__name__}({add_n_clicks})')

        for trigger in callback_context.triggered:
            trigger_prop_id = callback_context.triggered_prop_ids.get(trigger.get('prop_id'))
            trigger_value = trigger.get('value')
            logger.debug(f'Calling {trigger_prop_id}, value: {trigger_value}')

            if trigger_prop_id is None:
                continue

            if trigger_prop_id == COMPONENT_IDS['constraints']['add_button']:
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
                    return set_constraint_sense(trigger_name, trigger_value, figure)
                case 'constraint-rhs':
                    return set_constraint_rhs(trigger_name, float(trigger_value), figure)
                case _:
                    raise ValueError(f'Unhandled trigger type {trigger_type} for trigger name {trigger_name} with value {trigger_value}')

        return Patch(), Patch(), Patch()
