#!/usr/bin/env python3
"""
Unit tests for Enhanced Configuration Manager - Week 6 implementation.
Tests configuration validation, profiles, and template generation.
"""

import pytest
import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open
import tempfile
import os
from pathlib import Path
import yaml
import shutil
from typing import Dict, Any

# Import the modules to test
from src.meshachvetz.cli.config_manager import (
    ConfigurationManager, 
    ConfigurationProfile, 
    ConfigurationType, 
    ConfigurationError,
    ALGORITHM_SCHEMAS,
    CONSTRAINT_SCHEMAS
)


class TestConfigurationManager(unittest.TestCase):
    """Test cases for Enhanced Configuration Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigurationManager(self.temp_dir)
        
        # Sample valid optimizer configuration
        self.valid_optimizer_config = {
            'optimization': {
                'default_algorithm': 'genetic',
                'strategy': 'single',
                'algorithms': {
                    'genetic': {
                        'enabled': True,
                        'population_size': 50,
                        'generations': 100,
                        'mutation_rate': 0.1,
                        'crossover_rate': 0.8,
                        'elite_size': 5
                    },
                    'or_tools': {
                        'enabled': True,
                        'time_limit_seconds': 300,
                        'target_class_size': 25,
                        'class_size_tolerance': 3
                    }
                }
            },
            'constraints': {
                'minimum_friends': {
                    'default': 1,
                    'allow_override': True,
                    'max_allowed': 3
                }
            }
        }
        
        # Sample invalid configuration for testing
        self.invalid_config = {
            'optimization': {
                'algorithms': {
                    'genetic': {
                        'enabled': True,
                        'population_size': -10,  # Invalid: negative
                        'mutation_rate': 1.5,    # Invalid: > 1.0
                        'crossover_rate': 'invalid_string'  # Invalid: wrong type
                    }
                }
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test configuration manager initialization."""
        manager = ConfigurationManager(self.temp_dir)
        
        self.assertEqual(manager.config_dir, Path(self.temp_dir))
        self.assertIsInstance(manager.profiles, dict)
        self.assertIsInstance(manager.configs, dict)
        
        # Should have built-in profiles
        self.assertIn('small_school', manager.profiles)
        self.assertIn('large_school', manager.profiles)
        self.assertIn('balanced', manager.profiles)
    
    def test_builtin_profiles(self):
        """Test built-in configuration profiles."""
        profiles = self.config_manager.profiles
        
        # Test small_school profile
        small_school = profiles['small_school']
        self.assertEqual(small_school.name, "Small School")
        self.assertEqual(small_school.config_type, ConfigurationType.COMBINED)
        self.assertIn('small', small_school.tags)
        self.assertIn('or-tools', small_school.tags)
        
        # Test large_school profile
        large_school = profiles['large_school']
        self.assertEqual(large_school.name, "Large School")
        self.assertIn('large', large_school.tags)
        self.assertIn('fast', large_school.tags)
        
        # Test balanced profile
        balanced = profiles['balanced']
        self.assertEqual(balanced.name, "Balanced Approach")
        self.assertIn('balanced', balanced.tags)
        self.assertIn('recommended', balanced.tags)
    
    def test_discover_configs(self):
        """Test configuration file discovery."""
        # Create test config files
        test_config = {'test': 'value'}
        
        config_file1 = Path(self.temp_dir) / 'test1.yaml'
        config_file2 = Path(self.temp_dir) / 'test2.yaml'
        
        with open(config_file1, 'w') as f:
            yaml.dump(test_config, f)
        with open(config_file2, 'w') as f:
            yaml.dump(test_config, f)
        
        # Reinitialize to discover files
        manager = ConfigurationManager(self.temp_dir)
        
        self.assertIn('test1', manager.configs)
        self.assertIn('test2', manager.configs)
        self.assertEqual(manager.configs['test1'], test_config)
    
    def test_validate_configuration_valid(self):
        """Test validation of valid configuration."""
        errors = self.config_manager.validate_configuration(
            self.valid_optimizer_config, 
            ConfigurationType.OPTIMIZER
        )
        
        self.assertEqual(len(errors), 0, f"Valid config should have no errors, got: {errors}")
    
    def test_validate_configuration_invalid(self):
        """Test validation of invalid configuration."""
        errors = self.config_manager.validate_configuration(
            self.invalid_config, 
            ConfigurationType.OPTIMIZER
        )
        
        self.assertGreater(len(errors), 0, "Invalid config should have errors")
        
        # Check specific error types
        error_text = ' '.join(errors)
        self.assertIn('population_size', error_text)  # Should catch negative value
        self.assertIn('mutation_rate', error_text)    # Should catch > 1.0 value
    
    def test_validate_algorithm_params(self):
        """Test algorithm parameter validation."""
        # Test valid genetic algorithm parameters
        valid_genetic_params = {
            'population_size': 50,
            'generations': 100,
            'mutation_rate': 0.1,
            'crossover_rate': 0.8,
            'elite_size': 5
        }
        
        errors = self.config_manager._validate_algorithm_params('genetic', valid_genetic_params)
        self.assertEqual(len(errors), 0)
        
        # Test invalid genetic algorithm parameters
        invalid_genetic_params = {
            'population_size': 5,     # Below minimum
            'mutation_rate': 1.5,     # Above maximum
            'crossover_rate': 'bad'   # Wrong type
        }
        
        errors = self.config_manager._validate_algorithm_params('genetic', invalid_genetic_params)
        self.assertGreater(len(errors), 0)
        
        # Test OR-Tools parameters
        valid_ortools_params = {
            'time_limit_seconds': 300,
            'target_class_size': 25,
            'friend_weight': 10
        }
        
        errors = self.config_manager._validate_algorithm_params('or_tools', valid_ortools_params)
        self.assertEqual(len(errors), 0)
    
    def test_validate_parameter_types(self):
        """Test parameter type validation."""
        # Test integer parameter
        int_schema = {'type': int, 'min': 1, 'max': 100, 'default': 50}
        
        # Valid integer
        errors = self.config_manager._validate_parameter('test_param', 50, int_schema)
        self.assertEqual(len(errors), 0)
        
        # Invalid type
        errors = self.config_manager._validate_parameter('test_param', 'not_int', int_schema)
        self.assertGreater(len(errors), 0)
        self.assertIn('must be of type int', errors[0])
        
        # Out of range
        errors = self.config_manager._validate_parameter('test_param', 150, int_schema)
        self.assertGreater(len(errors), 0)
        self.assertIn('must be <=', errors[0])
        
        # Test string parameter with options
        string_schema = {'type': str, 'options': ['option1', 'option2'], 'default': 'option1'}
        
        # Valid option
        errors = self.config_manager._validate_parameter('test_param', 'option1', string_schema)
        self.assertEqual(len(errors), 0)
        
        # Invalid option
        errors = self.config_manager._validate_parameter('test_param', 'bad_option', string_schema)
        self.assertGreater(len(errors), 0)
        self.assertIn('must be one of', errors[0])
    
    def test_create_configuration_template(self):
        """Test configuration template creation."""
        # Test optimizer template
        template = self.config_manager.create_configuration_template(
            ConfigurationType.OPTIMIZER, 
            'genetic'
        )
        
        self.assertIn('optimization', template)
        self.assertIn('constraints', template)
        self.assertIn('performance', template)
        
        # Check default algorithm is set correctly
        self.assertEqual(template['optimization']['default_algorithm'], 'genetic')
        
        # Check genetic algorithm is included
        self.assertIn('genetic', template['optimization']['algorithms'])
        genetic_config = template['optimization']['algorithms']['genetic']
        self.assertTrue(genetic_config['enabled'])
        self.assertIn('population_size', genetic_config)
        
        # Test combined template
        combined_template = self.config_manager.create_configuration_template(
            ConfigurationType.COMBINED
        )
        
        self.assertIn('optimization', combined_template)
        self.assertIn('scoring', combined_template)
    
    def test_apply_profile(self):
        """Test applying configuration profiles."""
        base_config = self.config_manager.create_configuration_template()
        
        # Apply small_school profile
        small_school_config = self.config_manager.apply_profile('small_school', base_config)
        
        # Should have OR-Tools as default algorithm
        self.assertEqual(
            small_school_config['optimization']['default_algorithm'], 
            'or_tools'
        )
        
        # Should have OR-Tools enabled
        ortools_config = small_school_config['optimization']['algorithms']['or_tools']
        self.assertTrue(ortools_config['enabled'])
        
        # Test profile not found
        with self.assertRaises(ConfigurationError):
            self.config_manager.apply_profile('nonexistent_profile')
    
    def test_deep_merge(self):
        """Test deep merging of configurations."""
        base = {
            'level1': {
                'level2': {
                    'key1': 'base_value1',
                    'key2': 'base_value2'
                },
                'other_key': 'base_other'
            }
        }
        
        override = {
            'level1': {
                'level2': {
                    'key1': 'override_value1',
                    'key3': 'new_value3'
                }
            }
        }
        
        result = self.config_manager._deep_merge(base, override)
        
        # Check merged values
        self.assertEqual(result['level1']['level2']['key1'], 'override_value1')  # Overridden
        self.assertEqual(result['level1']['level2']['key2'], 'base_value2')     # Preserved
        self.assertEqual(result['level1']['level2']['key3'], 'new_value3')      # Added
        self.assertEqual(result['level1']['other_key'], 'base_other')           # Preserved
    
    def test_save_configuration(self):
        """Test saving configuration to file."""
        config_to_save = self.valid_optimizer_config
        filename = 'test_save_config.yaml'
        
        # Test saving with validation
        self.config_manager.save_configuration(config_to_save, filename, validate=True)
        
        # Check file was created
        saved_file = Path(self.temp_dir) / filename
        self.assertTrue(saved_file.exists())
        
        # Check content
        with open(saved_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        self.assertEqual(loaded_config, config_to_save)
        
        # Test saving invalid config with validation
        with self.assertRaises(ConfigurationError):
            self.config_manager.save_configuration(
                self.invalid_config, 
                'invalid_config.yaml', 
                validate=True
            )
    
    def test_get_profile_recommendations(self):
        """Test profile recommendations based on school characteristics."""
        # Small school recommendation
        small_recommendations = self.config_manager.get_profile_recommendations(150)
        self.assertIn('small_school', small_recommendations)
        
        # Large school recommendation
        large_recommendations = self.config_manager.get_profile_recommendations(600)
        self.assertIn('large_school', large_recommendations)
        
        # Medium school recommendation
        medium_recommendations = self.config_manager.get_profile_recommendations(300)
        self.assertIn('balanced', medium_recommendations)
        
        # Time-based recommendations
        quick_recommendations = self.config_manager.get_profile_recommendations(300, time_limit=30)
        # Should prefer fast algorithms for quick optimization
        recommended_profiles = [self.config_manager.profiles[p] for p in quick_recommendations]
        has_fast_profile = any('fast' in p.tags for p in recommended_profiles)
        self.assertTrue(has_fast_profile or 'large_school' in quick_recommendations)
    
    def test_get_available_profiles(self):
        """Test getting available profiles metadata."""
        profiles_info = self.config_manager.get_available_profiles()
        
        self.assertIsInstance(profiles_info, list)
        self.assertGreater(len(profiles_info), 0)
        
        # Check profile structure
        for profile_info in profiles_info:
            self.assertIn('name', profile_info)
            self.assertIn('display_name', profile_info)
            self.assertIn('description', profile_info)
            self.assertIn('tags', profile_info)
            self.assertIn('config_type', profile_info)
    
    def test_configuration_profile_dataclass(self):
        """Test ConfigurationProfile dataclass."""
        profile = ConfigurationProfile(
            name="Test Profile",
            description="A test profile",
            config_type=ConfigurationType.OPTIMIZER,
            config_data={'test': 'data'},
            tags=['test', 'example']
        )
        
        self.assertEqual(profile.name, "Test Profile")
        self.assertEqual(profile.description, "A test profile")
        self.assertEqual(profile.config_type, ConfigurationType.OPTIMIZER)
        self.assertEqual(profile.config_data, {'test': 'data'})
        self.assertEqual(profile.tags, ['test', 'example'])
        self.assertEqual(profile.author, "Meshachvetz")  # Default value
        self.assertEqual(profile.version, "1.0.0")       # Default value
    
    def test_configuration_type_enum(self):
        """Test ConfigurationType enum."""
        self.assertEqual(ConfigurationType.OPTIMIZER.value, "optimizer")
        self.assertEqual(ConfigurationType.SCORER.value, "scorer")
        self.assertEqual(ConfigurationType.COMBINED.value, "combined")
    
    def test_algorithm_schemas(self):
        """Test algorithm schema definitions."""
        # Test that all expected algorithms have schemas
        expected_algorithms = ['random_swap', 'genetic', 'simulated_annealing', 'local_search', 'or_tools']
        
        for algorithm in expected_algorithms:
            self.assertIn(algorithm, ALGORITHM_SCHEMAS)
            
        # Test genetic algorithm schema structure
        genetic_schema = ALGORITHM_SCHEMAS['genetic']
        expected_genetic_params = ['population_size', 'generations', 'mutation_rate', 'crossover_rate', 'elite_size']
        
        for param in expected_genetic_params:
            self.assertIn(param, genetic_schema)
            self.assertIn('type', genetic_schema[param])
            self.assertIn('default', genetic_schema[param])
        
        # Test OR-Tools schema
        ortools_schema = ALGORITHM_SCHEMAS['or_tools']
        expected_ortools_params = ['time_limit_seconds', 'target_class_size', 'class_size_tolerance']
        
        for param in expected_ortools_params:
            self.assertIn(param, ortools_schema)
    
    def test_constraint_schemas(self):
        """Test constraint schema definitions."""
        # Test minimum_friends constraint schema
        self.assertIn('minimum_friends', CONSTRAINT_SCHEMAS)
        min_friends_schema = CONSTRAINT_SCHEMAS['minimum_friends']
        
        expected_params = ['default', 'allow_override', 'max_allowed']
        for param in expected_params:
            self.assertIn(param, min_friends_schema)
            self.assertIn('type', min_friends_schema[param])
        
        # Test class_size_limits constraint schema
        self.assertIn('class_size_limits', CONSTRAINT_SCHEMAS)
        class_size_schema = CONSTRAINT_SCHEMAS['class_size_limits']
        
        expected_size_params = ['min_students_per_class', 'max_students_per_class', 'preferred_students_per_class']
        for param in expected_size_params:
            self.assertIn(param, class_size_schema)
    
    def test_interactive_configuration_wizard(self):
        """Test interactive configuration wizard placeholder."""
        # This is currently a placeholder method
        result = self.config_manager.interactive_configuration_wizard()
        
        # Should return a template configuration
        self.assertIsInstance(result, dict)
        self.assertIn('optimization', result)


class TestConfigurationErrors(unittest.TestCase):
    """Test configuration error handling."""
    
    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        error_message = "Test configuration error"
        
        with self.assertRaises(ConfigurationError) as context:
            raise ConfigurationError(error_message)
        
        self.assertEqual(str(context.exception), error_message)


if __name__ == '__main__':
    unittest.main() 