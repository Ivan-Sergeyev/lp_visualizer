from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class ObjectiveDict(TypedDict):
    """Stored in dcc.Store"""
    sense: str
    coeff_x: float
    coeff_y: float


class ObjectiveSense(Enum):
    MAX = 'max'
    MIN = 'min'

    @staticmethod
    def from_str(raw: str) -> ObjectiveSense:
        match raw:
            case ObjectiveSense.MAX.value:
                return ObjectiveSense.MAX
            case ObjectiveSense.MIN.value:
                return ObjectiveSense.MIN
            case _:
                raise ValueError(f'Unrecognized objective sense: {raw!r}')

    def __str__(self) -> str:
        return self.value


OBJECTIVE_SENSES = (str(ObjectiveSense.MAX), str(ObjectiveSense.MIN))


@dataclass
class Objective:
    """Used internally"""
    sense: ObjectiveSense
    coeff_x: float
    coeff_y: float

    @classmethod
    def from_dict(cls, objective_dict: ObjectiveDict) -> Objective:
        return Objective(
            sense=ObjectiveSense.from_str(objective_dict['sense']),
            coeff_x=objective_dict['coeff_x'],
            coeff_y=objective_dict['coeff_y'],
        )

    def to_dict(self) -> ObjectiveDict:
        return ObjectiveDict(
            sense=str(self.sense),
            coeff_x=self.coeff_x,
            coeff_y=self.coeff_y,
        )
