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
        
        # Algorithm-specific parameters
        self.max_passes = self.config.get('max_passes', 10)
        self.min_improvement = self.config.get('min_improvement', 0.01)
        self.shuffle_students = self.config.get('shuffle_students', True)
        self.greedy_mode = self.config.get('greedy_mode', True)  # Take first improvement vs best improvement
        
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
        current_solution = copy.deepcopy(school_data)
        current_score = self.start_optimization(current_solution)
        
        # Limit iterations by max_passes parameter rather than max_iterations
        effective_max_iterations = min(max_iterations, self.max_passes)
        
        students_list = list(current_solution.students.values())
        total_improvements = 0
        passes_without_improvement = 0
        
        for pass_num in range(effective_max_iterations):
            self.logger.debug(f"Starting pass {pass_num + 1}/{effective_max_iterations}")
            
            # Shuffle students order for each pass to avoid bias
            if self.shuffle_students:
                random.shuffle(students_list)
            
            pass_improvements = 0
            best_pass_improvement = 0
            
            for student in students_list:
                # Skip students with force constraints
                if (self.respect_force_constraints and 
                    student.force_class and student.force_class.strip()):
                    continue
                
                # Try moving student to each other class
                best_move = self._find_best_move(student, current_solution)
                
                if best_move:
                    target_class, improvement = best_move
                    
                    if improvement >= self.min_improvement:
                        # Make the move
                        self._move_student(current_solution, student, target_class)
                        current_score += improvement
                        pass_improvements += 1
                        total_improvements += 1
                        best_pass_improvement = max(best_pass_improvement, improvement)
                        
                        self.logger.debug(f"Moved student {student.student_id} to {target_class}, "
                                        f"improvement: +{improvement:.3f}")
                        
                        # In greedy mode, take first improvement; otherwise continue to find best
                        if self.greedy_mode:
                            break
            
            # Update progress tracking
            self.update_progress(current_solution, pass_num + 1)
            
            self.logger.debug(f"Pass {pass_num + 1} complete: {pass_improvements} improvements, "
                            f"best: +{best_pass_improvement:.3f}")
            
            # Check for convergence
            if pass_improvements == 0:
                passes_without_improvement += 1
                if passes_without_improvement >= 2:  # Stop after 2 passes without improvement
                    self.logger.info(f"Converged after {pass_num + 1} passes")
                    break
            else:
                passes_without_improvement = 0
        
        # Finalize optimization
        result = self.finish_optimization(current_solution, pass_num + 1)
        
        self.logger.info(f"Local Search completed: {total_improvements} total improvements")
        self.logger.info(f"Score: {result.initial_score:.2f} → {result.final_score:.2f} "
                        f"(+{result.improvement:.2f})")
        
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