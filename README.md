# Student Class Assignment Program

A Python program for optimizing student class assignments based on various constraints and preferences.

## Project Structure

```
student_class_program/
├── data/               # Data files and test cases
├── src/               # Source code
│   ├── models/        # Data models and structures
│   ├── constraints/   # Constraint definitions
│   └── optimizers/    # Optimization algorithms
└── tests/             # Test cases
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Test Cases

The `data/test_cases` directory contains various test scenarios:
- `simple_test.csv`: Basic test case with 15 students and simple constraints

## Development Status

Currently in Phase 1: Basic System Implementation
- [ ] Basic constraint checking
- [ ] Simple greedy algorithm
- [ ] Basic scoring system 