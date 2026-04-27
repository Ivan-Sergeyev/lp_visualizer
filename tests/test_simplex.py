"""Tests for algorithms/simplex.py — SimplexTableau, SimplexSolver, and Result types."""

import math

import numpy as np

from algorithms.simplex import (
    OptimizerStatus,
    Result,
    SimplexSolver,
    SimplexTableau,
    Solution,
)
from model.constraint import Constraint, ConstraintSense
from model.objective import Objective, ObjectiveSense

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_le(cx, cy, rhs):
    return Constraint(coeff_x=cx, coeff_y=cy, sense=ConstraintSense.LE, rhs=rhs)

def make_ge(cx, cy, rhs):
    return Constraint(coeff_x=cx, coeff_y=cy, sense=ConstraintSense.GE, rhs=rhs)

def make_eq(cx, cy, rhs):
    return Constraint(coeff_x=cx, coeff_y=cy, sense=ConstraintSense.EQ, rhs=rhs)

def solve_max(cx, cy, constraints):
    obj = Objective(sense=ObjectiveSense.MAX, coeff_x=cx, coeff_y=cy)
    return SimplexSolver.solve(obj, constraints).get_result()

def solve_min(cx, cy, constraints):
    obj = Objective(sense=ObjectiveSense.MIN, coeff_x=cx, coeff_y=cy)
    return SimplexSolver.solve(obj, constraints).get_result()


# ---------------------------------------------------------------------------
# OptimizerStatus.__str__
# ---------------------------------------------------------------------------

class TestOptimizerStatusStr:
    def test_optimal(self):
        assert "optimum" in str(OptimizerStatus.OPTIMAL).lower()

    def test_unbounded(self):
        assert "unbounded" in str(OptimizerStatus.UNBOUNDED).lower()

    def test_infeasible(self):
        assert "infeasible" in str(OptimizerStatus.INFEASIBLE).lower()

    def test_feasible(self):
        assert "feasible" in str(OptimizerStatus.FEASIBLE).lower()

    def test_none(self):
        assert "not been solved" in str(OptimizerStatus.NONE).lower()


# ---------------------------------------------------------------------------
# Solution / Result helpers
# ---------------------------------------------------------------------------

class TestSolutionStr:
    def test_contains_value_and_point(self):
        sol = Solution(point=np.array([1.5, 2.5]), objective_value=10.0)
        s = str(sol)
        assert "10.000" in s
        assert "1.500" in s
        assert "2.500" in s


class TestResultStr:
    def test_optimal_with_solution(self):
        sol = Solution(point=np.array([1.0, 2.0]), objective_value=5.0)
        r = Result(status=OptimizerStatus.OPTIMAL, solution=sol)
        assert "optimal" in str(r).lower()
        assert "5.000" in str(r)

    def test_infeasible_no_solution(self):
        r = Result(status=OptimizerStatus.INFEASIBLE, solution=None)
        assert "infeasible" in str(r).lower()


# ---------------------------------------------------------------------------
# SimplexTableau internals
# ---------------------------------------------------------------------------

class TestSimplexTableau:
    """Smoke-tests for tableau construction."""

    def _simple_tableau(self):
        obj = Objective(sense=ObjectiveSense.MAX, coeff_x=1.0, coeff_y=1.0)
        constraints = [make_le(1, 0, 4), make_le(0, 1, 4)]
        return SimplexTableau.canonical_from(obj, constraints)

    def test_shape(self):
        t = self._simple_tableau()
        # 2 LE constraints -> 2 constraint rows + 1 objective row = 3 rows
        # fixed cols 5 + 2 slacks = 7 cols
        assert t.num_rows() == 3
        assert t.num_cols() == 7

    def test_initial_basis_length(self):
        t = self._simple_tableau()
        basis = t.get_initial_basis()
        assert len(basis) == 2

    def test_rhs_non_negative_for_standard_form(self):
        t = self._simple_tableau()
        assert t.is_rhs_all_non_negative()

    def test_eq_constraint_doubles_rows(self):
        obj = Objective(sense=ObjectiveSense.MIN, coeff_x=1.0, coeff_y=0.0)
        constraints = [make_eq(1, 1, 5)]
        t = SimplexTableau.canonical_from(obj, constraints)
        # 1 EQ => 2 rows + 1 objective = 3 rows
        assert t.num_rows() == 3


# ---------------------------------------------------------------------------
# End-to-end LP solve tests
# ---------------------------------------------------------------------------

class TestSimplexOptimal:
    """Classic bounded feasible LPs that should return OPTIMAL."""

    def test_simple_max_box(self):
        """max x + y  s.t.  x ≤ 3, y ≤ 4  => optimal at (3,4) = 7"""
        result = solve_max(1, 1, [make_le(1, 0, 3), make_le(0, 1, 4)])
        assert result.status == OptimizerStatus.OPTIMAL
        assert result.solution is not None
        assert math.isclose(result.solution.objective_value, 7.0, abs_tol=1e-6)
        assert math.isclose(result.solution.point[0], 3.0, abs_tol=1e-6)
        assert math.isclose(result.solution.point[1], 4.0, abs_tol=1e-6)

    def test_max_with_diagonal_constraint(self):
        """max x + y  s.t.  x + y ≤ 5, x ≤ 4, y ≤ 4  => obj = 5"""
        constraints = [make_le(1, 1, 5), make_le(1, 0, 4), make_le(0, 1, 4)]
        result = solve_max(1, 1, constraints)
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, 5.0, abs_tol=1e-6)

    def test_min_trivial(self):
        """min x + y  s.t.  x ≥ 0, y ≥ 0, x + y ≥ 1  => min = 1"""
        constraints = [make_ge(1, 0, 0), make_ge(0, 1, 0), make_ge(1, 1, 1)]
        result = solve_min(1, 1, constraints)
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, 1.0, abs_tol=1e-6)

    def test_max_with_equality_constraint(self):
        """max x  s.t.  x + y = 3, y ≥ 0, x ≥ 0  => x = 3"""
        constraints = [make_eq(1, 1, 3), make_ge(1, 0, 0), make_ge(0, 1, 0)]
        result = solve_max(1, 0, constraints)
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, 3.0, abs_tol=1e-6)

    def test_zero_objective_coefficients(self):
        """max 0*x + 0*y  s.t.  x ≤ 5 => obj = 0"""
        result = solve_max(0, 0, [make_le(1, 0, 5)])
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, 0.0, abs_tol=1e-6)

    def test_negative_coefficients_max(self):
        """max -x - y  s.t.  x ≥ 1, y ≥ 1  => opt at (1,1), value = -2"""
        constraints = [make_ge(1, 0, 1), make_ge(0, 1, 1)]
        result = solve_max(-1, -1, constraints)
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, -2.0, abs_tol=1e-6)

    def test_fractional_optimum(self):
        """max x + y  s.t.  2x + y ≤ 3, x + 2y ≤ 3  => opt at (1,1) = 2"""
        constraints = [make_le(2, 1, 3), make_le(1, 2, 3)]
        result = solve_max(1, 1, constraints)
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, 2.0, abs_tol=1e-6)

    def test_min_with_equality(self):
        """min x + y  s.t.  x = 2, y = 3  => min = 5"""
        constraints = [make_eq(1, 0, 2), make_eq(0, 1, 3)]
        result = solve_min(1, 1, constraints)
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, 5.0, abs_tol=1e-6)

    def test_degenerate_opt_still_optimal(self):
        """Redundant constraints should not prevent finding the optimum."""
        constraints = [
            make_le(1, 0, 5),
            make_le(1, 0, 5),  # duplicate
            make_le(0, 1, 5),
        ]
        result = solve_max(1, 1, constraints)
        assert result.status == OptimizerStatus.OPTIMAL
        assert math.isclose(result.solution.objective_value, 10.0, abs_tol=1e-6)


class TestSimplexUnbounded:
    """LPs that should be detected as unbounded."""

    def test_max_no_upper_bound(self):
        """max x  s.t.  x ≥ 0  => unbounded"""
        result = solve_max(1, 0, [make_ge(1, 0, 0)])
        assert result.status == OptimizerStatus.UNBOUNDED
        assert result.solution is None

    def test_max_one_sided_constraint(self):
        """max x + y  s.t.  x - y ≤ 0  => unbounded (move along x=y direction)"""
        result = solve_max(1, 1, [make_le(1, -1, 0)])
        assert result.status == OptimizerStatus.UNBOUNDED

    def test_no_constraints_unbounded(self):
        """max x + y with no constraints should be unbounded, but currently crashes."""
        result = solve_max(1, 1, [])
        assert result.status == OptimizerStatus.UNBOUNDED


class TestSimplexInfeasible:
    """LPs that should be detected as infeasible."""

    def test_contradictory_le_ge(self):
        """x ≤ 1  and  x ≥ 2  => infeasible"""
        constraints = [make_le(1, 0, 1), make_ge(1, 0, 2)]
        result = solve_max(1, 0, constraints)
        assert result.status == OptimizerStatus.INFEASIBLE
        assert result.solution is None

    def test_empty_feasible_region(self):
        """x + y ≤ 0  and  x + y ≥ 1  => infeasible"""
        constraints = [make_le(1, 1, 0), make_ge(1, 1, 1)]
        result = solve_max(1, 1, constraints)
        assert result.status == OptimizerStatus.INFEASIBLE

    def test_equality_contradicts_inequality(self):
        """x + y = 5  and  x + y ≤ 3  => infeasible"""
        constraints = [make_eq(1, 1, 5), make_le(1, 1, 3)]
        result = solve_max(1, 0, constraints)
        assert result.status == OptimizerStatus.INFEASIBLE


# ---------------------------------------------------------------------------
# Objective value sign / sense symmetry
# ---------------------------------------------------------------------------

class TestMaxMinSymmetry:
    """max f  and  min -f should produce identical objective values."""

    def test_box_symmetry(self):
        constraints = [make_le(1, 0, 3), make_le(0, 1, 4)]
        r_max = solve_max(1, 1, constraints)
        r_min = solve_min(-1, -1, constraints)
        assert r_max.status == OptimizerStatus.OPTIMAL
        assert r_min.status == OptimizerStatus.OPTIMAL
        assert math.isclose(
            r_max.solution.objective_value,
            -r_min.solution.objective_value,
            abs_tol=1e-6,
        )
