import pytest
import pandas as pd
from pathlib import Path

# Test data path
TEST_DATA_PATH = Path(__file__).parent.parent / 'data' / 'test_cases' / 'simple_test.csv'

def test_data_loading():
    """Test that we can load the test data correctly."""
    df = pd.read_csv(TEST_DATA_PATH)
    assert len(df) == 15, "Should have 15 students in the test data"
    assert 'student_id' in df.columns, "Should have student_id column"
    assert 'behavior_rank' in df.columns, "Should have behavior_rank column"
    assert 'preferred_friend_1' in df.columns, "Should have preferred_friend_1 column"
    assert 'preferred_friend_2' in df.columns, "Should have preferred_friend_2 column"
    assert 'special_needs' in df.columns, "Should have special_needs column"

def test_behavior_rank_distribution():
    """Test that behavior ranks are distributed as expected."""
    df = pd.read_csv(TEST_DATA_PATH)
    rank_counts = df['behavior_rank'].value_counts()
    assert len(rank_counts) == 3, "Should have exactly 3 behavior ranks (A, B, C)"
    assert all(rank_counts == 5), "Each rank should have exactly 5 students"

def test_friend_preferences():
    """Test that friend preferences are valid."""
    df = pd.read_csv(TEST_DATA_PATH)
    student_ids = set(df['student_id'])
    
    # Check that preferred friends are valid student IDs
    for col in ['preferred_friend_1', 'preferred_friend_2']:
        assert all(df[col].isin(student_ids)), f"All {col} should be valid student IDs"
    
    # Check that students don't prefer themselves
    assert all(df['student_id'] != df['preferred_friend_1']), "Students shouldn't prefer themselves as friend 1"
    assert all(df['student_id'] != df['preferred_friend_2']), "Students shouldn't prefer themselves as friend 2" 