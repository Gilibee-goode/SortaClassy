from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Student:
    id: int
    name: str
    behavior_rank: str
    preferred_friends: Tuple[int, ...]
    special_needs: bool 