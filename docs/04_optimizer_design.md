# Optimizer Design Document

## Overview
The Meshachvetz optimizer improves student-class assignments by iteratively modifying placements to maximize the overall score. It uses various optimization algorithms and strategies to find better solutions.

## Optimization Loop
```
Input CSV → Initial Assignment → Score → Optimize → Score → Repeat until convergence
```

## Optimization Strategies

### 1. Random Swap Optimizer
**Algorithm**: Randomly swap students between classes and accept improvements.

**Implementation**:
- Select two random students from different classes
- Swap their assignments
- Calculate new score
- Accept if improvement, reject otherwise
- Repeat for specified iterations

**Parameters**:
- `max_iterations`: Maximum number of swap attempts
- `early_stop_threshold`: Stop if no improvement after N iterations
- `temperature`: Simulated annealing parameter (optional)

### 2. Greedy Local Search
**Algorithm**: Systematically try moving each student to find local improvements.

**Implementation**:
- For each student, try moving to each other class
- Calculate score improvement for each possible move
- Make the best move if it improves the score
- Repeat until no improvements found

**Parameters**:
- `max_passes`: Maximum number of complete passes through all students
- `min_improvement`: Minimum score improvement to accept a move

### 3. Genetic Algorithm
**Algorithm**: Evolve a population of solutions through selection, crossover, and mutation.

**Implementation**:
- **Population**: Set of different class assignments
- **Fitness**: Score from the scorer system
- **Selection**: Tournament or roulette wheel selection
- **Crossover**: Combine assignments from two parents
- **Mutation**: Random student reassignments
- **Elitism**: Keep best solutions in each generation

**Parameters**:
- `population_size`: Number of solutions in each generation
- `generations`: Maximum number of generations
- `mutation_rate`: Probability of random changes
- `crossover_rate`: Probability of combining solutions
- `elite_size`: Number of best solutions to preserve

### 4. OR-Tools Integration
**Algorithm**: Use Google's OR-Tools constraint programming for optimal solutions.

**Implementation**:
- Model as constraint satisfaction problem
- Define variables: student-class assignments
- Define constraints: class size limits, social preferences
- Define objective: maximize scorer output
- Use CP-SAT solver for optimal solution

**Constraints**:
- Each student assigned to exactly one class
- Class size limits (min/max students per class)
- Hard constraints vs soft preferences
- Gender balance requirements

### 5. Simulated Annealing
**Algorithm**: Accept worse solutions with decreasing probability over time.

**Implementation**:
- Start with high "temperature" (accept most changes)
- Gradually reduce temperature
- Accept improvements always
- Accept worse solutions with probability `exp(-delta/temperature)`
- Cool down according to cooling schedule

**Parameters**:
- `initial_temperature`: Starting temperature
- `cooling_rate`: Rate of temperature reduction
- `min_temperature`: Minimum temperature before stopping
- `cooling_schedule`: Linear, exponential, or custom

## Optimization Manager

### Class Structure
```python
class OptimizationManager:
    def __init__(self, scorer: Scorer, config: Dict)
    def optimize(self, initial_data: pd.DataFrame) -> pd.DataFrame
    def run_algorithm(self, algorithm: str, data: pd.DataFrame) -> pd.DataFrame
    def compare_solutions(self, solutions: List[pd.DataFrame]) -> pd.DataFrame
    def generate_optimization_report(self) -> Dict

class BaseOptimizer:
    def optimize(self, data: pd.DataFrame) -> pd.DataFrame
    def evaluate_solution(self, data: pd.DataFrame) -> float
    def is_valid_solution(self, data: pd.DataFrame) -> bool

class RandomSwapOptimizer(BaseOptimizer):
    def __init__(self, max_iterations: int, early_stop: int)
    def optimize(self, data: pd.DataFrame) -> pd.DataFrame

class GeneticOptimizer(BaseOptimizer):
    def __init__(self, population_size: int, generations: int, mutation_rate: float)
    def optimize(self, data: pd.DataFrame) -> pd.DataFrame
    def create_population(self, data: pd.DataFrame) -> List[pd.DataFrame]
    def selection(self, population: List[pd.DataFrame]) -> List[pd.DataFrame]
    def crossover(self, parent1: pd.DataFrame, parent2: pd.DataFrame) -> pd.DataFrame
    def mutate(self, individual: pd.DataFrame) -> pd.DataFrame

class ORToolsOptimizer(BaseOptimizer):
    def __init__(self, time_limit: int, constraints: Dict)
    def optimize(self, data: pd.DataFrame) -> pd.DataFrame
    def build_model(self, data: pd.DataFrame) -> cp_model.CpModel
```

## Configuration System

### Optimizer Configuration
```yaml
# optimizer_config.yaml
optimization:
  algorithms:
    - name: "random_swap"
      enabled: true
      parameters:
        max_iterations: 10000
        early_stop_threshold: 1000
        
    - name: "genetic"
      enabled: true
      parameters:
        population_size: 50
        generations: 100
        mutation_rate: 0.1
        crossover_rate: 0.8
        elite_size: 5
        
    - name: "or_tools"
      enabled: false
      parameters:
        time_limit: 300
        
  strategy: "sequential"  # or "parallel", "best_of"
  
constraints:
  class_size:
    min_students: 20
    max_students: 30
  minimum_friends:
    default: 1                    # Default minimum friends per student
    allow_override: true          # Can be overridden via CLI
    max_allowed: 3                # Maximum constraint value
  hard_constraints:
    - "gender_balance"
    - "class_size_limits"
    - "minimum_friends"
  soft_constraints:
    - "social_preferences"
    - "academic_balance"
```

## Multi-Algorithm Strategy

### Sequential Optimization
Run algorithms one after another, using the output of one as input to the next:
1. Start with random/greedy initialization
2. Apply genetic algorithm for global exploration
3. Apply local search for fine-tuning
4. Apply simulated annealing for final improvements

### Parallel Optimization
Run multiple algorithms simultaneously and select the best result:
- Each algorithm runs independently
- Compare final scores
- Select best solution
- Optionally combine solutions

### Hybrid Approach
Combine multiple algorithms within a single optimization run:
- Use genetic algorithm population
- Apply local search to each individual
- Use simulated annealing for population diversity

## Constraints and Validation

### Hard Constraints
Must be satisfied in any valid solution:
- Each student assigned to exactly one class
- Class size within specified limits
- **Force Class**: Students with force_class specified cannot be moved
- **Force Friend**: Students in force_friend groups must stay together
- **Minimum Friends**: Each student must have at least N friends in their class (configurable, default: 1)
- Mandatory groupings (if specified)

### Soft Constraints
Preferences that contribute to score but can be violated:
- Social preferences
- Academic balance
- Demographic balance

### Force Constraint Handling
**Force Class Constraints:**
- Students with `force_class` specified are locked to that class
- Optimizer algorithms must exclude these students from move operations
- Validation ensures force_class refers to existing class

**Force Friend Constraints:**
- Students with matching `force_friend` values form immutable groups
- All group members must be moved together as a single unit
- Optimizer treats groups as atomic entities
- Group size affects optimization complexity

**Minimum Friend Constraints:**
- Each student must have at least N preferred friends in their class
- Configurable parameter (default: 1, can be set to 0, 2, 3+)
- Hard constraint that must be satisfied by all algorithms
- Validation checks friend availability during optimization

### Validation Rules
- Solution feasibility check
- Constraint satisfaction verification
- Force constraint compliance verification
- Minimum friend constraint verification
- Score calculation validation
- Data integrity verification

## Performance Optimization

### Incremental Scoring
- Cache intermediate calculations
- Only recalculate affected scores after changes
- Use differential scoring for small changes

### Memory Management
- Efficient data structures for large datasets
- Garbage collection of intermediate solutions
- Streaming for very large problems

### Parallel Processing
- Multi-threading for independent operations
- GPU acceleration for genetic algorithms (future)
- Distributed computing for large problems (future)

## Progress Tracking and Reporting

### Progress Metrics
- Current best score
- Improvement over time
- Convergence rate
- Algorithm performance comparison

### Reporting
- Optimization history
- Algorithm comparison
- Solution quality metrics
- Runtime statistics

### Visualization (Future)
- Score improvement over time
- Class composition changes
- Student satisfaction histograms
- Balance metric trends

## Integration with Scorer

### Tight Integration
- Use scorer's configuration for optimization objectives
- Leverage scorer's validation and data processing
- Maintain consistency in scoring calculations

### Optimization Feedback
- Identify which metrics are hardest to optimize
- Suggest weight adjustments based on optimization results
- Provide insights into trade-offs between different objectives

## Error Handling and Robustness

### Algorithm Failures
- Graceful degradation when algorithms fail
- Fallback to simpler methods
- Error logging and reporting

### Invalid Solutions
- Validation of all generated solutions
- Repair mechanisms for constraint violations
- Rejection of invalid solutions

### Performance Issues
- Timeout handling for long-running algorithms
- Memory usage monitoring
- Progress interruption and resumption

## Testing and Validation

### Unit Tests
- Individual algorithm implementations
- Constraint validation
- Solution quality verification

### Integration Tests
- End-to-end optimization workflows
- Multi-algorithm coordination
- Performance benchmarking

### Validation Datasets
- Known optimal solutions for testing
- Synthetic data generation
- Real-world school data validation