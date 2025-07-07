#!/usr/bin/env python3
"""
Enhanced Configuration Manager for Meshachvetz - Provides comprehensive configuration
management, validation, and user-friendly features for optimization and scoring.
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import copy

# Configuration validation schemas
ALGORITHM_SCHEMAS = {
    'random_swap': {
        'max_iterations': {'type': int, 'min': 1, 'max': 10000, 'default': 1000},
        'early_stop_threshold': {'type': int, 'min': 1, 'max': 1000, 'default': 100},
        'accept_neutral_moves': {'type': bool, 'default': False},
        'max_swap_attempts': {'type': int, 'min': 1, 'max': 1000, 'default': 50}
    },
    'genetic': {
        'population_size': {'type': int, 'min': 10, 'max': 200, 'default': 50},
        'generations': {'type': int, 'min': 1, 'max': 1000, 'default': 100},
        'mutation_rate': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.1},
        'crossover_rate': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.8},
        'elite_size': {'type': int, 'min': 1, 'max': 50, 'default': 5}
    },
    'simulated_annealing': {
        'initial_temperature': {'type': float, 'min': 0.1, 'max': 1000.0, 'default': 100.0},
        'cooling_rate': {'type': float, 'min': 0.1, 'max': 0.999, 'default': 0.95},
        'min_temperature': {'type': float, 'min': 0.001, 'max': 10.0, 'default': 0.1},
        'cooling_schedule': {'type': str, 'options': ['linear', 'exponential', 'logarithmic'], 'default': 'exponential'}
    },
    'local_search': {
        'max_passes': {'type': int, 'min': 1, 'max': 100, 'default': 10},
        'min_improvement': {'type': float, 'min': 0.001, 'max': 10.0, 'default': 0.01}
    },
    'or_tools': {
        'time_limit_seconds': {'type': int, 'min': 1, 'max': 3600, 'default': 300},
        'target_class_size': {'type': int, 'min': 10, 'max': 50, 'default': 25},
        'class_size_tolerance': {'type': int, 'min': 1, 'max': 10, 'default': 3},
        'friend_weight': {'type': int, 'min': 1, 'max': 100, 'default': 10},
        'conflict_penalty': {'type': int, 'min': 1, 'max': 100, 'default': 20},
        'balance_weight': {'type': int, 'min': 1, 'max': 100, 'default': 5}
    }
}

CONSTRAINT_SCHEMAS = {
    'minimum_friends': {
        'default': {'type': int, 'min': 0, 'max': 3, 'default': 1},
        'allow_override': {'type': bool, 'default': True},
        'max_allowed': {'type': int, 'min': 0, 'max': 5, 'default': 3}
    },
    'class_size_limits': {
        'min_students_per_class': {'type': int, 'min': 1, 'max': 50, 'default': 15},
        'max_students_per_class': {'type': int, 'min': 10, 'max': 100, 'default': 30},
        'preferred_students_per_class': {'type': int, 'min': 10, 'max': 50, 'default': 25}
    }
}


class ConfigurationType(Enum):
    """Types of configuration files."""
    OPTIMIZER = "optimizer"
    SCORER = "scorer"
    COMBINED = "combined"


@dataclass
class ConfigurationProfile:
    """Configuration profile for different use cases."""
    name: str
    description: str
    config_type: ConfigurationType
    config_data: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    author: str = "Meshachvetz"
    version: str = "1.0.0"


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigurationManager:
    """
    Enhanced configuration manager for Meshachvetz.
    
    Provides comprehensive configuration management including validation,
    user-friendly parameter setting, template generation, and profile management.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(__name__)
        
        # Built-in configuration profiles
        self.profiles = self._load_builtin_profiles()
        
        # Load existing configuration files
        self.configs = self._discover_configs()
        
    def _load_builtin_profiles(self) -> Dict[str, ConfigurationProfile]:
        """Load built-in configuration profiles."""
        profiles = {}
        
        # Small school profile (< 200 students)
        profiles['small_school'] = ConfigurationProfile(
            name="Small School",
            description="Optimized for schools with fewer than 200 students. Uses OR-Tools for optimal solutions.",
            config_type=ConfigurationType.COMBINED,
            config_data={
                'optimization': {
                    'default_algorithm': 'or_tools',
                    'algorithms': {
                        'or_tools': {'enabled': True, 'time_limit_seconds': 120},
                        'genetic': {'enabled': True, 'population_size': 30, 'generations': 50}
                    }
                },
                'constraints': {
                    'minimum_friends': {'default': 1},
                    'class_size_limits': {'preferred_students_per_class': 20}
                }
            },
            tags=['small', 'optimal', 'or-tools']
        )
        
        # Large school profile (> 500 students)
        profiles['large_school'] = ConfigurationProfile(
            name="Large School",
            description="Optimized for schools with more than 500 students. Uses fast heuristic algorithms.",
            config_type=ConfigurationType.COMBINED,
            config_data={
                'optimization': {
                    'default_algorithm': 'genetic',
                    'algorithms': {
                        'genetic': {'enabled': True, 'population_size': 30, 'generations': 50},
                        'local_search': {'enabled': True, 'max_passes': 5}
                    }
                },
                'constraints': {
                    'minimum_friends': {'default': 1},
                    'class_size_limits': {'preferred_students_per_class': 28}
                },
                'performance': {
                    'max_iterations': 500,
                    'early_stop_threshold': 50
                }
            },
            tags=['large', 'fast', 'heuristic']
        )
        
        # Balanced approach profile
        profiles['balanced'] = ConfigurationProfile(
            name="Balanced Approach",
            description="Good balance of optimization quality and speed. Works well for most schools.",
            config_type=ConfigurationType.COMBINED,
            config_data={
                'optimization': {
                    'strategy': 'best_of',
                    'algorithms': {
                        'genetic': {'enabled': True, 'population_size': 40, 'generations': 75},
                        'simulated_annealing': {'enabled': True, 'initial_temperature': 50.0},
                        'local_search': {'enabled': True, 'max_passes': 8}
                    }
                },
                'constraints': {
                    'minimum_friends': {'default': 1}
                }
            },
            tags=['balanced', 'multi-algorithm', 'recommended']
        )
        
        return profiles
    
    def _discover_configs(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing configuration files."""
        configs = {}
        
        if not self.config_dir.exists():
            self.logger.warning(f"Configuration directory {self.config_dir} does not exist")
            return configs
        
        for config_file in self.config_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                configs[config_file.stem] = config_data
                self.logger.debug(f"Loaded configuration: {config_file.name}")
            except Exception as e:
                self.logger.warning(f"Failed to load {config_file.name}: {e}")
        
        return configs
    
    def validate_configuration(self, config: Dict[str, Any], 
                             config_type: ConfigurationType = ConfigurationType.OPTIMIZER) -> List[str]:
        """
        Validate a configuration against the schema.
        
        Args:
            config: Configuration to validate
            config_type: Type of configuration
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            if config_type in [ConfigurationType.OPTIMIZER, ConfigurationType.COMBINED]:
                errors.extend(self._validate_optimizer_config(config))
            
            if config_type in [ConfigurationType.SCORER, ConfigurationType.COMBINED]:
                errors.extend(self._validate_scorer_config(config))
                
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    def _validate_optimizer_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate optimizer configuration."""
        errors = []
        
        # Validate algorithm configurations
        if 'optimization' in config and 'algorithms' in config['optimization']:
            algorithms = config['optimization']['algorithms']
            
            # Handle both list and dict formats
            if isinstance(algorithms, list):
                for alg in algorithms:
                    if 'name' in alg and 'parameters' in alg:
                        alg_errors = self._validate_algorithm_params(alg['name'], alg['parameters'])
                        errors.extend(alg_errors)
            elif isinstance(algorithms, dict):
                for alg_name, alg_config in algorithms.items():
                    if isinstance(alg_config, dict) and 'enabled' in alg_config:
                        # Extract parameters, excluding 'enabled' flag
                        params = {k: v for k, v in alg_config.items() if k != 'enabled'}
                        alg_errors = self._validate_algorithm_params(alg_name, params)
                        errors.extend(alg_errors)
        
        # Validate constraint configurations
        if 'constraints' in config:
            constraints = config['constraints']
            
            # Validate minimum friends constraint
            if 'minimum_friends' in constraints:
                min_friends = constraints['minimum_friends']
                if isinstance(min_friends, dict):
                    for param, value in min_friends.items():
                        if param in CONSTRAINT_SCHEMAS['minimum_friends']:
                            param_errors = self._validate_parameter(
                                f"constraints.minimum_friends.{param}", 
                                value, 
                                CONSTRAINT_SCHEMAS['minimum_friends'][param]
                            )
                            errors.extend(param_errors)
        
        return errors
    
    def _validate_scorer_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate scorer configuration."""
        errors = []
        
        # Add scorer-specific validation logic here
        # This is a placeholder for future scorer configuration validation
        
        return errors
    
    def _validate_algorithm_params(self, algorithm_name: str, parameters: Dict[str, Any]) -> List[str]:
        """Validate algorithm-specific parameters."""
        errors = []
        
        if algorithm_name not in ALGORITHM_SCHEMAS:
            return errors  # Unknown algorithm, skip validation
        
        schema = ALGORITHM_SCHEMAS[algorithm_name]
        
        for param_name, param_value in parameters.items():
            if param_name in schema:
                param_errors = self._validate_parameter(
                    f"{algorithm_name}.{param_name}", 
                    param_value, 
                    schema[param_name]
                )
                errors.extend(param_errors)
        
        return errors
    
    def _validate_parameter(self, param_path: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate a single parameter against its schema."""
        errors = []
        
        expected_type = schema.get('type', str)
        
        # Type validation
        if not isinstance(value, expected_type):
            errors.append(f"Parameter '{param_path}' must be of type {expected_type.__name__}, got {type(value).__name__}")
            return errors
        
        # Range validation for numeric types
        if expected_type in [int, float]:
            if 'min' in schema and value < schema['min']:
                errors.append(f"Parameter '{param_path}' must be >= {schema['min']}, got {value}")
            if 'max' in schema and value > schema['max']:
                errors.append(f"Parameter '{param_path}' must be <= {schema['max']}, got {value}")
        
        # Options validation for string types
        if expected_type == str and 'options' in schema:
            if value not in schema['options']:
                errors.append(f"Parameter '{param_path}' must be one of {schema['options']}, got '{value}'")
        
        return errors
    
    def create_configuration_template(self, 
                                    config_type: ConfigurationType = ConfigurationType.OPTIMIZER,
                                    algorithm: str = None,
                                    include_comments: bool = True) -> Dict[str, Any]:
        """
        Create a configuration template with default values and comments.
        
        Args:
            config_type: Type of configuration template to create
            algorithm: Specific algorithm to focus on (optional)
            include_comments: Whether to include helpful comments
            
        Returns:
            Configuration template dictionary
        """
        template = {}
        
        if config_type in [ConfigurationType.OPTIMIZER, ConfigurationType.COMBINED]:
            template.update(self._create_optimizer_template(algorithm, include_comments))
        
        if config_type in [ConfigurationType.SCORER, ConfigurationType.COMBINED]:
            template.update(self._create_scorer_template(include_comments))
        
        return template
    
    def _create_optimizer_template(self, algorithm: str = None, include_comments: bool = True) -> Dict[str, Any]:
        """Create optimizer configuration template."""
        template = {
            'optimization': {
                'default_algorithm': algorithm or 'genetic',
                'strategy': 'single',  # Options: single, sequential, parallel, best_of
                'algorithms': {}
            },
            'constraints': {
                'minimum_friends': {
                    'default': 1,
                    'allow_override': True,
                    'max_allowed': 3
                },
                'force_constraints': {
                    'respect_force_class': True,
                    'respect_force_friend': True
                },
                'class_size_limits': {
                    'min_students_per_class': 15,
                    'max_students_per_class': 30,
                    'preferred_students_per_class': 25
                }
            },
            'performance': {
                'max_iterations': 1000,
                'early_stopping': True,
                'early_stop_threshold': 100
            }
        }
        
        # Add algorithm-specific configuration
        algorithms_to_include = [algorithm] if algorithm else ['genetic', 'or_tools', 'local_search']
        
        for alg_name in algorithms_to_include:
            if alg_name in ALGORITHM_SCHEMAS:
                alg_config = {'enabled': True}
                for param, schema in ALGORITHM_SCHEMAS[alg_name].items():
                    alg_config[param] = schema.get('default')
                template['optimization']['algorithms'][alg_name] = alg_config
        
        return template
    
    def _create_scorer_template(self, include_comments: bool = True) -> Dict[str, Any]:
        """Create scorer configuration template."""
        return {
            'scoring': {
                'weights': {
                    'student_layer': 60.0,
                    'class_layer': 10.0,
                    'school_layer': 30.0
                },
                'student_weights': {
                    'friend_satisfaction': 70.0,
                    'conflict_avoidance': 30.0
                },
                'class_weights': {
                    'gender_balance': 100.0
                },
                'school_weights': {
                    'academic_balance': 25.0,
                    'behavior_balance': 25.0,
                    'size_balance': 25.0,
                    'assistance_balance': 25.0
                }
            }
        }
    
    def apply_profile(self, profile_name: str, base_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Apply a configuration profile to a base configuration.
        
        Args:
            profile_name: Name of the profile to apply
            base_config: Base configuration to modify (optional)
            
        Returns:
            Configuration with profile applied
        """
        if profile_name not in self.profiles:
            raise ConfigurationError(f"Unknown profile: {profile_name}")
        
        profile = self.profiles[profile_name]
        
        if base_config is None:
            base_config = self.create_configuration_template(profile.config_type)
        
        # Deep merge profile configuration with base configuration
        return self._deep_merge(base_config, profile.config_data)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        
        return result
    
    def save_configuration(self, config: Dict[str, Any], filename: str, 
                         validate: bool = True) -> None:
        """
        Save configuration to file with optional validation.
        
        Args:
            config: Configuration to save
            filename: Output filename (will be saved in config directory)
            validate: Whether to validate before saving
        """
        if validate:
            errors = self.validate_configuration(config)
            if errors:
                raise ConfigurationError(f"Configuration validation failed:\n" + "\n".join(errors))
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        output_path = self.config_dir / filename
        if not output_path.suffix:
            output_path = output_path.with_suffix('.yaml')
        
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"Configuration saved to {output_path}")
    
    def get_profile_recommendations(self, student_count: int, 
                                  time_limit: Optional[int] = None) -> List[str]:
        """
        Get configuration profile recommendations based on school characteristics.
        
        Args:
            student_count: Number of students in the school
            time_limit: Maximum optimization time in seconds (optional)
            
        Returns:
            List of recommended profile names
        """
        recommendations = []
        
        if student_count < 200:
            recommendations.append('small_school')
        elif student_count > 500:
            recommendations.append('large_school')
        else:
            recommendations.append('balanced')
        
        # Add time-based recommendations
        if time_limit and time_limit < 60:
            # Quick optimization needed
            recommendations = [p for p in recommendations if 'fast' in self.profiles[p].tags]
            if not recommendations:
                recommendations.append('large_school')  # Fast by default
        
        return recommendations
    
    def get_available_profiles(self) -> List[Dict[str, Any]]:
        """Get list of available configuration profiles with metadata."""
        profiles_info = []
        
        for name, profile in self.profiles.items():
            profiles_info.append({
                'name': name,
                'display_name': profile.name,
                'description': profile.description,
                'tags': profile.tags,
                'config_type': profile.config_type.value
            })
        
        return profiles_info
    
    def interactive_configuration_wizard(self) -> Dict[str, Any]:
        """
        Interactive configuration wizard for creating custom configurations.
        This is a placeholder for a future interactive CLI feature.
        """
        # This would be implemented as an interactive CLI wizard
        # For now, return a basic template
        return self.create_configuration_template()


# Global configuration manager instance
config_manager = ConfigurationManager() 


# CLI Handler Functions
def handle_config_set_command(config_file: str) -> None:
    """Handle the config set command."""
    try:
        config_manager = ConfigurationManager()
        
        # Load the configuration file
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Error: Configuration file '{config_file}' not found.")
            return
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Validate the configuration
        errors = config_manager.validate_configuration(config_data)
        if errors:
            print(f"Error: Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return
        
        # Copy to default config location
        default_config_path = config_manager.config_dir / "default_optimizer.yaml"
        config_manager.save_configuration(config_data, str(default_config_path), validate=False)
        
        print(f"Configuration set successfully: {config_file} -> {default_config_path}")
        
    except Exception as e:
        print(f"Error setting configuration: {e}")


def handle_config_reset_command() -> None:
    """Handle the config reset command."""
    try:
        config_manager = ConfigurationManager()
        
        # Create default configuration
        default_config = config_manager.create_configuration_template()
        
        # Save to default location
        default_config_path = config_manager.config_dir / "default_optimizer.yaml"
        config_manager.save_configuration(default_config, str(default_config_path), validate=False)
        
        print(f"Configuration reset to defaults: {default_config_path}")
        
    except Exception as e:
        print(f"Error resetting configuration: {e}")


def handle_config_status_command() -> None:
    """Handle the config status command."""
    try:
        config_manager = ConfigurationManager()
        
        print("=== Configuration Status ===")
        print(f"Config directory: {config_manager.config_dir}")
        print(f"Available configurations: {len(config_manager.configs)}")
        
        for config_name, config_data in config_manager.configs.items():
            print(f"  - {config_name}.yaml")
        
        print(f"\nBuilt-in profiles: {len(config_manager.profiles)}")
        for profile_name, profile in config_manager.profiles.items():
            print(f"  - {profile_name}: {profile.description}")
        
        # Check if default config exists
        default_config_path = config_manager.config_dir / "default_optimizer.yaml"
        if default_config_path.exists():
            print(f"\nDefault configuration: {default_config_path}")
        else:
            print("\nDefault configuration: Not found")
        
    except Exception as e:
        print(f"Error getting configuration status: {e}") 