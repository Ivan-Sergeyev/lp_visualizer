from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class ConstraintDict(TypedDict):
    coeff_x: float
    coeff_y: float
    sense: str
    rhs: float


class ConstraintSense(Enum):
    LE = '≤'
    GE = '≥'
    EQ  = '='

    @staticmethod
    def from_str(sense: str) -> ConstraintSense:
        match sense:
            case ConstraintSense.LE.value | '<' | '<=' | '≤':
                return ConstraintSense.LE
            case '>' | '>=' | '≥':
                return ConstraintSense.GE
            case '=' | '==':
                return ConstraintSense.EQ
            case _:
                raise ValueError(f'Unrecognized constraint sense {sense}.')

    def __str__(self) -> str:
        return self.value


CONSTRAINT_SENSES = (str(ConstraintSense.LE), str(ConstraintSense.GE), str(ConstraintSense.EQ))


@dataclass
class Constraint:
    coeff_x: float = 0.
    coeff_y: float = 0.
    sense: ConstraintSense = ConstraintSense.LE
    rhs: float = 0.

    @classmethod
    def from_dict(cls, constraint_dict: ConstraintDict) -> Constraint:
        return Constraint(
            coeff_x=constraint_dict['coeff_x'],
            coeff_y=constraint_dict['coeff_y'],
            sense=ConstraintSense.from_str(constraint_dict['sense']),
            rhs=constraint_dict['rhs'],
        )

    def to_dict(self) -> ConstraintDict:
        return ConstraintDict(
            coeff_x=self.coeff_x,
            coeff_y=self.coeff_y,
            sense=str(self.sense),
            rhs=self.rhs,
        )

    def __str__(self):
        return f'{self.coeff_x} * x + {self.coeff_y} * y {str(self.sense)} {self.rhs}'
