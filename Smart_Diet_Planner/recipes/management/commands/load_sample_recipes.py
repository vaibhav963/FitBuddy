from django.core.management.base import BaseCommand
from recipes.models import Recipe
from datetime import timedelta

class Command(BaseCommand):
    help = 'Load sample recipes into the database for FitBuddy'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample recipes...')
        
        # Sample recipes with different diet types
        sample_recipes = [
            {
                'recipe_name': 'Avocado Toast with Eggs',
                'prep_time': timedelta(minutes=10),
                'cook_time': timedelta(minutes=5),
                'total_time': timedelta(minutes=15),
                'ingredients': '"Bread", "Avocado", "Eggs", "Salt", "Pepper", "Olive oil"',
                'instructions': '"Toast bread", "Mash avocado", "Fry eggs", "Assemble and season"',
                'calories': 350,
                'protein': 18,
                'carbohydrate': 25,
                'fat': 22,
                'fiber': 8,
                'sodium': 400,
                'type': 'breakfast',
                'cuisine': 'American',
                'diet_types': 'Balanced, Vegetarian, High Protein'
            },
            {
                'recipe_name': 'Grilled Chicken Salad',
                'prep_time': timedelta(minutes=15),
                'cook_time': timedelta(minutes=20),
                'total_time': timedelta(minutes=35),
                'ingredients': '"Chicken breast", "Mixed greens", "Tomatoes", "Cucumber", "Olive oil", "Lemon", "Salt", "Pepper"',
                'instructions': '"Season and grill chicken", "Prepare vegetables", "Make dressing", "Combine all ingredients"',
                'calories': 280,
                'protein': 35,
                'carbohydrate': 8,
                'fat': 12,
                'fiber': 4,
                'sodium': 350,
                'type': 'lunch',
                'cuisine': 'Mediterranean',
                'diet_types': 'Balanced, Low Carb, High Protein, Paleo'
            },
            {
                'recipe_name': 'Vegetarian Buddha Bowl',
                'prep_time': timedelta(minutes=20),
                'cook_time': timedelta(minutes=25),
                'total_time': timedelta(minutes=45),
                'ingredients': '"Quinoa", "Sweet potato", "Chickpeas", "Spinach", "Avocado", "Tahini", "Lemon", "Garlic"',
                'instructions': '"Cook quinoa", "Roast sweet potato", "Prepare chickpeas", "Make tahini dressing", "Assemble bowl"',
                'calories': 420,
                'protein': 15,
                'carbohydrate': 55,
                'fat': 16,
                'fiber': 12,
                'sodium': 300,
                'type': 'lunch',
                'cuisine': 'Mediterranean',
                'diet_types': 'Balanced, Vegetarian, Vegan, High Protein'
            },
            {
                'recipe_name': 'Keto Salmon with Asparagus',
                'prep_time': timedelta(minutes=10),
                'cook_time': timedelta(minutes=15),
                'total_time': timedelta(minutes=25),
                'ingredients': '"Salmon fillet", "Asparagus", "Butter", "Garlic", "Lemon", "Salt", "Pepper", "Herbs"',
                'instructions': '"Season salmon", "Prepare asparagus", "Cook salmon in butter", "Sauté asparagus", "Serve with lemon"',
                'calories': 380,
                'protein': 32,
                'carbohydrate': 6,
                'fat': 26,
                'fiber': 3,
                'sodium': 280,
                'type': 'dinner',
                'cuisine': 'Mediterranean',
                'diet_types': 'Ketogenic (Keto), Low Carb, High Protein, Paleo'
            },
            {
                'recipe_name': 'Greek Yogurt Parfait',
                'prep_time': timedelta(minutes=5),
                'cook_time': timedelta(minutes=0),
                'total_time': timedelta(minutes=5),
                'ingredients': '"Greek yogurt", "Berries", "Granola", "Honey", "Nuts"',
                'instructions': '"Layer yogurt in bowl", "Add berries", "Top with granola and nuts", "Drizzle with honey"',
                'calories': 250,
                'protein': 20,
                'carbohydrate': 30,
                'fat': 8,
                'fiber': 5,
                'sodium': 100,
                'type': 'breakfast',
                'cuisine': 'Greek',
                'diet_types': 'Balanced, Vegetarian, High Protein'
            },
            {
                'recipe_name': 'Vegetable Stir Fry',
                'prep_time': timedelta(minutes=15),
                'cook_time': timedelta(minutes=10),
                'total_time': timedelta(minutes=25),
                'ingredients': '"Mixed vegetables", "Tofu", "Soy sauce", "Ginger", "Garlic", "Sesame oil", "Rice"',
                'instructions': '"Prepare vegetables", "Cook tofu", "Stir fry vegetables", "Add sauce", "Serve over rice"',
                'calories': 320,
                'protein': 18,
                'carbohydrate': 45,
                'fat': 10,
                'fiber': 8,
                'sodium': 600,
                'type': 'dinner',
                'cuisine': 'Asian',
                'diet_types': 'Balanced, Vegetarian, Vegan'
            },
            {
                'recipe_name': 'Protein Smoothie Bowl',
                'prep_time': timedelta(minutes=10),
                'cook_time': timedelta(minutes=0),
                'total_time': timedelta(minutes=10),
                'ingredients': '"Protein powder", "Banana", "Berries", "Almond milk", "Chia seeds", "Coconut flakes"',
                'instructions': '"Blend protein powder with milk and banana", "Pour into bowl", "Top with berries, chia seeds, and coconut"',
                'calories': 300,
                'protein': 25,
                'carbohydrate': 35,
                'fat': 8,
                'fiber': 10,
                'sodium': 150,
                'type': 'breakfast',
                'cuisine': 'American',
                'diet_types': 'Balanced, High Protein, Gluten Free'
            },
            {
                'recipe_name': 'Mediterranean Quinoa Salad',
                'prep_time': timedelta(minutes=20),
                'cook_time': timedelta(minutes=15),
                'total_time': timedelta(minutes=35),
                'ingredients': '"Quinoa", "Tomatoes", "Cucumber", "Olives", "Feta cheese", "Olive oil", "Lemon", "Herbs"',
                'instructions': '"Cook quinoa and cool", "Chop vegetables", "Make dressing", "Combine all ingredients", "Chill before serving"',
                'calories': 280,
                'protein': 12,
                'carbohydrate': 35,
                'fat': 12,
                'fiber': 6,
                'sodium': 450,
                'type': 'lunch',
                'cuisine': 'Mediterranean',
                'diet_types': 'Balanced, Vegetarian, Mediterranean, Gluten Free'
            },
            {
                'recipe_name': 'Paleo Beef and Vegetable Skillet',
                'prep_time': timedelta(minutes=15),
                'cook_time': timedelta(minutes=20),
                'total_time': timedelta(minutes=35),
                'ingredients': '"Ground beef", "Bell peppers", "Onions", "Zucchini", "Tomatoes", "Coconut oil", "Herbs", "Spices"',
                'instructions': '"Brown ground beef", "Add vegetables", "Season well", "Cook until tender", "Serve hot"',
                'calories': 350,
                'protein': 28,
                'carbohydrate': 12,
                'fat': 22,
                'fiber': 4,
                'sodium': 400,
                'type': 'dinner',
                'cuisine': 'American',
                'diet_types': 'Paleo, Low Carb, High Protein'
            },
            {
                'recipe_name': 'Vegan Lentil Curry',
                'prep_time': timedelta(minutes=15),
                'cook_time': timedelta(minutes=30),
                'total_time': timedelta(minutes=45),
                'ingredients': '"Red lentils", "Coconut milk", "Onions", "Garlic", "Ginger", "Curry spices", "Tomatoes", "Spinach"',
                'instructions': '"Sauté aromatics", "Add lentils and spices", "Pour in coconut milk", "Simmer until tender", "Add spinach at end"',
                'calories': 320,
                'protein': 16,
                'carbohydrate': 45,
                'fat': 10,
                'fiber': 12,
                'sodium': 350,
                'type': 'dinner',
                'cuisine': 'Indian',
                'diet_types': 'Vegan, Vegetarian, High Protein, Gluten Free'
            }
        ]
        
        # Clear existing recipes
        Recipe.objects.all().delete()
        self.stdout.write('Cleared existing recipes.')
        
        # Create new recipes
        created_count = 0
        for recipe_data in sample_recipes:
            recipe, created = Recipe.objects.get_or_create(
                recipe_name=recipe_data['recipe_name'],
                defaults=recipe_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {recipe.recipe_name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {created_count} recipes into the database!'
            )
        )
        
        # Display diet type summary
        self.stdout.write('\nAvailable diet types:')
        for diet_type in Recipe.get_available_diet_types():
            count = Recipe.objects.filter(diet_types__icontains=diet_type).count()
            self.stdout.write(f'  {diet_type}: {count} recipes')