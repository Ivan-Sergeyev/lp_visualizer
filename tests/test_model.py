"""Tests for model/constraint.py and model/objective.py"""

import pytest

from model.constraint import Constraint, ConstraintDict, ConstraintSense
from model.objective import Objective, ObjectiveDict, ObjectiveSense

# ---------------------------------------------------------------------------
# ConstraintSense
# ---------------------------------------------------------------------------

class TestConstraintSenseFromStr:
    @pytest.mark.parametrize("raw", ["≤", "<", "<="])
    def test_le_variants(self, raw):
        assert ConstraintSense.from_str(raw) == ConstraintSense.LE

    @pytest.mark.parametrize("raw", ["≥", ">", ">="])
    def test_ge_variants(self, raw):
        assert ConstraintSense.from_str(raw) == ConstraintSense.GE

    @pytest.mark.parametrize("raw", ["=", "=="])
    def test_eq_variants(self, raw):
        assert ConstraintSense.from_str(raw) == ConstraintSense.EQ

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unrecognized"):
            ConstraintSense.from_str("!=")

    def test_str_le(self):
        assert str(ConstraintSense.LE) == "≤"

    def test_str_ge(self):
        assert str(ConstraintSense.GE) == "≥"

    def test_str_eq(self):
        assert str(ConstraintSense.EQ) == "="


# ---------------------------------------------------------------------------
# Constraint
# ---------------------------------------------------------------------------

class TestConstraintConstruction:
    def test_defaults(self):
        c = Constraint()
        assert c.coeff_x == 0.0
        assert c.coeff_y == 0.0
        assert c.sense == ConstraintSense.LE
        assert c.rhs == 0.0

    def test_custom(self):
        c = Constraint(coeff_x=2, coeff_y=-1, sense=ConstraintSense.GE, rhs=5)
        assert c.coeff_x == 2
        assert c.coeff_y == -1
        assert c.sense == ConstraintSense.GE
        assert c.rhs == 5


class TestConstraintFromDict:
    def test_le(self):
        d: ConstraintDict = {"coeff_x": 1.0, "coeff_y": 2.0, "sense": "≤", "rhs": 4.0}
        c = Constraint.from_dict(d)
        assert c.coeff_x == 1.0
        assert c.coeff_y == 2.0
        assert c.sense == ConstraintSense.LE
        assert c.rhs == 4.0

    def test_ge(self):
        d: ConstraintDict = {"coeff_x": -1.0, "coeff_y": 0.0, "sense": "≥", "rhs": -3.0}
        c = Constraint.from_dict(d)
        assert c.sense == ConstraintSense.GE

    def test_eq(self):
        d: ConstraintDict = {"coeff_x": 1.0, "coeff_y": 1.0, "sense": "=", "rhs": 1.0}
        c = Constraint.from_dict(d)
        assert c.sense == ConstraintSense.EQ


class TestConstraintToDict:
    def test_roundtrip(self):
        c = Constraint(coeff_x=3.0, coeff_y=-2.0, sense=ConstraintSense.GE, rhs=7.0)
        d = c.to_dict()
        c2 = Constraint.from_dict(d)
        assert c == c2

    def test_dict_keys(self):
        c = Constraint(coeff_x=1.0, coeff_y=1.0, sense=ConstraintSense.LE, rhs=10.0)
        d = c.to_dict()
        assert set(d.keys()) == {"coeff_x", "coeff_y", "sense", "rhs"}


class TestConstraintStr:
    def test_str_format(self):
        c = Constraint(coeff_x=1.0, coeff_y=2.0, sense=ConstraintSense.LE, rhs=3.0)
        s = str(c)
        assert "1.0" in s
        assert "2.0" in s
        assert "3.0" in s
        assert "≤" in s


# ---------------------------------------------------------------------------
# ObjectiveSense
# ---------------------------------------------------------------------------

class TestObjectiveSenseFromStr:
    def test_max(self):
        assert ObjectiveSense.from_str("max") == ObjectiveSense.MAX

    def test_min(self):
        assert ObjectiveSense.from_str("min") == ObjectiveSense.MIN

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unrecognized"):
            ObjectiveSense.from_str("maximize")

    def test_str_max(self):
        assert str(ObjectiveSense.MAX) == "max"

    def test_str_min(self):
        assert str(ObjectiveSense.MIN) == "min"


# ---------------------------------------------------------------------------
# Objective
# ---------------------------------------------------------------------------

class TestObjectiveFromDict:
    def test_max_objective(self):
        d: ObjectiveDict = {"sense": "max", "coeff_x": 3.0, "coeff_y": 5.0}
        obj = Objective.from_dict(d)
        assert obj.sense == ObjectiveSense.MAX
        assert obj.coeff_x == 3.0
        assert obj.coeff_y == 5.0

    def test_min_objective(self):
        d: ObjectiveDict = {"sense": "min", "coeff_x": -1.0, "coeff_y": 2.0}
        obj = Objective.from_dict(d)
        assert obj.sense == ObjectiveSense.MIN


class TestObjectiveToDict:
    def test_roundtrip(self):
        obj = Objective(sense=ObjectiveSense.MIN, coeff_x=4.0, coeff_y=-2.0)
        d = obj.to_dict()
        obj2 = Objective.from_dict(d)
        assert obj == obj2

    def test_dict_keys(self):
        obj = Objective(sense=ObjectiveSense.MAX, coeff_x=1.0, coeff_y=1.0)
        d = obj.to_dict()
        assert set(d.keys()) == {"sense", "coeff_x", "coeff_y"}
