#!/usr/bin/env python3
"""
Advanced Options Manager for Interactive CLI - handles dynamic configuration
of all CLI parameters that were previously hardcoded in the interactive interface.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AdvancedOptions:
    """Container for advanced CLI options."""
    
    # Logging Options
    log_level: str = "normal"
    verbose: bool = False
    quiet: bool = False
    
    # Algorithm Parameters
    min_friends: int = 1
    max_iterations: int = 1000
    early_stop: int = 100
    accept_neutral: bool = False
    
    # Constraint Options
    force_constraints: bool = True
    init_strategy: str = "constraint_aware"
    target_classes: Optional[int] = None
    no_auto_init: bool = False
    
    # Output Control
    reports: bool = True
    detailed: bool = True
    output_dir: Optional[str] = None
    output_prefix: str = "baseline"
    
    # Baseline-Specific Options
    random_seed: Optional[int] = None
    num_runs: int = 10
    
    # Additional Options
    algorithms: List[str] = field(default_factory=lambda: ['local_search', 'simulated_annealing', 'genetic'])
    strategy: str = "best_of"


class AdvancedOptionsManager:
    """Manager for advanced CLI options in interactive mode."""
    
    def __init__(self):
        """Initialize the options manager."""
        self.options = AdvancedOptions()
        
    def show_current_options(self) -> None:
        """Display current advanced options."""
        print("\n⚙️  CURRENT ADVANCED OPTIONS")
        print("=" * 50)
        
        print("📊 Logging Options:")
        print(f"  Log Level: {self.options.log_level}")
        print(f"  Verbose: {self.options.verbose}")
        print(f"  Quiet: {self.options.quiet}")
        
        print("\n🎯 Algorithm Parameters:")
        print(f"  Min Friends: {self.options.min_friends}")
        print(f"  Max Iterations: {self.options.max_iterations}")
        print(f"  Early Stop: {self.options.early_stop}")
        print(f"  Accept Neutral: {self.options.accept_neutral}")
        
        print("\n🔒 Constraint Options:")
        print(f"  Force Constraints: {self.options.force_constraints}")
        print(f"  Init Strategy: {self.options.init_strategy}")
        print(f"  Target Number of Classes: {self.options.target_classes or 'Auto-calculate'}")
        print(f"  No Auto Init: {self.options.no_auto_init}")
        
        print("\n📁 Output Control:")
        print(f"  Generate Reports: {self.options.reports}")
        print(f"  Detailed Output: {self.options.detailed}")
        print(f"  Output Directory: {self.options.output_dir or 'Auto'}")
        print(f"  Output Prefix: {self.options.output_prefix}")
        
        print("\n🎲 Baseline Options:")
        print(f"  Random Seed: {self.options.random_seed or 'Random'}")
        print(f"  Number of Runs: {self.options.num_runs}")
        
        print("\n🔧 Algorithm Options:")
        print(f"  Algorithms: {', '.join(self.options.algorithms)}")
        print(f"  Strategy: {self.options.strategy}")
        
        print("=" * 50)
    
    def configure_interactive(self) -> bool:
        """
        Interactive configuration of advanced options.
        
        Returns:
            True if user made changes, False if cancelled
        """
        print("\n⚙️  ADVANCED OPTIONS CONFIGURATION")
        print("=" * 50)
        print("Configure advanced options (press Enter to keep current value)")
        print("Type 'show' to see current values, 'reset' to restore defaults, 'done' when finished")
        print("=" * 50)
        
        while True:
            print("\nConfiguration categories:")
            print("1. Logging Options")
            print("2. Algorithm Parameters") 
            print("3. Constraint Options")
            print("4. Output Control")
            print("5. Baseline Options")
            print("6. Algorithm Selection")
            print("7. Show Current Settings")
            print("8. Reset to Defaults")
            print("9. Done")
            
            choice = input("\nSelect category (1-9): ").strip()
            
            if choice == '1':
                self._configure_logging()
            elif choice == '2':
                self._configure_algorithm_params()
            elif choice == '3':
                self._configure_constraints()
            elif choice == '4':
                self._configure_output()
            elif choice == '5':
                self._configure_baseline()
            elif choice == '6':
                self._configure_algorithms()
            elif choice == '7':
                self.show_current_options()
            elif choice == '8':
                confirm = input("Reset all options to defaults? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    self.options = AdvancedOptions()
                    print("✅ Options reset to defaults")
            elif choice == '9':
                return True
            elif choice.lower() in ['exit', 'quit', 'cancel']:
                return False
            else:
                print("❌ Invalid choice. Please select 1-9.")
    
    def _configure_logging(self) -> None:
        """Configure logging options."""
        print("\n📊 LOGGING OPTIONS")
        print("-" * 30)
        
        # Log level
        print(f"Current log level: {self.options.log_level}")
        print("Available levels: minimal, normal, detailed, debug")
        new_level = input("New log level (Enter to keep current): ").strip()
        if new_level and new_level in ['minimal', 'normal', 'detailed', 'debug']:
            self.options.log_level = new_level
        elif new_level:
            print("❌ Invalid log level")
        
        # Verbose
        current_verbose = "yes" if self.options.verbose else "no"
        verbose = input(f"Verbose mode? ({current_verbose}) [y/n]: ").strip().lower()
        if verbose in ['y', 'yes']:
            self.options.verbose = True
        elif verbose in ['n', 'no']:
            self.options.verbose = False
        
        # Quiet
        current_quiet = "yes" if self.options.quiet else "no"
        quiet = input(f"Quiet mode? ({current_quiet}) [y/n]: ").strip().lower()
        if quiet in ['y', 'yes']:
            self.options.quiet = True
        elif quiet in ['n', 'no']:
            self.options.quiet = False
    
    def _configure_algorithm_params(self) -> None:
        """Configure algorithm parameters."""
        print("\n🎯 ALGORITHM PARAMETERS")
        print("-" * 30)
        
        # Min friends
        min_friends = input(f"Min friends required ({self.options.min_friends}): ").strip()
        if min_friends:
            try:
                self.options.min_friends = int(min_friends)
            except ValueError:
                print("❌ Invalid number")
        
        # Max iterations
        max_iter = input(f"Max iterations ({self.options.max_iterations}): ").strip()
        if max_iter:
            try:
                self.options.max_iterations = int(max_iter)
            except ValueError:
                print("❌ Invalid number")
        
        # Early stop
        early_stop = input(f"Early stop threshold ({self.options.early_stop}): ").strip()
        if early_stop:
            try:
                self.options.early_stop = int(early_stop)
            except ValueError:
                print("❌ Invalid number")
        
        # Accept neutral
        current_neutral = "yes" if self.options.accept_neutral else "no"
        accept_neutral = input(f"Accept neutral moves? ({current_neutral}) [y/n]: ").strip().lower()
        if accept_neutral in ['y', 'yes']:
            self.options.accept_neutral = True
        elif accept_neutral in ['n', 'no']:
            self.options.accept_neutral = False
    
    def _configure_constraints(self) -> None:
        """Configure constraint options."""
        print("\n🔒 CONSTRAINT OPTIONS")
        print("-" * 30)
        
        # Force constraints
        current_force = "yes" if self.options.force_constraints else "no"
        force_constraints = input(f"Respect force constraints? ({current_force}) [y/n]: ").strip().lower()
        if force_constraints in ['y', 'yes']:
            self.options.force_constraints = True
        elif force_constraints in ['n', 'no']:
            self.options.force_constraints = False
        
        # Init strategy
        print(f"Current init strategy: {self.options.init_strategy}")
        print("Available strategies: random, balanced, constraint_aware, academic_balanced")
        new_strategy = input("New init strategy (Enter to keep current): ").strip()
        if new_strategy and new_strategy in ['random', 'balanced', 'constraint_aware', 'academic_balanced']:
            self.options.init_strategy = new_strategy
        elif new_strategy:
            print("❌ Invalid strategy")
        
        # Target classes
        current_target = self.options.target_classes or "Auto-calculate"
        print(f"\nTarget number of classes to create: {current_target}")
        print("(Auto-calculate will determine optimal number based on student count)")
        target_classes = input("Enter number of classes (or 'auto' for automatic): ").strip()
        if target_classes.lower() in ['auto', 'auto-calculate', 'none', '']:
            self.options.target_classes = None
        elif target_classes:
            try:
                self.options.target_classes = int(target_classes)
                print(f"✅ Target classes set to {target_classes}")
            except ValueError:
                print("❌ Invalid number")
        
        # No auto init
        current_no_auto = "yes" if self.options.no_auto_init else "no"
        no_auto_init = input(f"Disable auto initialization? ({current_no_auto}) [y/n]: ").strip().lower()
        if no_auto_init in ['y', 'yes']:
            self.options.no_auto_init = True
        elif no_auto_init in ['n', 'no']:
            self.options.no_auto_init = False
    
    def _configure_output(self) -> None:
        """Configure output options."""
        print("\n📁 OUTPUT CONTROL")
        print("-" * 30)
        
        # Reports
        current_reports = "yes" if self.options.reports else "no"
        reports = input(f"Generate reports? ({current_reports}) [y/n]: ").strip().lower()
        if reports in ['y', 'yes']:
            self.options.reports = True
        elif reports in ['n', 'no']:
            self.options.reports = False
        
        # Detailed
        current_detailed = "yes" if self.options.detailed else "no"
        detailed = input(f"Detailed output? ({current_detailed}) [y/n]: ").strip().lower()
        if detailed in ['y', 'yes']:
            self.options.detailed = True
        elif detailed in ['n', 'no']:
            self.options.detailed = False
        
        # Output directory
        current_output_dir = self.options.output_dir or "Auto"
        output_dir = input(f"Output directory ({current_output_dir}): ").strip()
        if output_dir.lower() in ['auto', 'none', '']:
            self.options.output_dir = None
        elif output_dir:
            self.options.output_dir = output_dir
        
        # Output prefix
        output_prefix = input(f"Output prefix ({self.options.output_prefix}): ").strip()
        if output_prefix:
            self.options.output_prefix = output_prefix
    
    def _configure_baseline(self) -> None:
        """Configure baseline-specific options."""
        print("\n🎲 BASELINE OPTIONS")
        print("-" * 30)
        
        # Random seed
        current_seed = self.options.random_seed or "Random"
        seed = input(f"Random seed ({current_seed}): ").strip()
        if seed.lower() in ['random', 'none', '']:
            self.options.random_seed = None
        elif seed:
            try:
                self.options.random_seed = int(seed)
            except ValueError:
                print("❌ Invalid number")
        
        # Number of runs
        num_runs = input(f"Number of runs ({self.options.num_runs}): ").strip()
        if num_runs:
            try:
                self.options.num_runs = int(num_runs)
            except ValueError:
                print("❌ Invalid number")
    
    def _configure_algorithms(self) -> None:
        """Configure algorithm selection options."""
        print("\n🔧 ALGORITHM SELECTION")
        print("-" * 30)
        
        # Available algorithms
        available_algorithms = ['random_swap', 'local_search', 'simulated_annealing', 'genetic', 'or_tools']
        
        print(f"Current algorithms: {', '.join(self.options.algorithms)}")
        print(f"Available algorithms: {', '.join(available_algorithms)}")
        
        # Algorithm selection
        print("\nSelect algorithms (comma-separated):")
        print("Press Enter to keep current selection")
        algo_input = input("Algorithms: ").strip()
        
        if algo_input:
            new_algorithms = [algo.strip() for algo in algo_input.split(',')]
            valid_algorithms = [algo for algo in new_algorithms if algo in available_algorithms]
            
            if valid_algorithms:
                self.options.algorithms = valid_algorithms
                print(f"✅ Selected algorithms: {', '.join(valid_algorithms)}")
            else:
                print("❌ No valid algorithms specified")
        
        # Strategy selection
        print(f"\nCurrent strategy: {self.options.strategy}")
        print("Available strategies: parallel, sequential, best_of, compare")
        strategy = input("New strategy (Enter to keep current): ").strip()
        if strategy and strategy in ['parallel', 'sequential', 'best_of', 'compare']:
            self.options.strategy = strategy
        elif strategy:
            print("❌ Invalid strategy")
    
    def reset_to_defaults(self) -> None:
        """Reset all options to default values."""
        self.options = AdvancedOptions()
    
    def get_options(self) -> AdvancedOptions:
        """Get the current options."""
        return self.options
    
    def apply_to_args(self, args_obj: Any, operation_type: str = "general") -> None:
        """
        Apply advanced options to a MockArgs object.
        
        Args:
            args_obj: MockArgs object to modify
            operation_type: Type of operation (optimize, baseline, compare, etc.)
        """
        # Apply common options
        args_obj.log_level = self.options.log_level
        args_obj.verbose = self.options.verbose
        args_obj.quiet = self.options.quiet
        args_obj.min_friends = self.options.min_friends
        args_obj.max_iterations = self.options.max_iterations
        args_obj.early_stop = self.options.early_stop
        args_obj.accept_neutral = self.options.accept_neutral
        args_obj.force_constraints = self.options.force_constraints
        args_obj.init_strategy = self.options.init_strategy
        args_obj.target_classes = self.options.target_classes
        args_obj.no_auto_init = self.options.no_auto_init
        args_obj.reports = self.options.reports
        args_obj.detailed = self.options.detailed
        args_obj.output_dir = self.options.output_dir
        
        # Apply operation-specific options
        if operation_type == "baseline":
            args_obj.random_seed = self.options.random_seed
            args_obj.num_runs = self.options.num_runs
            args_obj.output_prefix = self.options.output_prefix
        elif operation_type == "compare":
            args_obj.algorithms = self.options.algorithms
            args_obj.strategy = self.options.strategy
        elif operation_type == "optimize":
            # For single algorithm optimization, use first algorithm from list
            if hasattr(args_obj, 'algorithm'):
                args_obj.algorithm = self.options.algorithms[0] if self.options.algorithms else 'genetic'
    
    def quick_configure(self, session, prompt_text: str = "Configure advanced options?") -> bool:
        """
        Quick configuration prompt.
        
        Args:
            session: Interactive session object
            prompt_text: Prompt text to display
            
        Returns:
            True if user wants to configure options
        """
        configure = session.get_user_input(f"{prompt_text} (y/n)", ['y', 'n', 'yes', 'no'])
        if configure.lower() in ['y', 'yes']:
            return self.configure_interactive()
        return False 