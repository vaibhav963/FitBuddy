#!/usr/bin/env python
"""
Test script to create a sample recipe without an image for testing the image placeholder
"""
import os
import django
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

from recipes.models import Recipe

def create_test_recipe():
    """Create a test recipe without an image"""
    try:
        # Create a recipe without an image
        recipe = Recipe.objects.create(
            recipe_name="Test Recipe (No Image)",
            ingredients="Test ingredient 1, Test ingredient 2, Test ingredient 3",
            instructions="Step 1: Test instruction, Step 2: Another test instruction",
            calories=300,
            protein=20,
            carbohydrate=30,
            fat=15,
            type="Test",
            cuisine="Test Cuisine"
        )
        
        print(f"✅ Test recipe created successfully!")
        print(f"Recipe ID: {recipe.id}")
        print(f"Recipe Name: {recipe.recipe_name}")
        print(f"Image field: {recipe.image}")
        print(f"Has image: {bool(recipe.image)}")
        
        return recipe.id
        
    except Exception as e:
        print(f"❌ Error creating test recipe: {e}")
        return None

if __name__ == "__main__":
    print("Creating test recipe without image...")
    recipe_id = create_test_recipe()
    if recipe_id:
        print(f"\n🔗 Test the fix by visiting: http://127.0.0.1:8000/recipe/detail/{recipe_id}/")
    else:
        print("\n❌ Failed to create test recipe")