#!/usr/bin/env python
"""
Test script to debug AI meal planner functionality
"""
import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

# Now import Django models and functions
from recipes.simple_meal_planner import generate_simple_meal_plan

def test_meal_planner():
    """Test the meal planner functionality directly"""
    print("=== Testing AI Meal Planner ===")
    
    # Test user preferences
    user_preferences = {
        'days': 7,
        'goal': 'lose weight',
        'diet_type': 'balanced',
        'allergies': 'none',
        'calories': 1800,
        'age': 30,
        'weight': '75kg',
        'height': '5\'8"',
        'activity_level': 'moderate',
        'meals_per_day': 3,
        'preferences': 'none'
    }
    
    print(f"User preferences: {user_preferences}")
    print("\nGenerating meal plan...")
    
    try:
        result = generate_simple_meal_plan(user_preferences)
        print(f"\nResult: {result}")
        
        if result.get('success'):
            print("\n✅ Meal plan generated successfully!")
            if 'note' in result:
                print(f"Note: {result['note']}")
        else:
            print("\n❌ Meal plan generation failed!")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_meal_planner()