"""
Configuration management for Meshachvetz - handles YAML configuration files
for scoring weights and system parameters.
"""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from dataclasses import dataclass


class ConfigError(Exception):
    """Exception raised when configuration is invalid."""
    pass


@dataclass
class ScoringWeights:
    """Configuration for scoring weights."""
    # Student layer weights
    friends: float = 0.7
    dislikes: float = 0.3
    
    # Class layer weights
    gender_balance: float = 1.0
    
    # School layer weights
    academic_balance: float = 0.3
    behavior_balance: float = 0.2
    size_balance: float = 0.3
    assistance_balance: float = 0.2
    
    # Layer weights
    student_layer: float = 0.5
    class_layer: float = 0.2
    school_layer: float = 0.3
    
    def validate(self) -> None:
        """Validate that all weights are positive."""
        weights = [
            self.friends, self.dislikes, self.gender_balance,
            self.academic_balance, self.behavior_balance,
            self.size_balance, self.assistance_balance,
            self.student_layer, self.class_layer, self.school_layer
        ]
        
        for weight in weights:
            if weight < 0:
                raise ConfigError(f"Weight cannot be negative: {weight}")


@dataclass 
class NormalizationFactors:
    """Configuration for normalization factors."""
    academic_score_factor: float = 2.0
    behavior_rank_factor: float = 25.0
    class_size_factor: float = 5.0
    assistance_count_factor: float = 10.0
    
    def validate(self) -> None:
        """Validate that all factors are positive."""
        factors = [
            self.academic_score_factor, self.behavior_rank_factor,
            self.class_size_factor, self.assistance_count_factor
        ]
        
        for factor in factors:
            if factor <= 0:
                raise ConfigError(f"Normalization factor must be positive: {factor}")


@dataclass
class ValidationRules:
    """Configuration for data validation rules."""
    # Student ID validation
    student_id_length: int = 9
    student_id_pattern: str = r'^\d{9}$'
    
    # Name validation
    max_name_length: int = 50
    
    # Academic score validation
    min_academic_score: float = 0.0
    max_academic_score: float = 100.0
    
    # Behavior rank validation
    valid_behavior_ranks: list = None
    
    # Boolean validation
    valid_boolean_values: list = None
    
    def __post_init__(self):
        """Set default values for lists."""
        if self.valid_behavior_ranks is None:
            self.valid_behavior_ranks = ['A', 'B', 'C', 'D', 'E']
        
        if self.valid_boolean_values is None:
            self.valid_boolean_values = [
                'true', 'false', '1', '0', 'yes', 'no',
                'True', 'False', 'TRUE', 'FALSE', 'YES', 'NO'
            ]
            
    def validate(self) -> None:
        """Validate configuration values."""
        if self.student_id_length <= 0:
            raise ConfigError("Student ID length must be positive")
        
        if self.max_name_length <= 0:
            raise ConfigError("Max name length must be positive")
            
        if self.min_academic_score < 0 or self.max_academic_score < 0:
            raise ConfigError("Academic score bounds must be non-negative")
            
        if self.min_academic_score >= self.max_academic_score:
            raise ConfigError("Min academic score must be less than max")


class Config:
    """
    Main configuration class for Meshachvetz.
    
    Manages loading and validation of YAML configuration files.
    """
    
    DEFAULT_CONFIG = {
        'weights': {
            'student_layer': {
                'friends': 0.7,
                'dislikes': 0.3
            },
            'class_layer': {
                'gender_balance': 1.0
            },
            'school_layer': {
                'academic_balance': 0.3,
                'behavior_balance': 0.2,
                'size_balance': 0.3,
                'assistance_balance': 0.2
            },
            'layers': {
                'student': 0.5,
                'class': 0.2,
                'school': 0.3
            }
        },
        'normalization': {
            'academic_score_factor': 2.0,
            'behavior_rank_factor': 25.0,
            'class_size_factor': 5.0,
            'assistance_count_factor': 10.0
        },
        'validation': {
            'student_id_length': 9,
            'max_name_length': 50,
            'min_academic_score': 0.0,
            'max_academic_score': 100.0,
            'valid_behavior_ranks': ['A', 'B', 'C', 'D', 'E'],
            'valid_boolean_values': [
                'true', 'false', '1', '0', 'yes', 'no',
                'True', 'False', 'TRUE', 'FALSE', 'YES', 'NO'
            ]
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to YAML configuration file. If None, uses defaults.
        """
        self.config_file = config_file
        self.config_data = {}
        
        # Load configuration
        if config_file:
            self.load_from_file(config_file)
        else:
            self.config_data = self.DEFAULT_CONFIG.copy()
            
        # Create structured configuration objects
        self._create_config_objects()
        
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to the YAML configuration file
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise ConfigError(f"Configuration file not found: {file_path}")
                
            with open(path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                
            # Merge with defaults
            self.config_data = self._merge_with_defaults(loaded_config)
            
            # Validate configuration
            self._validate_config()
            
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML file: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")
            
    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded configuration with defaults.
        
        Args:
            loaded_config: Configuration loaded from file
            
        Returns:
            Merged configuration
        """
        merged = self.DEFAULT_CONFIG.copy()
        
        # Deep merge function
        def deep_merge(base: Dict, update: Dict) -> Dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base
        
        return deep_merge(merged, loaded_config)
        
    def _validate_config(self) -> None:
        """Validate the configuration structure and values."""
        required_sections = ['weights', 'normalization', 'validation']
        
        for section in required_sections:
            if section not in self.config_data:
                raise ConfigError(f"Missing required configuration section: {section}")
                
        # Validate weights section
        weights = self.config_data['weights']
        required_weight_sections = ['student_layer', 'class_layer', 'school_layer', 'layers']
        
        for section in required_weight_sections:
            if section not in weights:
                raise ConfigError(f"Missing required weights section: {section}")
                
    def _create_config_objects(self) -> None:
        """Create structured configuration objects from config data."""
        # Create weights object
        weights_config = self.config_data['weights']
        self.weights = ScoringWeights(
            friends=weights_config['student_layer']['friends'],
            dislikes=weights_config['student_layer']['dislikes'],
            gender_balance=weights_config['class_layer']['gender_balance'],
            academic_balance=weights_config['school_layer']['academic_balance'],
            behavior_balance=weights_config['school_layer']['behavior_balance'],
            size_balance=weights_config['school_layer']['size_balance'],
            assistance_balance=weights_config['school_layer']['assistance_balance'],
            student_layer=weights_config['layers']['student'],
            class_layer=weights_config['layers']['class'],
            school_layer=weights_config['layers']['school']
        )
        
        # Create normalization factors object
        norm_config = self.config_data['normalization']
        self.normalization = NormalizationFactors(
            academic_score_factor=norm_config['academic_score_factor'],
            behavior_rank_factor=norm_config['behavior_rank_factor'],
            class_size_factor=norm_config['class_size_factor'],
            assistance_count_factor=norm_config['assistance_count_factor']
        )
        
        # Create validation rules object
        val_config = self.config_data['validation']
        self.validation = ValidationRules(
            student_id_length=val_config['student_id_length'],
            max_name_length=val_config['max_name_length'],
            min_academic_score=val_config['min_academic_score'],
            max_academic_score=val_config['max_academic_score'],
            valid_behavior_ranks=val_config['valid_behavior_ranks'],
            valid_boolean_values=val_config['valid_boolean_values']
        )
        
        # Validate all objects
        self.weights.validate()
        self.normalization.validate()
        self.validation.validate()
        
    def save_to_file(self, file_path: str) -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            file_path: Path where to save the configuration
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigError(f"Error saving configuration: {e}")
            
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config_data.copy()
        
    def update_weights(self, **kwargs) -> None:
        """
        Update scoring weights.
        
        Args:
            **kwargs: Weight values to update
        """
        valid_weights = [
            'friends', 'dislikes', 'gender_balance',
            'academic_balance', 'behavior_balance',
            'size_balance', 'assistance_balance',
            'student_layer', 'class_layer', 'school_layer'
        ]
        
        for key, value in kwargs.items():
            if key not in valid_weights:
                raise ConfigError(f"Invalid weight name: {key}")
                
            if value < 0:
                raise ConfigError(f"Weight cannot be negative: {key}={value}")
                
            # Update the appropriate weight
            if key in ['friends', 'dislikes']:
                self.config_data['weights']['student_layer'][key] = value
            elif key in ['gender_balance']:
                self.config_data['weights']['class_layer'][key] = value
            elif key in ['academic_balance', 'behavior_balance', 'size_balance', 'assistance_balance']:
                self.config_data['weights']['school_layer'][key] = value
            elif key in ['student_layer', 'class_layer', 'school_layer']:
                layer_key = key.replace('_layer', '')
                self.config_data['weights']['layers'][layer_key] = value
                
        # Recreate config objects
        self._create_config_objects()
        
    @classmethod
    def create_default_config_file(cls, file_path: str) -> None:
        """
        Create a default configuration file.
        
        Args:
            file_path: Path where to create the configuration file
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(cls.DEFAULT_CONFIG, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigError(f"Error creating default configuration: {e}")
            
    def get_summary(self) -> str:
        """
        Get a formatted summary of the configuration.
        
        Returns:
            Formatted configuration summary
        """
        summary = []
        summary.append("📊 Meshachvetz Configuration Summary")
        summary.append("=" * 40)
        
        # Weights section
        summary.append("\n🎯 Scoring Weights:")
        summary.append(f"  Student Layer:")
        summary.append(f"    Friends: {self.weights.friends}")
        summary.append(f"    Dislikes: {self.weights.dislikes}")
        summary.append(f"  Class Layer:")
        summary.append(f"    Gender Balance: {self.weights.gender_balance}")
        summary.append(f"  School Layer:")
        summary.append(f"    Academic Balance: {self.weights.academic_balance}")
        summary.append(f"    Behavior Balance: {self.weights.behavior_balance}")
        summary.append(f"    Size Balance: {self.weights.size_balance}")
        summary.append(f"    Assistance Balance: {self.weights.assistance_balance}")
        summary.append(f"  Layer Weights:")
        summary.append(f"    Student Layer: {self.weights.student_layer}")
        summary.append(f"    Class Layer: {self.weights.class_layer}")
        summary.append(f"    School Layer: {self.weights.school_layer}")
        
        # Normalization section
        summary.append(f"\n⚖️  Normalization Factors:")
        summary.append(f"  Academic Score Factor: {self.normalization.academic_score_factor}")
        summary.append(f"  Behavior Rank Factor: {self.normalization.behavior_rank_factor}")
        summary.append(f"  Class Size Factor: {self.normalization.class_size_factor}")
        summary.append(f"  Assistance Count Factor: {self.normalization.assistance_count_factor}")
        
        # Validation section
        summary.append(f"\n✅ Validation Rules:")
        summary.append(f"  Student ID Length: {self.validation.student_id_length}")
        summary.append(f"  Max Name Length: {self.validation.max_name_length}")
        summary.append(f"  Academic Score Range: {self.validation.min_academic_score}-{self.validation.max_academic_score}")
        summary.append(f"  Valid Behavior Ranks: {', '.join(self.validation.valid_behavior_ranks)}")
        
        if self.config_file:
            summary.append(f"\n📁 Loaded from: {self.config_file}")
        else:
            summary.append(f"\n📁 Using default configuration")
            
        return "\n".join(summary) 