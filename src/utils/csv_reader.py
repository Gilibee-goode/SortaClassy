import csv
from typing import List
from src.models.student import Student

def read_students_from_csv(file_path: str) -> List[Student]:
    """Read student data from a CSV file and return a list of Student objects."""
    students = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert preferred_friends from comma-separated string to tuple of integers
            preferred_friends = tuple(int(friend) for friend in row['preferred_friends'].split(','))
            student = Student(
                id=int(row['id']),
                name=row['name'],
                behavior_rank=row['behavior_rank'],
                preferred_friends=preferred_friends,
                special_needs=row['special_needs'].lower() == 'true'
            )
            students.append(student)
    return students 