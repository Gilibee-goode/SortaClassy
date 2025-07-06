# Meshachvetz CLI User Guide

**A Simple Guide to Using the Meshachvetz Student Assignment Scoring System**

## What is Meshachvetz?

Meshachvetz is a tool that helps educators evaluate how well students are assigned to classes. It looks at three main things:
- **Student Happiness**: Are students placed with their friends and away from conflicts?
- **Class Balance**: Are classes balanced in terms of gender?
- **School Balance**: Are academic abilities and other factors evenly distributed across all classes?

The tool gives you a score from 0-100, where 100 means perfect assignments and 0 means very poor assignments.

## Getting Started

### Step 1: Install the System

If you haven't already, you'll need to install Meshachvetz:

```bash
pip install -e .
```

### Step 2: Prepare Your Student Data

Create a CSV file (Excel can save as CSV) with your student information. The file needs these columns:

**Required columns:**
- `student_id`: 9-digit student ID (e.g., 123456789)
- `first_name`: Student's first name
- `last_name`: Student's last name
- `gender`: M or F
- `class`: Which class they're currently in (1, 2, 3, etc.)
- `academic_score`: Academic score (0-100)
- `behavior_rank`: Behavior grade (A, B, C, D, or E)
- `assistance_package`: true or false (if student needs extra help)

**Optional columns (can be empty):**
- `preferred_friend_1`, `preferred_friend_2`, `preferred_friend_3`: Student IDs of friends they want to be with
- `disliked_peer_1` through `disliked_peer_5`: Student IDs of peers they prefer not to be with
- `force_class`: Force this student into a specific class
- `force_friend`: Force this student to be with specific friends

**Example CSV:**
```csv
student_id,first_name,last_name,gender,class,academic_score,behavior_rank,assistance_package,preferred_friend_1,preferred_friend_2,preferred_friend_3,disliked_peer_1,disliked_peer_2,disliked_peer_3,disliked_peer_4,disliked_peer_5,force_class,force_friend
123456789,John,Smith,M,1,85.5,A,false,987654321,876543210,,111111111,222222222,,,,,
987654321,Sarah,Johnson,F,1,92.0,B,true,123456789,,,333333333,444444444,,,,,
```

## Using the CLI

### Basic Commands

#### 1. Score Your Student Assignments

To get a score for your current class assignments:

```bash
python -m meshachvetz.cli.main score your_students.csv
```

**Example:**
```bash
python -m meshachvetz.cli.main score examples/test_data/perfect_score_test.csv
```

This will show you:
- Overall score (0-100)
- Breakdown by category
- Number of students and classes
- Basic statistics

#### 2. Generate Detailed Reports

To get comprehensive CSV reports saved to files:

```bash
python -m meshachvetz.cli.main score your_students.csv --reports
```

This creates a folder with detailed reports including:
- Summary of all scores
- Individual student details
- Class-by-class analysis
- School-wide balance metrics
- Configuration used

#### 3. Validate Your Data

Before scoring, check if your CSV file is formatted correctly:

```bash
python -m meshachvetz.cli.main validate your_students.csv
```

This will tell you about any errors in your data file.

#### 4. View Configuration

To see what weights and settings are being used:

```bash
python -m meshachvetz.cli.main show-config
```

### Advanced Options

#### Quiet Mode (Less Output)
```bash
python -m meshachvetz.cli.main score your_students.csv --quiet
```

#### Verbose Mode (More Details)
```bash
python -m meshachvetz.cli.main score your_students.csv --verbose
```

#### Custom Output Directory
```bash
python -m meshachvetz.cli.main score your_students.csv --reports --output my_results
```

#### Adjust Scoring Weights
You can change how much each factor matters:

```bash
# Make student happiness more important
python -m meshachvetz.cli.main score your_students.csv --student-weight 0.7

# Make class balance more important  
python -m meshachvetz.cli.main score your_students.csv --class-weight 0.4

# Make school balance more important
python -m meshachvetz.cli.main score your_students.csv --school-weight 0.5
```

#### Detailed Student Analysis
```bash
python -m meshachvetz.cli.main score your_students.csv --detailed
```

## Understanding Your Results

### Score Interpretation

- **85-100**: Excellent assignments! Students are well-placed with friends, classes are balanced
- **70-84**: Good assignments with room for minor improvements
- **55-69**: Moderate assignments - some students may be unhappy or classes unbalanced
- **40-54**: Poor assignments - significant issues with friend placement or balance
- **0-39**: Very poor assignments - major problems need addressing

### Report Files

When you use `--reports`, you'll get these files:

1. **summary_report.csv**: Overview of all scores and metrics
2. **student_details.csv**: Individual student satisfaction and placement
3. **class_details.csv**: Class-by-class gender balance analysis
4. **school_balance.csv**: School-wide distribution metrics
5. **configuration.csv**: Settings and weights used

### Key Metrics to Watch

- **Student Layer Score**: How happy students are (friend placement, conflict avoidance)
- **Class Layer Score**: How balanced classes are (gender distribution)
- **School Layer Score**: How evenly distributed students are across classes
- **Friend Satisfaction Rate**: Percentage of friend requests fulfilled
- **Conflict Rate**: Percentage of students placed with disliked peers

## Example Workflow

1. **Prepare your data**: Create a CSV file with student information
2. **Validate**: `python -m meshachvetz.cli.main validate students.csv`
3. **Score**: `python -m meshachvetz.cli.main score students.csv --reports --verbose`
4. **Review**: Open the generated report files to understand the results
5. **Adjust**: If needed, modify class assignments and re-score

## Common Issues and Solutions

### "Student ID must be exactly 9 digits"
- Make sure all student IDs are 9 digits long
- Add leading zeros if needed: 123456789 not 123456789

### "Gender must be 'M' or 'F'"
- Use only M or F (uppercase) for gender
- Check for typos like "Male" or "Female"

### "Academic score must be between 0 and 100"
- Ensure all academic scores are numbers between 0 and 100
- Check for missing values or text in the score column

### "Behavior rank must be A-E"
- Use only A, B, C, D, or E for behavior ranks
- Check for numbers or other letters

### "Missing required columns"
- Ensure your CSV has all required column names spelled correctly
- Check for extra spaces in column names

## Getting Help

### Command Help
```bash
python -m meshachvetz.cli.main --help
python -m meshachvetz.cli.main score --help
python -m meshachvetz.cli.main validate --help
```

### Sample Data
Look in the `examples/test_data/` folder for sample CSV files to see the correct format.

### Technical Documentation
For more detailed information, see the `docs/` folder with technical specifications.

## Tips for Best Results

1. **Complete Data**: Fill in as many social preferences as possible
2. **Accurate Scores**: Ensure academic scores and behavior ranks are current
3. **Realistic Expectations**: Perfect scores (95-100) are rare in real scenarios
4. **Iterative Process**: Use the tool to evaluate different assignment options
5. **Consider Context**: The tool provides data - use your professional judgment for final decisions

---

*This guide covers the basic usage of the Meshachvetz CLI. For advanced features and technical details, refer to the technical documentation in the `docs/` folder.* 