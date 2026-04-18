import math

from model.domain_transfer_objects import Constraint, Objective


EPSILON: float = 1e-5

def normal_objective_vector(objective: Objective) -> tuple[float, float]:
    len = math.sqrt(objective.x_coeff ** 2 + objective.y_coeff ** 2)

    if len < EPSILON:
        return (0., 0.)

    x, y = objective.x_coeff / len, objective.y_coeff / len
    return (x, y) if Objective.sense_to_ui(objective.sense) == 'max' else (-x, -y)


def point_is_in_bounding_box(x: float, y: float, x_min: float, x_max: float, y_min: float, y_max: float) -> bool:
    return x_min - EPSILON < x < x_max + EPSILON and y_min - EPSILON < y < y_max + EPSILON


def line_point_with_x(constraint: Constraint, x: float) -> tuple[float, float]:
    return (x, (constraint.rhs - constraint.x_coeff * x) / constraint.y_coeff)


def line_point_with_y(constraint: Constraint, y: float) -> tuple[float, float]:
    return ((constraint.rhs - constraint.y_coeff * y) / constraint.x_coeff, y)


def get_constraint_line_endpoints(constraint: Constraint, x_min: float, x_max: float, y_min: float, y_max: float) -> tuple[tuple[float, float], tuple[float, float]]:
    if constraint.x_coeff == 0 and constraint.y_coeff == 0:
        # degenerate line
        return ((x_min, y_min), (x_min, y_min))

    if constraint.x_coeff == 0:
        # horizontal line
        y_val = constraint.rhs / constraint.y_coeff
        return ((x_min, y_val), (x_max, y_val))

    if constraint.y_coeff == 0:
        # vertical line
        x_val = constraint.rhs / constraint.x_coeff
        return ((x_val, y_min), (x_val, y_max))

    intersections = list(set([
        line_point_with_x(constraint, x_min),
        line_point_with_x(constraint, x_max),
        line_point_with_y(constraint, y_min),
        line_point_with_y(constraint, y_max),
    ]))
    ret = [(x, y) for x, y in intersections if point_is_in_bounding_box(x, y, x_min, x_max, y_min, y_max)]

    if len(ret) < 2:
        # line outside of bounding box
        return (intersections[0], intersections[1])

    return (ret[0], ret[1])
