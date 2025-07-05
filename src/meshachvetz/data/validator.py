"""
Data validation module for Meshachvetz - validates CSV input data according to
the data format specification.
"""

from typing import List, Dict, Set, Optional, Any, Tuple
import pandas as pd
import re
from .models import Student


class DataValidationError(Exception):
    """Exception raised when data validation fails."""
    pass


class DataValidator:
    """
    Validates CSV data according to the Meshachvetz data format specification.
    
    Performs comprehensive validation including:
    - Required columns presence
    - Data type validation
    - Student ID format (9 digits)
    - Behavior rank validation (A-E)
    - Force constraint validation
    - Social preference validation
    - Cross-reference validation
    """
    
    # Required columns according to data format specification
    REQUIRED_COLUMNS = [
        'student_id', 'first_name', 'last_name', 'gender', 'class',
        'academic_score', 'behavior_rank', 'assistance_package'
    ]
    
    # Optional social preference columns
    OPTIONAL_COLUMNS = [
        'preferred_friend_1', 'preferred_friend_2', 'preferred_friend_3',
        'disliked_peer_1', 'disliked_peer_2', 'disliked_peer_3',
        'disliked_peer_4', 'disliked_peer_5',
        'force_class', 'force_friend'
    ]
    
    # All expected columns
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
    
    # Valid behavior ranks
    VALID_BEHAVIOR_RANKS = {'A', 'B', 'C', 'D', 'E'}
    
    # Valid gender values
    VALID_GENDERS = {'M', 'F'}
    
    # Valid boolean values for assistance_package
    VALID_BOOLEAN_VALUES = {
        'true', 'false', '1', '0', 'yes', 'no', 
        'True', 'False', 'TRUE', 'FALSE', 'YES', 'NO'
    }
    
    def __init__(self):
        """Initialize the validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate a pandas DataFrame containing student data.
        
        Args:
            df: DataFrame with student data
            
        Returns:
            Dict containing validation results:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'row_count': int,
                'column_count': int
            }
        """
        self.errors = []
        self.warnings = []
        
        # Basic structure validation
        self._validate_structure(df)
        
        if not self.errors:  # Only proceed if structure is valid
            # Validate each row
            self._validate_rows(df)
            
            # Validate cross-references
            self._validate_cross_references(df)
            
            # Validate force constraints
            self._validate_force_constraints(df)
            
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'row_count': len(df),
            'column_count': len(df.columns)
        }
        
    def _validate_structure(self, df: pd.DataFrame) -> None:
        """Validate DataFrame structure and columns."""
        # Check if DataFrame is empty
        if df.empty:
            self.errors.append("Input data is empty")
            return
            
        # Check for required columns
        missing_columns = []
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                missing_columns.append(col)
                
        if missing_columns:
            self.errors.append(f"Missing required columns: {missing_columns}")
            
        # Check for unexpected columns
        unexpected_columns = []
        for col in df.columns:
            if col not in self.ALL_COLUMNS:
                unexpected_columns.append(col)
                
        if unexpected_columns:
            self.warnings.append(f"Unexpected columns found: {unexpected_columns}")
            
    def _validate_rows(self, df: pd.DataFrame) -> None:
        """Validate each row of data."""
        for index, row in df.iterrows():
            row_num = index + 1  # 1-based row numbering for user-friendly messages
            
            # Validate student ID
            self._validate_student_id(row, row_num)
            
            # Validate names
            self._validate_names(row, row_num)
            
            # Validate gender
            self._validate_gender(row, row_num)
            
            # Validate academic score
            self._validate_academic_score(row, row_num)
            
            # Validate behavior rank
            self._validate_behavior_rank(row, row_num)
            
            # Validate assistance package
            self._validate_assistance_package(row, row_num)
            
            # Validate class
            self._validate_class(row, row_num)
            
            # Validate social preferences
            self._validate_social_preferences(row, row_num)
            
    def _validate_student_id(self, row: pd.Series, row_num: int) -> None:
        """Validate student ID format."""
        student_id = row.get('student_id')
        
        if pd.isna(student_id) or str(student_id).strip() == '':
            self.errors.append(f"Row {row_num}: Student ID cannot be empty")
            return
            
        student_id_str = str(student_id).strip()
        
        # Check 9-digit format
        if not re.match(r'^\d{9}$', student_id_str):
            self.errors.append(f"Row {row_num}: Student ID must be exactly 9 digits, got: {student_id_str}")
            
    def _validate_names(self, row: pd.Series, row_num: int) -> None:
        """Validate first and last names."""
        first_name = row.get('first_name')
        last_name = row.get('last_name')
        
        if pd.isna(first_name) or str(first_name).strip() == '':
            self.errors.append(f"Row {row_num}: First name cannot be empty")
            
        if pd.isna(last_name) or str(last_name).strip() == '':
            self.errors.append(f"Row {row_num}: Last name cannot be empty")
            
        # Check name length
        if not pd.isna(first_name) and len(str(first_name)) > 50:
            self.errors.append(f"Row {row_num}: First name cannot exceed 50 characters")
            
        if not pd.isna(last_name) and len(str(last_name)) > 50:
            self.errors.append(f"Row {row_num}: Last name cannot exceed 50 characters")
            
    def _validate_gender(self, row: pd.Series, row_num: int) -> None:
        """Validate gender value."""
        gender = row.get('gender')
        
        if pd.isna(gender) or str(gender).strip() == '':
            self.errors.append(f"Row {row_num}: Gender cannot be empty")
            return
            
        gender_str = str(gender).strip().upper()
        
        if gender_str not in self.VALID_GENDERS:
            self.errors.append(f"Row {row_num}: Gender must be 'M' or 'F', got: {gender}")
            
    def _validate_academic_score(self, row: pd.Series, row_num: int) -> None:
        """Validate academic score."""
        score = row.get('academic_score')
        
        if pd.isna(score):
            self.warnings.append(f"Row {row_num}: Academic score is missing, will default to 0.0")
            return
            
        try:
            score_float = float(score)
            if not (0.0 <= score_float <= 100.0):
                self.errors.append(f"Row {row_num}: Academic score must be between 0 and 100, got: {score}")
        except (ValueError, TypeError):
            self.errors.append(f"Row {row_num}: Academic score must be a number, got: {score}")
            
    def _validate_behavior_rank(self, row: pd.Series, row_num: int) -> None:
        """Validate behavior rank."""
        rank = row.get('behavior_rank')
        
        if pd.isna(rank) or str(rank).strip() == '':
            self.warnings.append(f"Row {row_num}: Behavior rank is missing, will default to 'A'")
            return
            
        rank_str = str(rank).strip().upper()
        
        if rank_str not in self.VALID_BEHAVIOR_RANKS:
            self.errors.append(f"Row {row_num}: Behavior rank must be A-E, got: {rank}")
            
    def _validate_assistance_package(self, row: pd.Series, row_num: int) -> None:
        """Validate assistance package boolean value."""
        assistance = row.get('assistance_package')
        
        if pd.isna(assistance):
            self.warnings.append(f"Row {row_num}: Assistance package is missing, will default to false")
            return
            
        assistance_str = str(assistance).strip().lower()
        
        if assistance_str not in [v.lower() for v in self.VALID_BOOLEAN_VALUES]:
            self.errors.append(f"Row {row_num}: Assistance package must be true/false, got: {assistance}")
            
    def _validate_class(self, row: pd.Series, row_num: int) -> None:
        """Validate class assignment."""
        class_id = row.get('class')
        
        if pd.isna(class_id) or str(class_id).strip() == '':
            self.errors.append(f"Row {row_num}: Class cannot be empty")
            
    def _validate_social_preferences(self, row: pd.Series, row_num: int) -> None:
        """Validate social preference columns."""
        student_id = str(row.get('student_id', '')).strip()
        
        # Validate preferred friends
        preferred_friends = []
        for i in range(1, 4):
            col_name = f'preferred_friend_{i}'
            friend_id = row.get(col_name)
            
            if not pd.isna(friend_id) and str(friend_id).strip():
                friend_id_str = str(friend_id).strip()
                
                # Check format
                if not re.match(r'^\d{9}$', friend_id_str):
                    self.errors.append(f"Row {row_num}: {col_name} must be 9 digits, got: {friend_id_str}")
                else:
                    # Check for self-reference
                    if friend_id_str == student_id:
                        self.warnings.append(f"Row {row_num}: {col_name} is self-reference, will be ignored")
                    else:
                        preferred_friends.append(friend_id_str)
                        
        # Check for duplicates in preferred friends
        if len(preferred_friends) != len(set(preferred_friends)):
            self.warnings.append(f"Row {row_num}: Duplicate preferred friends found, duplicates will be removed")
            
        # Validate disliked peers
        disliked_peers = []
        for i in range(1, 6):
            col_name = f'disliked_peer_{i}'
            peer_id = row.get(col_name)
            
            if not pd.isna(peer_id) and str(peer_id).strip():
                peer_id_str = str(peer_id).strip()
                
                # Check format
                if not re.match(r'^\d{9}$', peer_id_str):
                    self.errors.append(f"Row {row_num}: {col_name} must be 9 digits, got: {peer_id_str}")
                else:
                    # Check for self-reference
                    if peer_id_str == student_id:
                        self.warnings.append(f"Row {row_num}: {col_name} is self-reference, will be ignored")
                    else:
                        disliked_peers.append(peer_id_str)
                        
        # Check for duplicates in disliked peers
        if len(disliked_peers) != len(set(disliked_peers)):
            self.warnings.append(f"Row {row_num}: Duplicate disliked peers found, duplicates will be removed")
            
        # Check for overlap between preferred and disliked
        overlap = set(preferred_friends) & set(disliked_peers)
        if overlap:
            self.warnings.append(f"Row {row_num}: Student has same ID in both preferred and disliked lists: {overlap}")
            
    def _validate_cross_references(self, df: pd.DataFrame) -> None:
        """Validate that referenced student IDs exist in the dataset."""
        # Get all student IDs
        all_student_ids = set()
        for _, row in df.iterrows():
            student_id = row.get('student_id')
            if not pd.isna(student_id):
                all_student_ids.add(str(student_id).strip())
                
        # Check social preferences reference valid students
        for index, row in df.iterrows():
            row_num = index + 1
            
            # Check preferred friends
            for i in range(1, 4):
                col_name = f'preferred_friend_{i}'
                friend_id = row.get(col_name)
                
                if not pd.isna(friend_id) and str(friend_id).strip():
                    friend_id_str = str(friend_id).strip()
                    if friend_id_str not in all_student_ids:
                        self.errors.append(f"Row {row_num}: {col_name} references non-existent student: {friend_id_str}")
                        
            # Check disliked peers
            for i in range(1, 6):
                col_name = f'disliked_peer_{i}'
                peer_id = row.get(col_name)
                
                if not pd.isna(peer_id) and str(peer_id).strip():
                    peer_id_str = str(peer_id).strip()
                    if peer_id_str not in all_student_ids:
                        self.errors.append(f"Row {row_num}: {col_name} references non-existent student: {peer_id_str}")
                        
    def _validate_force_constraints(self, df: pd.DataFrame) -> None:
        """Validate force constraints."""
        # Get all class IDs
        all_class_ids = set()
        for _, row in df.iterrows():
            class_id = row.get('class')
            if not pd.isna(class_id):
                all_class_ids.add(str(class_id).strip())
                
        # Get all student IDs
        all_student_ids = set()
        for _, row in df.iterrows():
            student_id = row.get('student_id')
            if not pd.isna(student_id):
                all_student_ids.add(str(student_id).strip())
                
        # Validate force_class constraints
        for index, row in df.iterrows():
            row_num = index + 1
            
            force_class = row.get('force_class')
            if not pd.isna(force_class) and str(force_class).strip():
                force_class_str = str(force_class).strip()
                if force_class_str not in all_class_ids:
                    self.errors.append(f"Row {row_num}: force_class references non-existent class: {force_class_str}")
                    
                # Check if student is actually in the forced class
                current_class = str(row.get('class', '')).strip()
                if current_class != force_class_str:
                    self.errors.append(f"Row {row_num}: Student has force_class '{force_class_str}' but is in class '{current_class}'")
                    
        # Validate force_friend constraints
        force_groups = {}
        for index, row in df.iterrows():
            row_num = index + 1
            
            force_friend = row.get('force_friend')
            if not pd.isna(force_friend) and str(force_friend).strip():
                force_friend_str = str(force_friend).strip()
                
                # Parse comma-separated student IDs
                try:
                    friend_ids = [id.strip() for id in force_friend_str.split(',') if id.strip()]
                    
                    # Validate each ID format
                    for friend_id in friend_ids:
                        if not re.match(r'^\d{9}$', friend_id):
                            self.errors.append(f"Row {row_num}: force_friend contains invalid student ID: {friend_id}")
                        elif friend_id not in all_student_ids:
                            self.errors.append(f"Row {row_num}: force_friend references non-existent student: {friend_id}")
                            
                    # Track force groups
                    if force_friend_str not in force_groups:
                        force_groups[force_friend_str] = []
                    force_groups[force_friend_str].append({
                        'student_id': str(row.get('student_id', '')).strip(),
                        'class_id': str(row.get('class', '')).strip(),
                        'row_num': row_num
                    })
                    
                except Exception as e:
                    self.errors.append(f"Row {row_num}: Invalid force_friend format: {force_friend_str}")
                    
        # Validate force friend groups are in same class
        for group_id, students in force_groups.items():
            if len(students) > 1:
                classes = set(s['class_id'] for s in students)
                if len(classes) > 1:
                    student_info = [f"Student {s['student_id']} (row {s['row_num']}) in class {s['class_id']}" for s in students]
                    self.errors.append(f"Force friend group '{group_id}' has students in different classes: {'; '.join(student_info)}")
                    
    def validate_student_data(self, student_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate individual student data dictionary.
        
        Args:
            student_data: Dictionary containing student data
            
        Returns:
            Tuple of (is_valid, errors_list)
        """
        errors = []
        
        try:
            # Try to create Student object which will trigger validation
            student = Student(
                student_id=student_data.get('student_id', ''),
                first_name=student_data.get('first_name', ''),
                last_name=student_data.get('last_name', ''),
                gender=student_data.get('gender', ''),
                class_id=student_data.get('class', ''),
                academic_score=float(student_data.get('academic_score', 0.0)),
                behavior_rank=student_data.get('behavior_rank', 'A'),
                assistance_package=self._parse_boolean(student_data.get('assistance_package', False)),
                preferred_friend_1=student_data.get('preferred_friend_1', ''),
                preferred_friend_2=student_data.get('preferred_friend_2', ''),
                preferred_friend_3=student_data.get('preferred_friend_3', ''),
                disliked_peer_1=student_data.get('disliked_peer_1', ''),
                disliked_peer_2=student_data.get('disliked_peer_2', ''),
                disliked_peer_3=student_data.get('disliked_peer_3', ''),
                disliked_peer_4=student_data.get('disliked_peer_4', ''),
                disliked_peer_5=student_data.get('disliked_peer_5', ''),
                force_class=student_data.get('force_class', ''),
                force_friend=student_data.get('force_friend', '')
            )
            
        except (ValueError, TypeError) as e:
            errors.append(str(e))
            
        return len(errors) == 0, errors
        
    def _parse_boolean(self, value: Any) -> bool:
        """Parse boolean value from various formats."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 't', 'y']
        return False
        
    def get_validation_summary(self) -> str:
        """Get a formatted summary of validation results."""
        summary = []
        
        if self.errors:
            summary.append(f"❌ {len(self.errors)} validation error(s):")
            for error in self.errors:
                summary.append(f"  • {error}")
                
        if self.warnings:
            summary.append(f"⚠️  {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                summary.append(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            summary.append("✅ All validation checks passed!")
            
        return "\n".join(summary) 