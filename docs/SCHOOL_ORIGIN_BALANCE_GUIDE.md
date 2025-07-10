# School Origin Balance Feature Guide

## Overview

The School Origin Balance feature addresses fairness issues in class distribution by ensuring students from different origin schools are distributed appropriately across classes. This prevents situations where some classes consist entirely of students from 2 schools while others have diverse representation.

## Problem This Solves

**Before:** You might have:
- Class 1: 80% from School A, 20% from School B
- Class 2: 100% from School C
- Class 3: Mix of all 5 schools

**After:** With school origin balance:
- All classes have more balanced representation
- Large schools are present in most classes
- Small schools aren't forced to spread too thinly (preserving friend groups)

## How It Works

### Adaptive Distribution Rules

The system uses different targets based on school sizes:

- **Large schools (>40 students)**: Should be present in at least **80%** of classes
- **Medium schools (20-40 students)**: Should be present in at least **60%** of classes  
- **Small schools (<20 students)**: Should be present in at least **40%** of classes

### Anti-Dominance Rule

No single school should dominate any class (maximum **60%** from one school per class).

### Scoring Algorithm

The final score combines:
- **70%** representation score (how well schools meet their presence targets)
- **30%** non-dominance score (how well classes avoid single-school domination)

## Setup Instructions

### Step 1: Add School Column to Your CSV

Add a `school` column to your student data:

```csv
student_id,first_name,last_name,gender,class,academic_score,behavior_rank,studentiality_rank,assistance_package,school,preferred_friend_1,...
317328593,John,Smith,M,1,85.5,B,A,false,Beit Sefer Aleph,203765489,...
203765489,Sarah,Johnson,F,1,92.0,A,A,false,School Beta,317328593,...
213568467,Ahmed,Ali,M,2,78.3,C,B,true,Beit Sefer Aleph,456789123,...
```

**Notes:**
- The `school` column is optional for backwards compatibility
- Empty values (`""`) are allowed
- Use any string identifier for the school name

### Step 2: Enable in Configuration

Create or modify your configuration file to include school origin balance:

```yaml
weights:
  school_layer:
    school_origin_balance: 0.2    # Set to > 0.0 to enable (recommended: 0.1-0.3)
    
normalization:
  school_origin_factor: 20.0      # Normalization factor (default works well)
```

### Step 3: Run Optimization

Use the configuration with any optimizer:

```bash
# Using CLI
python -m meshachvetz.cli.main optimize --config config/school_origin_example.yaml --input students.csv

# Or through interactive CLI
python -m meshachvetz.cli.main
# Then select: 2. Optimize Student Placement
# Choose your configuration file
```

## Configuration Options

### Weights

- `school_origin_balance`: Weight for school origin balance (0.0 = disabled, 0.1-0.3 = typical)
- Higher values prioritize school distribution over other factors
- Default: `0.0` (disabled for backwards compatibility)

### Normalization Factor

- `school_origin_factor`: Controls sensitivity to school distribution imbalances
- Higher values = more penalty for poor distribution
- Default: `20.0` (works well for most cases)

## Understanding the Results

### Reports Include

1. **School Origin Balance Score**: Overall score (0-100)
2. **Representation Scores**: How well each school meets its target presence
3. **Dominance Scores**: How well classes avoid single-school domination
4. **Adaptive Targets**: The calculated targets for each school based on size
5. **Class Distribution**: Detailed breakdown by class and school

### Example Report Output

```
School Origin Balance: 74.81
  - Average Representation: 83.33
  - Average Dominance: 54.94
  
Representation Scores:
  - School A (60 students, large): 100.0 (target: 80% presence)
  - School B (50 students, large): 100.0 (target: 80% presence)  
  - School C (40 students, medium): 100.0 (target: 60% presence)
  - School D (30 students, medium): 66.7 (target: 60% presence)
  - School E (15 students, small): 50.0 (target: 40% presence)
```

## Best Practices

### Weight Recommendations

- **Conservative**: `0.1` - Gentle influence on distribution
- **Balanced**: `0.2` - Good balance with other factors  
- **Aggressive**: `0.3` - Strong emphasis on school distribution

### When to Use

✅ **Good use cases:**
- You have 3+ schools with varying sizes
- Some classes are dominated by 1-2 schools
- You want to improve fairness while preserving friendships

❌ **Not recommended when:**
- All students are from the same school
- You have very strict friend group requirements
- School origin data is unreliable

### Balancing with Other Factors

Consider adjusting other weights when enabling school origin balance:

```yaml
# Example balanced configuration
weights:
  layers:
    student: 0.7          # Still prioritize student satisfaction
    class: 0.1            # Gender balance
    school: 0.2           # School-wide metrics (including school origin)
  
  school_layer:
    behavior_balance: 0.3
    studentiality_balance: 0.3
    assistance_balance: 0.15
    school_origin_balance: 0.2   # Add school origin
    academic_balance: 0.05
```

## Troubleshooting

### Common Issues

**Problem**: School origin balance score is always 100
- **Cause**: Weight is set to 0.0
- **Solution**: Set `school_origin_balance` > 0.0 in your config

**Problem**: Small schools are split across all classes
- **Cause**: Weight is too high or targets too aggressive
- **Solution**: Reduce weight or check if your data has correct school sizes

**Problem**: Classes are still dominated by single schools
- **Cause**: Other constraints (force_friend, etc.) preventing movement
- **Solution**: Check force constraints or increase weight

### Validation Errors

**Error**: "School column not found"
- **Solution**: Add `school` column to your CSV (can be empty)

**Error**: "School origin factor must be positive"
- **Solution**: Set `school_origin_factor` > 0.0 in normalization section

## Advanced Usage

### Custom Targets

While the adaptive targets work well for most cases, you can understand and modify the logic by looking at the size categories:

```python
# In the code, schools are categorized as:
if school_size > 40:
    category = 'large'    # 80% target
elif school_size >= 20:
    category = 'medium'   # 60% target
else:
    category = 'small'    # 40% target
```

### Integration with Other Features

School origin balance works seamlessly with:
- Friend preferences (won't break friend groups unnecessarily)
- Force constraints (respects force_class and force_friend)
- Other school layer metrics (academic, behavior, assistance balance)
- All optimization algorithms (genetic, simulated annealing, local search)

## Example Scenarios

### Scenario 1: Large School Merger
You have students from 5 schools merging into one institution:
- School A: 60 students
- School B: 50 students  
- School C: 40 students
- School D: 30 students
- School E: 15 students

**Configuration**: Use `school_origin_balance: 0.2` to ensure fair distribution while maintaining friend groups.

### Scenario 2: Regional Consolidation
Students from multiple small schools (15-25 each) joining:

**Configuration**: Use `school_origin_balance: 0.15` to gently encourage mixing without forcing small schools to split completely.

### Scenario 3: Existing Institution
Adding school origin awareness to existing class optimization:

**Configuration**: Start with `school_origin_balance: 0.1` and gradually increase if needed.

## Technical Details

The school origin balance feature uses the Shannon diversity index for mathematical rigor and includes comprehensive statistics tracking. It's fully integrated with the three-layer scoring system and maintains backwards compatibility when disabled.

For technical implementation details, see:
- `src/meshachvetz/data/models.py` - Student and Class models with school support
- `src/meshachvetz/scorer/school_scorer.py` - School origin balance calculations
- `docs/02_data_format_specification.md` - Data format details
- `docs/03_scorer_design.md` - Scoring system integration 