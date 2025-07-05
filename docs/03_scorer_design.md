# Scorer Design Document

## Overview
The Meshachvetz scorer evaluates student-class assignments using a three-layer hierarchical scoring system. Each layer focuses on different aspects of the assignment quality, and the final score is a weighted combination of all layers.

## Three-Layer Architecture

### Layer 1: Student Layer (Individual Satisfaction)
Evaluates how well each student's preferences are met.

#### Metrics:
1. **Friend Satisfaction Score**
   - Formula: `(friends_placed / friends_requested) * 100`
   - Weight: `w_friends` (default: 0.7)
   - Range: 0-100

2. **Conflict Avoidance Score**
   - Formula: `(dislikes_avoided / dislikes_total) * 100`
   - Weight: `w_dislikes` (default: 0.3)
   - Range: 0-100

#### Student Layer Calculation:
```
student_score = (friend_satisfaction * w_friends + conflict_avoidance * w_dislikes) / (w_friends + w_dislikes)
```

### Layer 2: Class Layer (Intra-Class Balance)
Evaluates balance and composition within each class.

#### Metrics:
1. **Gender Balance Score**
   - Target: Equal distribution of genders
   - Formula: `100 - (abs(male_ratio - female_ratio) * 100)`
   - Weight: `w_gender_balance` (default: 1.0)
   - Range: 0-100

2. **Class Size Balance** (Future metric)
   - Ensures classes are of similar size
   - Weight: `w_class_size` (default: 0.5)

#### Class Layer Calculation:
```
class_score = gender_balance_score * w_gender_balance
```

### Layer 3: School Layer (Inter-Class Balance)
Evaluates how balanced the school is across all classes.

#### Metrics:
1. **Academic Score Balance**
   - Measures standard deviation of average academic scores across classes
   - Formula: `100 - (std_dev_academic_scores * normalization_factor)`
   - Weight: `w_academic_balance` (default: 0.3)

2. **Behavior Rank Balance**
   - Measures standard deviation of average behavior ranks across classes
   - Formula: `100 - (std_dev_behavior_ranks * normalization_factor)`
   - Weight: `w_behavior_balance` (default: 0.2)

3. **Class Size Balance**
   - Measures standard deviation of class sizes
   - Formula: `100 - (std_dev_class_sizes * normalization_factor)`
   - Weight: `w_size_balance` (default: 0.3)

4. **Assistance Package Balance**
   - Measures standard deviation of assistance package counts across classes
   - Formula: `100 - (std_dev_assistance_counts * normalization_factor)`
   - Weight: `w_assistance_balance` (default: 0.2)

#### School Layer Calculation:
```
school_score = (academic_balance * w_academic_balance + 
                behavior_balance * w_behavior_balance + 
                size_balance * w_size_balance + 
                assistance_balance * w_assistance_balance) / 
               (w_academic_balance + w_behavior_balance + w_size_balance + w_assistance_balance)
```

## Final Score Calculation

### Layer Weights:
- Student Layer: `w_student_layer` (default: 0.5)
- Class Layer: `w_class_layer` (default: 0.2)
- School Layer: `w_school_layer` (default: 0.3)

### Final Score Formula:
```
final_score = (avg_student_score * w_student_layer + 
               avg_class_score * w_class_layer + 
               school_score * w_school_layer) / 
              (w_student_layer + w_class_layer + w_school_layer)
```

## Implementation Details

### Configuration System
The scorer uses a configuration file to define weights and parameters:

```yaml
# scoring_config.yaml
weights:
  student_layer:
    friends: 0.7
    dislikes: 0.3
  class_layer:
    gender_balance: 1.0
  school_layer:
    academic_balance: 0.3
    behavior_balance: 0.2
    size_balance: 0.3
    assistance_balance: 0.2
  layers:
    student: 0.5
    class: 0.2
    school: 0.3

normalization:
  academic_score_factor: 2.0
  behavior_rank_factor: 25.0
  class_size_factor: 5.0
  assistance_count_factor: 10.0
```

### Class Structure

```python
class Scorer:
    def __init__(self, config_file: str = None)
    def load_data(self, csv_file: str) -> pd.DataFrame
    def calculate_student_scores(self) -> pd.DataFrame
    def calculate_class_scores(self) -> pd.DataFrame
    def calculate_school_scores(self) -> pd.DataFrame
    def calculate_final_score(self) -> float
    def generate_reports(self, output_dir: str)

class StudentScorer:
    def calculate_friend_satisfaction(self, student_id: str) -> float
    def calculate_conflict_avoidance(self, student_id: str) -> float
    def calculate_student_score(self, student_id: str) -> float

class ClassScorer:
    def calculate_gender_balance(self, class_id: str) -> float
    def calculate_class_score(self, class_id: str) -> float

class SchoolScorer:
    def calculate_academic_balance(self) -> float
    def calculate_behavior_balance(self) -> float
    def calculate_size_balance(self) -> float
    def calculate_assistance_balance(self) -> float
    def calculate_school_score(self) -> float
```

### Data Validation
Before scoring, the system validates:
1. All required columns are present (including social preference columns)
2. Student IDs are unique and follow 9-digit format
3. Class assignments are valid
4. Social preference references exist (up to 3 preferred friends, up to 5 disliked peers)
5. Behavior ranks are valid (A-E)
6. Force constraints are properly formatted
7. Numeric values are within acceptable ranges

### Social Preference Processing
- **Preferred Friends**: Extract non-empty values from preferred_friend_1, preferred_friend_2, preferred_friend_3
- **Disliked Peers**: Extract non-empty values from disliked_peer_1 through disliked_peer_5
- Duplicate preferences across columns are automatically removed
- Self-references are ignored during processing

### Force Constraint Handling
The scorer must account for placement constraints:
- **Force Class**: Students with force_class specified are scored normally but cannot be moved by optimizer
- **Force Friend**: Students in force_friend groups are scored as a unit and must remain together
- These constraints affect optimization but not scoring calculations

### Behavior Rank Processing
Behavior ranks are converted from string to numeric for calculations:
- A = 1 (Excellent)
- B = 2 (Good) 
- C = 3 (Medium)
- D = 4 (Below Average)
- E = 5 (Poor)
- Default for missing values: A = 1

### Error Handling
- Social preference columns are optional (empty strings allowed)
- Invalid behavior ranks (not A-E) trigger validation errors
- Force constraint references to non-existent students trigger validation errors
- Warnings are logged for data quality issues
- Graceful degradation when optional columns are missing

## Output Generation

### Student Scores CSV
- All original columns preserved
- Additional columns: `student_score`, `friend_satisfaction_percentage`, `conflict_avoidance_percentage`, `friends_placed`, `friends_requested`, `dislikes_avoided`, `dislikes_total`

### Class Scores CSV
- One row per class
- Columns: `class_id`, `class_score`, `gender_balance_score`, demographic summaries

### School Scores CSV
- One row per school-level metric
- Columns: `metric_name`, `metric_value`, `metric_score`, `class_values`, `standard_deviation`, `balance_score`

## Performance Considerations
- Use pandas for efficient data processing
- Vectorized operations where possible
- Caching of intermediate calculations
- Progress reporting for large datasets
- Memory-efficient processing for very large schools

## Testing Strategy
- Unit tests for each scoring component
- Integration tests with sample datasets
- Performance benchmarks
- Edge case validation (empty classes, missing data)
- Configuration validation tests 