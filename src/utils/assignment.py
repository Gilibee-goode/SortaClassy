from typing import List, Dict
from src.models.student import Student
from src.models.class_ import Class

def assign_students_to_classes(students: List[Student], classes: List[Class]) -> Dict[Student, Class]:
    """Assign students to classes in a round-robin fashion."""
    assignment = {}
    for i, student in enumerate(students):
        class_index = i % len(classes)
        assignment[student] = classes[class_index]
    return assignment 