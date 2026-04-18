import math

from model.domain_transfer_objects import Constraint, Objective


type Range2D = tuple[float, float]
type Point2D = tuple[float, float]

EPSILON: float = 1e-5


def float_in_range(a: float, range: Point2D) -> bool:
    return range[0] - EPSILON < a < range[1] + EPSILON


def float_eq(a: float, b: float) -> bool:
    return a - EPSILON < b < a + EPSILON


def point_eq(a: Point2D, b: Point2D) -> bool:
    return float_eq(a[0], b[0]) and float_eq(a[1], b[1])


def normal_objective_vector(objective: Objective) -> Point2D:
    length = math.sqrt(objective.x_coeff ** 2 + objective.y_coeff ** 2)

    if float_eq(length, 0.):
        return (0., 0.)

    x, y = objective.x_coeff / length, objective.y_coeff / length
    return (x, y) if Objective.sense_to_ui(objective.sense) == 'max' else (-x, -y)


def point_is_in_bounding_box(point: Point2D, x_range: Range2D, y_range: Range2D) -> bool:
    return float_in_range(point[0], x_range) and float_in_range(point[1], y_range)


def line_point_with_x(constraint: Constraint, x: float) -> Point2D:
    return x, (constraint.rhs - constraint.x_coeff * x) / constraint.y_coeff


def line_point_with_y(constraint: Constraint, y: float) -> Point2D:
    return (constraint.rhs - constraint.y_coeff * y) / constraint.x_coeff, y


def unique_float_tuples(points: list[Point2D]) -> list[Point2D]:
    return list(set(points))


def intersect_line_box(constraint: Constraint, x_range: Range2D, y_range: Range2D) -> list[Point2D]:
    intersections = []

    if not -EPSILON < constraint.x_coeff < EPSILON:
        intersections += [line_point_with_y(constraint, y) for y in y_range]

    if not -EPSILON < constraint.y_coeff < EPSILON:
        intersections += [line_point_with_x(constraint, x) for x in x_range]

    intersections = [point for point in intersections if point_is_in_bounding_box(point, x_range, y_range)]
    return unique_float_tuples(intersections)


def get_constraint_line_endpoints(constraint: Constraint, x_range: Range2D, y_range: Range2D) -> tuple[Point2D, Point2D]:
    intersections = intersect_line_box(constraint, x_range, y_range)
    match len(intersections):
        case 0:
            return (x_range[0], y_range[0]), (x_range[0], y_range[0])
        case 1:
            return intersections[0], intersections[0]
        case _:
            return intersections[0], intersections[1]
