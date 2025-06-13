import pytest
from src.utils.csv_reader import read_students_from_csv

def test_read_students_from_csv():
    """Test that the CSV reader correctly reads student data from a CSV file."""
    file_path = "data/sample_students.csv"
    students = read_students_from_csv(file_path)
    
    # Verify the number of students read
    assert len(students) == 6
    
    # Verify the first student's data
    assert students[0].id == 1
    assert students[0].name == "Alice"
    assert students[0].behavior_rank == "A"
    assert students[0].preferred_friends == (2, 3)
    assert students[0].special_needs is False
    
    # Verify the last student's data
    assert students[5].id == 6
    assert students[5].name == "Frank"
    assert students[5].behavior_rank == "C"
    assert students[5].preferred_friends == (4, 5)
    assert students[5].special_needs is False 