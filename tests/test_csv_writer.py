import pytest
import os
from src.utils.csv_writer import write_assignments_to_csv
from src.models.student import Student
from src.models.class_ import Class
import csv

def test_write_assignments_to_csv():
    """Test that the CSV writer correctly writes class assignments to a CSV file."""
    students = [
        Student(id=1, name="Alice", behavior_rank="A", preferred_friends=(2, 3), special_needs=False),
        Student(id=2, name="Bob", behavior_rank="B", preferred_friends=(1, 3), special_needs=False),
    ]
    classes = [
        Class(id=1, name="Class 1", max_size=30),
        Class(id=2, name="Class 2", max_size=30),
    ]
    
    assignment = {
        students[0]: classes[0],
        students[1]: classes[1],
    }
    
    file_path = "data/assignments.csv"
    write_assignments_to_csv(assignment, file_path)
    
    # Verify that the file exists
    assert os.path.exists(file_path)
    
    # Verify the contents of the file
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        assert header == ['student_id', 'student_name', 'class_id', 'class_name']
        
        row1 = next(reader)
        assert row1 == ['1', 'Alice', '1', 'Class 1']
        
        row2 = next(reader)
        assert row2 == ['2', 'Bob', '2', 'Class 2'] 