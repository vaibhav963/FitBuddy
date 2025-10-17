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

import google.generativeai as genai
from recipes.models import Recipe
from django.conf import settings

class SimpleMealPlanGenerator:
    def __init__(self):
        self.model = None
        self.recipes_data = None
        
    def get_recipes_data(self, diet_preference=None):
        """Get recipes data from database, optionally filtered by diet type"""
        try:
            recipes = Recipe.objects.all()
            
            # Filter by diet preference if specified
            if diet_preference and diet_preference != 'Any':
                recipes = recipes.filter(diet_types__icontains=diet_preference)
            
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
                    'diet_types': recipe.diet_types,
                    'prep_time': str(recipe.prep_time) if recipe.prep_time else 'N/A',
                    'cook_time': str(recipe.cook_time) if recipe.cook_time else 'N/A',
                })
            return recipes_data
        except Exception as e:
            print(f"Error getting recipes data: {e}")
            return []
    
    def initialize(self):
        """Initialize the AI model and recipe data"""
        if not self.model:
            try:
                api_key = getattr(settings, 'GOOGLE_API_KEY', '')
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in settings. Please add it to your .env file.")
                
                print(f"DEBUG: Initializing AI model with API key: {api_key[:10]}...")
                genai.configure(api_key=api_key)
                
                # Use current working models (try multiple options)
                models_to_try = [
                    'gemini-2.5-flash',
                    'gemini-flash-latest', 
                    'gemini-2.0-flash',
                    'gemini-pro-latest'
                ]
                
                model_initialized = False
                for model_name in models_to_try:
                    try:
                        print(f"DEBUG: Trying model: {model_name}")
                        self.model = genai.GenerativeModel(model_name)
                        
                        # Test the model with a simple request
                        test_response = self.model.generate_content("Hello, respond with 'OK'")
                        print(f"DEBUG: Model test successful: {test_response.text[:20]}")
                        print(f"DEBUG: Successfully initialized {model_name} model")
                        model_initialized = True
                        break
                        
                    except Exception as model_error:
                        print(f"DEBUG: Model {model_name} failed: {model_error}")
                        continue
                
                if not model_initialized:
                    raise ValueError("No working AI model found")
                        
            except Exception as init_error:
                print(f"DEBUG: Complete initialization error: {init_error}")
                raise init_error
        
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
        try:
            print("DEBUG: Starting meal plan generation...")
            print(f"DEBUG: User preferences: {user_preferences}")
            
            self.initialize()
            print("DEBUG: AI model initialized successfully")
            
            # Get recipes filtered by diet preference
            diet_preference = user_preferences.get('diet_type', 'Any')
            self.recipes_data = self.get_recipes_data(diet_preference)
            print(f"DEBUG: Loaded {len(self.recipes_data)} recipes for diet: {diet_preference}")
            
            # If no recipes available, return demo plan
            if not self.recipes_data:
                print("DEBUG: No recipes found, returning demo plan")
                return {
                    'success': True,
                    'meal_plan': self._create_demo_meal_plan(user_preferences),
                    'generated_at': datetime.now().isoformat(),
                    'note': 'Demo meal plan - no recipes found for selected diet type.'
                }
            
            # Create a summary of available recipes for the AI
            recipe_summary = self._create_recipe_summary()
            print("DEBUG: Recipe summary created")
            
            # Create the prompt
            prompt = f"""You are an expert nutritionist and meal planner. Create a personalized {user_preferences.get('days', 7)}-day meal plan based on the user's requirements.

User Profile:
- Goal: {user_preferences.get('goal', 'maintain weight')}
- Diet Type: {user_preferences.get('diet_type', 'balanced')}
- Allergies: {user_preferences.get('allergies', 'none')}
- Daily Calorie Target: {user_preferences.get('calories', 2000)} calories
- Age: {user_preferences.get('age', 30)}, Weight: {user_preferences.get('weight', '70kg')}, Height: {user_preferences.get('height', '5\'8"')}
- Activity Level: {user_preferences.get('activity_level', 'moderate')}
- Meals per day: {user_preferences.get('meals_per_day', 4)}
- Special Preferences: {user_preferences.get('preferences', 'none')}

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
      "date": "{datetime.now().strftime('%Y-%m-%d')}",
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
        }}
      }},
      "daily_totals": {{
        "calories": 1500,
        "protein": "100g",
        "carbs": "150g", 
        "fat": "60g"
      }}
    }}
  }},
  "plan_summary": {{
    "total_days": {user_preferences.get('days', 7)},
    "avg_daily_calories": 1500,
    "diet_compliance": "95%",
    "variety_score": "High",
    "tips": [
      "Drink plenty of water throughout the day",
      "Adjust portion sizes based on hunger levels"
    ]
  }}
}}

Generate the meal plan now:"""

            # Generate the meal plan
            print("DEBUG: Sending request to AI model...")
            try:
                response = self.model.generate_content(prompt)
                print("DEBUG: AI response received")
                print(f"DEBUG: Response text length: {len(response.text) if response.text else 0}")
                
                # Parse JSON response
                meal_plan = self._parse_ai_response(response.text)
                print("DEBUG: AI response parsed successfully")
                
                return {
                    'success': True,
                    'meal_plan': meal_plan,
                    'generated_at': datetime.now().isoformat()
                }
            except Exception as ai_error:
                print(f"DEBUG: AI generation failed: {ai_error}")
                print("DEBUG: Falling back to demo meal plan")
                return {
                    'success': True,
                    'meal_plan': self._create_demo_meal_plan(user_preferences),
                    'generated_at': datetime.now().isoformat(),
                    'note': f'Demo meal plan - AI generation failed: {str(ai_error)}'
                }
            
        except Exception as e:
            print(f"DEBUG: General error in meal plan generation: {e}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            # Check if it's a quota exceeded error
            if "quota" in str(e).lower() or "exceeded" in str(e).lower():
                print("DEBUG: Quota exceeded, returning demo plan")
                # Return a demo meal plan when quota is exceeded
                return {
                    'success': True,
                    'meal_plan': self._create_demo_meal_plan(user_preferences),
                    'generated_at': datetime.now().isoformat(),
                    'note': 'Demo meal plan - API quota exceeded. Try again later for AI-generated plan.'
                }
            else:
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
        for i, recipe in enumerate(self.recipes_data[:30]):  # Limit to 30 recipes to avoid token limits
            summary += f"{i+1}. {recipe['recipe_name']} - {recipe['type']} - {recipe['cuisine']} - "
            summary += f"Calories: {recipe['calories']}, Protein: {recipe['protein']}g, "
            summary += f"Carbs: {recipe['carbohydrate']}g, Fat: {recipe['fat']}g\n"
        
        return summary
    
    def _create_demo_meal_plan(self, user_preferences):
        """Create a demo meal plan using actual recipes from the database"""
        days = user_preferences.get('days', 7)
        calories_target = user_preferences.get('calories', 2000)
        
        # Get some popular recipes from the database
        breakfast_recipes = [r for r in self.recipes_data if r['type'] and 'breakfast' in r['type'].lower()][:3]
        lunch_recipes = [r for r in self.recipes_data if r['type'] and any(t in r['type'].lower() for t in ['lunch', 'main', 'dinner'])][:5]
        dinner_recipes = [r for r in self.recipes_data if r['type'] and any(t in r['type'].lower() for t in ['dinner', 'main'])][:5]
        
        if not breakfast_recipes:
            breakfast_recipes = self.recipes_data[:3]
        if not lunch_recipes:
            lunch_recipes = self.recipes_data[3:8]
        if not dinner_recipes:
            dinner_recipes = self.recipes_data[8:13]
        
        meal_plan = {}
        
        for day in range(1, min(days + 1, 8)):  # Limit to 7 days for demo
            day_key = f"day_{day}"
            date = (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d")
            
            # Select recipes for the day
            breakfast = breakfast_recipes[(day-1) % len(breakfast_recipes)] if breakfast_recipes else self.recipes_data[0]
            lunch = lunch_recipes[(day-1) % len(lunch_recipes)] if lunch_recipes else self.recipes_data[1]
            dinner = dinner_recipes[(day-1) % len(dinner_recipes)] if dinner_recipes else self.recipes_data[2]
            
            meal_plan[day_key] = {
                "date": date,
                "meals": {
                    "breakfast": {
                        "recipe_name": breakfast['recipe_name'],
                        "portion_size": "1 serving",
                        "calories": int(breakfast['calories']) if breakfast['calories'] else 350,
                        "time": "8:00 AM"
                    },
                    "lunch": {
                        "recipe_name": lunch['recipe_name'],
                        "portion_size": "1 serving",
                        "calories": int(lunch['calories']) if lunch['calories'] else 500,
                        "time": "12:00 PM"
                    },
                    "dinner": {
                        "recipe_name": dinner['recipe_name'],
                        "portion_size": "1 serving",
                        "calories": int(dinner['calories']) if dinner['calories'] else 600,
                        "time": "7:00 PM"
                    }
                },
                "daily_totals": {
                    "calories": (int(breakfast['calories']) if breakfast['calories'] else 350) + 
                               (int(lunch['calories']) if lunch['calories'] else 500) + 
                               (int(dinner['calories']) if dinner['calories'] else 600),
                    "protein": f"{int(breakfast['protein']) + int(lunch['protein']) + int(dinner['protein']) if all([breakfast['protein'], lunch['protein'], dinner['protein']]) else 100}g",
                    "carbs": f"{int(breakfast['carbohydrate']) + int(lunch['carbohydrate']) + int(dinner['carbohydrate']) if all([breakfast['carbohydrate'], lunch['carbohydrate'], dinner['carbohydrate']]) else 150}g",
                    "fat": f"{int(breakfast['fat']) + int(lunch['fat']) + int(dinner['fat']) if all([breakfast['fat'], lunch['fat'], dinner['fat']]) else 70}g"
                }
            }
        
        return {
            "meal_plan": meal_plan,
            "plan_summary": {
                "total_days": days,
                "avg_daily_calories": calories_target,
                "diet_compliance": "Demo Mode",
                "variety_score": "Good",
                "tips": [
                    "This is a demo meal plan using your recipe database",
                    "For AI-powered personalization, try again when API quota resets",
                    "All recipes are from your verified database"
                ]
            }
        }
    
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
simple_meal_plan_generator = SimpleMealPlanGenerator()

def generate_simple_meal_plan(user_preferences):
    """
    Main function to generate a meal plan using direct Google AI
    
    Args:
        user_preferences (dict): User dietary preferences
    
    Returns:
        dict: Generated meal plan or error message
    """
    return simple_meal_plan_generator.generate_meal_plan(user_preferences)

def get_simple_recipe_by_name(recipe_name):
    """Get recipe details by name"""
    return simple_meal_plan_generator.get_recipe_details(recipe_name)