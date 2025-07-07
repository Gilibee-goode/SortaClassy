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

**🎯 EASY INSTALLATION (Recommended for most users):**

**Windows Users:**
1. Download the project files to your computer
2. Double-click `install.bat` 
3. Wait for installation to complete
4. You're ready to go!

**Mac/Linux Users:**
1. Download the project files to your computer
2. Double-click `install.sh` (or run `./install.sh` in terminal)
3. Wait for installation to complete
4. You're ready to go!

**🔧 MANUAL INSTALLATION (For advanced users):**

If you prefer to install manually or the easy installation doesn't work:

```bash
# Create virtual environment
python -m venv meshachvetz_env

# Activate virtual environment
# On Windows:
meshachvetz_env\Scripts\activate
# On Mac/Linux:
source meshachvetz_env/bin/activate

# Install Meshachvetz
pip install -e .
```

**✅ VERIFY INSTALLATION:**

After installation, test that everything works:

**Windows:** Double-click `run_meshachvetz.bat`
**Mac/Linux:** Run `./run_meshachvetz.sh`

You should see the help message if everything is working correctly.

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

### 🎯 Interactive Mode (Recommended for Beginners)

The easiest way to use Meshachvetz is through the interactive menu system:

**Windows:**
```bash
run_meshachvetz.bat
```

**Mac/Linux:**
```bash
./run_meshachvetz.sh
```

This launches the interactive menu where you can:

#### Main Menu Options:
1. **Score Assignment** - Get scores for current class assignments
2. **Optimize Assignment** - Improve class assignments using AI algorithms
3. **Compare Algorithms** - Compare different optimization approaches
4. **Configuration** - Manage system settings and weights
5. **Generate Assignment** - Create initial class assignments from scratch
6. **Validate Data** - Check if your CSV file is correctly formatted
7. **Baseline Test** - Generate performance benchmarks for comparison
8. **Advanced Options** - Access detailed parameter configuration
9. **Master Solver (Coming Soon)** - Automated best-result optimization
10. **Exit** - Leave the program

#### 🔧 Advanced Options (NEW!)

Access option 8 from the main menu to configure detailed parameters:

**📊 Logging Options:**
- **Log Level**: Choose from minimal, normal, detailed, or debug output
- **Verbose Mode**: Enable extra detailed information
- **Quiet Mode**: Suppress non-essential output

**🎯 Algorithm Parameters:**
- **Min Friends**: Minimum number of friends required per student (default: 1)
- **Max Iterations**: Maximum optimization iterations (default: 1000)
- **Early Stop**: Stop optimization after this many iterations without improvement (default: 100)
- **Accept Neutral**: Allow moves that don't improve the score (default: false)

**🔒 Constraint Options:**
- **Force Constraints**: Respect force_class and force_friend requirements (default: true)
- **Init Strategy**: Choose initialization method (constraint_aware, balanced, random, academic_balanced)
- **Target Classes**: Set specific number of classes (default: auto-calculate)
- **No Auto Init**: Disable automatic initialization for unassigned students

**📁 Output Control:**
- **Generate Reports**: Create detailed CSV reports (default: true)
- **Detailed Output**: Include comprehensive statistics (default: true)
- **Output Directory**: Custom location for generated files
- **Output Prefix**: Custom prefix for generated file names

**🎲 Baseline Options:**
- **Random Seed**: Set seed for reproducible results (default: random)
- **Number of Runs**: How many baseline runs to perform (default: 10)

**🔧 Algorithm Selection:**
- **Algorithms**: Choose which optimization algorithms to use
- **Strategy**: Select comparison strategy (parallel, sequential, best_of, compare)

#### Using Advanced Options:

1. **Quick Configuration**: Each operation (Score, Optimize, etc.) now asks if you want to configure advanced options
2. **Persistent Settings**: Configure once, use for all operations in the session
3. **Easy Reset**: Reset to defaults at any time
4. **Show Current**: View all current settings before making changes

#### Example Interactive Session:

```
🎯 MESHACHVETZ - Student Class Assignment Optimizer
============================================================

🏠 MAIN MENU
------------------------------
1. Score Assignment
2. Optimize Assignment
...
8. Advanced Options
------------------------------
Select option: 8

⚙️  ADVANCED OPTIONS
------------------------------
1. Configure Advanced Options
2. Show Current Options
3. Reset to Defaults
4. Quick Configure for Next Operation
5. Back to Main Menu
------------------------------
Select option: 1

Configuration categories:
1. Logging Options
2. Algorithm Parameters
3. Constraint Options
...
```

### Command Line Mode (For Advanced Users)

You can also use Meshachvetz directly from the command line:

#### 1. Score Your Student Assignments

To get a score for your current class assignments:

**Windows:**
```bash
run_meshachvetz.bat score your_students.csv
```

**Mac/Linux:**
```bash
./run_meshachvetz.sh score your_students.csv
```

**Example:**
```bash
# Windows
run_meshachvetz.bat score examples/test_data/perfect_score_test.csv

# Mac/Linux
./run_meshachvetz.sh score examples/test_data/perfect_score_test.csv
```

This will show you:
- Overall score (0-100)
- Breakdown by category
- Number of students and classes
- Basic statistics

#### 2. Generate Detailed Reports

To get comprehensive CSV reports saved to files:

**Windows:**
```bash
run_meshachvetz.bat score your_students.csv --reports
```

**Mac/Linux:**
```bash
./run_meshachvetz.sh score your_students.csv --reports
```

This creates a folder with detailed reports including:
- Summary of all scores
- Individual student details
- Class-by-class analysis
- School-wide balance metrics
- Configuration used

#### 3. Validate Your Data

Before scoring, check if your CSV file is formatted correctly:

**Windows:**
```bash
run_meshachvetz.bat validate your_students.csv
```

**Mac/Linux:**
```bash
./run_meshachvetz.sh validate your_students.csv
```

This will tell you about any errors in your data file.

#### 4. View Configuration

To see what weights and settings are being used:

**Windows:**
```bash
run_meshachvetz.bat show-config
```

**Mac/Linux:**
```bash
./run_meshachvetz.sh show-config
```

### Advanced Command Line Options

#### Logging Control (NEW!)
```bash
# Set logging level
./run_meshachvetz.sh score students.csv --log-level debug
./run_meshachvetz.sh score students.csv --log-level minimal

# Quiet mode (less output)
./run_meshachvetz.sh score students.csv --quiet

# Verbose mode (more details) 
./run_meshachvetz.sh score students.csv --verbose
```

#### Algorithm Parameters (NEW!)
```bash
# Set minimum friends requirement
./run_meshachvetz.sh optimize students.csv --min-friends 2

# Set maximum iterations
./run_meshachvetz.sh optimize students.csv --max-iterations 2000

# Set early stopping threshold
./run_meshachvetz.sh optimize students.csv --early-stop 200

# Allow neutral moves
./run_meshachvetz.sh optimize students.csv --accept-neutral
```

#### Constraint Options (NEW!)
```bash
# Choose initialization strategy
./run_meshachvetz.sh optimize students.csv --init-strategy balanced

# Set target number of classes
./run_meshachvetz.sh optimize students.csv --target-classes 5

# Disable force constraints
./run_meshachvetz.sh optimize students.csv --no-force-constraints
```

#### Output Control (NEW!)
```bash
# Custom output directory
./run_meshachvetz.sh score students.csv --reports --output my_results

# Disable detailed output
./run_meshachvetz.sh score students.csv --no-detailed

# Custom output prefix for baseline
./run_meshachvetz.sh baseline students.csv --output-prefix my_baseline
```

#### Baseline Options (NEW!)
```bash
# Set random seed for reproducible results
./run_meshachvetz.sh baseline students.csv --random-seed 42

# Set number of baseline runs
./run_meshachvetz.sh baseline students.csv --num-runs 20
```

#### Legacy Options (Still Supported)
```bash
# Adjust scoring weights
./run_meshachvetz.sh score students.csv --student-weight 0.7
./run_meshachvetz.sh score students.csv --class-weight 0.4
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
2. **Validate**: 
   - **Windows:** `run_meshachvetz.bat validate students.csv`
   - **Mac/Linux:** `./run_meshachvetz.sh validate students.csv`
3. **Score**: 
   - **Windows:** `run_meshachvetz.bat score students.csv --reports --verbose`
   - **Mac/Linux:** `./run_meshachvetz.sh score students.csv --reports --verbose`
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

### "Python not found" or "Command not found"
- Make sure you ran the installation script first
- On Windows: Double-click `install.bat`
- On Mac/Linux: Run `./install.sh`

## Getting Help

### Command Help
**Windows:**
```bash
run_meshachvetz.bat --help
run_meshachvetz.bat score --help
run_meshachvetz.bat validate --help
```

**Mac/Linux:**
```bash
./run_meshachvetz.sh --help
./run_meshachvetz.sh score --help
./run_meshachvetz.sh validate --help
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