from typing import Dict
from ..models.student import Student
from ..models.class_ import Class
from .base import Constraint

class ClassSizeConstraint(Constraint):
    """Constraint for class size limits."""
    
    def __init__(self, min_size: int, max_size: int):
        self.min_size = min_size
        self.max_size = max_size
    
    def check(self, assignment: Dict[Student, Class]) -> bool:
        """Check if all classes are within size limits."""
        # Count students in each class
        class_sizes = {}
        for student, class_ in assignment.items():
            class_sizes[class_] = class_sizes.get(class_, 0) + 1
        
        # Check if any class is outside limits
        for class_, size in class_sizes.items():
            if size < self.min_size or size > self.max_size:
                return False
        return True
    
    def score(self, assignment: Dict[Student, Class]) -> float:
        """Calculate a score based on how well class sizes are balanced."""
        if not self.check(assignment):
            return 0.0
        
        # Count students in each class
        class_sizes = {}
        for student, class_ in assignment.items():
            class_sizes[class_] = class_sizes.get(class_, 0) + 1
        
        # Calculate how far each class is from the ideal size
        ideal_size = (self.min_size + self.max_size) / 2
        total_deviation = sum(abs(size - ideal_size) for size in class_sizes.values())
        max_possible_deviation = len(class_sizes) * (self.max_size - self.min_size)
        
        # Convert to a score between 0 and 1
        return 1.0 - (total_deviation / max_possible_deviation) 