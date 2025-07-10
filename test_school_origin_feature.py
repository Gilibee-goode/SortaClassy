#!/usr/bin/env python3
"""
Test script for the new school origin balance feature.
Creates sample data and tests the functionality.
"""

import pandas as pd
import os
from src.meshachvetz.scorer.main_scorer import Scorer
from src.meshachvetz.utils.config import Config

def create_test_data():
    """Create test data with students from different schools."""
    # Create sample data with 5 schools as per your example: 60, 50, 40, 30, 15 students
    students_data = []
    
    # School A: 60 students
    for i in range(60):
        students_data.append({
            'student_id': f'{100000000 + i:09d}',
            'first_name': f'Student{i}',
            'last_name': 'SchoolA',
            'gender': 'M' if i % 2 == 0 else 'F',
            'class': str((i % 5) + 1),  # Distribute among 5 classes
            'academic_score': 80.0 + (i % 20),
            'behavior_rank': 'A',
            'studentiality_rank': 'A',
            'assistance_package': 'false',
            'school': 'School A',
            'preferred_friend_1': '',
            'preferred_friend_2': '',
            'preferred_friend_3': '',
            'disliked_peer_1': '',
            'disliked_peer_2': '',
            'disliked_peer_3': '',
            'disliked_peer_4': '',
            'disliked_peer_5': '',
            'force_class': '',
            'force_friend': ''
        })
    
    # School B: 50 students
    for i in range(50):
        students_data.append({
            'student_id': f'{200000000 + i:09d}',
            'first_name': f'Student{i}',
            'last_name': 'SchoolB',
            'gender': 'M' if i % 2 == 0 else 'F',
            'class': str((i % 5) + 1),
            'academic_score': 75.0 + (i % 25),
            'behavior_rank': 'B',
            'studentiality_rank': 'B',
            'assistance_package': 'false',
            'school': 'School B',
            'preferred_friend_1': '',
            'preferred_friend_2': '',
            'preferred_friend_3': '',
            'disliked_peer_1': '',
            'disliked_peer_2': '',
            'disliked_peer_3': '',
            'disliked_peer_4': '',
            'disliked_peer_5': '',
            'force_class': '',
            'force_friend': ''
        })
    
    # School C: 40 students
    for i in range(40):
        students_data.append({
            'student_id': f'{300000000 + i:09d}',
            'first_name': f'Student{i}',
            'last_name': 'SchoolC',
            'gender': 'M' if i % 2 == 0 else 'F',
            'class': str((i % 5) + 1),
            'academic_score': 85.0 + (i % 15),
            'behavior_rank': 'A',
            'studentiality_rank': 'B',
            'assistance_package': 'false',
            'school': 'School C',
            'preferred_friend_1': '',
            'preferred_friend_2': '',
            'preferred_friend_3': '',
            'disliked_peer_1': '',
            'disliked_peer_2': '',
            'disliked_peer_3': '',
            'disliked_peer_4': '',
            'disliked_peer_5': '',
            'force_class': '',
            'force_friend': ''
        })
    
    # School D: 30 students
    for i in range(30):
        students_data.append({
            'student_id': f'{400000000 + i:09d}',
            'first_name': f'Student{i}',
            'last_name': 'SchoolD',
            'gender': 'M' if i % 2 == 0 else 'F',
            'class': str((i % 5) + 1),
            'academic_score': 70.0 + (i % 30),
            'behavior_rank': 'B',
            'studentiality_rank': 'B',
            'assistance_package': 'false',
            'school': 'School D',
            'preferred_friend_1': '',
            'preferred_friend_2': '',
            'preferred_friend_3': '',
            'disliked_peer_1': '',
            'disliked_peer_2': '',
            'disliked_peer_3': '',
            'disliked_peer_4': '',
            'disliked_peer_5': '',
            'force_class': '',
            'force_friend': ''
        })
    
    # School E: 15 students (small school)
    for i in range(15):
        students_data.append({
            'student_id': f'{500000000 + i:09d}',
            'first_name': f'Student{i}',
            'last_name': 'SchoolE',
            'gender': 'M' if i % 2 == 0 else 'F',
            'class': str((i % 3) + 1),  # Concentrate in first 3 classes
            'academic_score': 90.0 + (i % 10),
            'behavior_rank': 'A',
            'studentiality_rank': 'A',
            'assistance_package': 'false',
            'school': 'School E',
            'preferred_friend_1': '',
            'preferred_friend_2': '',
            'preferred_friend_3': '',
            'disliked_peer_1': '',
            'disliked_peer_2': '',
            'disliked_peer_3': '',
            'disliked_peer_4': '',
            'disliked_peer_5': '',
            'force_class': '',
            'force_friend': ''
        })
    
    return students_data

def test_school_origin_balance():
    """Test the school origin balance feature."""
    print("🧪 Testing School Origin Balance Feature")
    print("=" * 50)
    
    # Create test data
    print("📝 Creating test data...")
    students_data = create_test_data()
    
    # Create DataFrame
    df = pd.DataFrame(students_data)
    
    # Save to temporary CSV
    test_csv = "test_school_origin_data.csv"
    df.to_csv(test_csv, index=False)
    print(f"💾 Saved test data to {test_csv}")
    
    # Create config with school origin balance enabled
    config = Config()
    config.weights.school_origin_balance = 0.3  # Give it significant weight
    print(f"⚙️  Set school origin balance weight to {config.weights.school_origin_balance}")
    
    # Initialize scorer
    scorer = Scorer(config)
    
    # Load and score data
    print("🔍 Loading and scoring data...")
    school_data = scorer.load_data(test_csv)
    result = scorer.calculate_scores(school_data)
    
    # Print results
    print(f"\n📊 SCORING RESULTS")
    print(f"Final Score: {result.final_score:.2f}/100")
    print(f"School Layer Score: {result.school_layer_score:.2f}/100")
    
    # Print school origin balance details
    school_origin_balance = result.school_scores['school_origin_balance']
    print(f"\n🏫 SCHOOL ORIGIN BALANCE DETAILS")
    print(f"School Origin Balance Score: {school_origin_balance['score']:.2f}/100")
    
    # Print school distribution
    print(f"\n📈 SCHOOL DISTRIBUTION")
    for school, count in school_data.school_distribution.items():
        size_category = school_data.get_school_size_category(school)
        print(f"  {school}: {count} students ({size_category})")
    
    # Print adaptive targets
    if 'adaptive_targets' in school_origin_balance:
        print(f"\n🎯 ADAPTIVE TARGETS")
        for school, target in school_origin_balance['adaptive_targets'].items():
            print(f"  {school}: {target*100:.0f}% class presence target")
    
    # Print representation scores
    if 'representation_scores' in school_origin_balance:
        print(f"\n📊 REPRESENTATION SCORES")
        for school, score in school_origin_balance['representation_scores'].items():
            print(f"  {school}: {score:.1f}/100")
    
    # Print class distribution details
    print(f"\n🏫 CLASS DISTRIBUTION")
    class_dist = school_data.get_school_distribution_by_class()
    for class_id, schools in class_dist.items():
        total_in_class = sum(schools.values())
        print(f"  Class {class_id} ({total_in_class} students):")
        for school, count in schools.items():
            percentage = (count / total_in_class * 100) if total_in_class > 0 else 0
            print(f"    {school}: {count} ({percentage:.1f}%)")
    
    # Test diversity scores
    print(f"\n🌈 CLASS DIVERSITY SCORES")
    for class_id, class_data in school_data.classes.items():
        diversity_score = class_data.school_diversity_score
        dominance_score = class_data.get_school_dominance_score()
        print(f"  Class {class_id}: Diversity={diversity_score:.1f}/100, Non-dominance={dominance_score:.1f}/100")
    
    # Generate reports
    print(f"\n📋 Generating reports...")
    output_dir = scorer.generate_csv_reports(result, "test_school_origin_reports")
    print(f"📁 Reports saved to: {output_dir}")
    
    # Display focused summary
    print(f"\n{scorer.get_focused_summary(result)}")
    
    # Cleanup
    if os.path.exists(test_csv):
        os.remove(test_csv)
        print(f"🗑️  Cleaned up {test_csv}")
    
    print(f"\n✅ Test completed successfully!")
    return result

if __name__ == "__main__":
    try:
        result = test_school_origin_balance()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 