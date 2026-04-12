from dataclasses import dataclass
import traceback
from typing import Tuple

import mip


@dataclass
class ObjectiveDict:
    x_coeff: float
    y_coeff: float
    sense: str


def objective_sense_to_mip(sense: str) -> str:
    match sense:
        case 'max' | mip.MAXIMIZE:
            return mip.MAXIMIZE
        case 'min' | mip.MINIMIZE:
            return mip.MINIMIZE
        case _:
            raise ValueError(f'Unrecognized objective sense {sense}.')


@dataclass
class ConstraintDict:
    name: str
    x_coeff: float
    y_coeff: float
    sense: str
    rhs: float

    @property
    def sense_mip(self) -> str:
        match self.sense:
            case '<' | '<=' | '≤' | mip.LESS_OR_EQUAL:
                return mip.LESS_OR_EQUAL
            case '>' | '>=' | '≥' | mip.GREATER_OR_EQUAL:
                return mip.GREATER_OR_EQUAL
            case '=' | '==' | mip.EQUAL:
                return mip.EQUAL
            case _:
                raise ValueError(f'Unrecognized constraint sense {self.sense}.')

    def convert_sense_to_mip(self):
        self.sense = self.sense_mip()


def constraint_dict_from_mip(constraint: mip.Constr, x: mip.Var, y: mip.Var) -> ConstraintDict:
    return ConstraintDict(
        name=get_mip_constraint_name(constraint),
        x_coeff=get_mip_constraint_coeff(constraint, x),
        y_coeff=get_mip_constraint_coeff(constraint, y),
        sense=get_mip_constraint_sense(constraint),
        rhs=get_mip_constraint_rhs(constraint)
    )


def get_mip_constraint_name(constraint: mip.Constr) -> str:
    return constraint.name


def get_mip_constraint_coeff(constraint: mip.Constr, variable: mip.Var) -> float:
    return constraint.expr.expr.get(variable, 0.)


def get_mip_constraint_sense(constraint: mip.Constr) -> str:
    return constraint.expr.sense


def get_mip_constraint_rhs(constraint: mip.Constr) -> float:
    return constraint.rhs


def deconstruct_mip_constraint(constraint: mip.Constr, x: mip.Var, y: mip.Var) -> Tuple[str, float, float, str, float]:
    name = get_mip_constraint_name(constraint)
    x_coeff = get_mip_constraint_coeff(constraint, x)
    y_coeff = get_mip_constraint_coeff(constraint, y)
    sense = get_mip_constraint_sense(constraint)
    rhs = get_mip_constraint_rhs(constraint)
    return name, x_coeff, y_coeff, sense, rhs


@dataclass
class ModelState:
    model: mip.Model

    def __init__(
            self,
            objective: ObjectiveDict = ObjectiveDict(x_coeff=0.0, y_coeff=0.0, sense='max'),
            constraints: list[ConstraintDict] = []):
        self.model = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)

        self.x = self.model.add_var(name='x', lb=-mip.INF, ub=mip.INF, var_type=mip.CONTINUOUS)
        self.y = self.model.add_var(name='y', lb=-mip.INF, ub=mip.INF, var_type=mip.CONTINUOUS)

        self._update_objective_coeffs(objective.x_coeff, objective.y_coeff)
        self._update_sense(objective.sense)

        for constraint in constraints:
            self._add_constraint(constraint)

        self._optimize()
        # todo: return graph callback result to update entire graph

    def _optimize(self):
        print(f'Called _optimize()')
        for line in traceback.format_stack():
            print(line.strip())

        status = self.model.optimize()
        self.__debug()

        match status:
            case mip.OptimizationStatus.OPTIMAL:
                solution_value = self.model.objective_value
                solution_x = self.x.x
                solution_y = self.y.x
                print(f'Optimal solution found with value {solution_value} at x={solution_x}, y={solution_y}.')
                pass
                # todo: return graph callback result to update solution
            case mip.OptimizationStatus.UNBOUNDED:
                print('Model is unbounded.')
                # todo: return graph callback result to update solution
                pass
            case mip.OptimizationStatus.INFEASIBLE:
                print('Model is infeasible.')
                # todo: return graph callback result to update solution
                pass
            case _:
                # todo: display error message
                pass

    def __debug(self):
        print(self.model.objective)
        for constraint in self.model.constrs:
            print(constraint)

    def _update_objective_coeffs(self, x_coeff: float, y_coeff: float):
        self.model.objective = mip.LinExpr(variables=[self.x, self.y], coeffs=[x_coeff, y_coeff])

    def _update_sense(self, sense: str):
        self.model.sense = objective_sense_to_mip(sense)

    def _get_constraint(self, name: str) -> mip.Constr:
        print(f'looking for constr {name}')
        for constr in self.model.constrs:
            print(constr.name)

        constraint = self.model.constr_by_name(name)

        if constraint is None:
            raise ValueError(f'Constraint with name {name} not found.')

        return constraint

    def _add_constraint(self, constraint: ConstraintDict):
        lin_expr = mip.LinExpr(
            variables=[self.x, self.y],
            coeffs=[constraint.x_coeff, constraint.y_coeff],
            sense=constraint.sense_mip,
            const=-constraint.rhs,
        )
        self.model.add_constr(lin_expr, name=constraint.name)

    def _remove_constraint(self, constraint: mip.Constr):
        self.model.remove(constraint)

    def _update_constraint_x_coeff(self, constraint: mip.Constr, x_coeff: float):
        # note: constraint coeffs cannot be updated in-place in mip, so remove and re-add constraint with new coeffs
        updated_constraint = constraint_dict_from_mip(constraint, self.x, self.y)
        updated_constraint.x_coeff = x_coeff
        self._remove_constraint(constraint)
        self._add_constraint(updated_constraint)

    def _update_constraint_y_coeff(self, constraint: mip.Constr, y_coeff: float):
        # note: constraint coeffs cannot be updated in-place in mip, so remove and re-add constraint with new coeffs
        updated_constraint = constraint_dict_from_mip(constraint, self.x, self.y)
        updated_constraint.y_coeff = y_coeff
        self._remove_constraint(constraint)
        self._add_constraint(updated_constraint)

    def _update_constraint_sense(self, constraint: mip.Constr, sense: str):
        # note: constraint sense cannot be updated in-place in mip, so remove and re-add constraint with new sense
        updated_constraint = constraint_dict_from_mip(constraint, self.x, self.y)
        updated_constraint.sense = sense
        self._remove_constraint(constraint)
        self._add_constraint(updated_constraint)

    def _update_constraint_rhs(self, constraint: mip.Constr, rhs: float):
        # note: constraint right hand side can be updated in-place in mip
        constraint.rhs = rhs

    def update_solution(self):
        return self._optimize()

    def update_objective_sense(self, sense: str):
        print(f'Updating objective sense to {sense} in model state.')
        self._update_sense(sense)
        self._optimize()
        # todo: return graph callback result to change objective vector direction
        # todo: return graph callback result to update solution

    def update_objective(self, x_coeff: float, y_coeff: float):
        self._update_objective_coeffs(x_coeff, y_coeff)
        self._optimize()
        # todo: return graph callback result to change objective vector direction
        # todo: return graph callback result to update solution

    def add_constraint(self, constraint: ConstraintDict):
        # todo: ensure user_actions sends one of '<', '>', or '=' as sense
        self._add_constraint(constraint)
        self._optimize()
        # todo: return graph callback result to change constraint
        # todo: return graph callback result to update solution

    def update_constraint_x_coeff(self, name: str, x_coeff: float):
        constraint = self._get_constraint(name)
        self._update_constraint_x_coeff(constraint, x_coeff)
        self._optimize()
        # todo: return graph callback result to change constraint
        # todo: return graph callback result to update solution

    def update_constraint_y_coeff(self, name: str, y_coeff: float):
        constraint = self._get_constraint(name)
        self._update_constraint_y_coeff(constraint, y_coeff)
        self._optimize()
        # todo: return graph callback result to change constraint
        # todo: return graph callback result to update solution

    def update_constraint_sense(self, name: str, sense: str):
        constraint = self._get_constraint(name)
        self._update_constraint_sense(constraint, sense)
        self._optimize()
        # todo: return graph callback result to change constraint
        # todo: return graph callback result to update solution

    def update_constraint_rhs(self, name: str, rhs: float):
        constraint = self._get_constraint(name)
        self._update_constraint_rhs(constraint, rhs)
        self._optimize()
        # todo: return graph callback result to change constraint
        # todo: return graph callback result to update solution

    def remove_constraint(self, name: str):
        constraint = self._get_constraint(name)
        self._remove_constraint(constraint)
        self._optimize()
        # todo: return graph callback result to change constraint
        # todo: return graph callback result to update solution

    # todo: implement constraint toggle logic
