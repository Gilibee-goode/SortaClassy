from dataclasses import dataclass, field
from typing import List, Dict
from .student import Student
from .class_ import Class

@dataclass
class School:
    num_classes: int = 3
    classes: List[Class] = field(default_factory=list)
    students: List[Student] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the school with the specified number of classes."""
        self.classes = [
            Class(id=i, name=f"Class {i}", max_size=30)  # Default max size of 30
            for i in range(1, self.num_classes + 1)
        ]
    
    def add_student(self, student: Student) -> None:
        """Add a student to the school."""
        self.students.append(student)
    
    def get_class_by_id(self, class_id: int) -> Class:
        """Get a class by its ID."""
        for class_ in self.classes:
            if class_.id == class_id:
                return class_
        raise ValueError(f"Class with ID {class_id} not found")
    
    def get_student_by_id(self, student_id: int) -> Student:
        """Get a student by their ID."""
        for student in self.students:
            if student.id == student_id:
                return student
        raise ValueError(f"Student with ID {student_id} not found")
    
    def get_class_assignments(self) -> Dict[Student, Class]:
        """Get the current class assignments for all students."""
        assignments = {}
        for class_ in self.classes:
            for student in class_.students:
                assignments[student] = class_
        return assignments 