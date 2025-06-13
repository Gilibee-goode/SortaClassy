from abc import ABC, abstractmethod
from typing import Dict
from ..models.student import Student
from ..models.class_ import Class

class Constraint(ABC):
    """Base class for all constraints."""
    
    @abstractmethod
    def check(self, assignment: Dict[Student, Class]) -> bool:
        """Check if the assignment satisfies the constraint."""
        pass
    
    @abstractmethod
    def score(self, assignment: Dict[Student, Class]) -> float:
        """Calculate a score for how well the constraint is satisfied."""
        pass 