"""
Student scorer implementation for Meshachvetz - calculates individual student satisfaction
based on friend placement and conflict avoidance.
"""

from typing import Dict, List, Optional
import logging
from ..data.models import Student, SchoolData
from ..utils.config import Config


class StudentScorer:
    """
    Calculates individual student satisfaction scores based on:
    - Friend Satisfaction: How many preferred friends are in the same class
    - Conflict Avoidance: How many disliked peers are avoided
    
    Implements the Student Layer of the three-layer scoring system.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the StudentScorer.
        
        Args:
            config: Configuration object with scoring weights
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def calculate_friend_satisfaction(self, student: Student, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate friend satisfaction score for a student.
        
        Formula: (friends_placed / friends_requested) * 100
        
        Args:
            student: Student object
            school_data: Complete school data
            
        Returns:
            Dictionary with:
            - score: Friend satisfaction score (0-100)
            - friends_requested: Number of preferred friends requested
            - friends_placed: Number of preferred friends in same class
            - missing_friends: List of friend IDs not in same class
        """
        preferred_friends = student.get_preferred_friends()
        
        if not preferred_friends:
            # No friends requested, perfect satisfaction
            return {
                'score': 100.0,
                'friends_requested': 0,
                'friends_placed': 0,
                'missing_friends': []
            }
        
        # Find how many preferred friends are in the same class
        student_class = school_data.get_class_by_id(student.class_id)
        if not student_class:
            self.logger.warning(f"Student {student.student_id} has invalid class_id: {student.class_id}")
            return {
                'score': 0.0,
                'friends_requested': len(preferred_friends),
                'friends_placed': 0,
                'missing_friends': preferred_friends
            }
        
        # Get student IDs in the same class
        classmate_ids = {s.student_id for s in student_class.students}
        
        # Count how many preferred friends are in the same class
        friends_placed = 0
        missing_friends = []
        
        for friend_id in preferred_friends:
            if friend_id in classmate_ids:
                friends_placed += 1
            else:
                missing_friends.append(friend_id)
        
        # Calculate satisfaction score
        friends_requested = len(preferred_friends)
        score = (friends_placed / friends_requested) * 100.0
        
        return {
            'score': score,
            'friends_requested': friends_requested,
            'friends_placed': friends_placed,
            'missing_friends': missing_friends
        }
    
    def calculate_conflict_avoidance(self, student: Student, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate conflict avoidance score for a student.
        
        Formula: (dislikes_avoided / dislikes_total) * 100
        
        Args:
            student: Student object
            school_data: Complete school data
            
        Returns:
            Dictionary with:
            - score: Conflict avoidance score (0-100)
            - dislikes_total: Number of disliked peers
            - dislikes_avoided: Number of disliked peers not in same class
            - conflicts_present: List of disliked peer IDs in same class
        """
        disliked_peers = student.get_disliked_peers()
        
        if not disliked_peers:
            # No dislikes specified, perfect avoidance
            return {
                'score': 100.0,
                'dislikes_total': 0,
                'dislikes_avoided': 0,
                'conflicts_present': []
            }
        
        # Find how many disliked peers are in the same class
        student_class = school_data.get_class_by_id(student.class_id)
        if not student_class:
            self.logger.warning(f"Student {student.student_id} has invalid class_id: {student.class_id}")
            return {
                'score': 100.0,  # Assume best case if class not found
                'dislikes_total': len(disliked_peers),
                'dislikes_avoided': len(disliked_peers),
                'conflicts_present': []
            }
        
        # Get student IDs in the same class
        classmate_ids = {s.student_id for s in student_class.students}
        
        # Count how many disliked peers are in the same class (conflicts)
        conflicts_present = []
        for peer_id in disliked_peers:
            if peer_id in classmate_ids:
                conflicts_present.append(peer_id)
        
        # Calculate avoidance score
        dislikes_total = len(disliked_peers)
        dislikes_avoided = dislikes_total - len(conflicts_present)
        score = (dislikes_avoided / dislikes_total) * 100.0
        
        return {
            'score': score,
            'dislikes_total': dislikes_total,
            'dislikes_avoided': dislikes_avoided,
            'conflicts_present': conflicts_present
        }
    
    def calculate_student_score(self, student: Student, school_data: SchoolData) -> Dict[str, float]:
        """
        Calculate overall student satisfaction score.
        
        Combines friend satisfaction and conflict avoidance with configurable weights.
        
        Args:
            student: Student object
            school_data: Complete school data
            
        Returns:
            Dictionary with:
            - score: Overall student satisfaction score (0-100)
            - friend_satisfaction: Friend satisfaction component
            - conflict_avoidance: Conflict avoidance component
            - weighted_score: Detailed breakdown
        """
        # Calculate component scores
        friend_result = self.calculate_friend_satisfaction(student, school_data)
        conflict_result = self.calculate_conflict_avoidance(student, school_data)
        
        # Get weights from configuration
        w_friends = self.config.weights.friends
        w_dislikes = self.config.weights.dislikes
        
        # Calculate weighted score
        friend_score = friend_result['score']
        conflict_score = conflict_result['score']
        
        # Weighted combination
        total_weight = w_friends + w_dislikes
        if total_weight == 0:
            # Avoid division by zero
            overall_score = 0.0
        else:
            overall_score = (friend_score * w_friends + conflict_score * w_dislikes) / total_weight
        
        return {
            'score': overall_score,
            'friend_satisfaction': friend_result,
            'conflict_avoidance': conflict_result,
            'weighted_score': {
                'friend_component': friend_score * w_friends / total_weight if total_weight > 0 else 0,
                'conflict_component': conflict_score * w_dislikes / total_weight if total_weight > 0 else 0,
                'weights_used': {
                    'friends': w_friends,
                    'dislikes': w_dislikes
                }
            }
        }
    
    def calculate_all_student_scores(self, school_data: SchoolData) -> Dict[str, Dict[str, float]]:
        """
        Calculate scores for all students in the school.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Dictionary mapping student_id to score results
        """
        results = {}
        
        for student_id, student in school_data.students.items():
            try:
                results[student_id] = self.calculate_student_score(student, school_data)
            except Exception as e:
                self.logger.error(f"Error calculating score for student {student_id}: {e}")
                # Return zero score on error
                results[student_id] = {
                    'score': 0.0,
                    'friend_satisfaction': {'score': 0.0, 'friends_requested': 0, 'friends_placed': 0, 'missing_friends': []},
                    'conflict_avoidance': {'score': 0.0, 'dislikes_total': 0, 'dislikes_avoided': 0, 'conflicts_present': []},
                    'weighted_score': {'friend_component': 0.0, 'conflict_component': 0.0, 'weights_used': {'friends': 0, 'dislikes': 0}}
                }
        
        return results
        
    def get_average_student_score(self, school_data: SchoolData) -> float:
        """
        Calculate average student satisfaction score across all students.
        
        Args:
            school_data: Complete school data
            
        Returns:
            Average student satisfaction score (0-100)
        """
        all_scores = self.calculate_all_student_scores(school_data)
        
        if not all_scores:
            return 0.0
            
        total_score = sum(result['score'] for result in all_scores.values())
        return total_score / len(all_scores) 