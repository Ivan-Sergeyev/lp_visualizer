from __future__ import annotations

import math
from dataclasses import dataclass

EPSILON: float = 1e-9

def float_lt(a: float, b: float) -> bool:
    return a - EPSILON < b

def float_eq(a: float, b: float) -> bool:
    return abs(a - b) < EPSILON


@dataclass
class Vector2D:
    x: float = 0.
    y: float = 0.

    def __add__(self, other) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other) -> bool:
        return float_eq(self.x, other.x) and float_eq(self.y, other.y)

    def __lt__(self, other) -> bool:
        return float_lt(self.x, other.x) and float_lt(self.y, other.y)

    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def unit(self) -> Vector2D:
        length = self.length()

        if float_eq(length, 0.):
            return Vector2D(0., 0.)

        return Vector2D(self.x / length, self.y / length)


class Point2D(Vector2D):
    def is_in_box(self, bottom_left: Point2D, top_right: Point2D):
        return bottom_left < self < top_right


@dataclass
class Line2D(Vector2D):
    rhs: float = 0.

    def point_with_x(self, x: float) -> Point2D:
        return Point2D(x, (self.rhs - self.x * x) / self.y)

    def point_with_y(self, y: float) -> Point2D:
        return Point2D((self.rhs - self.y * y) / self.x, y)

    def intersect_box(self, bottom_left: Point2D, top_right: Point2D) -> list[Point2D]:
        intersections = []

        if not float_eq(self.x, 0.):
            intersections.append(self.point_with_y(bottom_left.y))
            intersections.append(self.point_with_y(top_right.y))

        if not float_eq(self.y, 0):
            intersections.append(self.point_with_x(bottom_left.x))
            intersections.append(self.point_with_x(top_right.x))

        unique_in_box = []
        for point in intersections:
            if point not in unique_in_box and point.is_in_box(bottom_left, top_right):
                unique_in_box.append(point)

        return unique_in_box

    def boxed_endpoints(self, bottom_left: Point2D, top_right: Point2D) -> tuple[Point2D, Point2D]:
        intersections = self.intersect_box(bottom_left, top_right)
        match len(intersections):
            case 0:
                return bottom_left, bottom_left
            case 1:
                return intersections[0], intersections[0]
            case _:
                return intersections[0], intersections[1]

    def intersect_line(self, other: Line2D) -> Point2D | None:
        det = self.x * other.y - other.x * self.y
        if float_eq(det, 0.):
            # parallel lines
            return None
        point_x = (self.rhs * other.y - self.y * other.rhs) / det
        point_y = (self.x * other.rhs - self.rhs * other.x) / det
        return Point2D(point_x, point_y)


def box_corners(bottom_left: Point2D, top_right: Point2D):
    return [
        bottom_left,
        Point2D(top_right.x, bottom_left.y),
        top_right,
        Point2D(bottom_left.x, top_right.y),
    ]
