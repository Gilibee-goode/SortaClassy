#!/usr/bin/env python3
"""
Test suite for Week 7 Interactive CLI implementation.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call
from io import StringIO
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz.cli.interactive_cli import InteractiveSession


class TestInteractiveSession:
    """Test the InteractiveSession class."""
    
    def test_initialization(self):
        """Test that InteractiveSession initializes correctly."""
        session = InteractiveSession()
        assert session.current_config is None
        assert session.temp_config_overrides == {}
        assert session.session_active is True
        
    def test_display_header(self, capsys):
        """Test header display."""
        session = InteractiveSession()
        session.display_header()
        captured = capsys.readouterr()
        assert "MESHACHVETZ" in captured.out
        assert "Interactive Menu System" in captured.out
        
    def test_display_config_summary(self, capsys):
        """Test configuration summary display."""
        session = InteractiveSession()
        session.display_config_summary()
        captured = capsys.readouterr()
        assert "Current Configuration Summary" in captured.out
        assert "Layer Weights" in captured.out
        assert "Student Layer" in captured.out
        assert "Class Layer" in captured.out
        assert "School Layer" in captured.out
        assert "Student Layer Weights" in captured.out
        assert "Friends" in captured.out
        assert "Dislikes" in captured.out
        assert "Class Layer Weights" in captured.out
        assert "Gender Balance" in captured.out
        assert "School Layer Weights" in captured.out
        assert "Academic Balance" in captured.out
        assert "Behavior Balance" in captured.out
        assert "Size Balance" in captured.out
        assert "Assistance Balance" in captured.out
        assert "Normalization Factors" in captured.out
        assert "Academic Score Factor" in captured.out
        assert "Behavior Rank Factor" in captured.out
        assert "Class Size Factor" in captured.out
        assert "Assistance Count Factor" in captured.out
        
    def test_display_main_menu(self, capsys):
        """Test main menu display."""
        session = InteractiveSession()
        session.display_main_menu()
        captured = capsys.readouterr()
        assert "MAIN MENU" in captured.out
        assert "Score Assignment" in captured.out
        assert "Optimize Assignment" in captured.out
        assert "Configuration" in captured.out
        
    def test_display_config_menu(self, capsys):
        """Test configuration menu display."""
        session = InteractiveSession()
        session.display_config_menu()
        captured = capsys.readouterr()
        assert "CONFIGURATION MENU" in captured.out
        assert "Show Current Configuration" in captured.out
        assert "Set Configuration File" in captured.out
        
    def test_show_help(self, capsys):
        """Test help display."""
        session = InteractiveSession()
        session.show_help()
        captured = capsys.readouterr()
        assert "HELP" in captured.out
        assert "Navigation" in captured.out
        assert "Features" in captured.out
        
    @patch('builtins.input', return_value='1')
    def test_get_user_input_valid(self, mock_input):
        """Test valid user input."""
        session = InteractiveSession()
        result = session.get_user_input("Select option", ['1', '2', '3'])
        assert result == '1'
        
    @patch('builtins.input', return_value='exit')
    def test_get_user_input_exit(self, mock_input):
        """Test exit input."""
        session = InteractiveSession()
        result = session.get_user_input("Select option", ['1', '2', '3'])
        assert result == 'exit'
        assert session.session_active is False
        
    @patch('builtins.input', side_effect=['invalid', '1'])
    def test_get_user_input_invalid_then_valid(self, mock_input, capsys):
        """Test invalid input followed by valid input."""
        session = InteractiveSession()
        result = session.get_user_input("Select option", ['1', '2', '3'])
        assert result == '1'
        captured = capsys.readouterr()
        assert "Invalid option" in captured.out
        
    @patch('builtins.input', return_value='help')
    def test_get_user_input_help(self, mock_input):
        """Test help input."""
        session = InteractiveSession()
        with patch.object(session, 'show_help') as mock_show_help:
            with patch('builtins.input', side_effect=['help', '1']):
                result = session.get_user_input("Select option", ['1', '2', '3'])
                assert result == '1'
                mock_show_help.assert_called_once()
                
    @patch('builtins.input', return_value='examples/sample_data/students_sample.csv')
    def test_get_file_path_valid(self, mock_input):
        """Test valid file path."""
        session = InteractiveSession()
        # Create a mock file
        sample_file = Path('examples/sample_data/students_sample.csv')
        if sample_file.exists():
            result = session.get_file_path("Enter file path")
            assert result == str(sample_file)
        else:
            pytest.skip("Sample file not found")
            
    @patch('builtins.input', return_value='nonexistent.csv')
    def test_get_file_path_invalid(self, mock_input, capsys):
        """Test invalid file path."""
        session = InteractiveSession()
        with patch('builtins.input', side_effect=['nonexistent.csv', 'exit']):
            result = session.get_file_path("Enter file path")
            assert result is None
            captured = capsys.readouterr()
            assert "File not found" in captured.out
            
    @patch('builtins.input', return_value='y')
    def test_ask_config_override_yes(self, mock_input):
        """Test config override confirmation - yes."""
        session = InteractiveSession()
        result = session.ask_config_override()
        assert result is True
        
    @patch('builtins.input', return_value='n')
    def test_ask_config_override_no(self, mock_input):
        """Test config override confirmation - no."""
        session = InteractiveSession()
        result = session.ask_config_override()
        assert result is False
        
    @patch('builtins.input', side_effect=['1', '0.5'])
    def test_handle_temp_config_override_student_weight(self, mock_input, capsys):
        """Test temporary config override for student weight."""
        session = InteractiveSession()
        session.handle_temp_config_override()
        assert session.temp_config_overrides['student_layer'] == 0.5
        captured = capsys.readouterr()
        assert "Student layer weight set to 0.5" in captured.out
        
    @patch('builtins.input', return_value='6')
    def test_handle_temp_config_override_clear(self, mock_input, capsys):
        """Test clearing temporary config overrides."""
        session = InteractiveSession()
        session.temp_config_overrides = {'student_layer': 0.5}
        session.handle_temp_config_override()
        assert session.temp_config_overrides == {}
        captured = capsys.readouterr()
        assert "All temporary overrides cleared" in captured.out
        
    @patch('builtins.input', return_value='7')
    def test_handle_temp_config_override_back(self, mock_input):
        """Test back option in temp config override."""
        session = InteractiveSession()
        session.handle_temp_config_override()
        # Should return without error
        assert True
        
    def test_temp_config_overrides_display(self, capsys):
        """Test that temp config overrides are displayed."""
        session = InteractiveSession()
        session.temp_config_overrides = {'student_layer': 0.5, 'friends': 0.8}
        session.display_config_summary()
        captured = capsys.readouterr()
        assert "Temporary Overrides Active" in captured.out
        assert "student_layer: 0.5" in captured.out
        assert "friends: 0.8" in captured.out


class TestInteractiveSessionIntegration:
    """Integration tests for InteractiveSession."""
    
    @patch('meshachvetz.cli.interactive_cli.handle_show_config_command')
    @patch('builtins.input', side_effect=['1', '6'])
    def test_config_menu_show_config(self, mock_input, mock_show_config):
        """Test config menu show configuration."""
        session = InteractiveSession()
        session.handle_configuration_menu()
        mock_show_config.assert_called_once()
        
    @patch('meshachvetz.cli.interactive_cli.handle_config_status_command')
    @patch('builtins.input', side_effect=['4', '6'])
    def test_config_menu_status(self, mock_input, mock_status):
        """Test config menu status."""
        session = InteractiveSession()
        session.handle_configuration_menu()
        mock_status.assert_called_once()
        
    @patch('meshachvetz.cli.interactive_cli.handle_config_reset_command')
    @patch('builtins.input', side_effect=['3', 'y', '6'])
    def test_config_menu_reset(self, mock_input, mock_reset):
        """Test config menu reset."""
        session = InteractiveSession()
        session.handle_configuration_menu()
        mock_reset.assert_called_once()
        assert session.current_config is None
        assert session.temp_config_overrides == {}
        
    @patch('meshachvetz.cli.interactive_cli.handle_validate_command')
    @patch('builtins.input', side_effect=['examples/sample_data/students_sample.csv'])
    def test_handle_validate_data(self, mock_input, mock_validate):
        """Test data validation handling."""
        session = InteractiveSession()
        sample_file = Path('examples/sample_data/students_sample.csv')
        if sample_file.exists():
            session.handle_validate_data()
            mock_validate.assert_called_once()
        else:
            pytest.skip("Sample file not found")


def test_main_function():
    """Test the main function can be called."""
    from meshachvetz.cli.interactive_cli import main
    
    # Mock the InteractiveSession to avoid actual interaction
    with patch('meshachvetz.cli.interactive_cli.InteractiveSession') as mock_session:
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance
        
        # Call main function
        main()
        
        # Verify session was created and run was called
        mock_session.assert_called_once()
        mock_instance.run.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 