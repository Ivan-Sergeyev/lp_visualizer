import dataclasses
import mip

from model.domain_transfer_objects import Constraint, Objective, OptimizationResult


@dataclasses.dataclass(init=False)
class LinearProgram:
    model: mip.Model
    x: mip.Var
    y: mip.Var

    def load(self, objective: Objective, constraints: list[Constraint]) -> None:
        self.model = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)
        self.x = self.model.add_var(name='x', lb=-mip.INF, ub=mip.INF, var_type=mip.CONTINUOUS)
        self.y = self.model.add_var(name='y', lb=-mip.INF, ub=mip.INF, var_type=mip.CONTINUOUS)
        self.set_objective_sense(objective.sense)
        self.set_objective_coeffs(objective.x_coeff, objective.y_coeff)
        for constraint in constraints:
            self.add_constraint(constraint)

    def __str__(self) -> str:
        return '\n'.join(
            [f'{self.model.sense} {self.model.objective}'] +
            [f'{constraint}' for constraint in self.model.constrs]
        )

    def _get_mip_constraint_by_name(self, name: str) -> mip.Constr:
        constraint = self.model.constr_by_name(name)

        if constraint is None:
            raise ValueError(f'Constraint {name} not found.')

        return constraint

    def _remove_mip_constraint(self, constraint: mip.Constr) -> None:
        self.model.remove(constraint)

    def _set_mip_constraint_x_coeff(self, constraint: mip.Constr, x_coeff: float) -> None:
        updated_constraint = Constraint.from_mip(constraint, self.x, self.y)
        updated_constraint.x_coeff = x_coeff
        self._remove_mip_constraint(constraint)
        self.add_constraint(updated_constraint)

    def _set_mip_constraint_y_coeff(self, constraint: mip.Constr, y_coeff: float) -> None:
        updated_constraint = Constraint.from_mip(constraint, self.x, self.y)
        updated_constraint.y_coeff = y_coeff
        self._remove_mip_constraint(constraint)
        self.add_constraint(updated_constraint)

    def _set_mip_constraint_sense(self, constraint: mip.Constr, sense: str) -> None:
        updated_constraint = Constraint.from_mip(constraint, self.x, self.y)
        updated_constraint.sense = sense
        self._remove_mip_constraint(constraint)
        self.add_constraint(updated_constraint)

    def _set_mip_constraint_rhs(self, constraint: mip.Constr, rhs: float) -> None:
        constraint.rhs = rhs

    def set_objective_sense(self, sense: str) -> None:
        self.model.sense = Objective.sense_to_mip(sense)

    def set_objective_coeffs(self, x_coeff: float, y_coeff: float) -> None:
        self.model.objective = mip.LinExpr(variables=[self.x, self.y], coeffs=[x_coeff, y_coeff])

    def add_constraint(self, constraint: Constraint) -> None:
        self.model.add_constr(constraint.to_lin_expr(self.x, self.y), name=constraint.name)

    def set_constraint_x_coeff(self, name: str, x_coeff: float) -> None:
        self._set_mip_constraint_x_coeff(self._get_mip_constraint_by_name(name), x_coeff)

    def set_constraint_y_coeff(self, name: str, y_coeff: float) -> None:
        self._set_mip_constraint_y_coeff(self._get_mip_constraint_by_name(name), y_coeff)

    def set_constraint_sense(self, name: str, sense: str) -> None:
        self._set_mip_constraint_sense(self._get_mip_constraint_by_name(name), sense)

    def set_constraint_rhs(self, name: str, rhs: float) -> None:
        self._set_mip_constraint_rhs(self._get_mip_constraint_by_name(name), rhs)

    def remove_constraint(self, name: str) -> None:
        self._remove_mip_constraint(self._get_mip_constraint_by_name(name))

    def optimize(self) -> None:
        self.model.optimize()

    def objective(self) -> Objective:
        return Objective.from_mip(objective=self.model.objective, sense=self.model.sense, x=self.x, y=self.y)

    def constraint(self, name: str) -> Constraint:
        return Constraint.from_mip(constraint=self._get_mip_constraint_by_name(name), x=self.x, y=self.y)

    def constraints(self) -> list[Constraint]:
        return [Constraint.from_mip(constraint=constraint, x=self.x, y=self.y) for constraint in self.model.constrs]

    def optimization_result(self, optimize: bool = True) -> OptimizationResult:
        if optimize:
            self.optimize()
        return OptimizationResult.from_mip(self.model.status, self.model.objective_value, self.x, self.y)


initial_objective = Objective(sense='max', x_coeff=6., y_coeff=9.)

initial_constraints = [
    Constraint(name='0', x_coeff=2., y_coeff=3., sense='<=', rhs=12.),
    Constraint(name='1', x_coeff=1., y_coeff=1., sense='<=', rhs=5.),
    Constraint(name='2', x_coeff=1., y_coeff=0., sense='>=', rhs=0.),
    Constraint(name='3', x_coeff=0., y_coeff=1., sense='>=', rhs=0.),
]

linear_program = LinearProgram()
linear_program.load(initial_objective, initial_constraints)
linear_program.optimize()
