from __future__ import annotations

import logging
from dataclasses import dataclass, field

import dash
import plotly.graph_objects as go

from algorithms.simplex import SimplexSolver
from callbacks import graph
from components.app_layout import PAGE_IDS
from components.common import STORAGE_TYPE
from components.constraint import CONSTRAINT_IDS, constraint_layout, constraint_store
from components.objective import OBJECTIVE_IDS
from model.constraint import Constraint, ConstraintDict, ConstraintSense
from model.objective import Objective, ObjectiveDict

logger = logging.getLogger(__name__)


# --- Objective ---

def objective_set_sense(sense: str) -> dash.Patch:
    logger.debug(f'Calling {objective_set_sense.__name__}({sense})')
    objective_patch = dash.Patch()
    objective_patch['sense'] = sense
    return objective_patch


def objective_set_coeff_x(coeff_x: float) -> dash.Patch:
    logger.debug(f'Calling {objective_set_coeff_x.__name__}({coeff_x})')
    objective_patch = dash.Patch()
    objective_patch['coeff_x'] = coeff_x
    return objective_patch


def objective_set_coeff_y(coeff_y: float) -> dash.Patch:
    logger.debug(f'Calling {objective_set_coeff_y.__name__}({coeff_y})')
    objective_patch = dash.Patch()
    objective_patch['coeff_y'] = coeff_y
    return objective_patch


# --- Constraint ---

type ConstraintPatchTuple = tuple[dash.Patch, dash.Patch, dash.Patch]

@dataclass
class ConstraintPatch:
    constraints: dash.Patch = field(default_factory=dash.Patch)
    figure: dash.Patch = field(default_factory=dash.Patch)
    store: dash.Patch = field(default_factory=dash.Patch)

    @staticmethod
    def _num_constraints(constraints_list: list) -> int:
        return len([
            prop for prop in constraints_list
            if isinstance(prop['props']['id'], dict)
                and prop['props']['id'].get('type') == 'constraint-row'
        ])

    @staticmethod
    def _pos_in_constraints_list(constraint_name: str, constraints_list: list) -> int:
        occurrences = [
            pos for pos, prop in enumerate(constraints_list)
            if prop['props']['id'] == CONSTRAINT_IDS['row'](constraint_name)
        ]

        if len(occurrences) < 1:
            raise ValueError(f'Constraint {constraint_name} not found in constraints list')

        if len(occurrences) > 1:
            raise ValueError(f'Constraint {constraint_name} found in constraints list at more than one index: {occurrences}')

        return occurrences[0]

    @staticmethod
    def _pos_in_constraints_store(constraint_name: str, constraints_store: list) -> int:
        occurrences = [
            pos for pos, prop in enumerate(constraints_store)
            if prop['props']['id'] == CONSTRAINT_IDS['store'](constraint_name)
        ]

        if len(occurrences) < 1:
            raise ValueError(f'Constraint {constraint_name} not found in constraints list')

        if len(occurrences) > 1:
            raise ValueError(f'Constraint {constraint_name} found in constraints list at more than one index: {occurrences}')

        return occurrences[0]

    def to_tuple(self) -> ConstraintPatchTuple:
        return self.constraints, self.figure, self.store

    def set_coeff_x(self, constraint_name: str, coeff_x: float, constraints_list: list, figure: go.Figure, constraints_store: list) -> ConstraintPatch:
        logger.debug(f'Calling {self.set_coeff_x.__name__}({coeff_x})')
        pos_in_store = self._pos_in_constraints_store(constraint_name, constraints_store)
        constraint_dict = constraints_store[pos_in_store]['props']['data']
        constraint_dict['coeff_x'] = coeff_x

        self.constraints = dash.Patch()
        self.figure = graph.figure_update_constraint(figure, constraint_name, Constraint.from_dict(constraint_dict))
        self.store[pos_in_store]['props']['data']['coeff_x'] = coeff_x
        return self

    def set_coeff_y(self, constraint_name: str, coeff_y: float, constraints_list: list, figure: go.Figure, constraints_store: list) -> ConstraintPatch:
        logger.debug(f'Calling {self.set_coeff_y.__name__}({coeff_y})')
        pos_in_store = self._pos_in_constraints_store(constraint_name, constraints_store)
        constraint_dict = constraints_store[pos_in_store]['props']['data']
        constraint_dict['coeff_y'] = coeff_y

        self.constraints = dash.Patch()
        self.figure = graph.figure_update_constraint(figure, constraint_name, Constraint.from_dict(constraint_dict))
        self.store[pos_in_store]['props']['data']['coeff_y'] = coeff_y
        return self

    def set_sense(self, constraint_name: str, sense: ConstraintSense, constraints_list: list, figure: go.Figure, constraints_store: list) -> ConstraintPatch:
        logger.debug(f'Calling {self.set_sense.__name__}({sense})')
        pos_in_store = self._pos_in_constraints_store(constraint_name, constraints_store)
        constraint_dict = constraints_store[pos_in_store]['props']['data']
        constraint_dict['sense'] = sense

        self.constraints = dash.Patch()
        self.figure = dash.Patch()
        self.store[pos_in_store]['props']['data']['sense'] = sense
        return self

    def set_rhs(self, constraint_name: str, rhs: float, constraints_list: list, figure: go.Figure, constraints_store: list) -> ConstraintPatch:
        logger.debug(f'Calling {self.set_rhs.__name__}({rhs})')
        pos_in_store = self._pos_in_constraints_store(constraint_name, constraints_store)
        constraint_dict = constraints_store[pos_in_store]['props']['data']
        constraint_dict['rhs'] = rhs

        self.constraints = dash.Patch()
        self.figure = graph.figure_update_constraint(figure, constraint_name, Constraint.from_dict(constraint_dict))
        self.store[pos_in_store]['props']['data']['rhs'] = rhs
        return self

    def add(self, constraint_name: str, figure: go.Figure) -> ConstraintPatch:
        logger.debug(f'Calling {self.add.__name__}({constraint_name})')
        constraint = Constraint()

        self.constraints.insert(-1, constraint_layout(constraint_name, constraint))
        self.figure = graph.figure_add_constraint(figure, constraint_name, constraint)
        self.store.append(constraint_store(constraint_name, constraint, STORAGE_TYPE))
        return self

    def _replace_with_default(self, constraint_name: str, constraints_list: list, figure: go.Figure, constraints_store: list) -> ConstraintPatch:
        logger.debug(f'Calling {self._replace_with_default.__name__}({constraint_name})')
        pos_in_constraints = self._pos_in_constraints_list(constraint_name, constraints_list)
        pos_in_store = self._pos_in_constraints_store(constraint_name, constraints_store)
        constraint = Constraint()

        self.constraints[pos_in_constraints] = constraint_layout(constraint_name, constraint)
        self.figure = graph.figure_update_constraint(figure, constraint_name, constraint)
        self.store[pos_in_store]['props']['data'] = constraint.to_dict()
        return self

    def _remove(self, constraint_name: str, constraints_list: list, figure: go.Figure, constraints_store: list) -> ConstraintPatch:
        logger.debug(f'Calling {self._remove.__name__}({constraint_name})')
        pos_in_constraints = self._pos_in_constraints_list(constraint_name, constraints_list)
        pos_in_store = self._pos_in_constraints_store(constraint_name, constraints_store)

        del self.constraints[pos_in_constraints]
        self.figure = graph.figure_remove_constraint(figure, constraint_name)
        del self.store[pos_in_store]
        return self

    def remove(self, constraint_name: str, constraints_list: list, figure: go.Figure, constraints_store: list) -> ConstraintPatch:
        logger.debug(f'Calling {self.remove.__name__}({constraint_name})')
        if self._num_constraints(constraints_list) == 1:
            return self._replace_with_default(constraint_name, constraints_list, figure, constraints_store)
        else:
            return self._remove(constraint_name, constraints_list, figure, constraints_store)


# --- Register ---

def register(app):
    # --- Objective ---

    @app.callback(
        dash.Output(OBJECTIVE_IDS['store'], 'data', allow_duplicate=True),
        dash.Input(OBJECTIVE_IDS['sense'], 'value'),
        prevent_initial_call=True,
    )
    def objective_sense_callback(sense: str) -> dash.Patch:
        return objective_set_sense(sense)

    @app.callback(
        dash.Output(OBJECTIVE_IDS['store'], 'data', allow_duplicate=True),
        dash.Input(OBJECTIVE_IDS['coeff_x'], 'value'),
        prevent_initial_call=True,
    )
    def objective_coeff_x_callback(coeff_x: float) -> dash.Patch:
        return objective_set_coeff_x(coeff_x)

    @app.callback(
        dash.Output(OBJECTIVE_IDS['store'], 'data', allow_duplicate=True),
        dash.Input(OBJECTIVE_IDS['coeff_y'], 'value'),
        prevent_initial_call=True,
    )
    def objective_coeff_y_callback(coeff_y: float) -> dash.Patch:
        return objective_set_coeff_y(coeff_y)

    @app.callback(
        dash.Output(PAGE_IDS['graph'], 'figure', allow_duplicate=True),
        dash.Input(OBJECTIVE_IDS['store'], 'data'),
        dash.State(PAGE_IDS['graph'], 'figure'),
        prevent_initial_call=True,
    )
    def objective_store_callback(objective: ObjectiveDict, figure: go.Figure) -> dash.Patch:
        logger.debug(f'Calling {objective_store_callback.__name__}({objective})')
        return graph.figure_update_objective(figure, Objective.from_dict(objective))

    # --- Constraint ---

    @app.callback(
        dash.Output(PAGE_IDS['constraints_list'], 'children', allow_duplicate=True),
        dash.Output(PAGE_IDS['graph'], 'figure', allow_duplicate=True),
        dash.Output('constraints-store', 'children', allow_duplicate=True),

        dash.Input(PAGE_IDS['add_constraint_button'], 'n_clicks'),

        dash.Input(CONSTRAINT_IDS['coeff_x'](dash.ALL), 'value'),
        dash.Input(CONSTRAINT_IDS['coeff_y'](dash.ALL), 'value'),
        dash.Input(CONSTRAINT_IDS['sense'](dash.ALL), 'value'),
        dash.Input(CONSTRAINT_IDS['rhs'](dash.ALL), 'value'),
        dash.Input(CONSTRAINT_IDS['remove_button'](dash.ALL), 'n_clicks'),

        dash.State(PAGE_IDS['constraints_list'], 'children'),
        dash.State(PAGE_IDS['graph'], 'figure'),
        dash.State('constraints-store', 'children'),

        prevent_initial_call=True,
        running=[
            (dash.Output(PAGE_IDS['add_constraint_button'], 'disabled'), True, False),
            (dash.Output(CONSTRAINT_IDS['remove_button'](dash.ALL), 'disabled'), True, False),
        ],
    )
    def constraint_master_callback(
        add_n_clicks: int,

        _coeff_xs: list[float],
        _coeffs_y: list[float],
        _senses: list[str],
        _rhss: list[float],
        _remove_n_clicks: tuple[int],

        constraints_list: list,
        figure: go.Figure,
        constraints_store: list,
    ) -> ConstraintPatchTuple:
        logger.debug(f'Calling {constraint_master_callback.__name__}()')

        trigger = dash.callback_context.triggered[0]
        trigger_prop_id = dash.callback_context.triggered_prop_ids.get(trigger.get('prop_id'), {})
        trigger_value = trigger.get('value')
        logger.debug(f'Triggered by {trigger_prop_id} with value {trigger_value}')

        if trigger_prop_id is None:
            return ConstraintPatch().to_tuple()

        if trigger_prop_id == PAGE_IDS['add_constraint_button']:
            return ConstraintPatch().add(str(add_n_clicks), figure).to_tuple()

        trigger_name = trigger_prop_id.get('name', '')

        if trigger_prop_id == CONSTRAINT_IDS['remove_button'](trigger_name):
            if trigger_value is None or trigger_value == 0:
                return ConstraintPatch().to_tuple()
            return ConstraintPatch().remove(trigger_name, constraints_list, figure, constraints_store).to_tuple()

        if trigger_prop_id == CONSTRAINT_IDS['coeff_x'](trigger_name):
            return ConstraintPatch().set_coeff_x(trigger_name, float(trigger_value), constraints_list, figure, constraints_store).to_tuple()

        if trigger_prop_id == CONSTRAINT_IDS['coeff_y'](trigger_name):
            return ConstraintPatch().set_coeff_y(trigger_name, float(trigger_value), constraints_list, figure, constraints_store).to_tuple()

        if trigger_prop_id == CONSTRAINT_IDS['sense'](trigger_name):
            return ConstraintPatch().set_sense(trigger_name, trigger_value, constraints_list, figure, constraints_store).to_tuple()

        if trigger_prop_id == CONSTRAINT_IDS['rhs'](trigger_name):
            return ConstraintPatch().set_rhs(trigger_name, float(trigger_value), constraints_list, figure, constraints_store).to_tuple()

        raise ValueError(f'Unhandled trigger {trigger_prop_id} with value {trigger_value}')

    # --- Result ---

    @app.callback(
        dash.Output(PAGE_IDS['result'], 'children'),
        dash.Input(OBJECTIVE_IDS['store'], 'data'),
        dash.Input(CONSTRAINT_IDS['store'](dash.ALL), 'data'),
        prevent_initial_call=True,
    )
    def result_callback(objective: ObjectiveDict, constraints: list[ConstraintDict]) -> dash.Patch:
        logger.debug(f'Calling {result_callback.__name__}({objective}, {[str(Constraint.from_dict(constraint)) for constraint in constraints]})')
        solver = SimplexSolver.solve(
            objective=Objective.from_dict(objective),
            constraints=[Constraint.from_dict(constraint) for constraint in constraints]
        )
        result = solver.get_result()
        return graph.update_result(str(result))
