import enum
import mip

from dataclasses import dataclass


class ConstraintSense(enum.Enum):
    LEQ = '≤'
    GEQ = '≥'
    EQ  = '='

    @staticmethod
    def from_str(sense: str) -> ConstraintSense:
        match sense:
            case '<' | '<=' | '≤':
                return ConstraintSense.LEQ
            case '>' | '>=' | '≥':
                return ConstraintSense.GEQ
            case '=' | '==':
                return ConstraintSense.EQ
            case _:
                raise ValueError(f'Unrecognized constraint sense {sense}.')

    def to_mip(self) -> str:
        match self:
            case ConstraintSense.LEQ:
                return mip.LESS_OR_EQUAL
            case ConstraintSense.GEQ:
                return mip.GREATER_OR_EQUAL
            case ConstraintSense.EQ:
                return mip.EQUAL
            case _:
                raise ValueError(f'Unrecognized constraint sense {self.name}.')

    def __str__(self) -> str:
        return self.value


@dataclass
class Constraint:
    name: str
    x_coeff: float = 0.
    y_coeff: float = 0.
    sense: ConstraintSense = ConstraintSense.LEQ
    rhs: float = 0.

    @classmethod
    def from_mip(cls, constraint: mip.Constr, x: mip.Var, y: mip.Var) -> Constraint:
        return cls(
            name=constraint.name,
            x_coeff=constraint.expr.expr.get(x, 0.),
            y_coeff=constraint.expr.expr.get(y, 0.),
            sense=ConstraintSense.from_str(constraint.expr.sense),
            rhs=constraint.rhs,
        )

    def lin_expr(self, x: mip.Var, y: mip.Var) -> mip.LinExpr:
        return mip.LinExpr(
            variables=[x, y],
            coeffs=[self.x_coeff, self.y_coeff],
            sense=ConstraintSense.to_mip(self.sense),
            const=-self.rhs,
        )


class ObjectiveSense(enum.Enum):
    MAX = 'max'
    MIN = 'min'

    @staticmethod
    def from_str(sense: str) -> ObjectiveSense:
        match sense:
            case 'max' | mip.MAXIMIZE:
                return ObjectiveSense.MAX
            case 'min' | mip.MINIMIZE:
                return ObjectiveSense.MIN
            case _:
                raise ValueError(f'Unrecognized objective sense {sense}.')

    def to_mip(self) -> str:
        match self:
            case ObjectiveSense.MAX:
                return mip.MAXIMIZE
            case ObjectiveSense.MIN:
                return mip.MINIMIZE
            case _:
                raise ValueError(f'Unrecognized objective sense {sense}.')

    def __str__(self) -> str:
        return self.value


@dataclass
class Objective:
    sense: ObjectiveSense
    x_coeff: float
    y_coeff: float

    @classmethod
    def from_mip(cls, objective: mip.LinExpr, sense: str, x: mip.Var, y: mip.Var) -> Objective:
        return cls(
            sense=ObjectiveSense.from_str(sense),
            x_coeff=objective.expr.get(x, 0.),
            y_coeff=objective.expr.get(y, 0.),
        )


class OptimizationStatus(enum.Enum):
    OPTIMAL = 'optimal'
    UNBOUNDED = 'unbounded'
    INFEASIBLE = 'infeasible'

    @staticmethod
    def from_str(status: str) -> OptimizationStatus:
        match status:
            case 'optimal':
                return OptimizationStatus.OPTIMAL
            case 'unbounded':
                return OptimizationStatus.UNBOUNDED
            case 'infeasible':
                return OptimizationStatus.INFEASIBLE
            case _:
                raise ValueError(f'Unrecognized optimization status {status}.')

    @staticmethod
    def from_mip(status: mip.OptimizationStatus) -> OptimizationStatus:
        match status:
            case mip.OptimizationStatus.OPTIMAL:
                return OptimizationStatus.OPTIMAL
            case mip.OptimizationStatus.UNBOUNDED:
                return OptimizationStatus.UNBOUNDED
            case mip.OptimizationStatus.INFEASIBLE:
                return OptimizationStatus.INFEASIBLE
            case _:
                raise ValueError(f'Unrecognized optimization status {status}.')


@dataclass
class OptimizationResult:
    status: OptimizationStatus
    solution_value: float | None
    solution_x: float | None
    solution_y: float | None

    @classmethod
    def from_mip(cls, status: mip.OptimizationStatus, objective_value: float | None, x: mip.Var, y: mip.Var) -> OptimizationResult:
        if status != mip.OptimizationStatus.OPTIMAL:
            return cls(status=OptimizationStatus.from_mip(status), solution_value=None, solution_x=None, solution_y=None)

        return cls(status=OptimizationStatus.from_mip(status), solution_value=objective_value, solution_x=x.x, solution_y=y.x)

    def __str__(self) -> str:
        match self.status:
            case OptimizationStatus.OPTIMAL:
                return f'Linear program attains optimal value {self.solution_value:.3f} at ({self.solution_x:.3f}, {self.solution_y:.3f})'
            case OptimizationStatus.UNBOUNDED:
                return 'Linear program is unbounded'
            case OptimizationStatus.INFEASIBLE:
                return 'Linear program is infeasible'
            case _:
                raise ValueError(f'Unrecognized optimization status {self.status}.')
