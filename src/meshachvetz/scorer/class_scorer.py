"""
Class scorer implementation for Meshachvetz - calculates intra-class balance scores
focusing on gender balance and class composition.
"""

from typing import Dict, List, Optional
import logging
from ..data.models import Student, ClassData, SchoolData
from ..utils.config import Config


class ClassScorer:
    """
    Calculates intra-class balance scores based on:
    - Gender Balance: How balanced the gender distribution is within each class
    
    Implements the Class Layer of the three-layer scoring system.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the ClassScorer.
        
        Args:
            config: Configuration object with scoring weights
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def calculate_gender_balance(self, class_data: ClassData) -> Dict[str, float]:
        """
        Calculate gender balance score for a class.
        
        Formula: 100 - (abs(male_ratio - female_ratio) * 100)
        Perfect balance (50/50) = 100, Complete imbalance (100/0) = 0
        
        Args:
            class_data: ClassData object
            
        Returns:
            Dictionary with:
            - score: Gender balance score (0-100)
            - male_count: Number of male students
            - female_count: Number of female students  
            - male_ratio: Ratio of male students (0-1)
            - female_ratio: Ratio of female students (0-1)
            - balance_difference: Absolute difference between ratios
        """
        if class_data.size == 0:
            # Empty class has perfect balance by default
            return {
                'score': 100.0,
                'male_count': 0,
                'female_count': 0,
                'male_ratio': 0.0,
                'female_ratio': 0.0,
                'balance_difference': 0.0
            }
        
        # Count students by gender
        male_count = class_data.male_count
        female_count = class_data.female_count
        total_students = class_data.size
        
        # Calculate ratios
        male_ratio = male_count / total_students
        female_ratio = female_count / total_students
        
        # Calculate balance difference
        balance_difference = abs(male_ratio - female_ratio)
        
        # Calculate score: 100 - (difference * 100)
        # Perfect balance (0.5/0.5) gives difference of 0, score of 100
        # Complete imbalance (1.0/0.0) gives difference of 1, score of 0
        score = 100.0 - (balance_difference * 100.0)
        
        return {
            'score': score,
            'male_count': male_count,
            'female_count': female_count,
            'male_ratio': male_ratio,
            'female_ratio': female_ratio,
            'balance_difference': balance_difference
        }
    
    def calculate_class_score(self, class_data: ClassData) -> Dict[str, float]:
        """
        Calculate overall class quality score.
        
        Currently only includes gender balance, but designed to be extensible
        for future metrics like academic distribution, behavior balance, etc.
        
        Args:
            class_data: ClassData object
            
        Returns:
            Dictionary with:
            - score: Overall class quality score (0-100)
            - gender_balance: Gender balance component
            - weighted_score: Detailed breakdown
        """
        # Calculate component scores
        gender_result = self.calculate_gender_balance(class_data)
        
        # Get weights from configuration
        w_gender = self.config.weights.gender_balance
        
        # Currently only gender balance, so the class score is just the gender balance score
        # weighted by the gender balance weight
        gender_score = gender_result['score']
        
        # For now, class score is just gender balance score
        # When we add more metrics, we'll need to combine them with weights
        overall_score = gender_score
        
        return {
            'score': overall_score,
            'gender_balance': gender_result,
            'weighted_score': {
                'gender_component': gender_score * w_gender,
                'weights_used': {
                    'gender_balance': w_gender
                }
            }
        }
    
    def calculate_all_class_scores(self, school_data: SchoolData) -> Dict[str, Dict[str, float]]:
        """
        Calculate scores for all classes in the school.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary mapping class_id to score results
        """
        results = {}
        
        for class_id, class_data in school_data.classes.items():
            try:
                results[class_id] = self.calculate_class_score(class_data)
            except Exception as e:
                self.logger.error(f"Error calculating score for class {class_id}: {e}")
                # Return zero score on error
                results[class_id] = {
                    'score': 0.0,
                    'gender_balance': {
                        'score': 0.0, 'male_count': 0, 'female_count': 0,
                        'male_ratio': 0.0, 'female_ratio': 0.0, 'balance_difference': 0.0
                    },
                    'weighted_score': {'gender_component': 0.0, 'weights_used': {'gender_balance': 0}}
                }
        
        return results
        
    def get_average_class_score(self, school_data: SchoolData) -> float:
        """
        Calculate average class quality score across all classes.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Average class quality score (0-100)
        """
        all_scores = self.calculate_all_class_scores(school_data)
        
        if not all_scores:
            return 0.0
            
        total_score = sum(result['score'] for result in all_scores.values())
        return total_score / len(all_scores)
    
    def get_class_summary(self, school_data: SchoolData) -> Dict[str, Dict[str, float]]:
        """
        Get a comprehensive summary of class-level metrics.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary with class summaries including demographics and scores
        """
        summary = {}
        
        for class_id, class_data in school_data.classes.items():
            class_score = self.calculate_class_score(class_data)
            
            summary[class_id] = {
                'class_id': class_id,
                'size': class_data.size,
                'score': class_score['score'],
                'gender_balance_score': class_score['gender_balance']['score'],
                'male_count': class_data.male_count,
                'female_count': class_data.female_count,
                'male_percentage': (class_data.male_count / class_data.size * 100) if class_data.size > 0 else 0,
                'female_percentage': (class_data.female_count / class_data.size * 100) if class_data.size > 0 else 0,
                'average_academic_score': class_data.average_academic_score,
                'average_behavior_rank': class_data.average_behavior_rank,
                'assistance_count': class_data.assistance_count,
                'assistance_percentage': (class_data.assistance_count / class_data.size * 100) if class_data.size > 0 else 0,
                'forced_students': class_data.forced_students_count,
                'forced_groups': class_data.forced_groups_count
            }
        
        return summary 