"""
Main scorer implementation for Meshachvetz - orchestrates the three-layer scoring system
and calculates the final weighted score.
"""

from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from ..data.models import SchoolData
from ..data.loader import DataLoader
from ..utils.config import Config
from .student_scorer import StudentScorer
from .class_scorer import ClassScorer
from .school_scorer import SchoolScorer


@dataclass
class ScoringResult:
    """
    Complete scoring result containing all layer scores and final score.
    """
    final_score: float
    student_layer_score: float
    class_layer_score: float
    school_layer_score: float
    student_scores: Dict[str, Dict[str, Any]]
    class_scores: Dict[str, Dict[str, Any]]
    school_scores: Dict[str, Any]
    layer_weights: Dict[str, float]
    total_students: int
    total_classes: int
    

class Scorer:
    """
    Main scorer that orchestrates the three-layer scoring system.
    
    Combines:
    - Student Layer: Individual satisfaction (friend placement, conflict avoidance)
    - Class Layer: Intra-class balance (gender balance)
    - School Layer: Inter-class balance (academic, behavior, size, assistance)
    
    Calculates final weighted score based on configurable layer weights.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the main scorer.
        
        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize layer scorers
        self.student_scorer = StudentScorer(self.config)
        self.class_scorer = ClassScorer(self.config)
        self.school_scorer = SchoolScorer(self.config)
        
        # Initialize data loader
        self.data_loader = DataLoader(validate_data=True)
        
    def load_data(self, csv_file: str) -> SchoolData:
        """
        Load and validate student data from CSV file.
        
        Args:
            csv_file: Path to CSV file containing student data
            
        Returns:
            SchoolData object with loaded and validated data
        """
        self.logger.info(f"Loading data from {csv_file}")
        school_data = self.data_loader.load_csv(csv_file)
        
        # Log basic statistics
        self.logger.info(f"Loaded {school_data.total_students} students in {school_data.total_classes} classes")
        
        # Validate force constraints
        constraint_errors = school_data.validate_force_constraints()
        if constraint_errors:
            self.logger.warning(f"Force constraint validation found {len(constraint_errors)} issues:")
            for error in constraint_errors:
                self.logger.warning(f"  - {error}")
        
        return school_data
    
    def calculate_scores(self, school_data: SchoolData) -> ScoringResult:
        """
        Calculate all scores for the school assignment.
        
        Args:
            school_data: Complete school data
            
        Returns:
            ScoringResult with all layer scores and final score
        """
        self.logger.info("Calculating scores for all layers")
        
        # Calculate scores for each layer
        student_scores = self.student_scorer.calculate_all_student_scores(school_data)
        class_scores = self.class_scorer.calculate_all_class_scores(school_data)
        school_scores = self.school_scorer.calculate_school_score(school_data)
        
        # Calculate average scores for each layer
        student_layer_score = self.student_scorer.get_average_student_score(school_data)
        class_layer_score = self.class_scorer.get_average_class_score(school_data)
        school_layer_score = school_scores['score']
        
        # Calculate final weighted score
        final_score = self._calculate_final_score(
            student_layer_score, 
            class_layer_score, 
            school_layer_score
        )
        
        # Get layer weights
        layer_weights = {
            'student': self.config.weights.student_layer,
            'class': self.config.weights.class_layer,
            'school': self.config.weights.school_layer
        }
        
        self.logger.info(f"Final score: {final_score:.2f}")
        self.logger.info(f"  Student layer: {student_layer_score:.2f} (weight: {layer_weights['student']})")
        self.logger.info(f"  Class layer: {class_layer_score:.2f} (weight: {layer_weights['class']})")
        self.logger.info(f"  School layer: {school_layer_score:.2f} (weight: {layer_weights['school']})")
        
        return ScoringResult(
            final_score=final_score,
            student_layer_score=student_layer_score,
            class_layer_score=class_layer_score,
            school_layer_score=school_layer_score,
            student_scores=student_scores,
            class_scores=class_scores,
            school_scores=school_scores,
            layer_weights=layer_weights,
            total_students=school_data.total_students,
            total_classes=school_data.total_classes
        )
    
    def _calculate_final_score(self, student_score: float, class_score: float, school_score: float) -> float:
        """
        Calculate final weighted score from layer scores.
        
        Args:
            student_score: Average student satisfaction score
            class_score: Average class balance score
            school_score: School balance score
            
        Returns:
            Final weighted score (0-100)
        """
        # Get layer weights
        w_student = self.config.weights.student_layer
        w_class = self.config.weights.class_layer
        w_school = self.config.weights.school_layer
        
        # Calculate weighted combination
        total_weight = w_student + w_class + w_school
        if total_weight == 0:
            self.logger.warning("All layer weights are zero, returning 0 score")
            return 0.0
        
        final_score = (
            student_score * w_student +
            class_score * w_class +
            school_score * w_school
        ) / total_weight
        
        return final_score
    
    def score_csv_file(self, csv_file: str) -> ScoringResult:
        """
        Convenience method to load CSV and calculate scores in one call.
        
        Args:
            csv_file: Path to CSV file containing student data
            
        Returns:
            ScoringResult with all layer scores and final score
        """
        school_data = self.load_data(csv_file)
        return self.calculate_scores(school_data)
    
    def get_detailed_report(self, result: ScoringResult) -> str:
        """
        Generate a detailed text report of the scoring results.
        
        Args:
            result: ScoringResult object
            
        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 60)
        report.append("MESHACHVETZ SCORING REPORT")
        report.append("=" * 60)
        
        # Overview section
        report.append(f"\n📊 OVERVIEW")
        report.append(f"Total Students: {result.total_students}")
        report.append(f"Total Classes: {result.total_classes}")
        report.append(f"Final Score: {result.final_score:.2f}/100")
        
        # Layer scores section
        report.append(f"\n🏆 LAYER SCORES")
        report.append(f"Student Layer: {result.student_layer_score:.2f}/100 (weight: {result.layer_weights['student']})")
        report.append(f"Class Layer:   {result.class_layer_score:.2f}/100 (weight: {result.layer_weights['class']})")
        report.append(f"School Layer:  {result.school_layer_score:.2f}/100 (weight: {result.layer_weights['school']})")
        
        # Student satisfaction details
        report.append(f"\n👥 STUDENT SATISFACTION DETAILS")
        satisfied_count = sum(1 for s in result.student_scores.values() if s['score'] >= 75)
        report.append(f"Highly Satisfied Students (≥75): {satisfied_count}/{result.total_students} ({satisfied_count/result.total_students*100:.1f}%)")
        
        low_satisfaction = sum(1 for s in result.student_scores.values() if s['score'] < 50)
        report.append(f"Low Satisfaction Students (<50): {low_satisfaction}/{result.total_students} ({low_satisfaction/result.total_students*100:.1f}%)")
        
        # Class balance details
        report.append(f"\n🏫 CLASS BALANCE DETAILS")
        for class_id, class_result in result.class_scores.items():
            gender_balance = class_result['gender_balance']
            report.append(f"Class {class_id}: {class_result['score']:.1f}/100 "
                         f"(M:{gender_balance['male_count']}/F:{gender_balance['female_count']}, "
                         f"Balance: {gender_balance['score']:.1f})")
        
        # School balance details
        report.append(f"\n🏛️  SCHOOL BALANCE DETAILS")
        school_scores = result.school_scores
        report.append(f"Academic Balance: {school_scores['academic_balance']['score']:.1f}/100 "
                     f"(σ={school_scores['academic_balance']['std_dev']:.2f})")
        report.append(f"Behavior Balance: {school_scores['behavior_balance']['score']:.1f}/100 "
                     f"(σ={school_scores['behavior_balance']['std_dev']:.2f})")
        report.append(f"Size Balance: {school_scores['size_balance']['score']:.1f}/100 "
                     f"(σ={school_scores['size_balance']['std_dev']:.2f})")
        report.append(f"Assistance Balance: {school_scores['assistance_balance']['score']:.1f}/100 "
                     f"(σ={school_scores['assistance_balance']['std_dev']:.2f})")
        
        return "\n".join(report)
    
    def get_student_satisfaction_summary(self, result: ScoringResult) -> Dict[str, Any]:
        """
        Get a summary of student satisfaction statistics.
        
        Args:
            result: ScoringResult object
            
        Returns:
            Dictionary with satisfaction statistics
        """
        scores = [s['score'] for s in result.student_scores.values()]
        friend_satisfaction = [s['friend_satisfaction']['score'] for s in result.student_scores.values()]
        conflict_avoidance = [s['conflict_avoidance']['score'] for s in result.student_scores.values()]
        
        return {
            'total_students': len(scores),
            'average_satisfaction': sum(scores) / len(scores) if scores else 0,
            'average_friend_satisfaction': sum(friend_satisfaction) / len(friend_satisfaction) if friend_satisfaction else 0,
            'average_conflict_avoidance': sum(conflict_avoidance) / len(conflict_avoidance) if conflict_avoidance else 0,
            'highly_satisfied_count': sum(1 for s in scores if s >= 75),
            'moderately_satisfied_count': sum(1 for s in scores if 50 <= s < 75),
            'low_satisfaction_count': sum(1 for s in scores if s < 50),
            'perfect_satisfaction_count': sum(1 for s in scores if s >= 95),
            'students_with_friends_placed': sum(1 for s in result.student_scores.values() 
                                              if s['friend_satisfaction']['friends_placed'] > 0),
            'students_with_conflicts': sum(1 for s in result.student_scores.values() 
                                         if len(s['conflict_avoidance']['conflicts_present']) > 0),
            'total_friend_requests': sum(s['friend_satisfaction']['friends_requested'] 
                                       for s in result.student_scores.values()),
            'total_friends_placed': sum(s['friend_satisfaction']['friends_placed'] 
                                      for s in result.student_scores.values())
        } 