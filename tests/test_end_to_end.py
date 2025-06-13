import pytest
import os
from src.utils.csv_reader import read_students_from_csv
from src.utils.class_creator import create_classes
from src.utils.assignment import assign_students_to_classes
from src.utils.constraint_checker import check_constraints
from src.utils.csv_writer import write_assignments_to_csv
from src.constraints.class_size import ClassSizeConstraint
from src.constraints.behavior_rank import BehaviorRankConstraint

def test_end_to_end():
    """Test the full pipeline: CSV input → assignment → constraint check → output."""
    # Step 1: Read students from CSV
    students = read_students_from_csv("data/sample_students.csv")
    assert len(students) == 6
    
    # Step 2: Create classes
    classes = create_classes(num_classes=3)
    assert len(classes) == 3
    
    # Step 3: Assign students to classes
    assignment = assign_students_to_classes(students, classes)
    assert len(assignment) == len(students)
    
    # Step 4: Check constraints
    constraints = [
        ClassSizeConstraint(min_size=1, max_size=4),
        BehaviorRankConstraint(max_low_rank=2),
    ]
    assert check_constraints(assignment, constraints) is True
    
    # Step 5: Write assignments to CSV
    output_file = "data/assignments.csv"
    write_assignments_to_csv(assignment, output_file)
    assert os.path.exists(output_file) 