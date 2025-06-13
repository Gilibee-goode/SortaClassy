import pytest
from src.utils.constraint_checker import check_constraints
from src.models.student import Student
from src.models.class_ import Class
from src.constraints.class_size import ClassSizeConstraint
from src.constraints.behavior_rank import BehaviorRankConstraint

def test_check_constraints():
    """Test that the constraint checker correctly checks if an assignment satisfies all constraints."""
    students = [
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False),
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False),
        Student(id=3, name="Charlie", behavior_rank="C", preferred_friends=(1, 2), special_needs=False),
    ]
    classes = [
        Class(id=1, name="Class 1", max_size=30),
        Class(id=2, name="Class 2", max_size=30),
    ]
    
    assignment = {
        students[0]: classes[0],
        students[1]: classes[0],
        students[2]: classes[1],
    }
    
    constraints = [
        ClassSizeConstraint(min_size=1, max_size=3),
        BehaviorRankConstraint(max_low_rank=1),
    ]
    
    assert check_constraints(assignment, constraints) is True 