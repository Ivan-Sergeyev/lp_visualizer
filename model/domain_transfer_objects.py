import mip

from dataclasses import dataclass


@dataclass
class Objective:
    sense: str
    x_coeff: float
    y_coeff: float

    @staticmethod
    def sense_to_mip(sense: str) -> str:
        match sense:
            case 'max' | mip.MAXIMIZE:
                return mip.MAXIMIZE
            case 'min' | mip.MINIMIZE:
                return mip.MINIMIZE
            case _:
                raise ValueError(f'Unrecognized objective sense {sense}.')

    @staticmethod
    def sense_to_ui(sense: str) -> str:
        match sense:
            case 'max' | mip.MAXIMIZE:
                return 'max'
            case 'min' | mip.MINIMIZE:
                return 'min'
            case _:
                raise ValueError(f'Unrecognized objective sense {sense}.')

    @classmethod
    def from_mip(cls, objective: mip.LinExpr, sense: str, x: mip.Var, y: mip.Var) -> Objective:
        return cls(
            sense=Objective.sense_to_ui(sense),
            x_coeff=objective.expr.get(x, 0.),
            y_coeff=objective.expr.get(y, 0.),
        )


@dataclass
class Constraint:
    name: str
    x_coeff: float
    y_coeff: float
    sense: str
    rhs: float

    @staticmethod
    def sense_to_mip(sense: str) -> str:
        match sense:
            case '<' | '<=' | '≤' | mip.LESS_OR_EQUAL:
                return mip.LESS_OR_EQUAL
            case '>' | '>=' | '≥' | mip.GREATER_OR_EQUAL:
                return mip.GREATER_OR_EQUAL
            case '=' | '==' | mip.EQUAL:
                return mip.EQUAL
            case _:
                raise ValueError(f'Unrecognized constraint sense {sense}.')

    @staticmethod
    def sense_to_ui(sense: str) -> str:
        match sense:
            case '<' | '<=' | '≤' | mip.LESS_OR_EQUAL:
                return '≤'
            case '>' | '>=' | '≥' | mip.GREATER_OR_EQUAL:
                return '≥'
            case '=' | '==' | mip.EQUAL:
                return '='
            case _:
                raise ValueError(f'Unrecognized constraint sense {sense}.')

    @classmethod
    def from_mip(cls, constraint: mip.Constr, x: mip.Var, y: mip.Var) -> Constraint:
        return cls(
            name=constraint.name,
            x_coeff=constraint.expr.expr.get(x, 0.),
            y_coeff=constraint.expr.expr.get(y, 0.),
            sense=Constraint.sense_to_ui(constraint.expr.sense),
            rhs=constraint.rhs,
        )

    def __init__(self, name: str, x_coeff: float = 0., y_coeff: float = 0., sense: str = '<=', rhs: float = 0.):
        self.name = name
        self.x_coeff = x_coeff
        self.y_coeff = y_coeff
        self.sense = Constraint.sense_to_ui(sense)
        self.rhs = rhs

    def to_lin_expr(self, x: mip.Var, y: mip.Var) -> mip.LinExpr:
        return mip.LinExpr(
            variables=[x, y],
            coeffs=[self.x_coeff, self.y_coeff],
            sense=Constraint.sense_to_mip(self.sense),
            const=-self.rhs,
        )


@dataclass
class OptimizationResult:
    status: str
    solution_value: float | None
    solution_x: float | None
    solution_y: float | None

    @staticmethod
    def status_to_mip(status: str) -> mip.OptimizationStatus:
        match status:
            case 'optimal':
                return mip.OptimizationStatus.OPTIMAL
            case 'unbounded':
                return mip.OptimizationStatus.UNBOUNDED
            case 'infeasible':
                return mip.OptimizationStatus.INFEASIBLE
            case _:
                raise ValueError(f'Unrecognized optimization status {status}.')

    @staticmethod
    def status_to_ui(status: mip.OptimizationStatus) -> str:
        match status:
            case mip.OptimizationStatus.OPTIMAL:
                return 'optimal'
            case mip.OptimizationStatus.UNBOUNDED:
                return 'unbounded'
            case mip.OptimizationStatus.INFEASIBLE:
                return 'infeasible'
            case _:
                raise ValueError(f'Unrecognized optimization status {status}.')

    @classmethod
    def from_mip(cls, status: mip.OptimizationStatus, objective_value: float | None, x: mip.Var, y: mip.Var) -> OptimizationResult:
        if status != mip.OptimizationStatus.OPTIMAL:
            return cls(status=OptimizationResult.status_to_ui(status), solution_value=None, solution_x=None, solution_y=None)

        return cls(status=OptimizationResult.status_to_ui(status), solution_value=objective_value, solution_x=x.x, solution_y=y.x)

    def __str__(self) -> str:
        match self.status:
            case 'optimal':
                return f'Linear program attains optimal value {self.solution_value:.3f} at ({self.solution_x:.3f}, {self.solution_y:.3f})'
            case 'unbounded':
                return 'Linear program is unbounded'
            case 'infeasible':
                return 'Linear program is infeasible'
            case _:
                raise ValueError(f'Unrecognized optimization status {self.status}.')
