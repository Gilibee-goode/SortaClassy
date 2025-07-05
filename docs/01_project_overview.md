# Meshachvetz - Project Overview

## Project Description
Meshachvetz is a suite of tools designed to help teachers sort students into balanced classes and create a well-organized school structure. The system optimizes student placement based on multiple criteria including social preferences, academic balance, and demographic distribution.

## Core Objectives
- **Balanced Class Formation**: Create classes that are balanced across multiple dimensions
- **Student Satisfaction**: Maximize placement of students with preferred peers while minimizing conflicts with disliked peers
- **School-wide Optimization**: Ensure all classes have similar characteristics and quality
- **Flexible Configuration**: Allow educators to adjust weights and priorities for different criteria

## System Architecture

### Two-Phase Approach
1. **Scorer Phase**: Evaluate existing student-class assignments
2. **Optimizer Phase**: Improve assignments through iterative algorithms

### Three-Layer Scoring System
1. **Student Layer**: Individual student satisfaction metrics
2. **Class Layer**: Intra-class balance and composition metrics  
3. **School Layer**: Inter-class balance and equity metrics

## Key Features
- CSV-based input/output for easy integration with existing systems
- Weighted scoring system for customizable priorities
- Multiple optimization algorithms (OR-Tools, genetic algorithms)
- Comprehensive reporting and analysis
- Modular design for easy extension

## Technology Stack
- **Language**: Python 3.8+
- **Optimization**: OR-Tools, genetic algorithms
- **Data Processing**: pandas, numpy
- **Configuration**: YAML/JSON for weights and parameters
- **Output**: CSV reports and analysis files

## Project Structure
```
meshachvetz/
├── docs/                    # Design documentation
├── src/
│   ├── scorer/             # Scoring system implementation
│   ├── optimizer/          # Optimization algorithms
│   ├── data/               # Data models and validation
│   └── utils/              # Shared utilities
├── tests/                  # Unit and integration tests
├── examples/               # Sample data and use cases
└── config/                 # Configuration files
```

## Development Phases
1. **Phase 1**: Scorer implementation and testing
2. **Phase 2**: Optimizer development and integration
3. **Phase 3**: Performance optimization and advanced features
4. **Phase 4**: User interface and deployment tools 