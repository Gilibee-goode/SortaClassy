from typing import Dict, List
from src.models.student import Student
from src.models.class_ import Class
from src.constraints.base import Constraint

def check_constraints(assignment: Dict[Student, Class], constraints: List[Constraint]) -> bool:
    """Check if an assignment satisfies all constraints."""
    return all(constraint.check(assignment) for constraint in constraints) 