#!/usr/bin/env python3
"""
Comprehensive Test Suite for Meshachvetz Scoring System

This script tests three scenarios:
1. Perfect Score Test - Optimally arranged students
2. Bad Score Test - Poorly arranged students  
3. Large Dataset Test - Performance with 60 students

Each test provides detailed analysis and performance metrics.
"""

import sys
import os
import time
import shutil
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz import Scorer, Config

def analyze_results(test_name: str, result, scorer: Scorer, processing_time: float, students_count: int) -> dict:
    """Analyze and display results for a test case."""
    
    print(f"\n📊 {test_name.upper()} ANALYSIS")
    print("=" * 60)
    
    # Basic metrics
    print(f"🎯 Overall Performance:")
    print(f"   Final Score: {result.final_score:.2f}/100")
    print(f"   Processing Time: {processing_time:.3f}s")
    print(f"   Students: {students_count}")
    print(f"   Classes: {result.total_classes}")
    print(f"   Throughput: {students_count/processing_time:.1f} students/second")
    
    # Layer breakdown
    print(f"\n🏗️  Layer Breakdown:")
    print(f"   Student Layer: {result.student_layer_score:.2f}/100 (weight: {result.layer_weights['student']:.1f})")
    print(f"   Class Layer:   {result.class_layer_score:.2f}/100 (weight: {result.layer_weights['class']:.1f})")
    print(f"   School Layer:  {result.school_layer_score:.2f}/100 (weight: {result.layer_weights['school']:.1f})")
    
    # Student satisfaction analysis
    satisfaction_summary = scorer.get_student_satisfaction_summary(result)
    print(f"\n👥 Student Satisfaction Analysis:")
    print(f"   Average Satisfaction: {satisfaction_summary['average_satisfaction']:.1f}/100")
    print(f"   Highly Satisfied (≥75): {satisfaction_summary['highly_satisfied_count']}/{students_count} ({satisfaction_summary['highly_satisfied_count']/students_count*100:.1f}%)")
    print(f"   Moderately Satisfied (50-74): {satisfaction_summary['moderately_satisfied_count']}/{students_count} ({satisfaction_summary['moderately_satisfied_count']/students_count*100:.1f}%)")
    print(f"   Low Satisfaction (<50): {satisfaction_summary['low_satisfaction_count']}/{students_count} ({satisfaction_summary['low_satisfaction_count']/students_count*100:.1f}%)")
    print(f"   Perfect Satisfaction (≥95): {satisfaction_summary['perfect_satisfaction_count']}/{students_count} ({satisfaction_summary['perfect_satisfaction_count']/students_count*100:.1f}%)")
    
    # Social metrics
    print(f"\n👫 Social Metrics:")
    print(f"   Total Friend Requests: {satisfaction_summary['total_friend_requests']}")
    print(f"   Friends Successfully Placed: {satisfaction_summary['total_friends_placed']}")
    friend_success_rate = (satisfaction_summary['total_friends_placed'] / satisfaction_summary['total_friend_requests'] * 100) if satisfaction_summary['total_friend_requests'] > 0 else 0
    print(f"   Friend Placement Rate: {friend_success_rate:.1f}%")
    print(f"   Students with Friends Placed: {satisfaction_summary['students_with_friends_placed']}/{students_count} ({satisfaction_summary['students_with_friends_placed']/students_count*100:.1f}%)")
    print(f"   Students with Conflicts: {satisfaction_summary['students_with_conflicts']}/{students_count} ({satisfaction_summary['students_with_conflicts']/students_count*100:.1f}%)")
    
    # Class balance analysis
    print(f"\n🏫 Class Balance Analysis:")
    for class_id, class_result in result.class_scores.items():
        gender_balance = class_result['gender_balance']
        total_in_class = gender_balance['male_count'] + gender_balance['female_count']
        print(f"   Class {class_id}: {class_result['score']:.1f}/100 (Size: {total_in_class}, M:{gender_balance['male_count']}/F:{gender_balance['female_count']})")
    
    # School balance analysis
    print(f"\n🏛️  School Balance Analysis:")
    school_scores = result.school_scores
    print(f"   Academic Balance: {school_scores['academic_balance']['score']:.1f}/100 (σ={school_scores['academic_balance']['std_dev']:.2f})")
    print(f"   Behavior Balance: {school_scores['behavior_balance']['score']:.1f}/100 (σ={school_scores['behavior_balance']['std_dev']:.2f})")
    print(f"   Size Balance: {school_scores['size_balance']['score']:.1f}/100 (σ={school_scores['size_balance']['std_dev']:.2f})")
    print(f"   Assistance Balance: {school_scores['assistance_balance']['score']:.1f}/100 (σ={school_scores['assistance_balance']['std_dev']:.2f})")
    
    # Performance rating
    performance_rating = "🟢 Excellent" if processing_time < 0.1 else "🟡 Good" if processing_time < 1.0 else "🟠 Acceptable" if processing_time < 5.0 else "🔴 Slow"
    print(f"\n⚡ Performance Rating: {performance_rating}")
    
    return {
        'test_name': test_name,
        'final_score': result.final_score,
        'processing_time': processing_time,
        'students_count': students_count,
        'classes_count': result.total_classes,
        'throughput': students_count/processing_time,
        'satisfaction_summary': satisfaction_summary,
        'friend_success_rate': friend_success_rate,
        'layer_scores': {
            'student': result.student_layer_score,
            'class': result.class_layer_score,
            'school': result.school_layer_score
        }
    }

def test_scenario(file_path: str, test_name: str, expected_score_range: tuple) -> dict:
    """Test a single scenario and return analysis."""
    
    if not os.path.exists(file_path):
        print(f"❌ Test file not found: {file_path}")
        return None
    
    print(f"\n🧪 Testing: {test_name}")
    print(f"📁 File: {file_path}")
    
    # Create scorer
    scorer = Scorer()
    
    # Time the scoring process
    start_time = time.time()
    result = scorer.score_csv_file(file_path)
    processing_time = time.time() - start_time
    
    # Analyze results
    analysis = analyze_results(test_name, result, scorer, processing_time, result.total_students)
    
    # Check if score meets expectations
    min_expected, max_expected = expected_score_range
    if min_expected <= result.final_score <= max_expected:
        print(f"✅ Score meets expectations: {result.final_score:.2f} within [{min_expected}, {max_expected}]")
        analysis['meets_expectations'] = True
    else:
        print(f"⚠️  Score outside expectations: {result.final_score:.2f} not within [{min_expected}, {max_expected}]")
        analysis['meets_expectations'] = False
    
    return analysis

def generate_comparative_report(analyses: list) -> None:
    """Generate a comparative report across all test scenarios."""
    
    print(f"\n📈 COMPARATIVE ANALYSIS")
    print("=" * 60)
    
    # Performance comparison
    print(f"🏁 Performance Comparison:")
    print(f"{'Test Name':<20} {'Score':<8} {'Students':<9} {'Time(s)':<8} {'Throughput':<12} {'Expectations':<12}")
    print("-" * 80)
    
    for analysis in analyses:
        if analysis:
            expectations_status = "✅ Met" if analysis['meets_expectations'] else "❌ Not Met"
            print(f"{analysis['test_name']:<20} {analysis['final_score']:<8.1f} {analysis['students_count']:<9} {analysis['processing_time']:<8.3f} {analysis['throughput']:<12.1f} {expectations_status:<12}")
    
    # Score distribution analysis
    print(f"\n📊 Score Distribution Analysis:")
    scores = [a['final_score'] for a in analyses if a]
    if scores:
        print(f"   Highest Score: {max(scores):.1f}")
        print(f"   Lowest Score: {min(scores):.1f}")
        print(f"   Score Range: {max(scores) - min(scores):.1f}")
        print(f"   Average Score: {sum(scores)/len(scores):.1f}")
    
    # Layer performance comparison
    print(f"\n🏗️  Layer Performance Comparison:")
    print(f"{'Test Name':<20} {'Student':<8} {'Class':<8} {'School':<8}")
    print("-" * 50)
    
    for analysis in analyses:
        if analysis:
            layer_scores = analysis['layer_scores']
            print(f"{analysis['test_name']:<20} {layer_scores['student']:<8.1f} {layer_scores['class']:<8.1f} {layer_scores['school']:<8.1f}")
    
    # Social metrics comparison
    print(f"\n👫 Social Metrics Comparison:")
    print(f"{'Test Name':<20} {'Friend Rate':<12} {'High Satisfaction':<16} {'Conflicts':<10}")
    print("-" * 65)
    
    for analysis in analyses:
        if analysis:
            ss = analysis['satisfaction_summary']
            high_sat_pct = ss['highly_satisfied_count'] / analysis['students_count'] * 100
            conflicts_pct = ss['students_with_conflicts'] / analysis['students_count'] * 100
            print(f"{analysis['test_name']:<20} {analysis['friend_success_rate']:<12.1f}% {high_sat_pct:<16.1f}% {conflicts_pct:<10.1f}%")

def main():
    """Run comprehensive testing suite."""
    
    print("🚀 MESHACHVETZ COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing multiple scenarios to validate scoring system performance")
    print("and accuracy across different student assignment configurations.")
    
    # Define test scenarios
    test_scenarios = [
        {
            'file': 'examples/test_data/perfect_score_test.csv',
            'name': 'Perfect Score Test',
            'expected_range': (85, 100),  # Expect very high score
            'description': 'Optimally arranged students with friends together, conflicts separated, perfect balance'
        },
        {
            'file': 'examples/test_data/bad_score_test.csv', 
            'name': 'Bad Score Test',
            'expected_range': (0, 40),   # Expect very low score
            'description': 'Poorly arranged students with friends separated, conflicts together, poor balance'
        },
        {
            'file': 'examples/test_data/large_dataset_test.csv',
            'name': 'Large Dataset Test',
            'expected_range': (50, 85),  # Expect moderate score due to randomness
            'description': '60 students across 5 classes for performance and scalability testing'
        }
    ]
    
    # Run all tests
    analyses = []
    
    for scenario in test_scenarios:
        print(f"\n📋 Scenario: {scenario['description']}")
        analysis = test_scenario(scenario['file'], scenario['name'], scenario['expected_range'])
        analyses.append(analysis)
    
    # Generate comparative report
    generate_comparative_report(analyses)
    
    # Test CSV report generation for one scenario
    print(f"\n📄 Testing CSV Report Generation...")
    if analyses and analyses[0]:
        try:
            scorer = Scorer()
            result = scorer.score_csv_file('examples/test_data/perfect_score_test.csv')
            
            start_time = time.time()
            output_path = scorer.generate_csv_reports(result, 'test_reports_comprehensive')
            report_time = time.time() - start_time
            
            # Check files were created
            if os.path.exists(output_path):
                files = os.listdir(output_path)
                total_size = sum(os.path.getsize(os.path.join(output_path, f)) for f in files)
                
                print(f"✅ CSV reports generated successfully!")
                print(f"   Output Directory: {output_path}")
                print(f"   Files Created: {len(files)}")
                print(f"   Total Size: {total_size:,} bytes")
                print(f"   Generation Time: {report_time:.3f}s")
                print(f"   Files: {', '.join(files)}")
                
                # Cleanup
                shutil.rmtree(output_path)
                print(f"   Cleanup: Directory removed")
            else:
                print(f"❌ CSV reports not generated")
                
        except Exception as e:
            print(f"❌ Error generating CSV reports: {e}")
    
    # Summary
    print(f"\n🎯 SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for a in analyses if a and a['meets_expectations'])
    total_tests = len([a for a in analyses if a])
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Total Students Processed: {sum(a['students_count'] for a in analyses if a)}")
    print(f"Total Processing Time: {sum(a['processing_time'] for a in analyses if a):.3f}s")
    
    if passed_tests == total_tests:
        print(f"🎉 All tests passed! The scoring system is working as expected.")
        print(f"✅ Perfect score test achieved high score")
        print(f"✅ Bad score test achieved low score")
        print(f"✅ Large dataset test performed well")
    else:
        print(f"⚠️  Some tests didn't meet expectations. Review the analysis above.")
    
    print(f"\n🔍 Class Configuration Note:")
    print(f"   Current default target classes: 5 (configurable in config/default_scoring.yaml)")
    print(f"   All test scenarios use 5 classes to match the new default")
    print(f"   Class size ranges from 6-12 students per class in current tests")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 