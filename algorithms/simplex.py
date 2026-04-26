import enum
import numpy as np
from dataclasses import dataclass

from model.constraint import Constraint, ConstraintSense
from model.objective import Objective, ObjectiveSense
from algorithms.geometry import EPSILON  # numerical zero for pivot and optimality checks


# --- Data types ---

class OptimizerStatus(enum.Enum):
    OPTIMAL = 'optimal'
    UNBOUNDED = 'unbounded'
    INFEASIBLE = 'infeasible'
    FEASIBLE = 'feasible'
    NONE = 'none'

    def __str__(self) -> str:
        match self:
            case OptimizerStatus.OPTIMAL:
                return 'Linear program has a finite optimum'
            case OptimizerStatus.UNBOUNDED:
                return 'Linear program is unbounded'
            case OptimizerStatus.INFEASIBLE:
                return 'Linear program is infeasible'
            case OptimizerStatus.FEASIBLE:
                return 'Linear program is feasible'
            case OptimizerStatus.NONE:
                return 'Linear program has not been solved yet'
            case _:
                raise ValueError(f'Unrecognized optimization status {self}.')


@dataclass
class Solution:
    point: np.ndarray
    objective_value: float

    def __str__(self) -> str:
        return (f'optimal value {self.objective_value:.3f} '
                f'is attained at ({self.point[0]:.3f}, {self.point[1]:.3f})')


@dataclass
class Result:
    status: OptimizerStatus
    solution: Solution | None

    def __str__(self) -> str:
        if self.status == OptimizerStatus.OPTIMAL and self.solution is not None:
            return str(self.status) + ': ' + str(self.solution)
        return str(self.status)


_TABLEAU_FIXED_COLS = 5   # RHS + x+ + x− + y+ + y−


@dataclass
class SimplexTableau:
    _tableau: np.ndarray
    _num_constraints: int

    @staticmethod
    def _canonical_objective(objective: Objective) -> list[float]:
        """
        Returns the cost row [0, cx+, cx-, cy+, cy-] in canonical (min) form.

        For MIN c^T x: costs are  [ cx,  -cx,  cy, -cy]
        For MAX c^T x: costs are  [-cx,   cx, -cy,  cy]  (negate to minimise)

        Column 0 (RHS) always has cost 0.
        """
        coeff_x, coeff_y = objective.coeff_x, objective.coeff_y
        match objective.sense:
            case ObjectiveSense.MAX:
                return [0., -coeff_x, coeff_x, -coeff_y, coeff_y]
            case ObjectiveSense.MIN:
                return [0., coeff_x, -coeff_x, coeff_y, -coeff_y]

    @staticmethod
    def _canonical_constraint(constraint: Constraint) -> list[list[float]]:
        """
        Returns one or two canonical rows for the constraint in the form:
            [rhs, cx+, cx-, cy+, cy-]

        LE:  1 row  (kept as-is)
        GE:  1 row  (negated -> equivalent LE)
        EQ:  2 rows (LE row + GE row)
        """
        rhs, coeff_x, coeff_y = constraint.rhs, constraint.coeff_x, constraint.coeff_y
        match constraint.sense:
            case ConstraintSense.LE:
                return [[rhs, coeff_x, -coeff_x, coeff_y, -coeff_y]]
            case ConstraintSense.GE:
                return [[-rhs, -coeff_x, coeff_x, -coeff_y, coeff_y]]
            case ConstraintSense.EQ:
                return [[rhs, coeff_x, -coeff_x, coeff_y, -coeff_y],
                        [-rhs, -coeff_x, coeff_x, -coeff_y, coeff_y]]

    @classmethod
    def canonical_from(cls, objective: Objective, constraints: list[Constraint]) -> SimplexTableau:
        """
        Build the initial simplex tableau in canonical form:

            b | A | I
            ---------
            0 | c | 0

        where the columns are [RHS | cx+ | cx- | cy+ | cy- | slacks].
        """
        objective_row = np.array(SimplexTableau._canonical_objective(objective))

        if len(constraints) == 0:
            return cls(_tableau=np.array([objective_row]), _num_constraints=0)

        constraint_rows: list[list[float]] = []
        for constraint in constraints:
            constraint_rows.extend(cls._canonical_constraint(constraint))
        num_constraints = len(constraint_rows)

        return cls(
            _tableau=np.vstack([
                np.hstack([constraint_rows, np.eye(num_constraints)]),
                np.hstack([objective_row, np.zeros(num_constraints)]),
            ]),
            _num_constraints=num_constraints,
        )

    def get_initial_basis(self) -> list[int]:
        return list(range(_TABLEAU_FIXED_COLS, self.num_cols()))

    def is_rhs_all_non_negative(self) -> bool:
        return bool(np.all(self._tableau[:self._num_constraints, 0] >= -EPSILON))

    def get_index_smallest_cost(self) -> int:
        return int(self._tableau[-1, 1:].argmin()) + 1

    def get_objective(self) -> np.ndarray:
        return self._tableau[-1]

    def get_objective_value(self) -> float:
        return self._tableau[-1, 0]

    def get_rhs(self, row: int) -> float:
        return self._tableau[row, 0]

    def num_rows(self) -> int:
        return self._tableau.shape[0]

    def num_cols(self) -> int:
        return self._tableau.shape[1]

    def min_ratio(self, col: int) -> int | None:
        """
        Bland's rule / minimum-ratio test. Returns the leaving row index
        or None if no positive entry exists (unbounded direction).
        """
        ratios = [
            (self.get_rhs(row) / self._tableau[row, col], row)
            for row in range(self._num_constraints)
            if self._tableau[row, col] > EPSILON
        ]
        return min(ratios, default=(None, None))[1]

    def pivot_row_operation(self, curr_row: int, pivot_row: int, pivot_col: int):
        self._tableau[curr_row] -= self._tableau[curr_row, pivot_col] * self._tableau[pivot_row]

    def pivot(self, row: int, col: int) -> None:
        """Pivot tableau on element (row, col) in-place"""
        self._tableau[row] /= self._tableau[row, col]
        for i in range(self._tableau.shape[0]):
            if i != row:
                self.pivot_row_operation(curr_row=i, pivot_row=row, pivot_col=col)

    def phase_1_add_objective(self, row: np.ndarray):
        self._tableau = np.vstack([self._tableau, row])

    def phase_1_add_artificial_variable(self, row: int):
        self._tableau[row] *= -1

        artificial_column = np.zeros((self._tableau.shape[0], 1))
        artificial_column[row,  0] = 1.0
        artificial_column[-1, 0] = 1.0

        self._tableau = np.hstack([self._tableau, artificial_column])

    def phase_1_drop_objective(self) -> None:
        self._tableau = self._tableau[:-1]

    def phase_1_drop_row(self, row: int) -> None:
        self._tableau = np.delete(self._tableau, row, axis=0)
        self._num_constraints -= 1

    def phase_1_remove_artificial_variables(self):
        self._tableau = self._tableau[:, :_TABLEAU_FIXED_COLS]


@dataclass
class SimplexSolver:
    _status: OptimizerStatus
    _sense: ObjectiveSense
    _tableau: SimplexTableau
    _basis: list[int]
    _artificial_variables: list[int]

    def _iterate(self) -> OptimizerStatus:
        """
        Drive simplex pivots on current tableau (last row = objective).

        Mutates _tableau and _basis in-place.

        Returns:
            Status.OPTIMAL: if all reduced costs >= 0; current BFS is optimal.
            Satus.UNBOUNDED: if an entering column has no positive constraint entries;
                the objective is unbounded.
        """
        while True:
            enter_col = self._tableau.get_index_smallest_cost()
            if self._tableau.get_objective()[enter_col] >= -EPSILON:
                return OptimizerStatus.OPTIMAL

            leave_row = self._tableau.min_ratio(enter_col)
            if leave_row is None:
                return OptimizerStatus.UNBOUNDED

            self._tableau.pivot(leave_row, enter_col)
            self._basis[leave_row] = enter_col

    def _phase_1_setup(self) -> None:
        """
        Append a phase-1 objective row (minimise sum of artificials),
        then for every constraint row whose RHS is negative:
        negate the row and add a fresh artificial variable column.
        """
        num_cols = self._tableau.num_cols()

        self._tableau.phase_1_add_objective(np.zeros(num_cols))

        self._artificial_variables = []
        for row in range(self._tableau._num_constraints):  # todo: fix encapsulation violation (self._tableau._num_constraints)
            if self._tableau.get_rhs(row) < -EPSILON:
                self._tableau.phase_1_add_artificial_variable(row)
                self._tableau.pivot_row_operation(curr_row=-1, pivot_row=row, pivot_col=num_cols)
                self._artificial_variables.append(num_cols)
                self._basis[row] = num_cols
                num_cols += 1

    def _phase_1_teardown(self) -> None:
        """
        Drop the phase-1 objective row, pivot out any artificial that is still
        basic at zero (degenerate BFS), then remove all artificial columns and
        re-index the basis.
        """
        # todo: fix encapsulation violations (self._tableau._tableau)

        self._tableau.phase_1_drop_objective()

        art_set = set(self._artificial_variables)
        first_artificial = min(self._artificial_variables)

        for row in range(len(self._basis) - 1, -1, -1):
            bv = self._basis[row]
            if bv not in art_set:
                continue
            swapped = False
            for j in range(first_artificial): # only non-artificial cols
                if abs(self._tableau._tableau[row, j]) > EPSILON:
                    self._tableau.pivot(row, j)
                    self._basis[row] = j
                    swapped = True
                    break
            if not swapped:
                # Row is linearly dependent — drop it.
                self._tableau.phase_1_drop_row(row)
                self._basis.pop(row)

        # Remove artificial columns and re-index basis.
        total_cols = self._tableau.num_cols()
        keep = [j for j in range(total_cols) if j not in art_set]
        self._tableau._tableau = self._tableau._tableau[:, keep]
        col_map = {old: new for new, old in enumerate(keep)}
        self._basis = [col_map[bv] for bv in self._basis]

    def _phase_1(self) -> None:
        self._phase_1_setup()

        self._iterate()

        if abs(self._tableau.get_objective_value()) > EPSILON:
            self._status = OptimizerStatus.INFEASIBLE
            return

        self._phase_1_teardown()
        self._status = OptimizerStatus.FEASIBLE

    @classmethod
    def solve(cls, objective: Objective, constraints: list[Constraint]) -> SimplexSolver:
        tableau = SimplexTableau.canonical_from(objective=objective, constraints=constraints)
        solver = SimplexSolver(
            _status=OptimizerStatus.NONE,
            _sense=objective.sense,
            _tableau=tableau,
            _basis=tableau.get_initial_basis(),
            _artificial_variables=[],
        )

        if solver._tableau.is_rhs_all_non_negative():
            solver._status = OptimizerStatus.FEASIBLE
        else:
            solver._phase_1()

        if solver._status is OptimizerStatus.FEASIBLE:
            solver._status = solver._iterate()

        return solver

    def _get_solution(self) -> Solution | None:
        if self._status != OptimizerStatus.OPTIMAL:
            return None

        basic_values: dict[int, float] = {
            basic_variable: self._tableau.get_rhs(row)
            for row, basic_variable in enumerate(self._basis)
        }
        x = basic_values.get(1, 0.0) - basic_values.get(2, 0.0)
        y = basic_values.get(3, 0.0) - basic_values.get(4, 0.0)
        point = np.array([x, y])

        objective_value = self._tableau.get_objective_value()
        if self._sense is ObjectiveSense.MIN:
            objective_value = -objective_value

        return Solution(point=point, objective_value=objective_value)

    def get_result(self) -> Result:
        return Result(status=self._status, solution=self._get_solution())
