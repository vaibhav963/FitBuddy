import os
import django
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from recipes.models import Recipe
from django.conf import settings

class MealPlanGenerator:
    def __init__(self):
        self.llm = None
        self.recipes_data = None
        
    def get_recipes_data(self):
        """Get recipes data from database"""
        try:
            recipes = Recipe.objects.all()
            recipes_data = []
            for recipe in recipes:
                recipes_data.append({
                    'recipe_name': recipe.recipe_name,
                    'type': recipe.type,
                    'cuisine': recipe.cuisine,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'calories': recipe.calories,
                    'protein': recipe.protein,
                    'carbohydrate': recipe.carbohydrate,
                    'fat': recipe.fat,
                    'fiber': recipe.fiber,
                    'sodium': recipe.sodium,
                    'prep_time': str(recipe.prep_time) if recipe.prep_time else 'N/A',
                    'cook_time': str(recipe.cook_time) if recipe.cook_time else 'N/A',
                })
            return recipes_data
        except Exception as e:
            print(f"Error getting recipes data: {e}")
            return []
    
    def initialize(self):
        """Initialize the AI model and recipe data"""
        if not self.llm:
            api_key = getattr(settings, 'GOOGLE_API_KEY', '')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in settings. Please add it to your .env file.")
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                api_key=api_key,
                temperature=0.7
            )
        
        if not self.recipes_data:
            self.recipes_data = self.get_recipes_data()
    
    def generate_meal_plan(self, user_preferences):
        """
        Generate a personalized meal plan based on user preferences
        
        Args:
            user_preferences (dict): User dietary preferences and requirements
        
        Returns:
            dict: Generated meal plan with recipes for each day
        """
        self.initialize()
        
        # Create a summary of available recipes for the AI
        recipe_summary = self._create_recipe_summary()
        
        # Create the prompt template
        system_template = """You are an expert nutritionist and meal planner. Create a personalized {days}-day meal plan based on the user's requirements.

User Profile:
- Goal: {goal}
- Diet Type: {diet_type}
- Allergies: {allergies}
- Daily Calorie Target: {calories} calories
- Age: {age}, Weight: {weight}, Height: {height}
- Activity Level: {activity_level}
- Meals per day: {meals_per_day}
- Special Preferences: {preferences}

Available Recipes Database:
{recipe_summary}

IMPORTANT INSTRUCTIONS:
1. Create a balanced meal plan that meets the user's calorie and macro targets
2. Only use recipes from the provided database above
3. Ensure variety - don't repeat the same recipe within 3 days
4. Consider the user's allergies and dietary restrictions
5. Balance macronutrients throughout the day
6. Provide portion sizes and meal timing suggestions

OUTPUT FORMAT (return valid JSON only):
{{
  "meal_plan": {{
    "day_1": {{
      "date": "YYYY-MM-DD",
      "meals": {{
        "breakfast": {{
          "recipe_name": "Recipe Name",
          "portion_size": "1 serving",
          "calories": 400,
          "time": "8:00 AM"
        }},
        "lunch": {{
          "recipe_name": "Recipe Name", 
          "portion_size": "1 serving",
          "calories": 500,
          "time": "12:00 PM"
        }},
        "dinner": {{
          "recipe_name": "Recipe Name",
          "portion_size": "1 serving", 
          "calories": 600,
          "time": "7:00 PM"
        }},
        "snack": {{
          "recipe_name": "Recipe Name",
          "portion_size": "0.5 serving",
          "calories": 200,
          "time": "3:00 PM"
        }}
      }},
      "daily_totals": {{
        "calories": 1700,
        "protein": "120g",
        "carbs": "150g", 
        "fat": "80g"
      }}
    }}
  }},
  "plan_summary": {{
    "total_days": {days},
    "avg_daily_calories": 1700,
    "diet_compliance": "95%",
    "variety_score": "High",
    "tips": [
      "Drink plenty of water throughout the day",
      "Adjust portion sizes based on hunger levels"
    ]
  }}
}}

Generate the meal plan now:"""

        # Create the prompt
        prompt = ChatPromptTemplate.from_template(system_template)
        
        # Create the chain
        chain = prompt | self.llm | StrOutputParser()
        
        # Generate the meal plan
        try:
            response = chain.invoke({
                "days": user_preferences.get('days', 7),
                "goal": user_preferences.get('goal', 'maintain weight'),
                "diet_type": user_preferences.get('diet_type', 'balanced'),
                "allergies": user_preferences.get('allergies', 'none'),
                "calories": user_preferences.get('calories', 2000),
                "age": user_preferences.get('age', 30),
                "weight": user_preferences.get('weight', '70kg'),
                "height": user_preferences.get('height', '5\'8"'),
                "activity_level": user_preferences.get('activity_level', 'moderate'),
                "meals_per_day": user_preferences.get('meals_per_day', 4),
                "preferences": user_preferences.get('preferences', 'none'),
                "recipe_summary": recipe_summary
            })
            
            # Parse JSON response
            meal_plan = self._parse_ai_response(response)
            return {
                'success': True,
                'meal_plan': meal_plan,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate meal plan. Please try again.'
            }
    
    def _create_recipe_summary(self):
        """Create a concise summary of available recipes for the AI"""
        if not self.recipes_data:
            return "No recipes available"
        
        summary = "Available Recipes:\n"
        for i, recipe in enumerate(self.recipes_data[:50]):  # Limit to 50 recipes to avoid token limits
            summary += f"{i+1}. {recipe['recipe_name']} - {recipe['type']} - {recipe['cuisine']} - "
            summary += f"Calories: {recipe['calories']}, Protein: {recipe['protein']}g, "
            summary += f"Carbs: {recipe['carbohydrate']}g, Fat: {recipe['fat']}g\n"
        
        return summary
    
    def _parse_ai_response(self, response):
        """Parse the AI response and extract meal plan data"""
        try:
            # Clean the response (remove any markdown formatting)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            # Parse JSON
            meal_plan_data = json.loads(cleaned_response)
            return meal_plan_data
            
        except json.JSONDecodeError:
            # If JSON parsing fails, create a fallback structure
            return {
                "meal_plan": {
                    "day_1": {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "meals": {
                            "breakfast": {
                                "recipe_name": "Scrambled Eggs",
                                "portion_size": "1 serving",
                                "calories": 300,
                                "time": "8:00 AM"
                            },
                            "lunch": {
                                "recipe_name": "Caesar Salad",
                                "portion_size": "1 serving", 
                                "calories": 400,
                                "time": "12:00 PM"
                            },
                            "dinner": {
                                "recipe_name": "Grilled Chicken",
                                "portion_size": "1 serving",
                                "calories": 500,
                                "time": "7:00 PM"
                            }
                        },
                        "daily_totals": {
                            "calories": 1200,
                            "protein": "80g",
                            "carbs": "50g",
                            "fat": "60g"
                        }
                    }
                },
                "plan_summary": {
                    "total_days": 1,
                    "avg_daily_calories": 1200,
                    "diet_compliance": "Good",
                    "variety_score": "Medium",
                    "tips": ["Stay hydrated", "Listen to your body"]
                }
            }

    def get_recipe_details(self, recipe_name):
        """Get detailed recipe information by name"""
        if not self.recipes_data:
            self.recipes_data = self.get_recipes_data()
        
        for recipe in self.recipes_data:
            if recipe['recipe_name'].lower() == recipe_name.lower():
                return recipe
        return None

# Create a global instance
meal_plan_generator = MealPlanGenerator()

def generate_custom_meal_plan(user_preferences):
    """
    Main function to generate a meal plan
    
    Args:
        user_preferences (dict): User dietary preferences
    
    Returns:
        dict: Generated meal plan or error message
    """
    return meal_plan_generator.generate_meal_plan(user_preferences)

def get_recipe_by_name(recipe_name):
    """Get recipe details by name"""
    return meal_plan_generator.get_recipe_details(recipe_name)