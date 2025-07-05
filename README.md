# Meshachvetz - Student Class Assignment Optimizer

A comprehensive suite of tools designed to help educators create balanced student class assignments based on multiple criteria including social preferences, academic balance, and demographic distribution.

## Features

- **Three-Layer Scoring System**: Student satisfaction, class balance, and school-wide equity
- **Multiple Optimization Algorithms**: Genetic algorithms, simulated annealing, OR-Tools integration
- **Flexible Configuration**: YAML-based configuration for weights and parameters
- **Comprehensive Reporting**: Detailed CSV reports and analytics
- **Force Constraints**: Support for mandatory class and friend group placements

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from Source
```bash
git clone https://github.com/meshachvetz/meshachvetz.git
cd meshachvetz
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/meshachvetz/meshachvetz.git
cd meshachvetz
pip install -e ".[dev]"
```

## Quick Start

### 1. Prepare Your Data
Create a CSV file with student data following the specified format (see [Data Format Specification](docs/02_data_format_specification.md)).

### 2. Run the Scorer
```bash
meshachvetz score --input students.csv --output results/
```

### 3. Run the Optimizer (Coming in Phase 2)
```bash
meshachvetz optimize --input students.csv --output results/ --algorithm genetic
```

## Documentation

- [Project Overview](docs/01_project_overview.md)
- [Data Format Specification](docs/02_data_format_specification.md)
- [Scorer Design](docs/03_scorer_design.md)
- [Optimizer Design](docs/04_optimizer_design.md)
- [Implementation Plan](docs/05_implementation_plan.md)
- [Technical Specifications](docs/06_technical_specifications.md)

## Development Status

This project is currently in **Phase 1: Foundation and Scorer** development.

### Current Phase: Week 1 - Project Setup and Data Layer ✅ COMPLETED
- [x] Project structure setup
- [x] Requirements and packaging
- [x] Data validation and loading utilities
- [x] Configuration system
- [x] Sample datasets

**Next Phase: Week 2 - Scorer Implementation**

See [Implementation Plan](docs/05_implementation_plan.md) for detailed roadmap.

## Contributing

This project follows a structured, phase-based development approach. Please see the [Implementation Plan](docs/05_implementation_plan.md) for current development priorities.

## License

This project is licensed under the MIT License.

## Support

For questions and support, please refer to the documentation in the `docs/` directory. 