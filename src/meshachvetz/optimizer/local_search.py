#!/usr/bin/env python3
"""
Greedy Local Search Optimizer for Meshachvetz - systematically searches for local improvements
by trying to move each student to each possible class.
"""

import logging
import copy
import random
from typing import Dict, List, Any, Optional, Tuple

from .base_optimizer import BaseOptimizer, OptimizationResult
from ..data.models import SchoolData, Student


class LocalSearchOptimizer(BaseOptimizer):
    """
    Greedy Local Search optimization algorithm.
    
    Systematically tries moving each student to each other class and accepts
    the best improvement found in each pass. Continues until no improvements
    are found or maximum iterations reached.
    """
    
    def __init__(self, scorer, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Local Search optimizer.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary with algorithm parameters
        """
        super().__init__(scorer, config)
        
        # Optimization parameters from config
        self.max_passes = config.get('max_passes', 10)
        self.min_improvement = config.get('min_improvement', 0.01)
        self.shuffle_students = config.get('shuffle_students', True)
        self.greedy_mode = config.get('greedy_mode', True)
        self.min_passes = config.get('min_passes', 2)
        self.min_improvement_threshold = config.get('min_improvement_threshold', 0.01)
        self.early_stop_threshold = config.get('early_stop_threshold', 100)
        self.accept_neutral_moves = config.get('accept_neutral_moves', False)
        
        self.logger = logging.getLogger(__name__)
    
    def get_algorithm_name(self) -> str:
        """Get the name of this optimization algorithm."""
        return "Greedy Local Search"
    
    def optimize(self, school_data: SchoolData, max_iterations: int = 1000) -> OptimizationResult:
        """
        Optimize using greedy local search algorithm.
        
        Args:
            school_data: Initial school data to optimize
            max_iterations: Maximum number of passes through all students
            
        Returns:
            OptimizationResult with optimized assignment and metrics
        """
        self.logger.info(f"Starting {self.get_algorithm_name()} optimization")
        self.logger.info(f"Parameters: max_passes={self.max_passes}, min_improvement={self.min_improvement}")
        
        # Initialize optimization tracking
        self.start_optimization(school_data)
        
        current_solution = copy.deepcopy(school_data)
        current_score = self.evaluate_solution(current_solution)
        best_solution = copy.deepcopy(current_solution)
        best_score = current_score
        
        no_improvement_count = 0
        total_moves_attempted = 0
        successful_moves = 0
        
        # Multi-pass local search
        for pass_num in range(self.max_passes):
            pass_start_score = current_score
            
            # Search within this pass
            for iteration in range(max_iterations // self.max_passes):
                total_iteration = pass_num * (max_iterations // self.max_passes) + iteration
                
                # Algorithm-specific metrics for enhanced logging
                additional_metrics = {
                    'pass_number': pass_num + 1,
                    'total_passes': self.max_passes,
                    'moves_attempted': total_moves_attempted,
                    'successful_moves': successful_moves,
                    'success_rate': (successful_moves / max(1, total_moves_attempted)) * 100,
                    'no_improvement_count': no_improvement_count
                }
                
                # Update progress with enhanced logging
                self.update_progress(current_solution, total_iteration + 1, additional_metrics)
                
                # Try to find a better solution
                improved = False
                
                # Get all students for random selection
                student_ids = list(current_solution.students.keys())
                random.shuffle(student_ids)
                
                # Try moves until we find improvement or exhaust attempts
                move_attempts = 0
                max_move_attempts = min(50, len(student_ids))
                
                while not improved and move_attempts < max_move_attempts:
                    student_id = student_ids[move_attempts % len(student_ids)]
                    student = current_solution.students[student_id]
                    
                    # Try moving this student to different classes
                    target_classes = list(current_solution.classes.keys())
                    random.shuffle(target_classes)
                    
                    for target_class in target_classes:
                        if target_class != student.class_id:
                            total_moves_attempted += 1
                            
                            # Check if move is valid
                            if self._can_move_student(student, target_class, current_solution):
                                # Make the move
                                candidate_solution = self._make_move(current_solution, student, target_class)
                                candidate_score = self.evaluate_solution(candidate_solution)
                                
                                # Accept improvement or neutral moves (if enabled)
                                if (candidate_score > current_score or 
                                    (self.accept_neutral_moves and candidate_score == current_score)):
                                    
                                    current_solution = candidate_solution
                                    current_score = candidate_score
                                    successful_moves += 1
                                    improved = True
                                    
                                    # Track best solution
                                    if current_score > best_score:
                                        best_solution = copy.deepcopy(current_solution)
                                        best_score = current_score
                                        no_improvement_count = 0
                                        
                                        self.iteration_logger.log_debug(f"New best score: {best_score:.2f} "
                                                                       f"(move: {student_id} -> {target_class})")
                                    
                                    break
                    
                    move_attempts += 1
                
                # Track stagnation
                if not improved:
                    no_improvement_count += 1
                
                # Early termination check
                if not self.should_continue(total_iteration + 1, max_iterations, no_improvement_count):
                    self.iteration_logger.log_info(f"Early termination at iteration {total_iteration + 1}")
                    break
            
            # Pass completion check
            pass_improvement = current_score - pass_start_score
            if pass_improvement < self.min_improvement_threshold:
                self.iteration_logger.log_info(f"Pass {pass_num + 1} completed with minimal improvement "
                                             f"({pass_improvement:.3f})")
                if pass_num >= self.min_passes - 1:  # Ensure minimum passes
                    break
            
            # Check if we should continue to next pass
            if no_improvement_count >= self.early_stop_threshold:
                self.iteration_logger.log_info(f"Early stopping after pass {pass_num + 1}")
                break
        
        # Finalize optimization with enhanced logging
        total_iterations = min(max_iterations, (pass_num + 1) * (max_iterations // self.max_passes))
        result = self.finish_optimization(best_solution, total_iterations)
        
        # Additional local search specific logging
        self.iteration_logger.log_info(f"Local Search completed after {total_iterations} iterations")
        self.iteration_logger.log_info(f"Total moves attempted: {total_moves_attempted}")
        self.iteration_logger.log_info(f"Successful moves: {successful_moves}")
        self.iteration_logger.log_info(f"Success rate: {(successful_moves / max(1, total_moves_attempted)) * 100:.1f}%")
        
        return result
    
    def _find_best_move(self, student: Student, school_data: SchoolData) -> Optional[Tuple[str, float]]:
        """
        Find the best class to move a student to.
        
        Args:
            student: Student to move
            school_data: Current school assignment
            
        Returns:
            Tuple of (target_class_id, score_improvement) or None if no improvement
        """
        current_class = student.class_id
        current_score = self.evaluate_solution(school_data)
        
        best_class = None
        best_improvement = 0
        
        for class_id in school_data.classes.keys():
            if class_id == current_class:
                continue
            
            # Check if move would violate force constraints
            if not self._can_move_student(student, class_id, school_data):
                continue
            
            # Try the move
            test_solution = copy.deepcopy(school_data)
            self._move_student(test_solution, test_solution.students[student.student_id], class_id)
            
            # Validate the solution
            is_valid, violations = self.is_valid_solution(test_solution)
            if not is_valid:
                continue
            
            # Calculate improvement
            new_score = self.evaluate_solution(test_solution)
            improvement = new_score - current_score
            
            if improvement > best_improvement:
                best_improvement = improvement
                best_class = class_id
        
        return (best_class, best_improvement) if best_class else None
    
    def _can_move_student(self, student: Student, target_class: str, school_data: SchoolData) -> bool:
        """
        Check if a student can be moved to a target class without violating constraints.
        
        Args:
            student: Student to move
            target_class: Target class ID
            school_data: Current school assignment
            
        Returns:
            True if move is allowed, False otherwise
        """
        # Force class constraint
        if (self.respect_force_constraints and 
            student.force_class and student.force_class.strip() and
            student.force_class.strip() != target_class):
            return False
        
        # Force friend constraint - check if student has force_friend group
        if (self.respect_force_constraints and 
            student.force_friend and student.force_friend.strip()):
            
            force_group = student.force_friend.strip()
            
            # Find all students in the same force group
            group_members = [s for s in school_data.students.values() 
                           if s.force_friend and s.force_friend.strip() == force_group]
            
            # All group members must be able to move together
            if len(group_members) > 1:
                # For now, don't move force friend groups in local search
                # This could be enhanced to move entire groups together
                return False
        
        return True
    
    def _move_student(self, school_data: SchoolData, student: Student, target_class: str) -> None:
        """
        Move a student from their current class to a target class.
        
        Args:
            school_data: School data to modify
            student: Student to move
            target_class: Target class ID
        """
        # Remove from current class
        current_class = student.class_id
        if current_class and current_class in school_data.classes:
            school_data.classes[current_class].students = [
                s for s in school_data.classes[current_class].students 
                if s.student_id != student.student_id
            ]
        
        # Add to target class
        student.class_id = target_class
        if target_class in school_data.classes:
            school_data.classes[target_class].students.append(student)
        
        # Update the student in the main students dict
        school_data.students[student.student_id] = student
    
    def _make_move(self, school_data: SchoolData, student: Student, target_class: str) -> SchoolData:
        """
        Create a copy of school data with a student moved to a target class.
        
        Args:
            school_data: Original school data
            student: Student to move
            target_class: Target class ID
            
        Returns:
            New SchoolData with the move applied
        """
        # Create a deep copy to avoid modifying the original
        candidate_solution = copy.deepcopy(school_data)
        
        # Get the student copy from the new solution
        student_copy = candidate_solution.students[student.student_id]
        
        # Move the student in the copy
        self._move_student(candidate_solution, student_copy, target_class)
        
        return candidate_solution
    
    def get_algorithm_parameters(self) -> Dict[str, Any]:
        """Get current algorithm parameters for reporting."""
        return {
            'max_passes': self.max_passes,
            'min_improvement': self.min_improvement,
            'shuffle_students': self.shuffle_students,
            'greedy_mode': self.greedy_mode,
            'min_friends_required': self.min_friends_required,
            'respect_force_constraints': self.respect_force_constraints
        } 