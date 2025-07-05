"""
Main scorer implementation for Meshachvetz - orchestrates the three-layer scoring system
and calculates the final weighted score.
"""

from typing import Dict, List, Optional, Any
import logging
import os
import csv
from datetime import datetime
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
    school_data: Optional[SchoolData] = None  # Add reference to original school data
    

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
            total_classes=school_data.total_classes,
            school_data=school_data  # Store reference to school data
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

    def generate_csv_reports(self, result: ScoringResult, output_dir: str = None) -> str:
        """
        Generate comprehensive CSV reports for the scoring results.
        
        Args:
            result: ScoringResult object containing all scoring data
            output_dir: Directory to save reports. If None, creates timestamp-based directory
            
        Returns:
            Path to the output directory containing all reports
        """
        # Create output directory with timestamp if not provided
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = f"results_{timestamp}"
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"Generating CSV reports in directory: {output_dir}")
        
        # Generate individual reports
        self._generate_summary_report(result, output_dir)
        self._generate_student_report(result, output_dir)
        self._generate_class_report(result, output_dir)
        self._generate_school_report(result, output_dir)
        
        # Generate configuration report
        self._generate_config_report(output_dir)
        
        self.logger.info(f"CSV reports generated successfully in: {output_dir}")
        return output_dir
    
    def _generate_summary_report(self, result: ScoringResult, output_dir: str) -> None:
        """Generate overall summary report."""
        summary_file = os.path.join(output_dir, "summary_report.csv")
        
        satisfaction_summary = self.get_student_satisfaction_summary(result)
        
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(["Meshachvetz Scoring Summary Report"])
            writer.writerow(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            
            # Overall metrics
            writer.writerow(["Overall Metrics"])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Final Score", f"{result.final_score:.2f}/100"])
            writer.writerow(["Total Students", result.total_students])
            writer.writerow(["Total Classes", result.total_classes])
            writer.writerow([])
            
            # Layer scores
            writer.writerow(["Layer Scores"])
            writer.writerow(["Layer", "Score", "Weight", "Weighted Contribution"])
            writer.writerow(["Student Layer", f"{result.student_layer_score:.2f}/100", 
                           result.layer_weights['student'], 
                           f"{result.student_layer_score * result.layer_weights['student']:.2f}"])
            writer.writerow(["Class Layer", f"{result.class_layer_score:.2f}/100", 
                           result.layer_weights['class'],
                           f"{result.class_layer_score * result.layer_weights['class']:.2f}"])
            writer.writerow(["School Layer", f"{result.school_layer_score:.2f}/100", 
                           result.layer_weights['school'],
                           f"{result.school_layer_score * result.layer_weights['school']:.2f}"])
            writer.writerow([])
            
            # Student satisfaction statistics
            writer.writerow(["Student Satisfaction Statistics"])
            writer.writerow(["Metric", "Count", "Percentage"])
            writer.writerow(["Highly Satisfied (≥75)", satisfaction_summary['highly_satisfied_count'],
                           f"{satisfaction_summary['highly_satisfied_count']/result.total_students*100:.1f}%"])
            writer.writerow(["Moderately Satisfied (50-74)", satisfaction_summary['moderately_satisfied_count'],
                           f"{satisfaction_summary['moderately_satisfied_count']/result.total_students*100:.1f}%"])
            writer.writerow(["Low Satisfaction (<50)", satisfaction_summary['low_satisfaction_count'],
                           f"{satisfaction_summary['low_satisfaction_count']/result.total_students*100:.1f}%"])
            writer.writerow(["Perfect Satisfaction (≥95)", satisfaction_summary['perfect_satisfaction_count'],
                           f"{satisfaction_summary['perfect_satisfaction_count']/result.total_students*100:.1f}%"])
            writer.writerow([])
            
            # Social metrics
            writer.writerow(["Social Metrics"])
            writer.writerow(["Metric", "Count", "Percentage"])
            writer.writerow(["Students with Friends Placed", satisfaction_summary['students_with_friends_placed'],
                           f"{satisfaction_summary['students_with_friends_placed']/result.total_students*100:.1f}%"])
            writer.writerow(["Students with Conflicts", satisfaction_summary['students_with_conflicts'],
                           f"{satisfaction_summary['students_with_conflicts']/result.total_students*100:.1f}%"])
            writer.writerow(["Total Friend Requests", satisfaction_summary['total_friend_requests'], ""])
            writer.writerow(["Total Friends Placed", satisfaction_summary['total_friends_placed'], ""])
            writer.writerow(["Friend Placement Rate", "",
                           f"{satisfaction_summary['total_friends_placed']/satisfaction_summary['total_friend_requests']*100:.1f}%" 
                           if satisfaction_summary['total_friend_requests'] > 0 else "N/A"])
    
    def _generate_student_report(self, result: ScoringResult, output_dir: str) -> None:
        """Generate detailed student-by-student report."""
        student_file = os.path.join(output_dir, "student_details.csv")
        
        with open(student_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(["Student ID", "Overall Score", "Friend Satisfaction", "Conflict Avoidance",
                           "Friends Requested", "Friends Placed", "Missing Friends", 
                           "Dislikes Total", "Conflicts Present", "Class ID", "First Name", "Last Name", 
                           "Gender", "Academic Score", "Behavior Rank", "Assistance Package"])
            
            # Student data
            for student_id, student_result in result.student_scores.items():
                friend_sat = student_result['friend_satisfaction']
                conflict_av = student_result['conflict_avoidance']
                
                # Get student information from school data
                student_class = "Unknown"
                first_name = "Unknown"
                last_name = "Unknown"
                gender = "Unknown"
                academic_score = "Unknown"
                behavior_rank = "Unknown"
                assistance_package = "Unknown"
                
                if result.school_data:
                    try:
                        student = result.school_data.get_student_by_id(student_id)
                        student_class = student.class_id
                        first_name = student.first_name
                        last_name = student.last_name
                        gender = student.gender
                        academic_score = student.academic_score
                        behavior_rank = student.behavior_rank
                        assistance_package = "Yes" if student.assistance_package else "No"
                    except:
                        pass
                
                writer.writerow([
                    student_id,
                    f"{student_result['score']:.2f}",
                    f"{friend_sat['score']:.2f}",
                    f"{conflict_av['score']:.2f}",
                    friend_sat['friends_requested'],
                    friend_sat['friends_placed'],
                    "|".join(friend_sat['missing_friends']),
                    conflict_av['dislikes_total'],
                    "|".join(conflict_av['conflicts_present']),
                    student_class,
                    first_name,
                    last_name,
                    gender,
                    academic_score,
                    behavior_rank,
                    assistance_package
                ])
    
    def _generate_class_report(self, result: ScoringResult, output_dir: str) -> None:
        """Generate detailed class-by-class report."""
        class_file = os.path.join(output_dir, "class_details.csv")
        
        with open(class_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(["Class ID", "Overall Score", "Gender Balance Score", "Male Count", "Female Count",
                           "Male Percentage", "Female Percentage", "Balance Difference"])
            
            # Class data
            for class_id, class_result in result.class_scores.items():
                gender_balance = class_result['gender_balance']
                total_students = gender_balance['male_count'] + gender_balance['female_count']
                
                male_percentage = (gender_balance['male_count'] / total_students * 100) if total_students > 0 else 0
                female_percentage = (gender_balance['female_count'] / total_students * 100) if total_students > 0 else 0
                
                writer.writerow([
                    class_id,
                    f"{class_result['score']:.2f}",
                    f"{gender_balance['score']:.2f}",
                    gender_balance['male_count'],
                    gender_balance['female_count'],
                    f"{male_percentage:.1f}%",
                    f"{female_percentage:.1f}%",
                    f"{gender_balance['balance_difference']:.3f}"
                ])
    
    def _generate_school_report(self, result: ScoringResult, output_dir: str) -> None:
        """Generate detailed school-level balance report."""
        school_file = os.path.join(output_dir, "school_balance.csv")
        
        school_scores = result.school_scores
        
        with open(school_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(["Balance Metric", "Score", "Standard Deviation", "Mean", "Min Value", "Max Value", "Range"])
            
            # Balance metrics
            metrics = [
                ("Academic Balance", school_scores['academic_balance']),
                ("Behavior Balance", school_scores['behavior_balance']),
                ("Size Balance", school_scores['size_balance']),
                ("Assistance Balance", school_scores['assistance_balance'])
            ]
            
            for name, metric_data in metrics:
                writer.writerow([
                    name,
                    f"{metric_data['score']:.2f}",
                    f"{metric_data['std_dev']:.3f}",
                    f"{metric_data['mean']:.2f}",
                    f"{metric_data['min_value']:.2f}",
                    f"{metric_data['max_value']:.2f}",
                    f"{metric_data['range']:.2f}"
                ])
            
            # Add class-specific values
            writer.writerow([])
            writer.writerow(["Class-Specific Values"])
            writer.writerow(["Class ID", "Academic Average", "Behavior Average", "Size", "Assistance Count"])
            
            for class_id in school_scores['academic_balance']['class_values'].keys():
                writer.writerow([
                    class_id,
                    f"{school_scores['academic_balance']['class_values'][class_id]:.2f}",
                    f"{school_scores['behavior_balance']['class_values'][class_id]:.2f}",
                    school_scores['size_balance']['class_values'][class_id],
                    school_scores['assistance_balance']['class_values'][class_id]
                ])
    
    def _generate_config_report(self, output_dir: str) -> None:
        """Generate configuration report showing all weights and parameters used."""
        config_file = os.path.join(output_dir, "configuration.csv")
        
        with open(config_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(["Configuration Used for Scoring"])
            writer.writerow(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            
            # Layer weights
            writer.writerow(["Layer Weights"])
            writer.writerow(["Layer", "Weight"])
            writer.writerow(["Student Layer", self.config.weights.student_layer])
            writer.writerow(["Class Layer", self.config.weights.class_layer])
            writer.writerow(["School Layer", self.config.weights.school_layer])
            writer.writerow([])
            
            # Student layer weights
            writer.writerow(["Student Layer Weights"])
            writer.writerow(["Metric", "Weight"])
            writer.writerow(["Friends", self.config.weights.friends])
            writer.writerow(["Dislikes", self.config.weights.dislikes])
            writer.writerow([])
            
            # School layer weights
            writer.writerow(["School Layer Weights"])
            writer.writerow(["Metric", "Weight"])
            writer.writerow(["Academic Balance", self.config.weights.academic_balance])
            writer.writerow(["Behavior Balance", self.config.weights.behavior_balance])
            writer.writerow(["Size Balance", self.config.weights.size_balance])
            writer.writerow(["Assistance Balance", self.config.weights.assistance_balance])
            writer.writerow([])
            
            # Normalization factors
            writer.writerow(["Normalization Factors"])
            writer.writerow(["Factor", "Value"])
            writer.writerow(["Academic Score Factor", self.config.normalization.academic_score_factor])
            writer.writerow(["Behavior Rank Factor", self.config.normalization.behavior_rank_factor])
            writer.writerow(["Class Size Factor", self.config.normalization.class_size_factor])
            writer.writerow(["Assistance Count Factor", self.config.normalization.assistance_count_factor])

    def score_csv_file_with_reports(self, csv_file: str, output_dir: str = None) -> tuple[ScoringResult, str]:
        """
        Convenience method to score CSV file and generate reports in one call.
        
        Args:
            csv_file: Path to CSV file containing student data
            output_dir: Directory to save reports. If None, creates timestamp-based directory
            
        Returns:
            Tuple of (ScoringResult, output_directory_path)
        """
        # Score the file
        result = self.score_csv_file(csv_file)
        
        # Generate reports
        output_path = self.generate_csv_reports(result, output_dir)
        
        return result, output_path 