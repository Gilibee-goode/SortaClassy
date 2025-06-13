import csv
from typing import Dict
from src.models.student import Student
from src.models.class_ import Class

def write_assignments_to_csv(assignment: Dict[Student, Class], file_path: str) -> None:
    """Write class assignments to a CSV file."""
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['student_id', 'student_name', 'class_id', 'class_name'])
        for student, class_ in assignment.items():
            writer.writerow([student.id, student.name, class_.id, class_.name]) 