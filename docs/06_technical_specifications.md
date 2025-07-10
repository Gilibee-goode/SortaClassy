# Technical Specifications

## Overview
This document provides detailed technical specifications for the Meshachvetz student assignment optimization system, including APIs, data structures, algorithms, and implementation details.

## Table of Contents
1. [Data Models](#data-models)
2. [Core APIs](#core-apis)
3. [Scoring System](#scoring-system)
4. [Optimization Algorithms](#optimization-algorithms)
5. [Configuration System](#configuration-system)
6. [Output Management System](#output-management-system)
7. [Validation System](#validation-system)
8. [Error Handling](#error-handling)
9. [Performance Requirements](#performance-requirements)
10. [Testing Framework](#testing-framework)

## System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Layer    │    │  Scoring Layer  │    │ Optimizer Layer │
│                 │    │                 │    │                 │
│ • CSV Loader    │───▶│ • Student Score │───▶│ • Random Swap   │
│ • Validator     │    │ • Class Score   │    │ • Genetic Alg   │
│ • Data Models   │    │ • School Score  │    │ • Local Search  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Configuration   │    │   Reporting     │    │      CLI        │
│                 │    │                 │    │                 │
│ • YAML Config   │    │ • CSV Output    │    │ • Scorer CLI    │
│ • Weight Mgmt   │    │ • Analytics     │    │ • Optimizer CLI │
│ • Validation    │    │ • Visualization │    │ • Main CLI      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### Data Layer
- **Purpose**: Handle data loading, validation, and transformation
- **Components**: CSV Loader, Data Validator, Data Models
- **Dependencies**: pandas, numpy

#### Scoring Layer
- **Purpose**: Calculate scores for students, classes, and school
- **Components**: Student Scorer, Class Scorer, School Scorer, Main Scorer
- **Dependencies**: numpy, scipy

#### Optimizer Layer
- **Purpose**: Improve student assignments using various algorithms
- **Components**: Base Optimizer, Algorithm Implementations, Optimization Manager
- **Dependencies**: OR-Tools, numpy, scipy

## Data Structures

### Student Data Model
```python
@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    gender: str
    class_id: str
    academic_score: float
    behavior_rank: str  # A-E format
    assistance_package: bool
    preferred_friend_1: str
    preferred_friend_2: str
    preferred_friend_3: str
    disliked_peer_1: str
    disliked_peer_2: str
    disliked_peer_3: str
    disliked_peer_4: str
    disliked_peer_5: str
    force_class: str  # Force placement in specific class
    force_friend: str  # Force group placement identifier
    
    def __post_init__(self):
        # Validation logic
        self.validate_student_id()
        self.validate_scores()
        self.validate_social_preferences()
        self.validate_behavior_rank()
        self.validate_force_constraints()
        
    def get_numeric_behavior_rank(behavior_rank: str) -> int:
        """
        Convert behavior rank string to numeric value.
        
        Args:
            behavior_rank: String rank (A, B, C, D)
            
        Returns:
            Numeric rank (1-4)
        """
        conversion = {"A": 1, "B": 2, "C": 3, "D": 4}
        return conversion.get(behavior_rank.upper(), 1)  # Default to A=1
        
    def get_preferred_friends(self) -> List[str]:
        """Get list of non-empty preferred friends"""
        return [f for f in [self.preferred_friend_1, self.preferred_friend_2, self.preferred_friend_3] if f.strip()]
        
    def get_disliked_peers(self) -> List[str]:
        """Get list of non-empty disliked peers"""
        return [p for p in [self.disliked_peer_1, self.disliked_peer_2, self.disliked_peer_3, 
                           self.disliked_peer_4, self.disliked_peer_5] if p.strip()]
```

### Class Data Model
```python
@dataclass
class ClassData:
    class_id: str
    students: List[Student]
    
    @property
    def size(self) -> int:
        return len(self.students)
    
    @property
    def gender_distribution(self) -> Dict[str, int]:
        return Counter(s.gender for s in self.students)
    
    @property
    def average_academic_score(self) -> float:
        return sum(s.academic_score for s in self.students) / len(self.students)
```

### School Data Model
```python
@dataclass
class SchoolData:
    classes: Dict[str, ClassData]
    students: Dict[str, Student]
    
    @property
    def total_students(self) -> int:
        return len(self.students)
    
    @property
    def class_sizes(self) -> List[int]:
        return [cls.size for cls in self.classes.values()]
    
    def get_student_by_id(self, student_id: str) -> Student:
        return self.students[student_id]
```

## API Specifications

### Scorer API

#### Main Scorer Class
```python
class Scorer:
    def __init__(self, config: ScoringConfig):
        self.config = config
        self.student_scorer = StudentScorer(config)
        self.class_scorer = ClassScorer(config)
        self.school_scorer = SchoolScorer(config)
    
    def load_data(self, csv_file: str) -> SchoolData:
        """Load and validate student data from CSV file."""
        
    def calculate_scores(self, school_data: SchoolData) -> ScoringResult:
        """Calculate all scores for the school assignment."""
        
    def generate_reports(self, result: ScoringResult, output_dir: str) -> None:
        """Generate CSV reports and analysis."""
```

#### Student Scorer
```python
class StudentScorer:
    def calculate_friend_satisfaction(self, student: Student, school: SchoolData) -> float:
        """Calculate how many preferred friends are in same class."""
        
    def calculate_conflict_avoidance(self, student: Student, school: SchoolData) -> float:
        """Calculate how many disliked peers are avoided."""
        
    def calculate_student_score(self, student: Student, school: SchoolData) -> StudentScore:
        """Calculate overall student satisfaction score."""
```

#### Class Scorer
```python
class ClassScorer:
    def calculate_gender_balance(self, class_data: ClassData) -> float:
        """Calculate gender balance score for a class."""
        
    def calculate_size_score(self, class_data: ClassData, target_size: int) -> float:
        """Calculate how close class size is to target."""
        
    def calculate_class_score(self, class_data: ClassData) -> ClassScore:
        """Calculate overall class quality score."""
```

#### School Scorer
```python
class SchoolScorer:
    def calculate_balance_score(self, values: List[float]) -> float:
        """Calculate balance score based on standard deviation."""
        
    def calculate_academic_balance(self, school: SchoolData) -> float:
        """Calculate academic score balance across classes."""
        
    def calculate_school_score(self, school: SchoolData) -> SchoolScore:
        """Calculate overall school balance score."""
```

### Optimizer API

#### Base Optimizer
```python
class BaseOptimizer(ABC):
    @abstractmethod
    def optimize(self, school_data: SchoolData) -> OptimizationResult:
        """Optimize student assignments and return improved solution."""
        
    @abstractmethod
    def evaluate_solution(self, school_data: SchoolData) -> float:
        """Evaluate quality of a solution."""
        
    def is_valid_solution(self, school_data: SchoolData) -> bool:
        """Check if solution satisfies all constraints."""
```

#### Genetic Algorithm Optimizer
```python
class GeneticOptimizer(BaseOptimizer):
    def __init__(self, population_size: int = 50, generations: int = 100,
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        
    def create_population(self, school_data: SchoolData) -> List[SchoolData]:
        """Create initial population of solutions."""
        
    def selection(self, population: List[SchoolData], fitness: List[float]) -> List[SchoolData]:
        """Select parents for next generation."""
        
    def crossover(self, parent1: SchoolData, parent2: SchoolData) -> SchoolData:
        """Combine two solutions to create offspring."""
        
    def mutate(self, individual: SchoolData) -> SchoolData:
        """Apply random mutations to solution."""
```

### Configuration API

#### Configuration Classes
```python
@dataclass
class ScoringWeights:
    student_layer: Dict[str, float]
    class_layer: Dict[str, float]
    school_layer: Dict[str, float]
    layers: Dict[str, float]

@dataclass
class ScoringConfig:
    weights: ScoringWeights
    normalization_factors: Dict[str, float]
    validation_rules: Dict[str, Any]
    
    @classmethod
    def from_file(cls, config_file: str) -> 'ScoringConfig':
        """Load configuration from YAML file."""
        
    def validate(self) -> None:
        """Validate configuration parameters."""
```

## Algorithm Specifications

### Scoring Algorithms

#### Student Layer Formulas
```python
def friend_satisfaction_score(student: Student, school: SchoolData) -> float:
    """
    Formula: (friends_placed / friends_requested) * 100
    Where:
    - friends_placed: number of preferred friends in same class
    - friends_requested: total number of preferred friends (0-3)
    """
    preferred_friends = student.get_preferred_friends()
    if not preferred_friends:
        return 100.0  # No preferences = perfect satisfaction
    
    same_class_friends = sum(
        1 for friend_id in preferred_friends
        if school.students[friend_id].class_id == student.class_id
    )
    return (same_class_friends / len(preferred_friends)) * 100

def conflict_avoidance_score(student: Student, school: SchoolData) -> float:
    """
    Formula: (dislikes_avoided / total_dislikes) * 100
    Where:
    - dislikes_avoided: number of disliked peers in different classes
    - total_dislikes: total number of disliked peers (0-5)
    """
    disliked_peers = student.get_disliked_peers()
    if not disliked_peers:
        return 100.0  # No dislikes = perfect avoidance
    
    avoided_conflicts = sum(
        1 for peer_id in disliked_peers
        if school.students[peer_id].class_id != student.class_id
    )
    return (avoided_conflicts / len(disliked_peers)) * 100
```

#### Class Layer Formulas
```python
def gender_balance_score(class_data: ClassData) -> float:
    """
    Formula: 100 - abs(male_ratio - female_ratio) * 100
    Where:
    - male_ratio: proportion of male students
    - female_ratio: proportion of female students
    """
    gender_counts = class_data.gender_distribution
    total = class_data.size
    
    if total == 0:
        return 100.0
    
    male_ratio = gender_counts.get('M', 0) / total
    female_ratio = gender_counts.get('F', 0) / total
    
    return 100 - abs(male_ratio - female_ratio) * 100
```

#### School Layer Formulas
```python
def balance_score(values: List[float], normalization_factor: float = 1.0) -> float:
    """
    Formula: 100 - (standard_deviation * normalization_factor)
    Measures how balanced values are across classes.
    """
    if len(values) <= 1:
        return 100.0
    
    std_dev = np.std(values)
    return max(0, 100 - (std_dev * normalization_factor))
```

### Optimization Algorithms

#### Random Swap Algorithm
```python
def random_swap_step(school_data: SchoolData) -> SchoolData:
    """
    1. Select two random students from different classes
    2. Swap their class assignments
    3. Validate the swap doesn't violate constraints
    4. Return modified school data
    """
    classes = list(school_data.classes.keys())
    class1, class2 = random.sample(classes, 2)
    
    student1 = random.choice(school_data.classes[class1].students)
    student2 = random.choice(school_data.classes[class2].students)
    
    # Perform swap
    new_school_data = deepcopy(school_data)
    new_school_data.move_student(student1.student_id, class2)
    new_school_data.move_student(student2.student_id, class1)
    
    return new_school_data
```

#### Genetic Algorithm Components
```python
def tournament_selection(population: List[SchoolData], fitness: List[float], 
                        tournament_size: int = 3) -> SchoolData:
    """Select best individual from random tournament."""
    
def uniform_crossover(parent1: SchoolData, parent2: SchoolData) -> SchoolData:
    """Combine parents by randomly selecting class assignment for each student."""
    
def random_mutation(individual: SchoolData, mutation_rate: float) -> SchoolData:
    """Randomly reassign students with given probability."""
```

## Output Management System

### OutputManager Class

**Purpose:** Centralized output handling with descriptive directory naming and organized file management.

**Location:** `src/meshachvetz/utils/output_manager.py`

**Key Features:**
- Descriptive directory naming based on operation type, input file, and algorithm
- Automatic timestamp inclusion for chronological organization
- Operation information tracking with detailed metadata
- Cleanup of old runs to prevent disk space issues
- Support for multiple output formats (CSV, TXT, JSON)

#### OutputConfig

```python
@dataclass
class OutputConfig:
    """Configuration for output generation."""
    base_dir: str = "outputs"
    include_timestamp: bool = True
    include_input_filename: bool = True
    preserve_old_runs: bool = True
    max_old_runs: int = 10
    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
```

#### Main Methods

```python
class OutputManager:
    def create_scoring_directory(self, input_file: str) -> Path:
        """Create descriptive directory for scoring operations."""
    
    def create_optimization_directory(self, input_file: str, algorithm: str) -> Path:
        """Create descriptive directory for optimization operations."""
    
    def create_baseline_directory(self, input_file: str, num_runs: int) -> Path:
        """Create descriptive directory for baseline generation."""
    
    def create_generation_directory(self, input_file: str, strategy: str) -> Path:
        """Create descriptive directory for assignment generation."""
    
    def save_operation_info(self, output_dir: Path, operation_info: Dict[str, Any]) -> None:
        """Save operation metadata to operation_info.txt file."""
    
    def list_recent_runs(self, operation_type: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """List recent operation runs with metadata."""
    
    def get_latest_run(self, operation_type: str, input_file: str = None) -> Optional[Path]:
        """Get the most recent run directory for specified operation type."""
```

#### Directory Naming Convention

**Format:** `{operation}_{input_file_stem}_{algorithm}_{timestamp}`

**Examples:**
- `score_students_sample_2025-07-10_13-32-15/`
- `optimize_large_dataset_local-search_2025-07-10_14-15-30/`
- `baseline_test_data_random-swap_20runs_2025-07-10_15-45-12/`
- `generate_unassigned_students_constraint-aware_2025-07-10_16-20-05/`

#### Operation Information File

Each output directory contains an `operation_info.txt` file with metadata:

```text
Meshachvetz Operation Information
========================================
Generated: 2025-07-10 13:32:44

Operation: Optimize Assignment
Input File: examples/sample_data/students_sample.csv
Algorithm: Random Swap
Initial Score: 68.13/100
Final Score: 68.13/100
Improvement: 0.00 (0.0%)
Execution Time: 0.45 seconds
Iterations: 100/100
Constraints Satisfied: No
```

### Integration with Components

#### Scorer Integration

```python
class Scorer:
    def generate_csv_reports(self, result: ScoringResult, output_dir: str = None, input_file: str = None) -> str:
        """
        Generate comprehensive CSV reports using OutputManager for organization.
        
        Args:
            result: ScoringResult object containing all scoring data
            output_dir: Directory to save reports (optional, uses OutputManager if None)
            input_file: Path to input CSV file (used for descriptive directory naming)
            
        Returns:
            Path to the output directory containing all reports
        """
```

#### Optimization Manager Integration

```python
class OptimizationManager:
    def optimize_and_save(self, school_data: SchoolData,
                         output_file: str = None,
                         input_file: str = None,
                         algorithm: str = None,
                         max_iterations: int = None,
                         initialization_strategy: str = "constraint_aware",
                         auto_initialize: bool = True,
                         generate_reports: bool = True,
                         target_classes: Optional[int] = None) -> Tuple[OptimizationResult, Any]:
        """
        Optimize assignments and save results using OutputManager for organization.
        
        When output_file is None and input_file is provided, OutputManager creates
        a descriptive directory structure automatically.
        """
```

#### Baseline Generator Integration

```python
class BaselineGenerator:
    def save_baseline_report(self, output_dir: str = None, input_file: str = None, prefix: str = "baseline") -> Tuple[str, str]:
        """
        Save comprehensive baseline reports using OutputManager for organization.
        
        When output_dir is None and input_file is provided, OutputManager creates
        a descriptive directory structure automatically.
        """
```

### CLI Integration

All CLI commands now support automatic output organization:

**Without Output Specification (uses OutputManager):**
```bash
meshachvetz score examples/sample_data/students_sample.csv --reports
# Creates: outputs/score_students_sample_YYYY-MM-DD_HH-MM-SS/

meshachvetz optimize examples/sample_data/students_sample.csv --algorithm local_search
# Creates: outputs/optimize_students_sample_local-search_YYYY-MM-DD_HH-MM-SS/

meshachvetz baseline examples/sample_data/students_sample.csv --runs 10
# Creates: outputs/baseline_students_sample_random-swap_10runs_YYYY-MM-DD_HH-MM-SS/
```

**With Explicit Output (legacy mode):**
```bash
meshachvetz score input.csv --output results/ --reports
# Creates: results/ (as specified)
```

### Output Structure Examples

#### Scoring Output

```
outputs/score_students_sample_2025-07-10_13-32-15/
├── operation_info.txt           # Operation metadata
├── summary_report.csv           # Overall scoring summary
├── student_details.csv          # Individual student scores
├── class_details.csv            # Class-level analysis
├── school_balance.csv           # School balance metrics
└── configuration.csv            # Configuration used
```

#### Optimization Output

```
outputs/optimize_students_sample_local-search_2025-07-10_14-15-30/
├── operation_info.txt           # Operation metadata
├── optimized_students_sample.csv # Final optimized assignment
├── optimization_report.csv     # Optimization progress and metrics
└── scoring_reports/            # Detailed scoring analysis
    ├── operation_info.txt
    ├── summary_report.csv
    ├── student_details.csv
    ├── class_details.csv
    ├── school_balance.csv
    └── configuration.csv
```

#### Baseline Output

```
outputs/baseline_test_data_random-swap_20runs_2025-07-10_15-45-12/
├── operation_info.txt          # Operation metadata
├── baseline_data.csv           # Statistical data from all runs
└── baseline_summary.txt        # Comprehensive analysis report
```

### Dynamic CSV Column Preservation

**New Feature:** The output system now preserves the exact column structure from input CSV files, allowing users to add custom columns without losing them in the output.

#### How It Works

1. **Original Column Tracking:** When loading CSV files, the system stores the original column order and names
2. **Class Column Handling:** If the input CSV is missing a 'class' column, it's automatically added after the 'gender' column
3. **Dynamic Output Generation:** The optimized CSV output preserves all original columns in their original order
4. **Unknown Column Support:** Any extra columns not part of the standard Student model are preserved as empty strings in output

#### Example

**Input CSV with extra columns:**
```csv
student_id,first_name,last_name,gender,academic_score,behavior_rank,studentiality_rank,assistance_package,extra_data,school,notes,preferred_friend_1,...
203765489,Sarah,Johnson,F,92.0,A,A,false,value1,School A,Important note,317328593,...
```

**Output CSV preserves structure:**
```csv
student_id,first_name,last_name,gender,class,academic_score,behavior_rank,studentiality_rank,assistance_package,extra_data,school,notes,preferred_friend_1,...
203765489,Sarah,Johnson,F,1,92.0,A,A,false,,School A,,317328593,...
```

**Note:** Custom column values are preserved as empty strings since they're not part of the Student data model, but the column structure remains intact.

#### Technical Implementation

- **DataLoader Enhancement:** Stores `_original_columns`, `_class_column_added`, and `_original_dataframe` metadata
- **SchoolData Extension:** Added optional attributes to preserve CSV structure information
- **OptimizationManager Update:** `_save_assignment_csv` method now uses dynamic column structure
- **Backward Compatibility:** Systems without metadata fall back to standard column structure

#### Benefits

1. **Custom Column Support:** Users can add workflow-specific columns (notes, IDs, metadata) without losing them
2. **Exact Column Preservation:** Output files maintain the exact same column order as input files
3. **Workflow Integration:** Enables seamless integration with existing data processing workflows
4. **Backward Compatibility:** Existing files and systems continue to work without changes

### Benefits

1. **Organization:** All outputs are contained in a single `outputs/` directory
2. **Descriptive Naming:** Directory names clearly indicate what operation was performed
3. **No File Conflicts:** Timestamp-based naming prevents overwrites
4. **Easy Navigation:** Chronological organization makes finding recent runs simple
5. **Metadata Tracking:** Operation info files provide complete context
6. **Automatic Cleanup:** Old runs are automatically removed to save disk space
7. **Backward Compatibility:** Explicit output paths still work for legacy scripts
8. **Column Preservation:** Input CSV column structure is exactly preserved in output files

## Performance Specifications

### Time Complexity
- **Data Loading**: O(n) where n = number of students
- **Student Scoring**: O(n * f) where f = average friends per student
- **Class Scoring**: O(c) where c = number of classes
- **School Scoring**: O(c)
- **Random Swap**: O(i) where i = number of iterations
- **Genetic Algorithm**: O(g * p * n) where g = generations, p = population size

### Space Complexity
- **Data Storage**: O(n) for student data
- **Scoring Results**: O(n + c) for all scores
- **Genetic Algorithm**: O(p * n) for population storage

### Performance Targets
- **Small School** (< 200 students): < 1 second scoring, < 10 seconds optimization
- **Medium School** (200-1000 students): < 5 seconds scoring, < 60 seconds optimization
- **Large School** (> 1000 students): < 30 seconds scoring, < 300 seconds optimization

## Error Handling

### Data Validation Errors
```python
class DataValidationError(Exception):
    """Raised when input data fails validation."""
    
class StudentDataError(DataValidationError):
    """Raised when student data is invalid."""
    
class ClassDataError(DataValidationError):
    """Raised when class data is invalid."""
```

### Optimization Errors
```python
class OptimizationError(Exception):
    """Raised when optimization fails."""
    
class ConstraintViolationError(OptimizationError):
    """Raised when solution violates constraints."""
    
class ConvergenceError(OptimizationError):
    """Raised when algorithm fails to converge."""
```

### Error Recovery Strategies
1. **Data Errors**: Provide detailed error messages and suggestions
2. **Constraint Violations**: Attempt to repair solutions automatically
3. **Algorithm Failures**: Fall back to simpler algorithms
4. **Performance Issues**: Implement timeouts and progress monitoring

## Security Considerations

### Input Validation
- Sanitize all CSV input data
- Validate file paths and names
- Limit file sizes and processing time
- Prevent path traversal attacks

### Data Privacy
- No personally identifiable information in logs
- Secure handling of student data
- Optional data anonymization features
- Clear data retention policies

### System Security
- Input sanitization for all user inputs
- Safe file handling for configuration and data files
- Resource limits to prevent DoS attacks
- Secure default configurations

## Deployment Specifications

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 512MB, recommended 2GB
- **Storage**: Minimum 100MB, recommended 1GB
- **CPU**: Any modern CPU, multi-core preferred for optimization

### Dependencies
```python
# Core dependencies
pandas >= 1.3.0
numpy >= 1.21.0
pyyaml >= 6.0
ortools >= 9.0

# Development dependencies
pytest >= 7.0
black >= 22.0
flake8 >= 4.0
mypy >= 0.950
```

### Installation Methods
1. **PyPI Package**: `pip install meshachvetz`
2. **Git Repository**: `git clone + pip install -e .`
3. **Docker Container**: `docker run meshachvetz/meshachvetz`
4. **Standalone Executable**: Platform-specific binaries

This technical specification provides the detailed foundation for implementing the Meshachvetz system according to the design documents. 