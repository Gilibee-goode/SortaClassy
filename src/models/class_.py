from dataclasses import dataclass, field
from typing import List
from .student import Student

@dataclass(unsafe_hash=True)
class Class:
    id: int
    name: str
    max_size: int
    students: List[Student] = field(default_factory=list, compare=False, hash=False)
    
    def add_student(self, student: Student) -> bool:
        """Add a student to the class if there's room."""
        if len(self.students) < self.max_size:
            self.students.append(student)
            return True
        return False
    
    def remove_student(self, student: Student) -> bool:
        """Remove a student from the class."""
        if student in self.students:
            self.students.remove(student)
            return True
        return False
    
    @property
    def current_size(self) -> int:
        """Get the current number of students in the class."""
        return len(self.students)
    
    @property
    def is_full(self) -> bool:
        """Check if the class is at maximum capacity."""
        return len(self.students) >= self.max_size 