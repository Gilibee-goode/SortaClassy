# Data Format Specification

## Input CSV Format

### Required Columns
The input CSV file must contain the following columns:

| Column Name | Data Type | Description | Example Values |
|-------------|-----------|-------------|----------------|
| `student_id` | String | Unique identifier for each student | "317328593", "203765489", "213568467" |
| `first_name` | String | Student's first name | "John", "Sarah", "Ahmed" |
| `last_name` | String | Student's last name | "Smith", "Johnson", "Ali" |
| `gender` | String | Student's gender | "M", "F" |
| `class` | String | Assigned class identifier | "1", "2", "3" |
| `academic_score` | Float | Academic performance score (0-100) | 85.5, 92.0, 78.3 |
| `behavior_rank` | String | Behavior ranking (A-D, where A=excellent) | "A", "B", "C", "D" |
| `studentiality_rank` | String | Academic diligence ranking (A-D, where A=excellent) | "A", "B", "C", "D" |
| `assistance_package` | Boolean | Whether student needs assistance | true, false |
| `school` | String | School of origin for distribution balance (optional) | "School A", "Beit Sefer B", "" |
| `preferred_friend_1` | String | First preferred friend ID (optional) | "203765489", "" |
| `preferred_friend_2` | String | Second preferred friend ID (optional) | "213568467", "" |
| `preferred_friend_3` | String | Third preferred friend ID (optional) | "456789123", "" |
| `disliked_peer_1` | String | First disliked peer ID (optional) | "317328593", "" |
| `disliked_peer_2` | String | Second disliked peer ID (optional) | "891234567", "" |
| `disliked_peer_3` | String | Third disliked peer ID (optional) | "", "" |
| `disliked_peer_4` | String | Fourth disliked peer ID (optional) | "", "" |
| `disliked_peer_5` | String | Fifth disliked peer ID (optional) | "", "" |
| `force_class` | String | Force placement in specific class (empty if no constraint) | "1", "2", "", "3" |
| `force_friend` | String | Comma-separated list of student IDs that must be placed together | "203765489,213568467", "" |

### Data Validation Rules

#### Student ID
- Must be unique across all rows
- Cannot be empty or null
- Required format: exactly 9 digits

#### Names
- Cannot be empty or null
- Should handle Unicode characters for international names
- Maximum length: 50 characters each

#### Gender
- Must be one of: "M", "F"
- Case-insensitive validation

#### Class
- Cannot be empty for scorer input
- Format: Alphanumeric identifier (e.g., "1", "2", "3", "Class1", "Room101")
- Must be consistent across students in same class

#### Academic Score
- Range: 0.0 to 100.0
- Null values will be treated as 0.0
- Decimal precision: up to 2 decimal places

#### Behavior Rank
- Must be one of: "A", "B", "C", "D"
- A = Excellent, B = Good, C = Almost Good, D = Not Good
- Case-insensitive validation
- Null values will be treated as "A" (Excellent)
- **Expected Distribution**: Most students should be A, then B, with steep drop to C, and D being rare

#### Studentiality Rank
- Must be one of: "A", "B", "C", "D"
- A = Excellent (consistently completes homework, proactive in studies), B = Good (usually completes work, engaged), C = Almost Good (sometimes misses assignments, needs reminders), D = Not Good (frequently misses work, needs significant support)
- Case-insensitive validation
- Null values will be treated as "A" (Excellent)
- **Expected Distribution**: Similar to behavior rank - most students should be A, then B, with steep drop to C, and D being rare
- **Independent of Behavior Rank**: A student can have different behavior and studentiality rankings (e.g., well-behaved but struggles with homework completion)

#### Assistance Package
- Boolean values: true/false, 1/0, yes/no
- Case-insensitive
- Null values will be treated as false

#### School of Origin
- Optional column for school distribution balance
- Can contain any string identifier for the student's previous school
- Empty string "" indicates no school data
- Used for calculating school origin balance in the School Layer scoring
- Enables adaptive distribution rules based on school sizes

#### Social Preferences
- **Preferred Friends**: Up to 3 optional columns (preferred_friend_1, preferred_friend_2, preferred_friend_3)
- **Disliked Peers**: Up to 5 optional columns (disliked_peer_1 through disliked_peer_5)
- Student IDs in preferences must exist in the dataset
- Self-references are ignored
- Duplicate IDs across preference columns are removed
- Empty string "" indicates no preference for that slot

#### Force Class
- Optional constraint to force student placement
- If specified, student cannot be moved by optimizer
- Must be a valid class identifier if not empty
- Empty string "" means no constraint
- Overrides optimization algorithms for this student

#### Force Friend
- Optional constraint to force group placement
- Students listed must be placed in the same class
- All students in the group move together during optimization
- Student IDs must exist in the dataset
- Empty string "" means no constraint
- Creates optimization constraint groups

## Sample Input File

```csv
student_id,first_name,last_name,gender,class,academic_score,behavior_rank,studentiality_rank,assistance_package,school,preferred_friend_1,preferred_friend_2,preferred_friend_3,disliked_peer_1,disliked_peer_2,disliked_peer_3,disliked_peer_4,disliked_peer_5,force_class,force_friend
317328593,John,Smith,M,1,85.5,B,A,false,School A,203765489,213568467,,456789123,891234567,,,,,
203765489,Sarah,Johnson,F,1,92.0,A,A,false,School B,317328593,456789123,,891234567,,,,203765489,213568467
213568467,Ahmed,Ali,M,2,78.3,C,B,true,School A,456789123,234567890,,317328593,891234567,,,203765489,213568467
456789123,Maria,Garcia,F,2,88.7,B,B,false,School C,203765489,213568467,,891234567,234567890,,,,
891234567,David,Brown,M,3,91.2,A,C,false,School B,317328593,234567890,,456789123,,,,3,
234567890,Emma,Wilson,F,3,82.4,B,A,true,School A,891234567,345678901,,317328593,456789123,,,,
```

## Output CSV Formats

### Student Scores Output
All input columns plus:
- `student_score`: Individual student satisfaction score (0-100)
- `friend_satisfaction_percentage`: Percentage of preferred friends placed in same class (0-100%)
- `conflict_avoidance_percentage`: Percentage of disliked peers avoided (0-100%)
- `friends_placed`: Number of preferred friends in same class
- `friends_requested`: Total number of preferred friends (0-3)
- `dislikes_avoided`: Number of disliked peers in different classes
- `dislikes_total`: Total number of disliked peers (0-5)
- `force_class_applied`: Whether force class constraint was applied
- `force_friend_group`: Group ID if part of forced friend group

### Class Scores Output
- `class_id`: Class identifier
- `class_score`: Overall class score (0-100)
- `gender_balance_score`: Gender balance score (0-100)
- `total_students`: Number of students in class
- `male_count`: Number of male students
- `female_count`: Number of female students
- `avg_academic_score`: Average academic score in class
- `avg_behavior_rank`: Average behavior rank in class (converted to numeric)
- `assistance_count`: Number of students with assistance packages
- `forced_students`: Number of students with force_class constraint
- `forced_groups`: Number of force_friend groups in class

### School Score Output
Each row represents one school-level balance metric:

- `metric_name`: Name of the school-level metric
  - "Academic Score Balance"
  - "Behavior Rank Balance"  
  - "Class Size Balance"
  - "Assistance Package Balance"
- `metric_value`: Raw value of the metric (e.g., standard deviation)
- `metric_score`: Normalized score (0-100) where 100 = perfect balance
- `class_values`: Comma-separated values for each class (e.g., "85.5,87.2,86.1")
- `standard_deviation`: Standard deviation across classes for this metric
- `balance_score`: How well-balanced this metric is across classes (0-100)

## Summary Score Output
- `layer_name`: Name of the scoring layer (Student, Class, School)
- `layer_score`: Average score for this layer (0-100)
- `layer_weight`: Weight applied to this layer
- `weighted_score`: Layer score multiplied by weight
- `total_final_score`: Overall weighted average of all three layers (0-100)

## School Layer Metrics (Inter-Class Balance)
The school layer evaluates how balanced classes are when compared to each other. It measures distribution equality across classes for:

### School Layer Balance Metrics
- **Academic Score Balance**: Measures how similar average academic scores are across classes
- **Behavior Rank Balance**: Measures how similar average behavior ranks are across classes  
- **Studentiality Rank Balance**: Measures how similar average studentiality ranks are across classes
- **Class Size Balance**: Measures how similar class sizes are across all classes
- **Assistance Package Balance**: Measures how evenly assistance package students are distributed
- **School Origin Balance**: Measures how well students from different origin schools are distributed across classes using adaptive rules based on school sizes

### Three-Layer System Summary
- **Student Layer**: Individual student satisfaction (friend placement, conflict avoidance)
- **Class Layer**: Intra-class balance (gender balance within each class)
- **School Layer**: Inter-class balance (comparing averages between classes)

### Perfect School Layer Score
A perfect school layer score (100) is achieved when all classes have:
- Identical average academic scores
- Identical average behavior ranks
- Identical average studentiality ranks
- Identical number of students
- Identical number of assistance package students
- Optimal school origin distribution based on adaptive rules:
  - Large schools (>40 students): Present in at least 80% of classes
  - Medium schools (20-40 students): Present in at least 60% of classes
  - Small schools (<20 students): Present in at least 40% of classes
  - No single school dominates any class (max 60% from one school)

### Final Summary Score
The summary score combines all three layers using weighted averaging to produce a single overall score reflecting the quality of the entire student placement system.

## Constraint Handling

### Force Class Constraints
- Students with `force_class` specified cannot be moved by optimizer
- Validation ensures force_class refers to existing class
- These students are excluded from optimization moves
- Scorer includes these students in all calculations

### Force Friend Constraints
- Students with matching `force_friend` values form a group
- All students in a group must be in the same class
- Optimizer treats the group as a single unit
- Group moves are atomic (all or nothing)
- Validation ensures all IDs in force_friend exist

### Behavior Rank Conversion
For numerical calculations, behavior ranks are converted:
- A = 1 (Excellent)
- B = 2 (Good)
- C = 3 (Almost Good)
- D = 4 (Not Good)

### Studentiality Rank Conversion
For numerical calculations, studentiality ranks are converted:
- A = 1 (Excellent)
- B = 2 (Good)
- C = 3 (Almost Good)
- D = 4 (Not Good)

## File Naming Conventions
- Input: `students_input.csv`
- Output directory: `results_YYYY-MM-DD_HH-MM-SS/`
- Student scores: `student_scores.csv`
- Class scores: `class_scores.csv`
- School scores: `school_scores.csv`
- Summary scores: `summary_scores.csv` 