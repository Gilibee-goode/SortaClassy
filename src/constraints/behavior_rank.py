from typing import Dict
from ..models.student import Student
from ..models.class_ import Class
from .base import Constraint

class BehaviorRankConstraint(Constraint):
    """Constraint for limiting the number of low behavior rank students per class."""
    
    def __init__(self, max_low_rank: int):
        self.max_low_rank = max_low_rank
    
    def check(self, assignment: Dict[Student, Class]) -> bool:
        """Check if no class has more than max_low_rank students with rank C."""
        # Count low rank students in each class
        class_low_ranks = {}
        for student, class_ in assignment.items():
            if student.behavior_rank == "C":
                class_low_ranks[class_] = class_low_ranks.get(class_, 0) + 1
        
        # Check if any class exceeds the limit
        return all(count <= self.max_low_rank for count in class_low_ranks.values())
    
    def score(self, assignment: Dict[Student, Class]) -> float:
        """Calculate a score based on how well behavior ranks are distributed."""
        if not self.check(assignment):
            return 0.0
        
        # Count low rank students in each class
        class_low_ranks = {}
        for student, class_ in assignment.items():
            if student.behavior_rank == "C":
                class_low_ranks[class_] = class_low_ranks.get(class_, 0) + 1
        
        # Calculate how far each class is from the ideal distribution
        total_low_ranks = sum(class_low_ranks.values())
        ideal_per_class = total_low_ranks / len(class_low_ranks)
        total_deviation = sum(abs(count - ideal_per_class) for count in class_low_ranks.values())
        max_possible_deviation = len(class_low_ranks) * self.max_low_rank
        
        # Convert to a score between 0 and 1
        return 1.0 - (total_deviation / max_possible_deviation) 