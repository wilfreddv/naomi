from dataclasses import dataclass
from typing import List, Optional

from inc import TYPES
from operators import Operator


@dataclass
class Variable:
    name: str
    type: str
    value: Optional[str] = None

    def __post_init__(self):
        try:
            self.size = TYPES[self.type]
        except KeyError:
            raise ValueError(f"`{type}`: No such type")

@dataclass
class Constant:
    type: str
    value: str


@dataclass
class Procedure:
    name: str
    body: List[Operator]
    locals: Optional[List[Variable]] = None
    parameters: Optional[List[Variable]] = None