"""
School scorer implementation for Meshachvetz - calculates inter-class balance scores
focusing on academic, behavior, size, and assistance balance across all classes.
"""

from typing import Dict, List, Optional
import logging
import numpy as np
from ..data.models import Student, ClassData, SchoolData
from ..utils.config import Config


class SchoolScorer:
    """
    Calculates inter-class balance scores based on:
    - Academic Balance: Standard deviation of average academic scores across classes
    - Behavior Balance: Standard deviation of average behavior ranks across classes
    - Size Balance: Standard deviation of class sizes
    - Assistance Balance: Standard deviation of assistance package counts across classes
    
    Implements the School Layer of the three-layer scoring system.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the SchoolScorer.
        
        Args:
            config: Configuration object with scoring weights and normalization factors
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def calculate_balance_score(self, values: List[float], normalization_factor: float) -> Dict[str, float]:
        """
        Calculate balance score based on standard deviation.
        
        Formula: 100 - (std_dev * normalization_factor)
        Lower standard deviation = better balance = higher score
        
        Args:
            values: List of values to calculate balance for
            normalization_factor: Factor to convert std dev to 0-100 scale
            
        Returns:
            Dictionary with:
            - score: Balance score (0-100)
            - std_dev: Standard deviation of values
            - mean: Mean of values
            - min_value: Minimum value
            - max_value: Maximum value
            - range: Range (max - min)
        """
        if not values:
            return {
                'score': 100.0,
                'std_dev': 0.0,
                'mean': 0.0,
                'min_value': 0.0,
                'max_value': 0.0,
                'range': 0.0
            }
        
        # Calculate statistics
        values_array = np.array(values)
        std_dev = np.std(values_array)
        mean = np.mean(values_array)
        min_value = np.min(values_array)
        max_value = np.max(values_array)
        value_range = max_value - min_value
        
        # Calculate score: 100 - (std_dev * normalization_factor)
        # Perfect balance (std_dev = 0) gives score of 100
        # Higher std_dev gives lower score
        score = 100.0 - (std_dev * normalization_factor)
        
        # Ensure score is in valid range
        score = max(0.0, min(100.0, score))
        
        return {
            'score': score,
            'std_dev': std_dev,
            'mean': mean,
            'min_value': min_value,
            'max_value': max_value,
            'range': value_range
        }
    
    def calculate_academic_balance(self, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate academic score balance across classes.
        
        Measures how evenly academic scores are distributed across classes.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with balance score and statistics
        """
        if not school_data.classes:
            return {
                'score': 100.0,
                'std_dev': 0.0,
                'mean': 0.0,
                'min_value': 0.0,
                'max_value': 0.0,
                'range': 0.0,
                'class_values': {}
            }
        
        # Get average academic score for each class
        class_averages = []
        class_values = {}
        
        for class_id, class_data in school_data.classes.items():
            avg_score = class_data.average_academic_score
            class_averages.append(avg_score)
            class_values[class_id] = avg_score
        
        # Calculate balance score
        balance_result = self.calculate_balance_score(
            class_averages, 
            self.config.normalization.academic_score_factor
        )
        
        # Add class-specific values
        balance_result['class_values'] = class_values
        
        return balance_result
    
    def calculate_behavior_balance(self, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate behavior rank balance across classes.
        
        Measures how evenly behavior ranks are distributed across classes.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with balance score and statistics
        """
        if not school_data.classes:
            return {
                'score': 100.0,
                'std_dev': 0.0,
                'mean': 0.0,
                'min_value': 0.0,
                'max_value': 0.0,
                'range': 0.0,
                'class_values': {}
            }
        
        # Get average behavior rank for each class
        class_averages = []
        class_values = {}
        
        for class_id, class_data in school_data.classes.items():
            avg_rank = class_data.average_behavior_rank
            class_averages.append(avg_rank)
            class_values[class_id] = avg_rank
        
        # Calculate balance score
        balance_result = self.calculate_balance_score(
            class_averages, 
            self.config.normalization.behavior_rank_factor
        )
        
        # Add class-specific values
        balance_result['class_values'] = class_values
        
        return balance_result
    
    def calculate_studentiality_balance(self, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate studentiality rank balance across classes.
        
        Measures how evenly studentiality ranks are distributed across classes.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with balance score and statistics
        """
        if not school_data.classes:
            return {
                'score': 100.0,
                'std_dev': 0.0,
                'mean': 0.0,
                'min_value': 0.0,
                'max_value': 0.0,
                'range': 0.0,
                'class_values': {}
            }
        
        # Get average studentiality rank for each class
        class_averages = []
        class_values = {}
        
        for class_id, class_data in school_data.classes.items():
            avg_rank = class_data.average_studentiality_rank
            class_averages.append(avg_rank)
            class_values[class_id] = avg_rank
        
        # Calculate balance score
        balance_result = self.calculate_balance_score(
            class_averages, 
            self.config.normalization.studentiality_rank_factor
        )
        
        # Add class-specific values
        balance_result['class_values'] = class_values
        
        return balance_result
    
    def calculate_size_balance(self, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate class size balance across classes.
        
        Measures how evenly students are distributed across classes.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with balance score and statistics
        """
        if not school_data.classes:
            return {
                'score': 100.0,
                'std_dev': 0.0,
                'mean': 0.0,
                'min_value': 0.0,
                'max_value': 0.0,
                'range': 0.0,
                'class_values': {}
            }
        
        # Get size for each class
        class_sizes = []
        class_values = {}
        
        for class_id, class_data in school_data.classes.items():
            size = class_data.size
            class_sizes.append(size)
            class_values[class_id] = size
        
        # Calculate balance score
        balance_result = self.calculate_balance_score(
            class_sizes, 
            self.config.normalization.class_size_factor
        )
        
        # Add class-specific values
        balance_result['class_values'] = class_values
        
        return balance_result
    
    def calculate_assistance_balance(self, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate assistance package balance across classes.
        
        Measures how evenly assistance packages are distributed across classes.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with balance score and statistics
        """
        if not school_data.classes:
            return {
                'score': 100.0,
                'std_dev': 0.0,
                'mean': 0.0,
                'min_value': 0.0,
                'max_value': 0.0,
                'range': 0.0,
                'class_values': {}
            }
        
        # Get assistance count for each class
        class_assistance = []
        class_values = {}
        
        for class_id, class_data in school_data.classes.items():
            assistance_count = class_data.assistance_count
            class_assistance.append(assistance_count)
            class_values[class_id] = assistance_count
        
        # Calculate balance score
        balance_result = self.calculate_balance_score(
            class_assistance, 
            self.config.normalization.assistance_count_factor
        )
        
        # Add class-specific values
        balance_result['class_values'] = class_values
        
        return balance_result
    
    def calculate_school_score(self, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate overall school balance score.
        
        Combines all balance metrics with configurable weights.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with:
            - score: Overall school balance score (0-100)
            - academic_balance: Academic balance component
            - behavior_balance: Behavior balance component
            - studentiality_balance: Studentiality balance component
            - size_balance: Size balance component
            - assistance_balance: Assistance balance component
            - weighted_score: Detailed breakdown
        """
        # Calculate component scores
        academic_result = self.calculate_academic_balance(school_data)
        behavior_result = self.calculate_behavior_balance(school_data)
        studentiality_result = self.calculate_studentiality_balance(school_data)
        size_result = self.calculate_size_balance(school_data)
        assistance_result = self.calculate_assistance_balance(school_data)
        
        # Get weights from configuration
        w_academic = self.config.weights.academic_balance
        w_behavior = self.config.weights.behavior_balance
        w_studentiality = self.config.weights.studentiality_balance
        w_size = self.config.weights.size_balance
        w_assistance = self.config.weights.assistance_balance
        
        # Calculate weighted score
        academic_score = academic_result['score']
        behavior_score = behavior_result['score']
        studentiality_score = studentiality_result['score']
        size_score = size_result['score']
        assistance_score = assistance_result['score']
        
        # Weighted combination
        total_weight = w_academic + w_behavior + w_studentiality + w_size + w_assistance
        if total_weight == 0:
            # Avoid division by zero
            overall_score = 0.0
        else:
            overall_score = (
                academic_score * w_academic +
                behavior_score * w_behavior +
                studentiality_score * w_studentiality +
                size_score * w_size +
                assistance_score * w_assistance
            ) / total_weight
        
        return {
            'score': overall_score,
            'academic_balance': academic_result,
            'behavior_balance': behavior_result,
            'studentiality_balance': studentiality_result,
            'size_balance': size_result,
            'assistance_balance': assistance_result,
            'weighted_score': {
                'academic_component': academic_score * w_academic / total_weight if total_weight > 0 else 0,
                'behavior_component': behavior_score * w_behavior / total_weight if total_weight > 0 else 0,
                'studentiality_component': studentiality_score * w_studentiality / total_weight if total_weight > 0 else 0,
                'size_component': size_score * w_size / total_weight if total_weight > 0 else 0,
                'assistance_component': assistance_score * w_assistance / total_weight if total_weight > 0 else 0,
                'weights_used': {
                    'academic_balance': w_academic,
                    'behavior_balance': w_behavior,
                    'studentiality_balance': w_studentiality,
                    'size_balance': w_size,
                    'assistance_balance': w_assistance
                }
            }
        }
    
    def get_school_summary(self, school_data: SchoolData) -> Dict[str, float]:
        """
        Get a comprehensive summary of school-level metrics.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with school-wide statistics and balance scores
        """
        school_score = self.calculate_school_score(school_data)
        
        # Calculate overall school statistics
        all_students = list(school_data.students.values())
        total_students = len(all_students)
        
        if total_students == 0:
            return {
                'total_students': 0,
                'total_classes': 0,
                'school_score': 0.0,
                'academic_balance_score': 0.0,
                'behavior_balance_score': 0.0,
                'studentiality_balance_score': 0.0,
                'size_balance_score': 0.0,
                'assistance_balance_score': 0.0
            }
        
        # Calculate school-wide averages
        avg_academic = sum(s.academic_score for s in all_students) / total_students
        avg_behavior = sum(s.get_numeric_behavior_rank() for s in all_students) / total_students
        avg_studentiality = sum(s.get_numeric_studentiality_rank() for s in all_students) / total_students
        total_assistance = sum(1 for s in all_students if s.assistance_package)
        
        return {
            'total_students': total_students,
            'total_classes': len(school_data.classes),
            'school_score': school_score['score'],
            'academic_balance_score': school_score['academic_balance']['score'],
            'behavior_balance_score': school_score['behavior_balance']['score'],
            'studentiality_balance_score': school_score['studentiality_balance']['score'],
            'size_balance_score': school_score['size_balance']['score'],
            'assistance_balance_score': school_score['assistance_balance']['score'],
            'school_average_academic': avg_academic,
            'school_average_behavior': avg_behavior,
            'school_average_studentiality': avg_studentiality,
            'total_assistance_students': total_assistance,
            'assistance_percentage': (total_assistance / total_students * 100) if total_students > 0 else 0,
            'average_class_size': total_students / len(school_data.classes) if school_data.classes else 0,
            'class_size_range': school_score['size_balance']['range'],
            'academic_range': school_score['academic_balance']['range'],
            'behavior_range': school_score['behavior_balance']['range'],
            'studentiality_range': school_score['studentiality_balance']['range'],
            'assistance_range': school_score['assistance_balance']['range']
        } 