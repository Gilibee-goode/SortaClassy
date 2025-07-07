#!/usr/bin/env python3
"""
Genetic Algorithm Optimizer for Meshachvetz - evolves a population of solutions
through selection, crossover, and mutation to find optimal class assignments.
"""

import logging
import copy
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .base_optimizer import BaseOptimizer, OptimizationResult
from ..data.models import SchoolData, Student


@dataclass
class Individual:
    """Represents an individual solution in the genetic algorithm population."""
    school_data: SchoolData
    fitness: float
    age: int = 0
    
    def __post_init__(self):
        """Initialize fitness if not provided."""
        if self.fitness < 0:
            self.fitness = 0.0


class GeneticOptimizer(BaseOptimizer):
    """
    Genetic Algorithm optimization.
    
    Maintains a population of solutions and evolves them through:
    - Selection: Choose parents based on fitness
    - Crossover: Combine two parent solutions
    - Mutation: Random changes to solutions
    - Elitism: Keep best solutions across generations
    """
    
    def __init__(self, scorer, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Genetic Algorithm optimizer.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary with algorithm parameters
        """
        super().__init__(scorer, config)
        
        # Population parameters
        self.population_size = self.config.get('population_size', 50)
        self.elite_size = self.config.get('elite_size', 5)
        self.max_generations = self.config.get('max_generations', 100)
        
        # Genetic operators parameters
        self.crossover_rate = self.config.get('crossover_rate', 0.8)
        self.mutation_rate = self.config.get('mutation_rate', 0.1)
        self.tournament_size = self.config.get('tournament_size', 3)
        
        # Selection and diversity parameters
        self.selection_method = self.config.get('selection_method', 'tournament')
        self.diversity_penalty = self.config.get('diversity_penalty', 0.1)
        self.max_age = self.config.get('max_age', 10)  # For aging-based diversity
        
        # Convergence parameters
        self.convergence_generations = self.config.get('convergence_generations', 10)
        self.min_improvement = self.config.get('min_improvement', 0.01)
        
        self.logger = logging.getLogger(__name__)
        
        # Selection methods
        self.selection_methods = {
            'tournament': self._tournament_selection,
            'roulette': self._roulette_selection,
            'rank': self._rank_selection
        }
    
    def get_algorithm_name(self) -> str:
        """Get the name of this optimization algorithm."""
        return "Genetic Algorithm"
    
    def optimize(self, school_data: SchoolData, max_iterations: int = 1000) -> OptimizationResult:
        """
        Optimize using genetic algorithm.
        
        Args:
            school_data: Initial school data to optimize
            max_iterations: Maximum number of generations (overrides max_generations)
            
        Returns:
            OptimizationResult with optimized assignment and metrics
        """
        self.logger.info(f"Starting {self.get_algorithm_name()} optimization")
        
        # Performance optimizations for large datasets
        student_count = len(school_data.students)
        if student_count > 100:
            # Adjust parameters for large datasets
            self.population_size = min(self.population_size, max(20, student_count // 4))
            self.convergence_generations = min(self.convergence_generations, 5)
            self.logger.info(f"Large dataset detected ({student_count} students). Optimizing parameters:")
            self.logger.info(f"  Population size: {self.population_size}")
            self.logger.info(f"  Convergence generations: {self.convergence_generations}")
        
        self.logger.info(f"Parameters: pop_size={self.population_size}, generations={self.max_generations}, "
                        f"crossover_rate={self.crossover_rate}, mutation_rate={self.mutation_rate}")
        
        # Use the smaller of max_iterations and max_generations
        effective_generations = min(max_iterations, self.max_generations)
        
        # Initialize optimization tracking
        initial_score = self.start_optimization(school_data)
        
        # Create initial population
        self.logger.info(f"Creating initial population of {self.population_size} individuals...")
        population = self._create_initial_population(school_data)
        
        # Track best solution
        best_individual = max(population, key=lambda ind: ind.fitness)
        best_fitness_history = [best_individual.fitness]
        generations_without_improvement = 0
        
        # Start enhanced logging
        self.start_optimization(school_data)
        
        for generation in range(effective_generations):
            # Algorithm-specific metrics for enhanced logging
            additional_metrics = {
                'population_size': len(population),
                'best_fitness': best_individual.fitness,
                'generations_without_improvement': generations_without_improvement,
                'diversity': self._calculate_diversity(population)
            }
            
            # Update progress with enhanced logging
            self.update_progress(best_individual.school_data, generation + 1, additional_metrics)
            
            # Selection
            selection_method = self.selection_methods.get(
                self.selection_method, self._tournament_selection
            )
            selected_parents = selection_method(population)
            
            # Create new population
            new_population = []
            
            # Elitism: Keep best individuals
            elite_individuals = sorted(population, key=lambda ind: ind.fitness, reverse=True)[:self.elite_size]
            new_population.extend([copy.deepcopy(ind) for ind in elite_individuals])
            
            # Generate offspring
            offspring_attempts = 0
            max_offspring_attempts = self.population_size * 3  # Prevent infinite loops
            
            while len(new_population) < self.population_size and offspring_attempts < max_offspring_attempts:
                try:
                    # Select parents
                    parent1 = random.choice(selected_parents)
                    parent2 = random.choice(selected_parents)
                    
                    # Crossover
                    if random.random() < self.crossover_rate:
                        offspring = self._crossover(parent1, parent2)
                    else:
                        offspring = copy.deepcopy(random.choice([parent1, parent2]))
                    
                    # Mutation
                    if random.random() < self.mutation_rate:
                        offspring = self._mutate(offspring)
                    
                    # Evaluate offspring
                    if self._is_valid_individual(offspring):
                        fitness = self.evaluate_solution(offspring.school_data)
                        offspring.fitness = fitness
                        offspring.age = 0
                        new_population.append(offspring)
                    
                    offspring_attempts += 1
                    
                except Exception as e:
                    self.iteration_logger.log_debug(f"Offspring generation failed: {e}")
                    offspring_attempts += 1
            
            # If we couldn't create enough offspring, fill with copies of elite individuals
            while len(new_population) < self.population_size:
                elite_copy = copy.deepcopy(random.choice(elite_individuals))
                new_population.append(elite_copy)
            
            # Age the population
            for individual in new_population:
                individual.age += 1
            
            # Update population
            population = new_population[:self.population_size]
            
            # Track best solution
            current_best = max(population, key=lambda ind: ind.fitness)
            if current_best.fitness > best_individual.fitness:
                improvement = current_best.fitness - best_individual.fitness
                best_individual = copy.deepcopy(current_best)
                generations_without_improvement = 0
                self.iteration_logger.log_debug(f"New best fitness: {best_individual.fitness:.3f} (+{improvement:.3f})")
            else:
                generations_without_improvement += 1
            
            best_fitness_history.append(best_individual.fitness)
            
            # Check convergence
            if generations_without_improvement >= self.convergence_generations:
                self.iteration_logger.log_info(f"Converged after {generation + 1} generations "
                                             f"({generations_without_improvement} generations without improvement)")
                break
        
        # Finalize optimization with enhanced logging
        result = self.finish_optimization(best_individual.school_data, generation + 1)
        
        # Additional genetic algorithm specific logging
        self.iteration_logger.log_info(f"Genetic Algorithm completed after {generation + 1} generations")
        self.iteration_logger.log_info(f"Best fitness: {best_individual.fitness:.3f}")
        self.iteration_logger.log_info(f"Score: {result.initial_score:.2f} → {result.final_score:.2f} "
                                     f"(+{result.improvement:.2f})")
        
        return result
    
    def _create_initial_population(self, school_data: SchoolData) -> List[Individual]:
        """
        Create initial population of solutions.
        
        Args:
            school_data: Base school data to create variations from
            
        Returns:
            List of Individual solutions
        """
        population = []
        
        # Add the original solution
        original_fitness = self.evaluate_solution(school_data)
        population.append(Individual(copy.deepcopy(school_data), original_fitness))
        
        # Create random variations with safety mechanisms
        max_attempts_per_individual = 20  # Reduced from 50 for better performance
        max_modifications_per_individual = min(5, len(school_data.students) // 50)  # Fewer modifications for large datasets
        
        for i in range(self.population_size - 1):
            attempts = 0
            created_individual = False
            
            while attempts < max_attempts_per_individual and not created_individual:
                individual_data = copy.deepcopy(school_data)
                
                # Apply fewer random modifications for large datasets
                num_modifications = random.randint(1, max_modifications_per_individual)
                modification_attempts = 0
                
                for _ in range(num_modifications):
                    if modification_attempts < 5:  # Reduced from 10
                        try:
                            individual_data = self._random_modification(individual_data)
                            modification_attempts += 1
                        except Exception as e:
                            self.logger.debug(f"Modification failed: {e}")
                            break
                
                # Validate and evaluate
                is_valid, _ = self._is_valid_solution_genetic(individual_data)
                if is_valid:
                    fitness = self.evaluate_solution(individual_data)
                    population.append(Individual(individual_data, fitness))
                    created_individual = True
                    self.logger.debug(f"Created individual {i+1}/{self.population_size-1} after {attempts+1} attempts")
                else:
                    attempts += 1
            
            # If we couldn't create a valid individual after max attempts, use the original with minimal changes
            if not created_individual:
                self.logger.debug(f"Using original for individual {i+1} after {max_attempts_per_individual} attempts")
                population.append(Individual(copy.deepcopy(school_data), original_fitness))
        
        # Final safety check: if we somehow still don't have enough individuals, fill with copies of the original
        while len(population) < self.population_size:
            self.logger.warning(f"Filling population with original solution copy (current size: {len(population)})")
            population.append(Individual(copy.deepcopy(school_data), original_fitness))
        
        self.logger.info(f"Created initial population of {len(population)} individuals")
        
        # Log population diversity
        unique_fitness_values = len(set(ind.fitness for ind in population))
        self.logger.info(f"Population diversity: {unique_fitness_values} unique fitness values")
        
        return population
    
    def _tournament_selection(self, population: List[Individual]) -> List[Individual]:
        """
        Tournament selection: randomly select groups and pick the best from each.
        
        Args:
            population: Current population
            
        Returns:
            Selected parents for reproduction
        """
        selected = []
        selection_size = len(population) // 2  # Select half the population as parents
        
        for _ in range(selection_size):
            tournament = random.sample(population, min(self.tournament_size, len(population)))
            winner = max(tournament, key=lambda ind: ind.fitness)
            selected.append(winner)
        
        return selected
    
    def _roulette_selection(self, population: List[Individual]) -> List[Individual]:
        """
        Roulette wheel selection: select based on fitness proportions.
        
        Args:
            population: Current population
            
        Returns:
            Selected parents for reproduction
        """
        total_fitness = sum(ind.fitness for ind in population)
        if total_fitness == 0:
            return random.sample(population, len(population) // 2)
        
        selected = []
        selection_size = len(population) // 2
        
        for _ in range(selection_size):
            pick = random.uniform(0, total_fitness)
            current = 0
            for individual in population:
                current += individual.fitness
                if current > pick:
                    selected.append(individual)
                    break
        
        return selected
    
    def _rank_selection(self, population: List[Individual]) -> List[Individual]:
        """
        Rank selection: select based on rank rather than raw fitness.
        
        Args:
            population: Current population
            
        Returns:
            Selected parents for reproduction
        """
        sorted_population = sorted(population, key=lambda ind: ind.fitness)
        selection_size = len(population) // 2
        
        selected = []
        for _ in range(selection_size):
            # Higher ranked individuals have higher probability
            rank_weights = list(range(1, len(sorted_population) + 1))
            chosen_individual = random.choices(sorted_population, weights=rank_weights)[0]
            selected.append(chosen_individual)
        
        return selected
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Individual:
        """
        Create offspring by combining two parent solutions.
        
        Args:
            parent1: First parent solution
            parent2: Second parent solution
            
        Returns:
            Offspring individual
        """
        offspring_data = copy.deepcopy(parent1.school_data)
        
        # Uniform crossover: for each student, randomly choose parent
        for student_id, student in offspring_data.students.items():
            if random.random() < 0.5:
                # Use parent2's assignment for this student
                parent2_student = parent2.school_data.students[student_id]
                target_class = parent2_student.class_id
                
                # Check if move is valid
                if self._can_move_student_genetic(student, target_class, offspring_data):
                    self._move_student(offspring_data, student, target_class)
        
        return Individual(offspring_data, -1)  # Fitness will be calculated later
    
    def _mutate(self, individual: Individual) -> Individual:
        """
        Apply random mutations to an individual.
        
        Args:
            individual: Individual to mutate
            
        Returns:
            Mutated individual
        """
        try:
            mutated_data = copy.deepcopy(individual.school_data)
            
            # Number of mutations based on mutation rate
            num_mutations = max(1, int(len(mutated_data.students) * self.mutation_rate))
            
            # Limit mutations for large datasets to prevent excessive changes
            if len(mutated_data.students) > 100:
                num_mutations = min(num_mutations, 5)
            
            successful_mutations = 0
            mutation_attempts = 0
            max_mutation_attempts = num_mutations * 3  # Allow some failures
            
            while successful_mutations < num_mutations and mutation_attempts < max_mutation_attempts:
                try:
                    original_data = copy.deepcopy(mutated_data)
                    mutated_data = self._random_modification(mutated_data)
                    
                    # Check if mutation actually changed something
                    if self._data_changed(original_data, mutated_data):
                        successful_mutations += 1
                    
                    mutation_attempts += 1
                    
                except Exception as e:
                    self.logger.debug(f"Mutation attempt failed: {e}")
                    mutation_attempts += 1
            
            return Individual(mutated_data, -1)  # Fitness will be calculated later
            
        except Exception as e:
            self.logger.debug(f"Mutation failed completely: {e}")
            # Return original individual if mutation fails
            return Individual(copy.deepcopy(individual.school_data), -1)
    
    def _random_modification(self, school_data: SchoolData) -> SchoolData:
        """
        Apply a random modification to school data.
        
        Args:
            school_data: School data to modify
            
        Returns:
            Modified school data
        """
        try:
            modification_type = random.choice(['swap', 'move', 'group_move'])
            
            if modification_type == 'swap':
                return self._random_swap_genetic(school_data)
            elif modification_type == 'move':
                return self._random_move_genetic(school_data)
            else:  # group_move
                return self._random_group_move(school_data)
        except Exception as e:
            self.logger.debug(f"Random modification failed: {e}")
            # Return original data if modification fails
            return school_data
    
    def _random_swap_genetic(self, school_data: SchoolData) -> SchoolData:
        """Perform a random swap between students."""
        try:
            classes_with_students = [cls for cls in school_data.classes.values() if cls.students]
            
            if len(classes_with_students) < 2:
                return school_data
            
            class1, class2 = random.sample(classes_with_students, 2)
            
            movable_students1 = [s for s in class1.students 
                               if self._can_move_student_genetic(s, class2.class_id, school_data)]
            movable_students2 = [s for s in class2.students 
                               if self._can_move_student_genetic(s, class1.class_id, school_data)]
            
            if movable_students1 and movable_students2:
                student1 = random.choice(movable_students1)
                student2 = random.choice(movable_students2)
                
                self._move_student(school_data, student1, class2.class_id)
                self._move_student(school_data, student2, class1.class_id)
            
            return school_data
        except Exception as e:
            self.logger.debug(f"Random swap failed: {e}")
            return school_data
    
    def _random_move_genetic(self, school_data: SchoolData) -> SchoolData:
        """Perform a random move of a student."""
        try:
            all_students = list(school_data.students.values())
            if not all_students:
                return school_data
                
            random.shuffle(all_students)
            
            for student in all_students:
                possible_classes = [class_id for class_id in school_data.classes.keys()
                                  if class_id != student.class_id and 
                                  self._can_move_student_genetic(student, class_id, school_data)]
                
                if possible_classes:
                    target_class = random.choice(possible_classes)
                    self._move_student(school_data, student, target_class)
                    break
            
            return school_data
        except Exception as e:
            self.logger.debug(f"Random move failed: {e}")
            return school_data
    
    def _random_group_move(self, school_data: SchoolData) -> SchoolData:
        """Perform a random move of a small group of students."""
        try:
            all_students = list(school_data.students.values())
            if len(all_students) < 2:
                return school_data
                
            group_size = random.randint(2, min(5, len(all_students)))
            group = random.sample(all_students, group_size)
            
            # Find a class where all group members can move
            possible_classes = []
            for class_id in school_data.classes.keys():
                if all(self._can_move_student_genetic(student, class_id, school_data) 
                       for student in group):
                    possible_classes.append(class_id)
            
            if possible_classes:
                target_class = random.choice(possible_classes)
                for student in group:
                    if student.class_id != target_class:
                        self._move_student(school_data, student, target_class)
            
            return school_data
        except Exception as e:
            self.logger.debug(f"Random group move failed: {e}")
            return school_data
    
    def _can_move_student_genetic(self, student: Student, target_class: str, school_data: SchoolData) -> bool:
        """Check if student can be moved (genetic algorithm version)."""
        # Force class constraint
        if (self.respect_force_constraints and 
            student.force_class and student.force_class.strip() and
            student.force_class.strip() != target_class):
            return False
        
        # Force friend constraint - in GA, we're more flexible
        if (self.respect_force_constraints and 
            student.force_friend and student.force_friend.strip()):
            
            force_group = student.force_friend.strip()
            group_members = [s for s in school_data.students.values() 
                           if s.force_friend and s.force_friend.strip() == force_group]
            
            if len(group_members) > 1:
                # Allow breaking force friend groups with higher probability in GA
                return random.random() < 0.3
        
        return True
    
    def _move_student(self, school_data: SchoolData, student: Student, target_class: str) -> None:
        """Move a student to a target class."""
        try:
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
            
            school_data.students[student.student_id] = student
        except Exception as e:
            self.logger.debug(f"Move student failed: {e}")
            # Don't change anything if move fails
    
    def _is_valid_individual(self, individual: Individual) -> bool:
        """Check if an individual represents a valid solution."""
        # Use genetic-specific validation that's more permissive
        is_valid, _ = self._is_valid_solution_genetic(individual.school_data)
        return is_valid
    
    def _is_valid_solution_genetic(self, school_data: SchoolData) -> tuple[bool, List[str]]:
        """
        Check if a solution satisfies HARD constraints for genetic algorithm.
        This is more permissive than the base validation to allow exploration.
        
        Args:
            school_data: School data to validate
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        try:
            # Check basic data integrity (HARD constraint)
            if not school_data.students or not school_data.classes:
                violations.append("Missing students or classes data")
                return False, violations
            
            # Check that all students are assigned to classes (HARD constraint)
            assigned_students = set()
            for class_data in school_data.classes.values():
                for student in class_data.students:
                    if student.student_id in assigned_students:
                        violations.append(f"Student {student.student_id} assigned to multiple classes")
                    assigned_students.add(student.student_id)
            
            missing_students = set(school_data.students.keys()) - assigned_students
            if missing_students:
                violations.append(f"Students not assigned to any class: {list(missing_students)[:5]}")
            
            # Check force constraints if enabled (HARD constraint)
            if self.respect_force_constraints:
                constraint_violations = school_data.validate_force_constraints()
                violations.extend(constraint_violations)
            
            # DON'T check minimum friend constraints during genetic evolution
            # This is a SOFT constraint that will be optimized by the fitness function
            # but shouldn't prevent genetic diversity
            
            return len(violations) == 0, violations
            
        except Exception as e:
            violations.append(f"Validation error: {e}")
            return False, violations
    
    def _calculate_diversity(self, population: List[Individual]) -> float:
        """Calculate population diversity (simplified metric)."""
        if len(population) < 2:
            return 0.0
        
        # Calculate average fitness difference
        fitness_values = [ind.fitness for ind in population]
        avg_fitness = sum(fitness_values) / len(fitness_values)
        
        diversity = sum(abs(fitness - avg_fitness) for fitness in fitness_values) / len(fitness_values)
        return diversity
    
    def get_algorithm_parameters(self) -> Dict[str, Any]:
        """Get current algorithm parameters for reporting."""
        return {
            'population_size': self.population_size,
            'elite_size': self.elite_size,
            'max_generations': self.max_generations,
            'crossover_rate': self.crossover_rate,
            'mutation_rate': self.mutation_rate,
            'tournament_size': self.tournament_size,
            'selection_method': self.selection_method,
            'convergence_generations': self.convergence_generations,
            'min_friends_required': self.min_friends_required,
            'respect_force_constraints': self.respect_force_constraints
        } 

    def _data_changed(self, original_data: SchoolData, modified_data: SchoolData) -> bool:
        """Check if school data was actually modified."""
        try:
            # Quick check: compare student class assignments
            for student_id in original_data.students:
                if (original_data.students[student_id].class_id != 
                    modified_data.students[student_id].class_id):
                    return True
            return False
        except Exception:
            # If comparison fails, assume data changed
            return True 