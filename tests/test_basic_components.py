import pytest
import dataclasses
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

def test_student_immutability():
    """Test that a Student instance cannot be modified after creation."""
    student = Student(
        id=1,
        name="Alice",
        behavior_rank="A",
        preferred_friends=(2, 3),
        special_needs=False
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        student.name = "Bob"

def test_student_hashability():
    """Test that a Student instance can be used as a dictionary key."""
    student = Student(
        id=1,
        name="Alice",
        behavior_rank="A",
        preferred_friends=(2, 3),
        special_needs=False
    )
    d = {student: "value"}
    assert d[student] == "value"

def test_class_creation():
    """Test that we can create a class with a maximum size."""
    class_ = Class(id=1, name="Class 1", max_size=5)
    assert class_.id == 1
    assert class_.name == "Class 1"
    assert class_.max_size == 5
    assert len(class_.students) == 0

def test_class_add_student():
    """Test that adding a student to a class works correctly."""
    class_ = Class(id=1, name="Class 1", max_size=5)
    student = Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False)
    assert class_.add_student(student) is True
    assert len(class_.students) == 1
    assert student in class_.students

def test_class_remove_student():
    """Test that removing a student from a class works correctly."""
    class_ = Class(id=1, name="Class 1", max_size=5)
    student = Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False)
    class_.add_student(student)
    assert class_.remove_student(student) is True
    assert len(class_.students) == 0

def test_class_is_full():
    """Test that the is_full property correctly indicates when a class is at its maximum capacity."""
    class_ = Class(id=1, name="Class 1", max_size=2)
    student1 = Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False)
    student2 = Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False)
    class_.add_student(student1)
    assert class_.is_full is False
    class_.add_student(student2)
    assert class_.is_full is True

def test_school_creation():
    """Test that we can create a school with a specified number of classes."""
    school = School(num_classes=3)
    assert len(school.classes) == 3
    assert all(isinstance(c, Class) for c in school.classes)
    assert len(school.students) == 0

def test_school_add_student():
    """Test that adding a student to the school works correctly."""
    school = School(num_classes=3)
    student = Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False)
    school.add_student(student)
    assert student in school.students

def test_school_get_class_by_id():
    """Test that retrieving a class by its ID works correctly."""
    school = School(num_classes=3)
    class_ = school.get_class_by_id(1)
    assert class_.id == 1

def test_school_get_student_by_id():
    """Test that retrieving a student by their ID works correctly."""
    school = School(num_classes=3)
    student = Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False)
    school.add_student(student)
    retrieved_student = school.get_student_by_id(1)
    assert retrieved_student == student

def test_school_get_class_assignments():
    """Test that the method returns the correct dictionary of student-to-class assignments."""
    school = School(num_classes=3)
    student = Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False)
    school.add_student(student)
    school.classes[0].add_student(student)
    assignments = school.get_class_assignments()
    assert assignments[student] == school.classes[0]

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

def test_class_size_constraint_edge_cases():
    """Test the ClassSizeConstraint with edge cases."""
    constraint = ClassSizeConstraint(min_size=2, max_size=4)
    school = School(num_classes=3)
    
    # Edge case: exactly min_size students
    edge_assignment_min = {
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False): school.classes[0],
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False): school.classes[0],
    }
    
    # Edge case: exactly max_size students
    edge_assignment_max = {
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False): school.classes[0],
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False): school.classes[0],
        Student(id=3, name="Charlie", behavior_rank="C", preferred_friends=(1, 2), special_needs=False): school.classes[0],
        Student(id=4, name="Diana", behavior_rank="A", preferred_friends=(5, 6), special_needs=False): school.classes[0],
    }
    
    assert constraint.check(edge_assignment_min) is True
    assert constraint.check(edge_assignment_max) is True

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

def test_behavior_rank_constraint_edge_cases():
    """Test the BehaviorRankConstraint with edge cases."""
    constraint = BehaviorRankConstraint(max_low_rank=1)  # Max 1 student with rank C
    school = School(num_classes=3)
    
    # Edge case: exactly max_low_rank students with rank C
    edge_assignment = {
        Student(id=1, name="Alice", behavior_rank="C", preferred_friends=(2, 3), special_needs=False): school.classes[0],
        Student(id=2, name="Bob", behavior_rank="A", preferred_friends=(1, 3), special_needs=False): school.classes[0],
    }
    
    assert constraint.check(edge_assignment) is True

def test_school_with_constraints():
    """Test that the School model works correctly with constraints."""
    school = School(num_classes=3)
    student1 = Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False)
    student2 = Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False)
    student3 = Student(id=3, name="Charlie", behavior_rank="C", preferred_friends=(1, 2), special_needs=False)
    
    school.add_student(student1)
    school.add_student(student2)
    school.add_student(student3)
    
    school.classes[0].add_student(student1)
    school.classes[0].add_student(student2)
    school.classes[1].add_student(student3)
    
    assignments = school.get_class_assignments()
    
    size_constraint = ClassSizeConstraint(min_size=1, max_size=3)
    rank_constraint = BehaviorRankConstraint(max_low_rank=1)
    
    assert size_constraint.check(assignments) is True
    assert rank_constraint.check(assignments) is True 