#!/usr/bin/env python3
"""
Interactive CLI for Meshachvetz - Menu-driven interface for student assignment optimization.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Add src directory to path for imports
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from meshachvetz import Config, Scorer
from .scorer_cli import handle_score_command, handle_validate_command, handle_show_config_command
from .optimizer_cli import handle_optimize_command, handle_compare_command, handle_generate_assignment_command
from .config_manager import handle_config_set_command, handle_config_reset_command, handle_config_status_command
from .baseline_cli import generate_baseline_command


class InteractiveSession:
    """Interactive session manager for Meshachvetz CLI."""
    
    def __init__(self):
        """Initialize the interactive session."""
        self.current_config = None
        self.temp_config_overrides = {}
        self.session_active = True
        
    def display_header(self):
        """Display the application header."""
        print("\n" + "=" * 60)
        print("🎯 MESHACHVETZ - Student Class Assignment Optimizer")
        print("=" * 60)
        print("Interactive Menu System")
        print("Type 'help' for navigation assistance or 'exit' to quit")
        print("=" * 60)
        
    def display_config_summary(self):
        """Display current configuration summary."""
        print("\n📋 Current Configuration Summary:")
        print("-" * 40)
        
        try:
            # Load current configuration
            config = Config()
            if self.current_config:
                config = Config(self.current_config)
            
            # Display complete configuration details like config show command
            print(f"🏗️  Layer Weights:")
            print(f"   Student Layer: {config.weights.student_layer}")
            print(f"   Class Layer:   {config.weights.class_layer}")
            print(f"   School Layer:  {config.weights.school_layer}")
            
            print(f"\n👥 Student Layer Weights:")
            print(f"   Friends:  {config.weights.friends}")
            print(f"   Dislikes: {config.weights.dislikes}")
            
            print(f"\n🏫 Class Layer Weights:")
            print(f"   Gender Balance: {config.weights.gender_balance}")
            
            print(f"\n🏛️  School Layer Weights:")
            print(f"   Academic Balance:     {config.weights.academic_balance}")
            print(f"   Behavior Balance:     {config.weights.behavior_balance}")
            print(f"   Studentiality Balance: {config.weights.studentiality_balance}")
            print(f"   Size Balance:         {config.weights.size_balance}")
            print(f"   Assistance Balance:   {config.weights.assistance_balance}")
            
            print(f"\n📏 Normalization Factors:")
            print(f"   Academic Score Factor:    {config.normalization.academic_score_factor}")
            print(f"   Behavior Rank Factor:     {config.normalization.behavior_rank_factor}")
            print(f"   Studentiality Rank Factor: {config.normalization.studentiality_rank_factor}")
            print(f"   Class Size Factor:        {config.normalization.class_size_factor}")
            print(f"   Assistance Count Factor:  {config.normalization.assistance_count_factor}")
            
            # Show temporary overrides if any
            if self.temp_config_overrides:
                print(f"\n⚠️  Temporary Overrides Active:")
                for key, value in self.temp_config_overrides.items():
                    print(f"   {key}: {value}")
                    
        except Exception as e:
            print(f"❌ Error displaying configuration: {e}")
            
        print("-" * 40)
        
    def display_main_menu(self):
        """Display the main menu options."""
        print("\n🏠 MAIN MENU")
        print("-" * 30)
        print("1. Score Assignment")
        print("2. Optimize Assignment")
        print("3. Compare Algorithms")
        print("4. Configuration")
        print("5. Generate Assignment")
        print("6. Validate Data")
        print("7. Baseline Test")
        print("8. Master Solver (Coming Soon)")
        print("9. Exit")
        print("-" * 30)
        
    def display_config_menu(self):
        """Display the configuration menu options."""
        print("\n⚙️  CONFIGURATION MENU")
        print("-" * 30)
        print("1. Show Current Configuration")
        print("2. Set Configuration File")
        print("3. Reset to Defaults")
        print("4. Configuration Status")
        print("5. Temporary Override (This Session)")
        print("6. Back to Main Menu")
        print("-" * 30)
        
    def get_user_input(self, prompt: str, valid_options: Optional[list] = None) -> str:
        """Get validated user input."""
        while True:
            try:
                user_input = input(f"{prompt}: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    self.session_active = False
                    return 'exit'
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if valid_options and user_input not in valid_options:
                    print(f"❌ Invalid option. Please choose from: {', '.join(valid_options)}")
                    continue
                    
                return user_input
                
            except KeyboardInterrupt:
                print("\n⚠️  Operation cancelled by user.")
                self.session_active = False
                return 'exit'
            except EOFError:
                print("\n👋 Goodbye!")
                self.session_active = False
                return 'exit'
                
    def show_help(self):
        """Display help information."""
        print("\n📖 HELP")
        print("-" * 30)
        print("Navigation:")
        print("• Enter the number of your choice")
        print("• Type 'help' for this help message")
        print("• Type 'exit' or 'quit' to leave")
        print("• Use Ctrl+C to cancel operations")
        print("")
        print("Features:")
        print("• Configuration changes can be temporary (session only)")
        print("• All operations show current config before running")
        print("• File paths can be absolute or relative")
        print("-" * 30)
        
    def get_file_path(self, prompt: str, must_exist: bool = True) -> Optional[str]:
        """Get and validate file path from user."""
        while True:
            filepath = self.get_user_input(prompt)
            if filepath == 'exit':
                return None
                
            if not filepath:
                print("❌ Please enter a file path")
                continue
                
            path = Path(filepath)
            if must_exist and not path.exists():
                print(f"❌ File not found: {filepath}")
                continue
                
            return filepath
            
    def ask_config_override(self) -> bool:
        """Ask user if they want to override configuration for this run."""
        response = self.get_user_input(
            "Would you like to modify configuration for this run only? (y/n)", 
            ['y', 'n', 'yes', 'no']
        )
        return response.lower() in ['y', 'yes']
        
    def handle_temp_config_override(self):
        """Handle temporary configuration override."""
        print("\n⚠️  TEMPORARY CONFIGURATION OVERRIDE")
        print("Changes will only apply to this session")
        print("-" * 40)
        
        print("Available overrides:")
        print("1. Student Layer Weight")
        print("2. Class Layer Weight") 
        print("3. School Layer Weight")
        print("4. Friend Weight")
        print("5. Conflict Weight")
        print("6. Clear All Overrides")
        print("7. Back")
        
        choice = self.get_user_input("Select override option", ['1', '2', '3', '4', '5', '6', '7'])
        
        if choice == '1':
            value = self.get_user_input("Enter Student Layer Weight (0.0-1.0)")
            try:
                self.temp_config_overrides['student_layer'] = float(value)
                print(f"✅ Student layer weight set to {value}")
            except ValueError:
                print("❌ Invalid number format")
        elif choice == '2':
            value = self.get_user_input("Enter Class Layer Weight (0.0-1.0)")
            try:
                self.temp_config_overrides['class_layer'] = float(value)
                print(f"✅ Class layer weight set to {value}")
            except ValueError:
                print("❌ Invalid number format")
        elif choice == '3':
            value = self.get_user_input("Enter School Layer Weight (0.0-1.0)")
            try:
                self.temp_config_overrides['school_layer'] = float(value)
                print(f"✅ School layer weight set to {value}")
            except ValueError:
                print("❌ Invalid number format")
        elif choice == '4':
            value = self.get_user_input("Enter Friend Weight (0.0-1.0)")
            try:
                self.temp_config_overrides['friends'] = float(value)
                print(f"✅ Friend weight set to {value}")
            except ValueError:
                print("❌ Invalid number format")
        elif choice == '5':
            value = self.get_user_input("Enter Conflict Weight (0.0-1.0)")
            try:
                self.temp_config_overrides['dislikes'] = float(value)
                print(f"✅ Conflict weight set to {value}")
            except ValueError:
                print("❌ Invalid number format")
        elif choice == '6':
            self.temp_config_overrides.clear()
            print("✅ All temporary overrides cleared")
        elif choice == '7':
            return
            
    def handle_score_assignment(self):
        """Handle score assignment operation."""
        print("\n📊 SCORE ASSIGNMENT")
        print("-" * 30)
        
        # Show current configuration
        self.display_config_summary()
        
        # Ask for configuration override
        if self.ask_config_override():
            self.handle_temp_config_override()
            
        # Get file path
        csv_file = self.get_file_path("Enter CSV file path")
        if not csv_file:
            return
            
        # Create mock args for existing function
        class MockArgs:
            def __init__(self, session):
                self.csv_file = csv_file
                self.config = session.current_config
                self.reports = False
                self.output = None
                self.detailed = True
                self.verbose = False
                self.quiet = False
                self.student_weight = session.temp_config_overrides.get('student_layer')
                self.class_weight = session.temp_config_overrides.get('class_layer')
                self.school_weight = session.temp_config_overrides.get('school_layer')
                self.friends_weight = session.temp_config_overrides.get('friends')
                self.dislikes_weight = session.temp_config_overrides.get('dislikes')
                
        # Ask for reports
        reports_choice = self.get_user_input("Generate CSV reports? (y/n)", ['y', 'n', 'yes', 'no'])
        
        args = MockArgs(self)
        args.reports = reports_choice.lower() in ['y', 'yes']
        
        if args.reports:
            output_dir = self.get_user_input("Enter output directory (press Enter for default)", [])
            if output_dir and output_dir != 'exit':
                args.output = output_dir
                
        # Execute scoring
        try:
            handle_score_command(args)
        except Exception as e:
            print(f"❌ Error during scoring: {e}")
            
    def handle_optimize_assignment(self):
        """Handle optimize assignment operation."""
        print("\n🚀 OPTIMIZE ASSIGNMENT")
        print("-" * 30)
        
        # Show current configuration
        self.display_config_summary()
        
        # Ask for configuration override
        if self.ask_config_override():
            self.handle_temp_config_override()
            
        # Get file path
        csv_file = self.get_file_path("Enter CSV file path")
        if not csv_file:
            return
            
        # Algorithm selection
        print("\nAvailable algorithms:")
        print("1. Genetic Algorithm (recommended)")
        print("2. Local Search")
        print("3. Simulated Annealing")
        print("4. Random Swap")
        print("5. OR-Tools (experimental)")
        
        algo_choice = self.get_user_input("Select algorithm", ['1', '2', '3', '4', '5'])
        
        algorithms = {
            '1': 'genetic',
            '2': 'local_search', 
            '3': 'simulated_annealing',
            '4': 'random_swap',
            '5': 'or_tools'
        }
        
        selected_algorithm = algorithms[algo_choice]
        
        # Create mock args for existing function
        class MockArgs:
            def __init__(self, session):
                self.csv_file = csv_file
                self.config = session.current_config
                self.algorithm = selected_algorithm
                self.output = None
                self.output_dir = None
                self.max_iterations = 1000
                self.reports = True
                self.detailed = True
                self.verbose = False
                self.quiet = False
                self.min_friends = 1
                self.early_stop = 100
                self.accept_neutral = False
                self.force_constraints = True
                self.init_strategy = 'constraint_aware'
                self.no_auto_init = False
                self.target_classes = None
                
        args = MockArgs(self)
        
        # Ask for output file
        output_file = self.get_user_input("Enter output file path (press Enter for default)", [])
        if output_file and output_file != 'exit':
            args.output = output_file
            
        # Execute optimization
        try:
            handle_optimize_command(args)
        except Exception as e:
            print(f"❌ Error during optimization: {e}")
            
    def handle_compare_algorithms(self):
        """Handle algorithm comparison operation."""
        print("\n🔬 COMPARE ALGORITHMS")
        print("-" * 30)
        
        # Show current configuration
        self.display_config_summary()
        
        # Ask for configuration override
        if self.ask_config_override():
            self.handle_temp_config_override()
            
        # Get file path
        csv_file = self.get_file_path("Enter CSV file path")
        if not csv_file:
            return
            
        # Strategy selection
        print("\nComparison strategies:")
        print("1. Parallel (run all algorithms simultaneously)")
        print("2. Sequential (run algorithms one after another)")
        print("3. Best Of (run all and pick best result)")
        
        strategy_choice = self.get_user_input("Select strategy", ['1', '2', '3'])
        
        strategies = {
            '1': 'parallel',
            '2': 'sequential',
            '3': 'best_of'
        }
        
        selected_strategy = strategies[strategy_choice]
        
        # Create mock args for existing function
        class MockArgs:
            def __init__(self, session):
                self.input_file = csv_file
                self.algorithms = ['local_search', 'simulated_annealing', 'genetic']
                self.strategy = selected_strategy
                self.max_iterations = 1000
                self.min_friends = 1
                self.init_strategy = 'constraint_aware'
                self.target_classes = None
                self.verbose = False
                self.quiet = False
                
        args = MockArgs(self)
        
        # Execute comparison
        try:
            handle_compare_command(args)
        except Exception as e:
            print(f"❌ Error during comparison: {e}")
            
    def handle_configuration_menu(self):
        """Handle configuration menu operations."""
        while self.session_active:
            self.display_config_menu()
            
            choice = self.get_user_input("Select option", ['1', '2', '3', '4', '5', '6'])
            
            if choice == 'exit':
                return
            elif choice == '1':
                # Show current configuration
                class MockArgs:
                    def __init__(self, session):
                        self.config = session.current_config
                        
                try:
                    handle_show_config_command(MockArgs(self))
                except Exception as e:
                    print(f"❌ Error showing configuration: {e}")
                    
            elif choice == '2':
                # Set configuration file
                config_file = self.get_file_path("Enter configuration file path")
                if config_file:
                    try:
                        handle_config_set_command(config_file)
                        self.current_config = config_file
                    except Exception as e:
                        print(f"❌ Error setting configuration: {e}")
                        
            elif choice == '3':
                # Reset to defaults
                confirm = self.get_user_input("Reset to defaults? This will clear custom settings (y/n)", ['y', 'n', 'yes', 'no'])
                if confirm.lower() in ['y', 'yes']:
                    try:
                        handle_config_reset_command()
                        self.current_config = None
                        self.temp_config_overrides.clear()
                        print("✅ Configuration reset to defaults")
                    except Exception as e:
                        print(f"❌ Error resetting configuration: {e}")
                        
            elif choice == '4':
                # Configuration status
                try:
                    handle_config_status_command()
                except Exception as e:
                    print(f"❌ Error getting configuration status: {e}")
                    
            elif choice == '5':
                # Temporary override
                self.handle_temp_config_override()
                
            elif choice == '6':
                # Back to main menu
                return
                
    def handle_generate_assignment(self):
        """Handle generate assignment operation."""
        print("\n🔧 GENERATE ASSIGNMENT")
        print("-" * 30)
        
        # Show current configuration
        self.display_config_summary()
        
        # Get file path
        csv_file = self.get_file_path("Enter CSV file path")
        if not csv_file:
            return
            
        # Strategy selection
        print("\nGeneration strategies:")
        print("1. Constraint Aware (recommended)")
        print("2. Academic Balanced")
        print("3. Random")
        print("4. Balanced")
        
        strategy_choice = self.get_user_input("Select strategy", ['1', '2', '3', '4'])
        
        strategies = {
            '1': 'constraint_aware',
            '2': 'academic_balanced',
            '3': 'random',
            '4': 'balanced'
        }
        
        selected_strategy = strategies[strategy_choice]
        
        # Create mock args for existing function
        class MockArgs:
            def __init__(self, session):
                self.csv_file = csv_file
                self.config = session.current_config
                self.strategy = selected_strategy
                self.output = None
                self.output_dir = None
                self.target_classes = None
                self.verbose = False
                self.quiet = False
                
        args = MockArgs(self)
        
        # Ask for output file
        output_file = self.get_user_input("Enter output file path (press Enter for default)", [])
        if output_file and output_file != 'exit':
            args.output = output_file
            
        # Execute generation
        try:
            handle_generate_assignment_command(args)
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            
    def handle_validate_data(self):
        """Handle data validation operation."""
        print("\n✅ VALIDATE DATA")
        print("-" * 30)
        
        # Get file path
        csv_file = self.get_file_path("Enter CSV file path")
        if not csv_file:
            return
            
        # Create mock args for existing function
        class MockArgs:
            def __init__(self, session):
                self.csv_file = csv_file
                self.verbose = True
                
        args = MockArgs(self)
        
        # Execute validation
        try:
            handle_validate_command(args)
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            
    def handle_baseline_test(self):
        """Handle baseline test generation operation."""
        print("\n🎯 GENERATE BASELINE")
        print("-" * 30)
        
        # Show current configuration
        self.display_config_summary()
        
        # Get file path
        csv_file = self.get_file_path("Enter CSV file path")
        if not csv_file:
            return
            
        # Ask for optional parameters
        print("\nBaseline options (press Enter for defaults):")
        
        num_runs_input = self.get_user_input("Number of runs (default: 10)", [])
        num_runs = 10
        if num_runs_input and num_runs_input != 'exit':
            try:
                num_runs = int(num_runs_input)
            except ValueError:
                print("⚠️ Invalid number, using default (10)")
        
        max_iterations_input = self.get_user_input("Max iterations per run (default: 1000)", [])
        max_iterations = 1000
        if max_iterations_input and max_iterations_input != 'exit':
            try:
                max_iterations = int(max_iterations_input)
            except ValueError:
                print("⚠️ Invalid number, using default (1000)")
        
        output_dir_input = self.get_user_input("Output directory for reports (optional)", [])
        output_dir = None
        if output_dir_input and output_dir_input != 'exit' and output_dir_input.strip():
            output_dir = output_dir_input.strip()
            
        # Create mock args for existing function
        class MockArgs:
            def __init__(self, session):
                self.csv_file = csv_file
                self.config = session.current_config
                self.num_runs = num_runs
                self.max_iterations = max_iterations
                self.output_dir = output_dir
                self.output_prefix = 'baseline'
                self.log_level = 'normal'
                self.quiet = False
                self.min_friends = 0
                self.early_stop = 100
                self.accept_neutral = False
                self.force_constraints = True
                self.random_seed = None
                
        args = MockArgs(self)
        
        # Execute baseline generation
        try:
            generate_baseline_command(args)
        except Exception as e:
            print(f"❌ Error during baseline generation: {e}")
            
    def run(self):
        """Run the interactive CLI session."""
        self.display_header()
        
        while self.session_active:
            self.display_main_menu()
            
            choice = self.get_user_input("Select option", ['1', '2', '3', '4', '5', '6', '7', '8', '9'])
            
            if choice == 'exit':
                break
            elif choice == '1':
                self.handle_score_assignment()
            elif choice == '2':
                self.handle_optimize_assignment()
            elif choice == '3':
                self.handle_compare_algorithms()
            elif choice == '4':
                self.handle_configuration_menu()
            elif choice == '5':
                self.handle_generate_assignment()
            elif choice == '6':
                self.handle_validate_data()
            elif choice == '7':
                self.handle_baseline_test()
            elif choice == '8':
                print("🔧 Master Solver feature coming soon in next update!")
            elif choice == '9':
                break
                
        print("\n👋 Thank you for using Meshachvetz!")
        print("Visit our documentation for more advanced features.")


def main():
    """Main entry point for interactive CLI."""
    try:
        session = InteractiveSession()
        session.run()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 