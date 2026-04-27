"""Tests for algorithms/geometry.py"""

import math

from algorithms.geometry import (
    EPSILON,
    Line2D,
    Point2D,
    Vector2D,
    box_corners,
    float_eq,
    float_lt,
)

# ---------------------------------------------------------------------------
# float_eq / float_lt
# ---------------------------------------------------------------------------

class TestFloatEq:
    def test_exact_equal(self):
        assert float_eq(1.0, 1.0)

    def test_within_epsilon(self):
        assert float_eq(1.0, 1.0 + EPSILON / 2)

    def test_just_outside_epsilon(self):
        assert not float_eq(0.0, EPSILON * 2)

    def test_negative_values(self):
        assert float_eq(-3.5, -3.5)

    def test_zero_self(self):
        assert float_eq(0.0, 0.0)


class TestFloatLt:
    def test_strictly_less(self):
        assert float_lt(1.0, 2.0)

    def test_equal_values_returns_true(self):
        # float_lt is a <= with tolerance: a - eps < b
        assert float_lt(1.0, 1.0)

    def test_greater_returns_false(self):
        assert not float_lt(2.0, 1.0)


# ---------------------------------------------------------------------------
# Vector2D
# ---------------------------------------------------------------------------

class TestVector2D:
    def test_default_construction(self):
        v = Vector2D()
        assert v.x == 0.0 and v.y == 0.0

    def test_construction(self):
        v = Vector2D(3.0, 4.0)
        assert v.x == 3.0 and v.y == 4.0

    def test_add(self):
        assert Vector2D(1, 2) + Vector2D(3, 4) == Vector2D(4, 6)

    def test_sub(self):
        assert Vector2D(5, 7) - Vector2D(2, 3) == Vector2D(3, 4)

    def test_neg(self):
        assert -Vector2D(1, -2) == Vector2D(-1, 2)

    def test_eq_uses_epsilon(self):
        v1 = Vector2D(1.0, 2.0)
        v2 = Vector2D(1.0 + EPSILON / 2, 2.0)
        assert v1 == v2

    def test_neq(self):
        assert Vector2D(1, 2) != Vector2D(1, 3)

    def test_length_345(self):
        assert math.isclose(Vector2D(3, 4).length(), 5.0)

    def test_length_zero(self):
        assert Vector2D(0, 0).length() == 0.0

    def test_unit_normal(self):
        u = Vector2D(3, 4).unit()
        assert math.isclose(u.length(), 1.0)
        assert math.isclose(u.x, 0.6)
        assert math.isclose(u.y, 0.8)

    def test_unit_zero_vector(self):
        u = Vector2D(0, 0).unit()
        assert u == Vector2D(0, 0)

    def test_lt_both_components(self):
        assert Vector2D(1, 1) < Vector2D(2, 2)

    def test_lt_one_component_fails(self):
        assert not (Vector2D(3, 1) < Vector2D(2, 2))


# ---------------------------------------------------------------------------
# Point2D
# ---------------------------------------------------------------------------

class TestPoint2D:
    def test_is_in_box_inside(self):
        p = Point2D(1, 1)
        assert p.is_in_box(Point2D(0, 0), Point2D(2, 2))

    def test_is_in_box_on_boundary_included_due_to_epsilon(self):
        # float_lt uses (a - EPSILON < b), so a point exactly on the boundary
        # of the box is treated as "inside" due to the epsilon tolerance.
        p = Point2D(0, 0)
        assert p.is_in_box(Point2D(0, 0), Point2D(2, 2))

    def test_is_in_box_clearly_outside_boundary(self):
        # A point strictly outside (far from boundary) is correctly excluded.
        p = Point2D(-1, -1)
        assert not p.is_in_box(Point2D(0, 0), Point2D(2, 2))

    def test_is_in_box_outside(self):
        p = Point2D(5, 5)
        assert not p.is_in_box(Point2D(0, 0), Point2D(2, 2))

    def test_inherits_vector_ops(self):
        p = Point2D(1, 2) + Vector2D(3, 4)
        assert p.x == 4 and p.y == 6


# ---------------------------------------------------------------------------
# Line2D
# ---------------------------------------------------------------------------

class TestLine2DPointWith:
    """Test the two helpers that compute a point on a line from one coordinate."""

    def test_point_with_x_horizontal(self):
        # Line: 0*x + 1*y = 3  =>  y = 3 for any x
        line = Line2D(x=0, y=1, rhs=3)
        p = line.point_with_x(5)
        assert math.isclose(p.x, 5) and math.isclose(p.y, 3)

    def test_point_with_y_vertical(self):
        # Line: 1*x + 0*y = 2  =>  x = 2 for any y
        line = Line2D(x=1, y=0, rhs=2)
        p = line.point_with_y(7)
        assert math.isclose(p.x, 2) and math.isclose(p.y, 7)

    def test_point_with_x_diagonal(self):
        # Line: x + y = 4  =>  at x=1, y=3
        line = Line2D(x=1, y=1, rhs=4)
        p = line.point_with_x(1)
        assert math.isclose(p.x, 1) and math.isclose(p.y, 3)


class TestLine2DIntersectLine:
    def test_parallel_lines_return_none(self):
        l1 = Line2D(x=1, y=1, rhs=2)
        l2 = Line2D(x=1, y=1, rhs=5)
        assert l1.intersect_line(l2) is None

    def test_perpendicular_lines(self):
        # x = 3  and  y = 4
        l1 = Line2D(x=1, y=0, rhs=3)
        l2 = Line2D(x=0, y=1, rhs=4)
        p = l1.intersect_line(l2)
        assert p is not None
        assert math.isclose(p.x, 3) and math.isclose(p.y, 4)

    def test_diagonal_intersection(self):
        # x + y = 2  and  x - y = 0  =>  (1, 1)
        l1 = Line2D(x=1, y=1, rhs=2)
        l2 = Line2D(x=1, y=-1, rhs=0)
        p = l1.intersect_line(l2)
        assert p is not None
        assert math.isclose(p.x, 1) and math.isclose(p.y, 1)

    def test_coincident_lines_return_none(self):
        line = Line2D(x=2, y=3, rhs=6)
        assert line.intersect_line(line) is None


class TestLine2DBoxIntersect:
    """Test intersect_box and boxed_endpoints."""

    def setup_method(self):
        self.bl = Point2D(0, 0)
        self.tr = Point2D(10, 10)

    def test_diagonal_line_two_intersections(self):
        # x + y = 5 crosses box from (0,5) to (5,0)
        line = Line2D(x=1, y=1, rhs=5)
        pts = line.intersect_box(self.bl, self.tr)
        assert len(pts) == 2

    def test_vertical_like_line_intersections(self):
        # x = 5 (as 1*x + 0*y = 5)
        line = Line2D(x=1, y=0, rhs=5)
        pts = line.intersect_box(self.bl, self.tr)
        # Only point_with_y branch fires; gives (5,0) and (5,10)
        assert len(pts) == 2
        xs = {p.x for p in pts}
        assert xs == {5.0}

    def test_line_outside_box_zero_intersections(self):
        # x + y = 25 is entirely outside box [0,10]^2
        line = Line2D(x=1, y=1, rhs=25)
        pts = line.intersect_box(self.bl, self.tr)
        assert len(pts) == 0

    def test_boxed_endpoints_no_intersection(self):
        line = Line2D(x=1, y=1, rhs=25)
        p1, p2 = line.boxed_endpoints(self.bl, self.tr)
        assert p1 == self.bl and p2 == self.bl  # degenerate fallback


# ---------------------------------------------------------------------------
# box_corners
# ---------------------------------------------------------------------------

class TestBoxCorners:
    def test_returns_four_corners(self):
        bl = Point2D(0, 0)
        tr = Point2D(4, 6)
        corners = box_corners(bl, tr)
        assert len(corners) == 4

    def test_corner_positions(self):
        bl = Point2D(1, 2)
        tr = Point2D(5, 7)
        corners = box_corners(bl, tr)
        assert Point2D(1, 2) in corners
        assert Point2D(5, 7) in corners
        assert Point2D(5, 2) in corners
        assert Point2D(1, 7) in corners
