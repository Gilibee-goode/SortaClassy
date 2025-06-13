import pytest
from src.models.student import Student
from src.models.class_ import Class
from src.models.school import School
from src.constraints.class_size import ClassSizeConstraint
from src.constraints.behavior_rank import BehaviorRankConstraint

# Test data
SIMPLE_TEST_DATA = [
    {"id": 1, "name": "Alice", "behavior_rank": "A", "preferred_friends": (2, 3), "special_needs": False},
    {"id": 2, "name": "Bob", "behavior_rank": "B", "preferred_friends": (1, 3), "special_needs": False},
    {"id": 3, "name": "Charlie", "behavior_rank": "C", "preferred_friends": (1, 2), "special_needs": False},
    {"id": 4, "name": "Diana", "behavior_rank": "A", "preferred_friends": (5, 6), "special_needs": False},
    {"id": 5, "name": "Eve", "behavior_rank": "B", "preferred_friends": (4, 6), "special_needs": False},
    {"id": 6, "name": "Frank", "behavior_rank": "C", "preferred_friends": (4, 5), "special_needs": False},
]

def test_student_creation():
    """Test that we can create a student with all required attributes."""
    student = Student(
        id=1,
        name="Alice",
        behavior_rank="A",
        preferred_friends=(2, 3),
        special_needs=False
    )
    assert student.id == 1
    assert student.name == "Alice"
    assert student.behavior_rank == "A"
    assert student.preferred_friends == (2, 3)
    assert student.special_needs is False

def test_class_creation():
    """Test that we can create a class with a maximum size."""
    class_ = Class(id=1, name="Class 1", max_size=5)
    assert class_.id == 1
    assert class_.name == "Class 1"
    assert class_.max_size == 5
    assert len(class_.students) == 0

def test_school_creation():
    """Test that we can create a school with a specified number of classes."""
    school = School(num_classes=3)
    assert len(school.classes) == 3
    assert all(isinstance(c, Class) for c in school.classes)
    assert len(school.students) == 0

def test_class_size_constraint():
    """Test that the class size constraint works correctly."""
    constraint = ClassSizeConstraint(min_size=2, max_size=4)
    school = School(num_classes=3)
    
    # Create a valid assignment (all classes have at least 2 students)
    valid_assignment = {
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False): school.classes[0],
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False): school.classes[0],
        Student(id=3, name="Charlie", behavior_rank="C", preferred_friends=(1, 2), special_needs=False): school.classes[1],
        Student(id=4, name="Diana", behavior_rank="A", preferred_friends=(5, 6), special_needs=False): school.classes[1],
        Student(id=5, name="Eve", behavior_rank="B", preferred_friends=(4, 6), special_needs=False): school.classes[2],
        Student(id=6, name="Frank", behavior_rank="C", preferred_friends=(4, 5), special_needs=False): school.classes[2],
    }
    
    # Create an invalid assignment (too many students in one class)
    invalid_assignment = {
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False): school.classes[0],
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False): school.classes[0],
        Student(id=3, name="Charlie", behavior_rank="C", preferred_friends=(1, 2), special_needs=False): school.classes[0],
        Student(id=4, name="Diana", behavior_rank="A", preferred_friends=(5, 6), special_needs=False): school.classes[0],
        Student(id=5, name="Eve", behavior_rank="B", preferred_friends=(4, 6), special_needs=False): school.classes[0],
    }
    
    assert constraint.check(valid_assignment) is True
    assert constraint.check(invalid_assignment) is False

def test_behavior_rank_constraint():
    """Test that the behavior rank constraint works correctly."""
    constraint = BehaviorRankConstraint(max_low_rank=1)  # Max 1 student with rank C
    school = School(num_classes=3)
    
    # Create a valid assignment
    valid_assignment = {
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False): school.classes[0],
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False): school.classes[0],
        Student(id=3, name="Charlie", behavior_rank="C", preferred_friends=(1, 2), special_needs=False): school.classes[1],
    }
    
    # Create an invalid assignment (too many C ranks in one class)
    invalid_assignment = {
        Student(id=1, name="Alice", behavior_rank="C", preferred_friends=(2, 3), special_needs=False): school.classes[0],
        Student(id=2, name="Bob", behavior_rank="C", preferred_friends=(1, 3), special_needs=False): school.classes[0],
        Student(id=3, name="Charlie", behavior_rank="A", preferred_friends=(1, 2), special_needs=False): school.classes[0],
    }
    
    assert constraint.check(valid_assignment) is True
    assert constraint.check(invalid_assignment) is False 