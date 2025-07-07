"""
Data loading module for Meshachvetz - loads CSV files and converts them to
data models with comprehensive error handling and validation.
"""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
from .models import Student, ClassData, SchoolData
from .validator import DataValidator, DataValidationError


class DataLoadError(Exception):
    """Exception raised when data loading fails."""
    pass


class DataLoader:
    """
    Loads CSV files and converts them to Meshachvetz data models.
    
    Features:
    - CSV file loading with error handling
    - Missing data imputation using column averages for ranged fields
    - Data type conversion and normalization
    - Integration with DataValidator
    - Conversion to Student, ClassData, and SchoolData models
    - Comprehensive error reporting
    """
    
    def __init__(self, validate_data: bool = True):
        """
        Initialize the DataLoader.
        
        Args:
            validate_data: Whether to validate data during loading
        """
        self.validate_data = validate_data
        self.validator = DataValidator() if validate_data else None
        self.imputation_stats = {}  # Store imputation statistics
        
    def load_csv(self, file_path: str) -> SchoolData:
        """
        Load student data from CSV file and convert to SchoolData model.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            SchoolData object with all students and classes
            
        Raises:
            DataLoadError: If file cannot be loaded or data is invalid
            DataValidationError: If data validation fails
        """
        try:
            # Load CSV file
            df = self._load_csv_file(file_path)
            
            # Apply missing data imputation
            df = self._apply_missing_data_imputation(df)
            
            # Validate data if requested
            if self.validate_data:
                validation_result = self.validator.validate_dataframe(df)
                if not validation_result['valid']:
                    error_msg = f"Data validation failed:\n{self.validator.get_validation_summary()}"
                    raise DataValidationError(error_msg)
                    
            # Convert to data models
            students = self._convert_to_students(df)
            
            # Check if any students have empty class assignments
            has_unassigned = any(not s.class_id or not s.class_id.strip() for s in students)
            
            if has_unassigned:
                school_data = SchoolData.from_students_list_with_unassigned(students)
            else:
                school_data = SchoolData.from_students_list(students)
            
            return school_data
            
        except FileNotFoundError:
            raise DataLoadError(f"CSV file not found: {file_path}")
        except pd.errors.EmptyDataError:
            raise DataLoadError(f"CSV file is empty: {file_path}")
        except pd.errors.ParserError as e:
            raise DataLoadError(f"Error parsing CSV file: {e}")
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading data: {e}")
    
    def _apply_missing_data_imputation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply missing data imputation using column averages for ranged fields.
        
        Args:
            df: DataFrame with potentially missing data
            
        Returns:
            DataFrame with missing values filled using averages
        """
        # Reset imputation stats
        self.imputation_stats = {
            'academic_score': {'count': 0, 'average': 0.0},
            'behavior_rank': {'count': 0, 'average': 'A'},
            'studentiality_rank': {'count': 0, 'average': 'A'}
        }
        
        # Create a copy to avoid modifying the original
        df_imputed = df.copy()
        
        # Handle academic_score (numeric field)
        if 'academic_score' in df_imputed.columns:
            df_imputed = self._impute_academic_score(df_imputed)
        
        # Handle behavior_rank (categorical field A-D)
        if 'behavior_rank' in df_imputed.columns:
            df_imputed = self._impute_behavior_rank(df_imputed)
        
        # Handle studentiality_rank (categorical field A-D)
        if 'studentiality_rank' in df_imputed.columns:
            df_imputed = self._impute_studentiality_rank(df_imputed)
        
        return df_imputed
    
    def _impute_academic_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing academic scores using column average.
        
        Args:
            df: DataFrame with academic_score column
            
        Returns:
            DataFrame with academic_score missing values filled
        """
        score_col = 'academic_score'
        
        # Convert to numeric, marking non-numeric as NaN
        df[score_col] = pd.to_numeric(df[score_col], errors='coerce')
        
        # Count missing values
        missing_count = df[score_col].isna().sum()
        
        if missing_count > 0:
            # Calculate average of non-missing values
            valid_scores = df[score_col].dropna()
            if len(valid_scores) > 0:
                average_score = valid_scores.mean()
                # Fill missing values with average
                df[score_col] = df[score_col].fillna(average_score)
                
                # Store imputation stats
                self.imputation_stats['academic_score'] = {
                    'count': missing_count,
                    'average': round(average_score, 2)
                }
                
                print(f"Imputed {missing_count} missing academic scores with average: {average_score:.2f}")
            else:
                # If all values are missing, use default
                df[score_col] = df[score_col].fillna(0.0)
                self.imputation_stats['academic_score'] = {
                    'count': missing_count,
                    'average': 0.0
                }
                print(f"All academic scores missing, using default: 0.0")
        
        return df
    
    def _impute_behavior_rank(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing behavior ranks using most common rank (mode).
        
        Args:
            df: DataFrame with behavior_rank column
            
        Returns:
            DataFrame with behavior_rank missing values filled
        """
        rank_col = 'behavior_rank'
        
        # Standardize values and identify missing
        df[rank_col] = df[rank_col].astype(str).str.strip().str.upper()
        missing_mask = df[rank_col].isin(['', 'NAN', 'NONE', 'NULL'])
        missing_count = missing_mask.sum()
        
        if missing_count > 0:
            # Get valid ranks
            valid_ranks = df[~missing_mask][rank_col]
            valid_ranks = valid_ranks[valid_ranks.isin(['A', 'B', 'C', 'D'])]
            
            if len(valid_ranks) > 0:
                # Calculate mode (most common rank)
                mode_rank = valid_ranks.mode().iloc[0] if not valid_ranks.mode().empty else 'A'
                
                # Fill missing values with mode
                df.loc[missing_mask, rank_col] = mode_rank
                
                # Store imputation stats
                self.imputation_stats['behavior_rank'] = {
                    'count': missing_count,
                    'average': mode_rank
                }
                
                print(f"Imputed {missing_count} missing behavior ranks with mode: {mode_rank}")
            else:
                # If all values are missing, use default
                df.loc[missing_mask, rank_col] = 'A'
                self.imputation_stats['behavior_rank'] = {
                    'count': missing_count,
                    'average': 'A'
                }
                print(f"All behavior ranks missing, using default: A")
        
        return df
    
    def _impute_studentiality_rank(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing studentiality ranks using most common rank (mode).
        
        Args:
            df: DataFrame with studentiality_rank column
            
        Returns:
            DataFrame with studentiality_rank missing values filled
        """
        rank_col = 'studentiality_rank'
        
        # Standardize values and identify missing
        df[rank_col] = df[rank_col].astype(str).str.strip().str.upper()
        missing_mask = df[rank_col].isin(['', 'NAN', 'NONE', 'NULL'])
        missing_count = missing_mask.sum()
        
        if missing_count > 0:
            # Get valid ranks
            valid_ranks = df[~missing_mask][rank_col]
            valid_ranks = valid_ranks[valid_ranks.isin(['A', 'B', 'C', 'D'])]
            
            if len(valid_ranks) > 0:
                # Calculate mode (most common rank)
                mode_rank = valid_ranks.mode().iloc[0] if not valid_ranks.mode().empty else 'A'
                
                # Fill missing values with mode
                df.loc[missing_mask, rank_col] = mode_rank
                
                # Store imputation stats
                self.imputation_stats['studentiality_rank'] = {
                    'count': missing_count,
                    'average': mode_rank
                }
                
                print(f"Imputed {missing_count} missing studentiality ranks with mode: {mode_rank}")
            else:
                # If all values are missing, use default
                df.loc[missing_mask, rank_col] = 'A'
                self.imputation_stats['studentiality_rank'] = {
                    'count': missing_count,
                    'average': 'A'
                }
                print(f"All studentiality ranks missing, using default: A")
        
        return df
    
    def get_imputation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of missing data imputation performed.
        
        Returns:
            Dictionary with imputation statistics
        """
        return self.imputation_stats.copy()
        
    def _load_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV file into pandas DataFrame with proper handling.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            pandas DataFrame with the loaded data
        """
        # Verify file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Load with pandas, keeping string type for all columns initially
        # Explicitly set index_col=False to prevent pandas from using first column as index
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False, na_values=[], index_col=False)
        
        # Basic cleanup
        if df.empty:
            raise DataLoadError("CSV file contains no data")
            
        # Fill any NaN values with empty strings
        df = df.fillna('')
        
        # Strip whitespace from all string columns
        for col in df.columns:
            if col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
                
        return df
        
    def _convert_to_students(self, df: pd.DataFrame) -> List[Student]:
        """
        Convert DataFrame to list of Student objects.
        
        Args:
            df: DataFrame with student data
            
        Returns:
            List of Student objects
        """
        students = []
        
        for index, row in df.iterrows():
            try:
                student = self._convert_row_to_student(row, index + 1)
                students.append(student)
            except Exception as e:
                raise DataLoadError(f"Error converting row {index + 1} to student: {e}")
                
        return students
        
    def _convert_row_to_student(self, row: pd.Series, row_num: int) -> Student:
        """
        Convert a single DataFrame row to a Student object.
        
        Args:
            row: pandas Series representing a single row
            row_num: Row number for error reporting
            
        Returns:
            Student object
        """
        try:
            # Extract and normalize required fields
            student_id = self._get_string_value(row, 'student_id')
            first_name = self._get_string_value(row, 'first_name')
            last_name = self._get_string_value(row, 'last_name')
            gender = self._get_string_value(row, 'gender', default='').upper()
            class_id = self._get_string_value(row, 'class')
            
            # Convert numeric fields - no longer need defaults since imputation was applied
            academic_score = self._get_float_value(row, 'academic_score', default=0.0)
            behavior_rank = self._get_string_value(row, 'behavior_rank', default='A').upper()
            studentiality_rank = self._get_string_value(row, 'studentiality_rank', default='A').upper()
            assistance_package = self._get_boolean_value(row, 'assistance_package', default=False)
            
            # Extract optional social preference fields
            preferred_friend_1 = self._get_string_value(row, 'preferred_friend_1', default='')
            preferred_friend_2 = self._get_string_value(row, 'preferred_friend_2', default='')
            preferred_friend_3 = self._get_string_value(row, 'preferred_friend_3', default='')
            
            disliked_peer_1 = self._get_string_value(row, 'disliked_peer_1', default='')
            disliked_peer_2 = self._get_string_value(row, 'disliked_peer_2', default='')
            disliked_peer_3 = self._get_string_value(row, 'disliked_peer_3', default='')
            disliked_peer_4 = self._get_string_value(row, 'disliked_peer_4', default='')
            disliked_peer_5 = self._get_string_value(row, 'disliked_peer_5', default='')
            
            # Extract force constraint fields
            force_class = self._get_string_value(row, 'force_class', default='')
            force_friend = self._get_string_value(row, 'force_friend', default='')
            
            # Create Student object
            student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                class_id=class_id,
                academic_score=academic_score,
                behavior_rank=behavior_rank,
                studentiality_rank=studentiality_rank,
                assistance_package=assistance_package,
                preferred_friend_1=preferred_friend_1,
                preferred_friend_2=preferred_friend_2,
                preferred_friend_3=preferred_friend_3,
                disliked_peer_1=disliked_peer_1,
                disliked_peer_2=disliked_peer_2,
                disliked_peer_3=disliked_peer_3,
                disliked_peer_4=disliked_peer_4,
                disliked_peer_5=disliked_peer_5,
                force_class=force_class,
                force_friend=force_friend
            )
            
            return student
            
        except Exception as e:
            raise DataLoadError(f"Error processing row {row_num}: {e}")
            
    def _get_string_value(self, row: pd.Series, column: str, default: str = '') -> str:
        """
        Get string value from row with proper null handling.
        
        Args:
            row: pandas Series representing a row
            column: Column name to extract
            default: Default value if column is missing or null
            
        Returns:
            String value
        """
        if column not in row:
            return default
            
        value = row[column]
        if not value or value.strip() == '':
            return default
            
        return value.strip()
        
    def _get_float_value(self, row: pd.Series, column: str, default: float = 0.0) -> float:
        """
        Get float value from row with proper null handling.
        
        Args:
            row: pandas Series representing a row
            column: Column name to extract
            default: Default value if column is missing or null
            
        Returns:
            Float value
        """
        if column not in row:
            return default
            
        value = row[column]
        if pd.isna(value):
            return default
            
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
            
    def _get_boolean_value(self, row: pd.Series, column: str, default: bool = False) -> bool:
        """
        Get boolean value from row with proper null handling.
        
        Args:
            row: pandas Series representing a row
            column: Column name to extract
            default: Default value if column is missing or null
            
        Returns:
            Boolean value
        """
        if column not in row:
            return default
            
        value = row[column]
        if pd.isna(value):
            return default
            
        # Handle various boolean representations
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 't', 'y']
            
        return default
        
    def load_students_only(self, file_path: str) -> List[Student]:
        """
        Load only the students from a CSV file without creating SchoolData.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of Student objects
        """
        df = self._load_csv_file(file_path)
        
        # Apply missing data imputation
        df = self._apply_missing_data_imputation(df)
        
        if self.validate_data:
            validation_result = self.validator.validate_dataframe(df)
            if not validation_result['valid']:
                error_msg = f"Data validation failed:\n{self.validator.get_validation_summary()}"
                raise DataValidationError(error_msg)
                
        return self._convert_to_students(df)
        
    def get_data_summary(self, school_data: SchoolData) -> Dict[str, Any]:
        """
        Get a summary of the loaded data.
        
        Args:
            school_data: SchoolData object
            
        Returns:
            Dictionary with data summary
        """
        summary = {
            'total_students': school_data.total_students,
            'total_classes': school_data.total_classes,
            'class_sizes': school_data.class_sizes,
            'classes': {}
        }
        
        # Add class-level summaries
        for class_id, class_data in school_data.classes.items():
            summary['classes'][class_id] = {
                'size': class_data.size,
                'male_count': class_data.male_count,
                'female_count': class_data.female_count,
                'avg_academic_score': round(class_data.average_academic_score, 2),
                'avg_behavior_rank': round(class_data.average_behavior_rank, 2),
                'assistance_count': class_data.assistance_count,
                'forced_students': class_data.forced_students_count,
                'forced_groups': class_data.forced_groups_count
            }
            
        # Add school-level statistics
        all_academic_scores = [s.academic_score for s in school_data.students.values()]
        all_behavior_ranks = [s.get_numeric_behavior_rank() for s in school_data.students.values()]
        
        summary['statistics'] = {
            'academic_score_mean': round(np.mean(all_academic_scores), 2),
            'academic_score_std': round(np.std(all_academic_scores), 2),
            'behavior_rank_mean': round(np.mean(all_behavior_ranks), 2),
            'behavior_rank_std': round(np.std(all_behavior_ranks), 2),
            'total_assistance_students': sum(1 for s in school_data.students.values() if s.assistance_package),
            'total_forced_students': sum(1 for s in school_data.students.values() if s.has_force_class()),
            'total_forced_groups': len(school_data.get_force_friend_groups())
        }
        
        # Add imputation statistics
        if hasattr(self, 'imputation_stats'):
            summary['imputation_stats'] = self.imputation_stats
        
        return summary
        
    def export_to_csv(self, school_data: SchoolData, output_path: str) -> None:
        """
        Export SchoolData back to CSV format.
        
        Args:
            school_data: SchoolData object to export
            output_path: Path for the output CSV file
        """
        # Convert students to list of dictionaries
        student_dicts = []
        for student in school_data.students.values():
            student_dict = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'gender': student.gender,
                'class': student.class_id,
                'academic_score': student.academic_score,
                'behavior_rank': student.behavior_rank,
                'studentiality_rank': student.studentiality_rank,
                'assistance_package': student.assistance_package,
                'preferred_friend_1': student.preferred_friend_1,
                'preferred_friend_2': student.preferred_friend_2,
                'preferred_friend_3': student.preferred_friend_3,
                'disliked_peer_1': student.disliked_peer_1,
                'disliked_peer_2': student.disliked_peer_2,
                'disliked_peer_3': student.disliked_peer_3,
                'disliked_peer_4': student.disliked_peer_4,
                'disliked_peer_5': student.disliked_peer_5,
                'force_class': student.force_class,
                'force_friend': student.force_friend
            }
            student_dicts.append(student_dict)
            
        # Create DataFrame and export
        df = pd.DataFrame(student_dicts)
        df.to_csv(output_path, index=False)
        
    @staticmethod
    def validate_csv_file(file_path: str) -> Dict[str, Any]:
        """
        Validate a CSV file without loading it into memory completely.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary with validation results
        """
        validator = DataValidator()
        
        try:
            # Load just the header first
            df_header = pd.read_csv(file_path, nrows=0)
            
            # Check columns
            if df_header.empty:
                return {
                    'valid': False,
                    'errors': ['File has no columns'],
                    'warnings': []
                }
                
            # Load full file for validation
            df = pd.read_csv(file_path)
            return validator.validate_dataframe(df)
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Error reading file: {e}'],
                'warnings': []
            } 