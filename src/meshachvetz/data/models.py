"""
Data models for Meshachvetz - defines the core data structures for students,
classes, and schools according to the technical specifications.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from collections import Counter
import re
import math


@dataclass
class Student:
    """
    Student data model representing a single student with all required fields
    and social preferences as specified in the data format specification.
    """
    student_id: str
    first_name: str
    last_name: str
    gender: str
    class_id: str
    academic_score: float
    behavior_rank: str  # A-D format
    studentiality_rank: str  # A-D format
    assistance_package: bool
    school: str = ""  # School of origin for distribution balance
    preferred_friend_1: str = ""
    preferred_friend_2: str = ""
    preferred_friend_3: str = ""
    disliked_peer_1: str = ""
    disliked_peer_2: str = ""
    disliked_peer_3: str = ""
    disliked_peer_4: str = ""
    disliked_peer_5: str = ""
    force_class: str = ""  # Force placement in specific class
    force_friend: str = ""  # Force group placement identifier
    
    def __post_init__(self):
        """Validate student data after initialization."""
        self.validate_student_id()
        self.validate_names()
        self.validate_gender()
        self.validate_academic_score()
        self.validate_behavior_rank()
        self.validate_studentiality_rank()
        self.validate_school()
        self.validate_force_constraints()
        
    def validate_student_id(self) -> None:
        """Validate student ID is exactly 9 digits."""
        if not self.student_id:
            raise ValueError("Student ID cannot be empty")
        if not re.match(r'^\d{9}$', self.student_id):
            raise ValueError(f"Student ID must be exactly 9 digits, got: {self.student_id}")
            
    def validate_names(self) -> None:
        """Validate first and last names."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name cannot be empty")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name cannot be empty")
        if len(self.first_name) > 50:
            raise ValueError("First name cannot exceed 50 characters")
        if len(self.last_name) > 50:
            raise ValueError("Last name cannot exceed 50 characters")
            
    def validate_gender(self) -> None:
        """Validate gender is M or F."""
        if self.gender.upper() not in ['M', 'F']:
            raise ValueError(f"Gender must be 'M' or 'F', got: {self.gender}")
        # Normalize to uppercase
        self.gender = self.gender.upper()
        
    def validate_academic_score(self) -> None:
        """Validate academic score is between 0 and 100."""
        if not isinstance(self.academic_score, (int, float)):
            raise ValueError(f"Academic score must be a number, got: {type(self.academic_score)}")
        if not (0.0 <= self.academic_score <= 100.0):
            raise ValueError(f"Academic score must be between 0 and 100, got: {self.academic_score}")
            
    def validate_behavior_rank(self) -> None:
        """Validate behavior rank is A-D."""
        if self.behavior_rank.upper() not in ['A', 'B', 'C', 'D']:
            raise ValueError(f"Behavior rank must be A-D, got: {self.behavior_rank}")
        # Normalize to uppercase
        self.behavior_rank = self.behavior_rank.upper()
        
    def validate_studentiality_rank(self) -> None:
        """Validate studentiality rank is A-D."""
        if self.studentiality_rank.upper() not in ['A', 'B', 'C', 'D']:
            raise ValueError(f"Studentiality rank must be A-D, got: {self.studentiality_rank}")
        # Normalize to uppercase
        self.studentiality_rank = self.studentiality_rank.upper()
        
    def validate_school(self) -> None:
        """Validate school of origin."""
        if self.school is None:
            self.school = ""
        # School can be empty (for backwards compatibility) or any non-empty string
        # We'll normalize it to handle case variations
        if self.school:
            self.school = self.school.strip()
        
    def validate_force_constraints(self) -> None:
        """Validate force constraint formats."""
        # force_class can be empty or any string (will be validated against existing classes later)
        # force_friend should be comma-separated student IDs or empty
        if self.force_friend:
            # Split by comma and validate each ID
            friend_ids = [id.strip() for id in self.force_friend.split(',') if id.strip()]
            for friend_id in friend_ids:
                if not re.match(r'^\d{9}$', friend_id):
                    raise ValueError(f"Force friend ID must be 9 digits, got: {friend_id}")
        
    def get_numeric_behavior_rank(self) -> int:
        """Convert string behavior rank to numeric value for calculations."""
        conversion = {"A": 1, "B": 2, "C": 3, "D": 4}
        return conversion.get(self.behavior_rank.upper(), 1)
        
    def get_numeric_studentiality_rank(self) -> int:
        """Convert string studentiality rank to numeric value for calculations."""
        conversion = {"A": 1, "B": 2, "C": 3, "D": 4}
        return conversion.get(self.studentiality_rank.upper(), 1)
        
    def get_preferred_friends(self) -> List[str]:
        """Get list of non-empty preferred friends."""
        friends = []
        for friend in [self.preferred_friend_1, self.preferred_friend_2, self.preferred_friend_3]:
            if friend and friend.strip():
                friends.append(friend.strip())
        return friends
        
    def get_disliked_peers(self) -> List[str]:
        """Get list of non-empty disliked peers."""
        peers = []
        for peer in [self.disliked_peer_1, self.disliked_peer_2, self.disliked_peer_3, 
                    self.disliked_peer_4, self.disliked_peer_5]:
            if peer and peer.strip():
                peers.append(peer.strip())
        return peers
        
    def get_force_friend_ids(self) -> List[str]:
        """Get list of student IDs in force friend group."""
        if not self.force_friend:
            return []
        return [id.strip() for id in self.force_friend.split(',') if id.strip()]
        
    def has_force_class(self) -> bool:
        """Check if student has force class constraint."""
        return bool(self.force_class and self.force_class.strip())
        
    def has_force_friend(self) -> bool:
        """Check if student has force friend constraint."""
        return bool(self.force_friend and self.force_friend.strip())


@dataclass
class ClassData:
    """
    Class data model representing a single class with all its students.
    """
    class_id: str
    students: List[Student]
    
    def __post_init__(self):
        """Validate class data after initialization."""
        if not self.class_id:
            raise ValueError("Class ID cannot be empty")
        if not isinstance(self.students, list):
            raise ValueError("Students must be a list")
    
    @property
    def size(self) -> int:
        """Get number of students in this class."""
        return len(self.students)
    
    @property
    def gender_distribution(self) -> Dict[str, int]:
        """Get gender distribution in this class."""
        return Counter(s.gender for s in self.students)
    
    @property
    def average_academic_score(self) -> float:
        """Get average academic score for this class."""
        if not self.students:
            return 0.0
        return sum(s.academic_score for s in self.students) / len(self.students)
        
    @property
    def average_behavior_rank(self) -> float:
        """Get average numeric behavior rank for this class."""
        if not self.students:
            return 1.0  # Default to 'A' equivalent
        return sum(s.get_numeric_behavior_rank() for s in self.students) / len(self.students)
        
    @property
    def average_studentiality_rank(self) -> float:
        """Get average numeric studentiality rank for this class."""
        if not self.students:
            return 1.0  # Default to 'A' equivalent
        return sum(s.get_numeric_studentiality_rank() for s in self.students) / len(self.students)
        
    @property
    def assistance_count(self) -> int:
        """Get number of students with assistance packages."""
        return sum(1 for s in self.students if s.assistance_package)
        
    @property
    def male_count(self) -> int:
        """Get number of male students."""
        return sum(1 for s in self.students if s.gender == 'M')
        
    @property
    def female_count(self) -> int:
        """Get number of female students."""
        return sum(1 for s in self.students if s.gender == 'F')
        
    @property
    def forced_students_count(self) -> int:
        """Get number of students with force_class constraint."""
        return sum(1 for s in self.students if s.has_force_class())
        
    @property
    def forced_groups_count(self) -> int:
        """Get number of unique force_friend groups in this class."""
        groups = set()
        for student in self.students:
            if student.has_force_friend():
                groups.add(student.force_friend)
        return len(groups)
        
    @property
    def school_distribution(self) -> Dict[str, int]:
        """Get distribution of students by school of origin."""
        return Counter(s.school for s in self.students if s.school)
        
    @property
    def unique_schools(self) -> Set[str]:
        """Get set of unique schools represented in this class."""
        return {s.school for s in self.students if s.school}
        
    @property
    def school_diversity_score(self) -> float:
        """
        Calculate school diversity score using Shannon's diversity index.
        Returns 0-100 where 100 is maximum diversity.
        """
        if not self.students:
            return 100.0  # Empty class is perfectly diverse
            
        # Get school distribution
        school_counts = self.school_distribution
        if not school_counts:
            return 100.0  # No school data means perfect diversity
            
        total = sum(school_counts.values())
        if total == 0:
            return 100.0
            
        # Calculate Shannon diversity index
        shannon_index = 0.0
        for count in school_counts.values():
            if count > 0:
                proportion = count / total
                shannon_index -= proportion * math.log(proportion)
        
        # Normalize to 0-100 scale
        # Maximum diversity occurs when all schools are equally represented
        max_possible_diversity = math.log(len(school_counts))
        if max_possible_diversity == 0:
            return 100.0
            
        diversity_ratio = shannon_index / max_possible_diversity
        return min(100.0, diversity_ratio * 100.0)
        
    def get_school_dominance_score(self) -> float:
        """
        Calculate how dominated this class is by a single school.
        Returns 0-100 where 0 means one school dominates completely, 100 means perfect balance.
        """
        if not self.students:
            return 100.0
            
        school_counts = self.school_distribution
        if not school_counts:
            return 100.0
            
        total = sum(school_counts.values())
        if total == 0:
            return 100.0
            
        # Find the largest school representation
        max_count = max(school_counts.values())
        dominance_ratio = max_count / total
        
        # Convert to balance score: 0% dominance = 100 points, 100% dominance = 0 points
        balance_score = (1 - dominance_ratio) * 100
        return balance_score
        
    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID from this class."""
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
        
    def add_student(self, student: Student) -> None:
        """Add a student to this class."""
        if self.get_student_by_id(student.student_id):
            raise ValueError(f"Student {student.student_id} already exists in class {self.class_id}")
        student.class_id = self.class_id
        self.students.append(student)
        
    def remove_student(self, student_id: str) -> bool:
        """Remove a student from this class. Returns True if removed, False if not found."""
        for i, student in enumerate(self.students):
            if student.student_id == student_id:
                del self.students[i]
                return True
        return False


@dataclass
class SchoolData:
    """
    School data model representing the entire school with all classes and students.
    """
    classes: Dict[str, ClassData]
    students: Dict[str, Student]
    
    def __post_init__(self):
        """Validate school data after initialization."""
        if not isinstance(self.classes, dict):
            raise ValueError("Classes must be a dictionary")
        if not isinstance(self.students, dict):
            raise ValueError("Students must be a dictionary")
        
        # Validate consistency between classes and students
        self._validate_consistency()
        
    def _validate_consistency(self) -> None:
        """Validate that class and student data are consistent."""
        # Check that all students in classes exist in students dict
        for class_id, class_data in self.classes.items():
            for student in class_data.students:
                if student.student_id not in self.students:
                    raise ValueError(f"Student {student.student_id} in class {class_id} not found in students dict")
                if self.students[student.student_id] != student:
                    raise ValueError(f"Student {student.student_id} data inconsistent between class and students dict")
                    
        # Check that assigned students are in their correct classes
        students_in_classes = set()
        for class_data in self.classes.values():
            for student in class_data.students:
                students_in_classes.add(student.student_id)
                
        # Allow students to exist without class assignment (for initialization)
        for student_id, student in self.students.items():
            if student.class_id and student.class_id.strip():
                # Student claims to be in a class, verify it exists and contains them
                if student_id not in students_in_classes:
                    raise ValueError(f"Student {student_id} claims to be in class '{student.class_id}' but is not found there")
    
    @property
    def total_students(self) -> int:
        """Get total number of students in the school."""
        return len(self.students)
    
    @property
    def total_classes(self) -> int:
        """Get total number of classes in the school."""
        return len(self.classes)
    
    @property
    def class_sizes(self) -> List[int]:
        """Get list of class sizes."""
        return [cls.size for cls in self.classes.values()]
        
    @property
    def class_ids(self) -> List[str]:
        """Get list of all class IDs."""
        return list(self.classes.keys())
        
    @property
    def student_ids(self) -> List[str]:
        """Get list of all student IDs."""
        return list(self.students.keys())
    
    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID from the school."""
        return self.students.get(student_id)
        
    def get_class_by_id(self, class_id: str) -> Optional[ClassData]:
        """Get class by ID from the school."""
        return self.classes.get(class_id)
        
    def move_student(self, student_id: str, new_class_id: str) -> bool:
        """
        Move a student from one class to another.
        Returns True if successful, False if student or class not found.
        """
        student = self.get_student_by_id(student_id)
        if not student:
            return False
            
        new_class = self.get_class_by_id(new_class_id)
        if not new_class:
            return False
            
        # Remove from old class
        old_class = self.get_class_by_id(student.class_id)
        if old_class:
            old_class.remove_student(student_id)
            
        # Add to new class
        new_class.add_student(student)
        
        return True
        
    def get_students_by_class(self, class_id: str) -> List[Student]:
        """Get all students in a specific class."""
        class_data = self.get_class_by_id(class_id)
        return class_data.students if class_data else []
        
    def get_force_friend_groups(self) -> Dict[str, List[str]]:
        """Get all force friend groups as dict of group_id -> list of student IDs."""
        groups = {}
        for student in self.students.values():
            if student.has_force_friend():
                if student.force_friend not in groups:
                    groups[student.force_friend] = []
                groups[student.force_friend].append(student.student_id)
        return groups
        
    def validate_force_constraints(self) -> List[str]:
        """
        Validate all force constraints are consistent.
        Returns list of validation errors.
        """
        errors = []
        
        # Validate force_class constraints
        for student in self.students.values():
            if student.has_force_class():
                if student.force_class not in self.classes:
                    errors.append(f"Student {student.student_id} has force_class '{student.force_class}' which doesn't exist")
                elif student.class_id != student.force_class:
                    errors.append(f"Student {student.student_id} has force_class '{student.force_class}' but is in class '{student.class_id}'")
                    
        # Validate force_friend constraints
        force_groups = self.get_force_friend_groups()
        for group_id, student_ids in force_groups.items():
            # Check all students in group exist
            for student_id in student_ids:
                if student_id not in self.students:
                    errors.append(f"Force friend group '{group_id}' contains non-existent student {student_id}")
                    
            # Check all students in group are in same class
            if len(student_ids) > 1:
                classes = set()
                for student_id in student_ids:
                    if student_id in self.students:
                        classes.add(self.students[student_id].class_id)
                if len(classes) > 1:
                    errors.append(f"Force friend group '{group_id}' has students in different classes: {classes}")
                    
        return errors
        
    @classmethod
    def from_students_list(cls, students: List[Student]) -> 'SchoolData':
        """Create SchoolData from a list of students."""
        # Create students dict
        students_dict = {s.student_id: s for s in students}
        
        # Group students by class
        classes_dict = {}
        for student in students:
            if student.class_id not in classes_dict:
                classes_dict[student.class_id] = ClassData(student.class_id, [])
            classes_dict[student.class_id].students.append(student)
            
        return cls(classes_dict, students_dict)
    
    @classmethod
    def from_students_list_with_unassigned(cls, students: List[Student]) -> 'SchoolData':
        """
        Create SchoolData from a list of students, properly handling unassigned students.
        
        Args:
            students: List of students, some may have empty class_id
            
        Returns:
            SchoolData with assigned students in classes and unassigned students accessible
        """
        # Create students dict
        students_dict = {s.student_id: s for s in students}
        
        # Group students by class, but only for assigned students
        classes_dict = {}
        for student in students:
            if student.class_id and student.class_id.strip():
                class_id = student.class_id.strip()
                if class_id not in classes_dict:
                    classes_dict[class_id] = ClassData(class_id, [])
                classes_dict[class_id].students.append(student)
        
        return cls(classes_dict, students_dict)
    
    def get_unassigned_students(self) -> List[Student]:
        """
        Get list of students who are not assigned to any class.
        
        Returns:
            List of unassigned students
        """
        assigned_student_ids = set()
        for class_data in self.classes.values():
            for student in class_data.students:
                assigned_student_ids.add(student.student_id)
        
        unassigned = []
        for student_id, student in self.students.items():
            if student_id not in assigned_student_ids:
                unassigned.append(student)
        
        return unassigned
        
    @property
    def school_distribution(self) -> Dict[str, int]:
        """Get overall distribution of students by school of origin."""
        return Counter(s.school for s in self.students.values() if s.school)
        
    @property
    def unique_schools(self) -> Set[str]:
        """Get set of all unique schools in the dataset."""
        return {s.school for s in self.students.values() if s.school}
        
    def get_school_size_category(self, school: str) -> str:
        """
        Categorize school by size for adaptive distribution rules.
        
        Args:
            school: School name
            
        Returns:
            'large', 'medium', or 'small'
        """
        school_dist = self.school_distribution
        school_size = school_dist.get(school, 0)
        
        if school_size > 40:
            return 'large'
        elif school_size >= 20:
            return 'medium'
        else:
            return 'small'
            
    def get_school_distribution_by_class(self) -> Dict[str, Dict[str, int]]:
        """
        Get school distribution for each class.
        
        Returns:
            Dict mapping class_id -> dict of school -> count
        """
        result = {}
        for class_id, class_data in self.classes.items():
            result[class_id] = class_data.school_distribution
        return result 