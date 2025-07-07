#!/usr/bin/env python3
"""
Optimizer CLI for Meshachvetz - Command-line interface for optimizing student assignments.
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add src directory to path for imports
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from meshachvetz import Scorer, Config
from meshachvetz.optimizer import OptimizationManager


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_file_exists(filepath: str) -> str:
    """Validate that a file exists."""
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError(f"File does not exist: {filepath}")
    return filepath


def validate_output_dir(output_dir: str) -> str:
    """Validate and create output directory if needed."""
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def main():
    """Main CLI function for optimization."""
    parser = argparse.ArgumentParser(
        description="Meshachvetz Optimizer - Create optimized student class assignments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimize with default random swap algorithm
  python optimizer_cli.py optimize students.csv

  # Optimize and save to specific file
  python optimizer_cli.py optimize students.csv --output optimized_assignment.csv

  # Optimize with specific algorithm and parameters
  python optimizer_cli.py optimize students.csv --algorithm random_swap --max-iterations 2000

  # Optimize with custom configuration
  python optimizer_cli.py optimize students.csv --config custom_optimizer.yaml

  # Optimize with custom minimum friends constraint
  python optimizer_cli.py optimize students.csv --min-friends 2

  # Optimize with detailed progress and reports
  python optimizer_cli.py optimize students.csv --verbose --reports --detailed

  # Compare multiple algorithms
  python optimizer_cli.py optimize students.csv --compare-algorithms --output-dir comparison_results
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize student class assignments')
    optimize_parser.add_argument('csv_file', type=validate_file_exists, 
                                help='Path to CSV file containing student data')
    optimize_parser.add_argument('--output', '-o', type=str, 
                                help='Output file for optimized assignment (default: optimized_<input_file>)')
    optimize_parser.add_argument('--output-dir', type=validate_output_dir, 
                                help='Output directory for all generated files')
    optimize_parser.add_argument('--algorithm', '-a', type=str, 
                                choices=['random_swap', 'local_search', 'simulated_annealing', 'genetic', 'or_tools'],
                                default='local_search',
                                help='Optimization algorithm to use (default: local_search)')
    optimize_parser.add_argument('--max-iterations', type=int, default=1000,
                                help='Maximum number of optimization iterations (default: 1000)')
    optimize_parser.add_argument('--config', '-c', type=str, 
                                help='Path to YAML configuration file')
    optimize_parser.add_argument('--reports', '-r', action='store_true', 
                                help='Generate detailed reports')
    optimize_parser.add_argument('--detailed', '-d', action='store_true', 
                                help='Show detailed optimization progress')
    optimize_parser.add_argument('--verbose', '-v', action='store_true', 
                                help='Enable verbose logging')
    optimize_parser.add_argument('--quiet', '-q', action='store_true', 
                                help='Suppress non-essential output')
    optimize_parser.add_argument('--compare-algorithms', action='store_true',
                                help='Compare multiple algorithms (future feature)')
    
    # Initialization options
    optimize_parser.add_argument('--init-strategy', type=str, 
                                choices=['random', 'balanced', 'constraint_aware', 'academic_balanced'],
                                default='constraint_aware',
                                help='Initialization strategy for unassigned students (default: constraint_aware)')
    optimize_parser.add_argument('--no-auto-init', action='store_true',
                                help='Disable automatic initialization of unassigned students')
    optimize_parser.add_argument('--target-classes', type=int, default=5,
                                help='Number of target classes (default: 5, auto-calculated if set to 0)')
    
    # Optimizer-specific options
    optimize_parser.add_argument('--min-friends', type=int, default=1,
                                help='Minimum friends required per student (default: 1, use 0 to disable)')
    optimize_parser.add_argument('--early-stop', type=int, default=100,
                                help='Early stopping threshold (iterations without improvement)')
    optimize_parser.add_argument('--accept-neutral', action='store_true',
                                help='Accept neutral moves (no score change)')
    optimize_parser.add_argument('--force-constraints', action='store_true', default=True,
                                help='Respect force_class and force_friend constraints')
    
    # List algorithms command
    list_parser = subparsers.add_parser('list-algorithms', help='List available optimization algorithms')
    
    # Generate assignment command
    generate_parser = subparsers.add_parser('generate-assignment', help='Generate initial class assignments')
    generate_parser.add_argument('csv_file', type=validate_file_exists,
                                help='Path to CSV file containing student data')
    generate_parser.add_argument('--output', '-o', type=str,
                                help='Output file for generated assignment (default: assignment_<input_file>)')
    generate_parser.add_argument('--output-dir', type=validate_output_dir,
                                help='Output directory for generated files')
    generate_parser.add_argument('--strategy', '-s', type=str,
                                choices=['random', 'balanced', 'constraint_aware', 'academic_balanced'],
                                default='constraint_aware',
                                help='Assignment generation strategy (default: constraint_aware)')
    generate_parser.add_argument('--target-classes', type=int, default=5,
                                help='Number of target classes (default: 5, auto-calculated if set to 0)')
    generate_parser.add_argument('--config', '-c', type=str,
                                help='Path to YAML configuration file')
    generate_parser.add_argument('--verbose', '-v', action='store_true',
                                help='Enable verbose logging')
    generate_parser.add_argument('--quiet', '-q', action='store_true',
                                help='Suppress non-essential output')
    
    # Add compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple optimization algorithms')
    compare_parser.add_argument('input_file', type=str, help='Input CSV file with student data')
    compare_parser.add_argument('--algorithms', nargs='+', 
                               choices=['random_swap', 'local_search', 'simulated_annealing', 'genetic', 'or_tools'],
                               default=['random_swap', 'local_search', 'simulated_annealing', 'genetic'],
                               help='Algorithms to compare (default: all)')
    compare_parser.add_argument('--max-iterations', type=int, default=500,
                               help='Maximum iterations per algorithm (default: 500)')
    compare_parser.add_argument('--output', '-o', type=str,
                               help='Output file for comparison report (CSV format)')
    compare_parser.add_argument('--strategy', type=str,
                               choices=['parallel', 'sequential', 'best_of'],
                               default='parallel',
                               help='Multi-algorithm strategy (default: parallel)')
    compare_parser.add_argument('--init-strategy', type=str,
                               choices=['random', 'balanced', 'constraint_aware', 'academic_balanced'],
                               default='constraint_aware',
                               help='Initialization strategy for unassigned students (default: constraint_aware)')
    compare_parser.add_argument('--target-classes', type=int, default=5,
                               help='Number of target classes (default: 5, auto-calculated if set to 0)')
    compare_parser.add_argument('--min-friends', type=int, default=1,
                               help='Minimum friends constraint (default: 1)')
    compare_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Enable verbose output')
    compare_parser.add_argument('--quiet', '-q', action='store_true',
                               help='Minimal output')

    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Set up logging
    if hasattr(args, 'verbose') and args.verbose:
        setup_logging("DEBUG")
    elif hasattr(args, 'quiet') and args.quiet:
        setup_logging("WARNING")
    else:
        setup_logging("WARNING")  # Default to WARNING, only show INFO with --verbose
    
    try:
        if args.command == 'optimize':
            handle_optimize_command(args)
        elif args.command == 'list-algorithms':
            handle_list_algorithms_command(args)
        elif args.command == 'generate-assignment':
            handle_generate_assignment_command(args)
        elif args.command == 'compare':
            handle_compare_command(args)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Optimization cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def handle_optimize_command(args):
    """Handle the optimize command."""
    print("🎯 Meshachvetz Optimizer")
    print("=" * 40)
    
    # Load configuration
    config = Config()
    if args.config:
        print(f"📋 Loading configuration from: {args.config}")
        config = Config(args.config)
    else:
        print("📋 Using default configuration")
    
    # Create scorer
    scorer = Scorer(config)
    
    # Create optimization manager with algorithm-specific config
    optimizer_config = {
        'min_friends': args.min_friends,
        'early_stop_threshold': args.early_stop,
        'accept_neutral_moves': args.accept_neutral,
        'respect_force_constraints': args.force_constraints,
        'max_iterations': args.max_iterations,
        'default_algorithm': args.algorithm
    }
    
    optimization_manager = OptimizationManager(scorer, optimizer_config)
    
    print(f"📁 Loading student data: {args.csv_file}")
    
    # Load data
    school_data = scorer.load_data(args.csv_file)
    
    print(f"✅ Loaded {school_data.total_students} students in {school_data.total_classes} classes")
    
    # Check assignment status
    assignment_status, unassigned_count = optimization_manager.detect_assignment_status(school_data)
    print(f"📊 Assignment status: {assignment_status.value}")
    if unassigned_count > 0:
        print(f"   Found {unassigned_count} unassigned students")
        if not args.no_auto_init:
            print(f"   Will initialize using {args.init_strategy} strategy")
        else:
            print(f"   Automatic initialization disabled")
    
    # Create output paths
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.csv_file)
        output_file = str(input_path.parent / f"optimized_{input_path.name}")
    
    if args.output_dir:
        output_path = Path(args.output_dir)
        output_file = str(output_path / Path(output_file).name)
    
    print(f"🚀 Starting optimization with {args.algorithm} algorithm...")
    
    # Convert target_classes: 0 means auto-calculate (None), otherwise use the value
    target_classes = None if args.target_classes == 0 else args.target_classes
    
    try:
        result, scoring_result = optimization_manager.optimize_and_save(
            school_data=school_data,
            output_file=output_file,
            algorithm=args.algorithm,
            max_iterations=args.max_iterations,
            initialization_strategy=args.init_strategy,
            auto_initialize=not args.no_auto_init,
            generate_reports=args.reports,
            target_classes=target_classes
        )
        
        # Display results
        if not args.quiet:
            print(f"\n🏆 OPTIMIZATION RESULTS")
            print(f"Algorithm: {result.algorithm_name}")
            print(f"Initial Score: {result.initial_score:.2f}/100")
            print(f"Final Score: {result.final_score:.2f}/100")
            print(f"Improvement: +{result.improvement:.2f} ({result.improvement_percentage:.1f}%)")
            print(f"Execution Time: {result.execution_time:.2f} seconds")
            print(f"Iterations: {result.iterations_completed}/{result.total_iterations}")
            print(f"Constraints: {'✅ Satisfied' if result.constraints_satisfied else '❌ Violated'}")
            
            # Display detailed scoring breakdown from scorer
            print(f"\n📊 DETAILED SCORING BREAKDOWN")
            print(f"Final Score: {scoring_result.final_score:.2f}/100")
            print(f"Total Students: {scoring_result.total_students}")
            print(f"Total Classes: {scoring_result.total_classes}")
            print(f"\n📈 Layer Performance:")
            print(f"   Student Layer: {scoring_result.student_layer_score:.2f}/100 (weight: {scoring_result.layer_weights['student']:.1f})")
            print(f"   Class Layer:   {scoring_result.class_layer_score:.2f}/100 (weight: {scoring_result.layer_weights['class']:.1f})")
            print(f"   School Layer:  {scoring_result.school_layer_score:.2f}/100 (weight: {scoring_result.layer_weights['school']:.1f})")
            
            # Add focused summary with detailed statistics
            if args.detailed:
                focused_summary = optimization_manager.scorer.get_focused_summary(scoring_result)
                print(f"\n{focused_summary}")
            
            if result.constraint_violations:
                print(f"\n⚠️  Constraint Violations:")
                for violation in result.constraint_violations[:5]:  # Show first 5
                    print(f"   - {violation}")
                if len(result.constraint_violations) > 5:
                    print(f"   ... and {len(result.constraint_violations) - 5} more")
            
            # Show detailed progress if requested
            if args.detailed:
                print(f"\n📊 Optimization Progress:")
                print(f"   Best score achieved: {result.best_score_achieved:.2f}")
                if result.convergence_iteration is not None:
                    print(f"   Convergence at iteration: {result.convergence_iteration}")
                
                print(f"   Score history (last 10 iterations):")
                history = result.score_history[-10:]
                for i, score in enumerate(history):
                    iteration = len(result.score_history) - 10 + i
                    print(f"     Iteration {iteration}: {score:.2f}")
        
        print(f"\n✅ Optimization completed successfully!")
        print(f"📄 Optimized assignment saved to: {output_file}")
        
        if args.reports:
            output_dir = os.path.dirname(output_file) or "."
            base_name = os.path.splitext(os.path.basename(output_file))[0]
            reports_dir = os.path.join(output_dir, f"{base_name}_reports")
            print(f"📊 Detailed reports available in: {reports_dir}")
            
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def handle_list_algorithms_command(args):
    """Handle the list-algorithms command."""
    print("🔧 Available Optimization Algorithms")
    print("=" * 40)
    
    # Create a dummy optimization manager to get algorithm list
    from meshachvetz import Scorer
    scorer = Scorer()
    manager = OptimizationManager(scorer)
    
    algorithms = manager.get_available_algorithms()
    
    print(f"Currently available algorithms:")
    for i, algorithm in enumerate(algorithms, 1):
        print(f"  {i}. {algorithm}")
    
    print(f"\nTotal: {len(algorithms)} algorithms")
    
    # Future algorithms info
    print(f"\n🔮 Coming in future releases:")
    future_algorithms = [
        "genetic - Genetic Algorithm optimization",
        "simulated_annealing - Simulated Annealing optimization", 
        "local_search - Local Search optimization",
        "or_tools - OR-Tools constraint programming"
    ]
    
    for i, algorithm in enumerate(future_algorithms, len(algorithms) + 1):
        print(f"  {i}. {algorithm}")
    
    print(f"\nUse --algorithm <name> to specify which algorithm to use.")


def handle_generate_assignment_command(args):
    """Handle the generate-assignment command."""
    print("🎯 Meshachvetz Assignment Generator")
    print("=" * 40)
    
    # Load configuration
    config = Config()
    if args.config:
        print(f"📋 Loading configuration from: {args.config}")
        config = Config(args.config)
    else:
        print("📋 Using default configuration")
    
    # Create scorer
    scorer = Scorer(config)
    
    # Create optimization manager
    optimization_manager = OptimizationManager(scorer, {})
    
    print(f"📁 Loading student data: {args.csv_file}")
    
    # Load data
    school_data = scorer.load_data(args.csv_file)
    
    print(f"✅ Loaded {school_data.total_students} students")
    
    # Check assignment status
    assignment_status, unassigned_count = optimization_manager.detect_assignment_status(school_data)
    print(f"📊 Assignment status: {assignment_status.value}")
    if unassigned_count > 0:
        print(f"   Found {unassigned_count} unassigned students")
    
    # Create output paths
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.csv_file)
        output_file = str(input_path.parent / f"assignment_{input_path.name}")
    
    if args.output_dir:
        output_path = Path(args.output_dir)
        output_file = str(output_path / Path(output_file).name)
    
    print(f"🔧 Generating assignment with {args.strategy} strategy")
    
    # Convert target_classes: 0 means auto-calculate (None), otherwise use the value
    target_classes = None if args.target_classes == 0 else args.target_classes
    
    if target_classes is not None:
        print(f"   Target classes: {target_classes}")
    else:
        print(f"   Target classes: auto-calculated")
    
    try:
        result_data = optimization_manager.generate_initial_assignment(
            school_data=school_data,
            output_file=output_file,
            strategy=args.strategy,
            target_classes=target_classes
        )
        
        # Get summary and score the result
        summary = optimization_manager.get_assignment_summary(result_data)
        scoring_result = scorer.calculate_scores(result_data)
        
        # Display results
        if not args.quiet:
            print(f"\n🏆 ASSIGNMENT GENERATION RESULTS")
            print(f"Strategy: {args.strategy}")
            print(f"Total students: {summary['total_students']}")
            print(f"Total classes: {summary['total_classes']}")
            print(f"Class sizes: {summary['class_sizes']}")
            print(f"Assignment score: {scoring_result.final_score:.2f}/100")
            print(f"Force constraints: {summary['force_class_constraints']}")
            print(f"Force friend groups: {summary['force_friend_groups']}")
        
        print(f"\n✅ Assignment generation completed successfully!")
        print(f"📄 Generated assignment saved to: {output_file}")
            
    except Exception as e:
        print(f"❌ Assignment generation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def handle_compare_command(args):
    """Handle the compare command for algorithm comparison."""
    try:
        # Configure logging
        log_level = "DEBUG" if args.verbose else "WARNING" if args.quiet else "INFO"
        setup_logging(log_level)
        
        # Load and validate data
        print(f"📁 Loading data from: {args.input_file}")
        
        from meshachvetz.data.loader import DataLoader
        from meshachvetz.scorer.main_scorer import Scorer
        from meshachvetz.optimizer.optimization_manager import OptimizationManager
        
        loader = DataLoader(validate_data=True)
        school_data = loader.load_csv(args.input_file)
        
        print(f"✅ Loaded {school_data.total_students} students")
        
        # Configure optimizer
        config = {
            'min_friends': args.min_friends,
            'respect_force_constraints': True,
            'allow_constraint_override': True
        }
        
        scorer = Scorer()
        optimization_manager = OptimizationManager(scorer, config)
        
        # Convert target_classes: 0 means auto-calculate (None), otherwise use the value
        target_classes = None if args.target_classes == 0 else args.target_classes
        
        # Auto-initialize if needed
        from meshachvetz.optimizer.optimization_manager import AssignmentStatus
        assignment_status, unassigned_count = optimization_manager.detect_assignment_status(school_data)
        
        if assignment_status != AssignmentStatus.FULLY_ASSIGNED:
            print(f"🔧 Initializing {unassigned_count} unassigned students using {args.init_strategy} strategy")
            from meshachvetz.optimizer.optimization_manager import InitializationStrategy
            school_data = optimization_manager.initialize_assignments(
                school_data,
                InitializationStrategy(args.init_strategy),
                target_classes
            )
        
        # Run algorithm comparison
        print(f"🚀 Starting algorithm comparison with {args.strategy} strategy")
        print(f"   Algorithms: {', '.join(args.algorithms)}")
        print(f"   Max iterations per algorithm: {args.max_iterations}")
        
        if args.strategy == 'compare':
            # Use the comprehensive comparison function
            comparison = optimization_manager.run_algorithm_comparison(
                school_data=school_data,
                algorithms=args.algorithms,
                max_iterations=args.max_iterations,
                output_file=args.output
            )
            
            # Display results
            if not args.quiet:
                print(f"\n🏆 ALGORITHM COMPARISON RESULTS")
                print("="*50)
                
                # Show rankings
                if 'rankings' in comparison and 'by_score' in comparison['rankings']:
                    print("\n📊 Rankings by Final Score:")
                    for i, (alg, score) in enumerate(comparison['rankings']['by_score'], 1):
                        print(f"   {i}. {alg}: {score:.2f}/100")
                
                if 'performance_metrics' in comparison:
                    metrics = comparison['performance_metrics']
                    print(f"\n📈 Performance Summary:")
                    if 'score_stats' in metrics:
                        print(f"   Best Score: {metrics['score_stats']['best']:.2f}/100")
                        print(f"   Average Score: {metrics['score_stats']['average']:.2f}/100")
                        print(f"   Score Range: {metrics['score_stats']['best'] - metrics['score_stats']['worst']:.2f}")
                    
                    if 'time_stats' in metrics:
                        print(f"   Fastest Algorithm: {metrics['time_stats']['fastest']:.2f}s")
                        print(f"   Average Time: {metrics['time_stats']['average']:.2f}s")
                
                if args.output:
                    print(f"\n💾 Detailed report saved to: {args.output}")
        
        else:
            # Use multi-algorithm strategy
            results = optimization_manager.optimize_with_multiple_algorithms(
                school_data=school_data,
                algorithms=args.algorithms,
                max_iterations=args.max_iterations,
                strategy=args.strategy
            )
            
            # Display results
            if not args.quiet:
                print(f"\n🏆 MULTI-ALGORITHM RESULTS ({args.strategy.upper()})")
                print("="*50)
                
                if args.strategy == 'best_of':
                    best_result = results['best_result']
                    best_algorithm = results['best_algorithm']
                    print(f"🥇 Best Algorithm: {best_algorithm}")
                    print(f"   Final Score: {best_result.final_score:.2f}/100")
                    print(f"   Improvement: +{best_result.improvement:.2f}")
                    print(f"   Time: {best_result.execution_time:.2f}s")
                    
                    if 'comparison_stats' in results:
                        stats = results['comparison_stats']
                        print(f"\n📊 Comparison Statistics:")
                        print(f"   Score Range: {stats['worst_score']:.2f} - {stats['best_score']:.2f}")
                        print(f"   Average Score: {stats['average_score']:.2f}")
                
                else:
                    # Show all results
                    for alg_name, result in results.items():
                        if hasattr(result, 'final_score'):  # Skip non-result entries
                            print(f"\n🔧 {alg_name}:")
                            print(f"   Score: {result.initial_score:.2f} → {result.final_score:.2f} (+{result.improvement:.2f})")
                            print(f"   Time: {result.execution_time:.2f}s")
                            print(f"   Iterations: {result.iterations_completed}")
        
        print(f"\n✅ Algorithm comparison completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during algorithm comparison: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    main() 