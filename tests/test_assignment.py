import pytest
from src.utils.assignment import assign_students_to_classes
from src.models.student import Student
from src.models.class_ import Class

def test_assign_students_to_classes():
    """Test that the assignment function correctly assigns students to classes in a round-robin fashion."""
    students = [
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False),
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False),
        Student(id=3, name="Charlie", behavior_rank="C", preferred_friends=(1, 2), special_needs=False),
    ]
    classes = [
        Class(id=1, name="Class 1", max_size=30),
        Class(id=2, name="Class 2", max_size=30),
    ]
    
    assignment = assign_students_to_classes(students, classes)
    
    # Verify that each student is assigned to a class
    assert len(assignment) == len(students)
    
    # Verify round-robin assignment
    assert assignment[students[0]] == classes[0]
    assert assignment[students[1]] == classes[1]
    assert assignment[students[2]] == classes[0] 