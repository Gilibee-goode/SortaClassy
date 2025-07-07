#!/usr/bin/env python3
"""
Simulated Annealing Optimizer for Meshachvetz - accepts worse solutions with decreasing
probability over time to escape local optima and find global optimum.
"""

import logging
import copy
import random
import math
from typing import Dict, List, Any, Optional, Callable

from .base_optimizer import BaseOptimizer, OptimizationResult
from ..data.models import SchoolData, Student


class SimulatedAnnealingOptimizer(BaseOptimizer):
    """
    Simulated Annealing optimization algorithm.
    
    Uses a temperature-based acceptance probability to accept worse solutions
    early in the optimization process, gradually becoming more selective as
    the temperature cools down.
    """
    
    def __init__(self, scorer, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Simulated Annealing optimizer.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary with algorithm parameters
        """
        super().__init__(scorer, config)
        
        # Algorithm-specific parameters
        self.initial_temperature = self.config.get('initial_temperature', 100.0)
        self.min_temperature = self.config.get('min_temperature', 0.01)
        self.cooling_rate = self.config.get('cooling_rate', 0.95)
        self.cooling_schedule = self.config.get('cooling_schedule', 'exponential')
        self.iterations_per_temperature = self.config.get('iterations_per_temperature', 50)
        
        # Movement parameters
        self.swap_probability = self.config.get('swap_probability', 0.7)  # vs single move
        self.max_group_size = self.config.get('max_group_size', 3)  # For group moves
        
        self.logger = logging.getLogger(__name__)
        
        # Cooling schedule functions
        self.cooling_functions = {
            'linear': self._linear_cooling,
            'exponential': self._exponential_cooling,
            'logarithmic': self._logarithmic_cooling,
            'adaptive': self._adaptive_cooling
        }
    
    def get_algorithm_name(self) -> str:
        """Get the name of this optimization algorithm."""
        return "Simulated Annealing"
    
    def optimize(self, school_data: SchoolData, max_iterations: int = 1000) -> OptimizationResult:
        """
        Optimize using simulated annealing algorithm.
        
        Args:
            school_data: Initial school data to optimize
            max_iterations: Maximum number of optimization iterations
            
        Returns:
            OptimizationResult with optimized assignment and metrics
        """
        self.logger.info(f"Starting {self.get_algorithm_name()} optimization")
        self.logger.info(f"Parameters: initial_temp={self.initial_temperature}, "
                        f"min_temp={self.min_temperature}, cooling_rate={self.cooling_rate}")
        
        # Initialize optimization tracking
        current_solution = copy.deepcopy(school_data)
        current_score = self.start_optimization(current_solution)
        
        # Keep track of best solution found
        best_solution = copy.deepcopy(current_solution)
        best_score = current_score
        
        # Temperature and iteration tracking
        temperature = self.initial_temperature
        temperature_iteration = 0
        accepted_moves = 0
        rejected_moves = 0
        
        cooling_function = self.cooling_functions.get(
            self.cooling_schedule, self._exponential_cooling
        )
        
        for iteration in range(max_iterations):
            # Check if we should cool down
            if temperature_iteration >= self.iterations_per_temperature:
                temperature = cooling_function(temperature, iteration, max_iterations)
                temperature_iteration = 0
                
                self.logger.debug(f"Temperature cooled to {temperature:.4f} at iteration {iteration}")
                
                # Stop if temperature is too low
                if temperature < self.min_temperature:
                    self.logger.info(f"Minimum temperature reached at iteration {iteration}")
                    break
            
            # Generate a neighbor solution
            neighbor_solution = self._generate_neighbor(current_solution)
            
            # Validate the neighbor solution
            is_valid, violations = self.is_valid_solution(neighbor_solution)
            if not is_valid:
                rejected_moves += 1
                temperature_iteration += 1
                continue
            
            # Evaluate the neighbor
            neighbor_score = self.evaluate_solution(neighbor_solution)
            
            # Calculate score difference
            delta_score = neighbor_score - current_score
            
            # Decide whether to accept the move
            if self._accept_move(delta_score, temperature):
                current_solution = neighbor_solution
                current_score = neighbor_score
                accepted_moves += 1
                
                # Update best solution if this is better
                if current_score > best_score:
                    best_solution = copy.deepcopy(current_solution)
                    best_score = current_score
                    
                    self.logger.debug(f"New best score: {best_score:.3f} at iteration {iteration}")
                
                self.logger.debug(f"Accepted move: Δ={delta_score:.3f}, T={temperature:.3f}")
            else:
                rejected_moves += 1
                self.logger.debug(f"Rejected move: Δ={delta_score:.3f}, T={temperature:.3f}")
            
            # Update progress tracking
            self.update_progress(best_solution, iteration + 1)
            temperature_iteration += 1
            
            # Early termination if solution is very good
            if best_score >= 99.0:
                self.logger.info(f"Excellent solution found at iteration {iteration}")
                break
        
        # Use best solution found
        current_solution = best_solution
        
        # Finalize optimization
        result = self.finish_optimization(current_solution, iteration + 1)
        
        acceptance_rate = accepted_moves / (accepted_moves + rejected_moves) if (accepted_moves + rejected_moves) > 0 else 0
        self.logger.info(f"Simulated Annealing completed: {accepted_moves} accepted, {rejected_moves} rejected")
        self.logger.info(f"Acceptance rate: {acceptance_rate:.1%}, Final temperature: {temperature:.4f}")
        self.logger.info(f"Score: {result.initial_score:.2f} → {result.final_score:.2f} "
                        f"(+{result.improvement:.2f})")
        
        return result
    
    def _generate_neighbor(self, school_data: SchoolData) -> SchoolData:
        """
        Generate a neighbor solution by making a random modification.
        
        Args:
            school_data: Current solution
            
        Returns:
            Modified copy of the school data
        """
        neighbor = copy.deepcopy(school_data)
        
        # Choose between swap and single move
        if random.random() < self.swap_probability:
            return self._random_swap(neighbor)
        else:
            return self._random_move(neighbor)
    
    def _random_swap(self, school_data: SchoolData) -> SchoolData:
        """
        Perform a random swap between two students from different classes.
        
        Args:
            school_data: School data to modify
            
        Returns:
            Modified school data
        """
        classes_with_students = [cls for cls in school_data.classes.values() if cls.students]
        
        if len(classes_with_students) < 2:
            return school_data
        
        # Select two different classes
        class1, class2 = random.sample(classes_with_students, 2)
        
        # Select students that can be moved (respect force constraints)
        movable_students1 = [s for s in class1.students 
                           if self._can_move_student(s, class2.class_id, school_data)]
        movable_students2 = [s for s in class2.students 
                           if self._can_move_student(s, class1.class_id, school_data)]
        
        if not movable_students1 or not movable_students2:
            return school_data
        
        student1 = random.choice(movable_students1)
        student2 = random.choice(movable_students2)
        
        # Perform the swap
        self._move_student(school_data, student1, class2.class_id)
        self._move_student(school_data, student2, class1.class_id)
        
        return school_data
    
    def _random_move(self, school_data: SchoolData) -> SchoolData:
        """
        Perform a random move of a student to a different class.
        
        Args:
            school_data: School data to modify
            
        Returns:
            Modified school data
        """
        all_students = list(school_data.students.values())
        random.shuffle(all_students)
        
        for student in all_students:
            # Find classes the student can move to
            possible_classes = [class_id for class_id in school_data.classes.keys()
                              if class_id != student.class_id and 
                              self._can_move_student(student, class_id, school_data)]
            
            if possible_classes:
                target_class = random.choice(possible_classes)
                self._move_student(school_data, student, target_class)
                break
        
        return school_data
    
    def _accept_move(self, delta_score: float, temperature: float) -> bool:
        """
        Determine whether to accept a move based on score change and temperature.
        
        Args:
            delta_score: Change in score (positive = improvement)
            temperature: Current temperature
            
        Returns:
            True if move should be accepted, False otherwise
        """
        if delta_score > 0:
            return True  # Always accept improvements
        
        if temperature <= 0:
            return False  # Never accept worse moves at zero temperature
        
        # Calculate acceptance probability using Boltzmann distribution
        try:
            probability = math.exp(delta_score / temperature)
            return random.random() < probability
        except (OverflowError, ZeroDivisionError):
            return False
    
    def _linear_cooling(self, temperature: float, iteration: int, max_iterations: int) -> float:
        """Linear cooling schedule."""
        return self.initial_temperature * (1 - iteration / max_iterations)
    
    def _exponential_cooling(self, temperature: float, iteration: int, max_iterations: int) -> float:
        """Exponential cooling schedule."""
        return temperature * self.cooling_rate
    
    def _logarithmic_cooling(self, temperature: float, iteration: int, max_iterations: int) -> float:
        """Logarithmic cooling schedule."""
        return self.initial_temperature / math.log(2 + iteration)
    
    def _adaptive_cooling(self, temperature: float, iteration: int, max_iterations: int) -> float:
        """Adaptive cooling based on acceptance rate."""
        # This could be enhanced to track acceptance rate and adjust cooling accordingly
        return temperature * self.cooling_rate
    
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
        
        # Force friend constraint - for SA, we allow breaking force friend groups
        # with low probability to explore more solutions
        if (self.respect_force_constraints and 
            student.force_friend and student.force_friend.strip()):
            
            force_group = student.force_friend.strip()
            group_members = [s for s in school_data.students.values() 
                           if s.force_friend and s.force_friend.strip() == force_group]
            
            if len(group_members) > 1:
                # Allow breaking force friend groups with small probability
                return random.random() < 0.1
        
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
            'initial_temperature': self.initial_temperature,
            'min_temperature': self.min_temperature,
            'cooling_rate': self.cooling_rate,
            'cooling_schedule': self.cooling_schedule,
            'iterations_per_temperature': self.iterations_per_temperature,
            'swap_probability': self.swap_probability,
            'max_group_size': self.max_group_size,
            'min_friends_required': self.min_friends_required,
            'respect_force_constraints': self.respect_force_constraints
        } 