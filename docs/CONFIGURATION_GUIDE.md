# Configuration Guide

## Overview
The Meshachvetz system provides flexible configuration options for customizing weights, normalization factors, and other parameters. This guide explains all available configuration methods and what each parameter does.

## 🔧 Configuration Methods

### 1. Custom YAML Configuration Files (Recommended)

Create your own configuration file with custom values:

```yaml
# my_custom_config.yaml
weights:
  student_layer:
    friends: 0.8      # Prioritize friend placement more
    dislikes: 0.2     # Prioritize conflict avoidance less
  
  class_layer:
    gender_balance: 1.0
  
  school_layer:
    academic_balance: 0.4     # Increase academic balance importance
    behavior_balance: 0.1     # Decrease behavior balance importance
    size_balance: 0.4         # Increase size balance importance
    assistance_balance: 0.1   # Decrease assistance balance importance
  
  layers:
    student: 0.6    # Increase student satisfaction weight
    class: 0.1      # Decrease class balance weight  
    school: 0.3     # Keep school balance weight same

normalization:
  academic_score_factor: 1.5    # Less sensitive to academic imbalances
  behavior_rank_factor: 40.0    # More sensitive to behavior imbalances
  class_size_factor: 8.0        # More sensitive to size imbalances
  assistance_count_factor: 15.0 # More sensitive to assistance imbalances
```

**Usage:**
```bash
./run_meshachvetz.sh score students.csv --config my_custom_config.yaml
```

### 2. CLI Weight Overrides (Quick Adjustments)

Override specific weights without creating a config file:

```bash
# Override layer weights
./run_meshachvetz.sh score students.csv \
  --student-weight 0.7 \
  --class-weight 0.1 \
  --school-weight 0.2

# Override student layer sub-weights
./run_meshachvetz.sh score students.csv \
  --friends-weight 0.9 \
  --dislikes-weight 0.1

# Combine multiple overrides
./run_meshachvetz.sh score students.csv \
  --student-weight 0.6 \
  --friends-weight 0.8 \
  --dislikes-weight 0.2
```

### 3. Modifying Default Configuration

Edit the main configuration file directly:
```bash
# Edit the default configuration
nano config/default_scoring.yaml
```

### 4. Viewing Current Configuration

```bash
# View current configuration
./run_meshachvetz.sh config show

# View configuration from custom file
./run_meshachvetz.sh config show --config my_custom_config.yaml
```

## 📊 Configuration Parameters Explained

### Layer Weights (How much each layer contributes to final score)

| Parameter | Default | Description | Range |
|-----------|---------|-------------|-------|
| `student` | 0.5 | Student satisfaction weight | 0.0-1.0 |
| `class` | 0.2 | Class balance weight | 0.0-1.0 |
| `school` | 0.3 | School balance weight | 0.0-1.0 |

**Note**: Weights are automatically normalized, so they don't need to sum to 1.0.

### Student Layer Weights (Within student satisfaction)

| Parameter | Default | Description | Range |
|-----------|---------|-------------|-------|
| `friends` | 0.7 | Friend placement importance | 0.0-1.0 |
| `dislikes` | 0.3 | Conflict avoidance importance | 0.0-1.0 |

### School Layer Weights (Balance across classes)

| Parameter | Default | Description | Range |
|-----------|---------|-------------|-------|
| `academic_balance` | 0.3 | Academic score balance | 0.0-1.0 |
| `behavior_balance` | 0.2 | Behavior rank balance | 0.0-1.0 |
| `size_balance` | 0.3 | Class size balance | 0.0-1.0 |
| `assistance_balance` | 0.2 | Assistance package balance | 0.0-1.0 |

### Normalization Factors (Sensitivity to imbalances)

| Parameter | Default | Description | Effect |
|-----------|---------|-------------|--------|
| `academic_score_factor` | 2.0 | Academic score sensitivity | Higher = more sensitive to academic imbalances |
| `behavior_rank_factor` | 35.0 | Behavior rank sensitivity | Higher = more sensitive to behavior imbalances |
| `class_size_factor` | 5.0 | Class size sensitivity | Higher = more sensitive to size imbalances |
| `assistance_count_factor` | 10.0 | Assistance package sensitivity | Higher = more sensitive to assistance imbalances |

## 🎯 Common Configuration Scenarios

### Scenario 1: Prioritize Student Happiness
```yaml
weights:
  layers:
    student: 0.8    # Much higher student weight
    class: 0.1      # Lower class weight
    school: 0.1     # Lower school weight
  student_layer:
    friends: 0.9    # Heavily prioritize friends
    dislikes: 0.1   # Less concerned about conflicts
```

### Scenario 2: Prioritize Academic Balance
```yaml
weights:
  layers:
    student: 0.2    # Lower student weight
    class: 0.2      # Keep class weight
    school: 0.6     # Much higher school weight
  school_layer:
    academic_balance: 0.6     # High academic balance
    behavior_balance: 0.2     # Normal behavior balance
    size_balance: 0.1         # Lower size balance
    assistance_balance: 0.1   # Lower assistance balance
```

### Scenario 3: Strict Balance Requirements
```yaml
normalization:
  academic_score_factor: 5.0    # Very sensitive to academic imbalances
  behavior_rank_factor: 50.0    # Very sensitive to behavior imbalances
  class_size_factor: 10.0       # Very sensitive to size imbalances
  assistance_count_factor: 20.0 # Very sensitive to assistance imbalances
```

### Scenario 4: Large Classes Setup
```yaml
class_config:
  target_classes: 3           # Fewer classes
  min_class_size: 25          # Larger minimum
  max_class_size: 40          # Larger maximum
  preferred_class_size: 35    # Larger preferred size
  allow_uneven_classes: true  # Allow some variation
```

## 📈 Understanding the Impact

### Weight Impact Examples

**Default Configuration:**
```
Final Score = (Student_Score × 0.5) + (Class_Score × 0.2) + (School_Score × 0.3)
```

**Student-Focused Configuration:**
```
Final Score = (Student_Score × 0.8) + (Class_Score × 0.1) + (School_Score × 0.1)
```

### Normalization Factor Impact

The normalization factors control how much imbalance is tolerated:

**Example**: Classes with academic averages of 85, 87, 89
- Standard deviation: 1.63
- **Low sensitivity** (factor=1.0): Score = 100 - (1.63 × 1.0) = 98.37
- **Medium sensitivity** (factor=2.0): Score = 100 - (1.63 × 2.0) = 96.74
- **High sensitivity** (factor=5.0): Score = 100 - (1.63 × 5.0) = 91.85

## 🔍 Testing Your Configuration

### Compare Configurations
```bash
# Test with default configuration
./run_meshachvetz.sh score students.csv --detailed

# Test with custom configuration
./run_meshachvetz.sh score students.csv --config my_config.yaml --detailed

# Test with CLI overrides
./run_meshachvetz.sh score students.csv --student-weight 0.8 --detailed
```

### Generate Reports for Analysis
```bash
# Generate detailed CSV reports
./run_meshachvetz.sh score students.csv --config my_config.yaml --reports --output results/
```

## ⚠️ Configuration Tips

### Best Practices
1. **Start with defaults**: Understand the baseline before making changes
2. **Test incrementally**: Change one parameter at a time to see its effect
3. **Document changes**: Keep notes on why you made specific changes
4. **Validate results**: Always check that results make sense for your context

### Common Mistakes
1. **Extreme weights**: Avoid setting weights to 0.0 or 1.0 unless intentional
2. **Ignoring normalization**: Very high normalization factors can dominate scores
3. **Not testing**: Always test configuration changes with your actual data
4. **Over-optimization**: Don't fine-tune based on a single test case

### Troubleshooting
```bash
# Check if configuration is valid
./run_meshachvetz.sh config show --config my_config.yaml

# Run with verbose output to see detailed calculations
./run_meshachvetz.sh score students.csv --config my_config.yaml --verbose --detailed
```

## 📚 Configuration File Templates

### Balanced Configuration (Default)
```yaml
# Copy from config/default_scoring.yaml
```

### Student-Focused Configuration
```yaml
# See examples/student_focused_config.yaml
```

### Academic-Focused Configuration  
```yaml
# See examples/academic_focused_config.yaml
```

### Strict Balance Configuration
```yaml
# See examples/strict_balance_config.yaml
```

---

This guide covers all available configuration options. For specific use cases or questions, refer to the other documentation files or use the `--help` option with CLI commands. 