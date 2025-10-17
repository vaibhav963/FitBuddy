from django.core.management.base import BaseCommand
from recipes.models import Recipe


class Command(BaseCommand):
    help = 'Categorize recipes based on their nutritional profile and ingredients'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting recipe categorization...'))
        
        recipes = Recipe.objects.all()
        updated_count = 0
        
        for recipe in recipes:
            old_diet_types = recipe.diet_types
            new_diet_types = self.categorize_recipe(recipe)
            
            if new_diet_types != old_diet_types:
                recipe.diet_types = new_diet_types
                recipe.save()
                updated_count += 1
                self.stdout.write(f"Updated {recipe.recipe_name}: {new_diet_types}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully categorized {updated_count} recipes!')
        )
        
        # Check coverage for each diet type
        self.check_diet_coverage()
    
    def categorize_recipe(self, recipe):
        """Categorize recipe based on nutritional profile and ingredients"""
        diet_types = []
        
        # Get nutritional values (per 100g)
        calories = recipe.calories or 0
        protein = recipe.protein or 0
        carbs = recipe.carbohydrate or 0  # Using correct field name
        fats = recipe.fat or 0  # Using correct field name
        fiber = recipe.fiber or 0
        
        # Calculate percentages for macro analysis
        total_macros = protein * 4 + carbs * 4 + fats * 9
        if total_macros > 0:
            protein_pct = (protein * 4) / total_macros * 100
            carb_pct = (carbs * 4) / total_macros * 100
            fat_pct = (fats * 9) / total_macros * 100
        else:
            protein_pct = carb_pct = fat_pct = 0
        
        # Get recipe name and type for analysis
        name = recipe.recipe_name.lower()  # Using correct field name
        recipe_type = recipe.type.lower() if recipe.type else ""
        
        # Ketogenic Diet (High fat >70%, very low carb <10%)
        if fat_pct > 65 and carb_pct < 15:
            diet_types.append("Ketogenic")
        elif any(keto_word in name for keto_word in ["keto", "ketogenic", "fat bomb"]):
            diet_types.append("Ketogenic")
        elif recipe_type == "keto":
            diet_types.append("Ketogenic")
        
        # Paleo Diet (no grains, dairy, legumes, processed foods)
        paleo_friendly = True
        paleo_avoid = ["bread", "pasta", "rice", "oats", "quinoa", "beans", "lentils", 
                      "cheese", "milk", "yogurt", "peanut", "soy"]
        
        if any(avoid in name for avoid in paleo_avoid):
            paleo_friendly = False
        elif recipe_type == "paleo":
            paleo_friendly = True
        elif any(paleo_word in name for paleo_word in ["paleo", "caveman"]):
            paleo_friendly = True
        
        if paleo_friendly and not any(avoid in name for avoid in paleo_avoid):
            diet_types.append("Paleo")
        
        # Vegan Diet (no animal products)
        vegan_indicators = ["vegan", "plant-based", "tofu", "quinoa", "lentil", "chickpea"]
        animal_products = ["meat", "chicken", "beef", "pork", "fish", "salmon", "tuna", 
                          "egg", "cheese", "milk", "cream", "butter", "bacon", "ham"]
        
        is_vegan = False
        if any(vegan in name for vegan in vegan_indicators):
            is_vegan = True
        elif recipe_type == "vegan":
            is_vegan = True
        elif not any(animal in name for animal in animal_products):
            # If no obvious animal products and contains plant proteins
            plant_proteins = ["beans", "lentils", "chickpea", "tofu", "quinoa", "nuts"]
            if any(plant in name for plant in plant_proteins):
                is_vegan = True
        
        if is_vegan:
            diet_types.append("Vegan")
            diet_types.append("Vegetarian")  # Vegan is also vegetarian
        
        # Vegetarian Diet (no meat, but may include dairy/eggs)
        meat_products = ["meat", "chicken", "beef", "pork", "fish", "salmon", "tuna", 
                        "bacon", "ham", "turkey", "lamb"]
        
        if not any(meat in name for meat in meat_products) and "Vegan" not in diet_types:
            diet_types.append("Vegetarian")
        
        # Mediterranean Diet (olive oil, fish, vegetables, whole grains)
        med_indicators = ["mediterranean", "olive", "fish", "salmon", "tuna", "tomato", 
                         "herbs", "Greek", "Italian"]
        
        if any(med in name for med in med_indicators):
            diet_types.append("Mediterranean")
        elif recipe_type == "mediterranean":
            diet_types.append("Mediterranean")
        
        # Low Carb Diet (carbs < 30% of calories)
        if carb_pct < 30 and carbs < 20:
            diet_types.append("Low Carb")
        elif any(low_carb in name for low_carb in ["low carb", "low-carb", "no carb"]):
            diet_types.append("Low Carb")
        
        # High Protein Diet (protein > 25% of calories or >20g per serving)
        if protein_pct > 25 or protein > 20:
            diet_types.append("High Protein")
        elif any(protein_word in name for protein_word in ["protein", "lean", "muscle"]):
            diet_types.append("High Protein")
        
        # Gluten Free Diet (no wheat, barley, rye)
        gluten_sources = ["bread", "pasta", "wheat", "flour", "barley", "rye", "oats"]
        gluten_free_indicators = ["gluten-free", "gluten free", "rice", "quinoa"]
        
        has_gluten = any(gluten in name for gluten in gluten_sources)
        is_gluten_free = any(gf in name for gf in gluten_free_indicators)
        
        if not has_gluten or is_gluten_free:
            diet_types.append("Gluten Free")
        
        # Balanced Diet (default for recipes that don't fit other categories)
        if not diet_types:
            diet_types.append("Balanced")
        elif len(diet_types) == 1 and diet_types[0] in ["Vegetarian", "Gluten Free"]:
            # Add Balanced for simple vegetarian or gluten-free recipes
            diet_types.append("Balanced")
        
        return ", ".join(sorted(set(diet_types)))
    
    def check_diet_coverage(self):
        """Check if each diet type has at least one recipe"""
        diet_types = ["Balanced", "Ketogenic", "Paleo", "Vegetarian", "Vegan", 
                     "Mediterranean", "Low Carb", "High Protein", "Gluten Free"]
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("DIET TYPE COVERAGE:")
        self.stdout.write("="*50)
        
        for diet_type in diet_types:
            recipes = Recipe.objects.filter(diet_types__icontains=diet_type)
            count = recipes.count()
            
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {diet_type}: {count} recipes")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ {diet_type}: {count} recipes")
                )
        
        # If any diet types are missing, create sample recipes
        self.create_missing_diet_recipes()
    
    def create_missing_diet_recipes(self):
        """Create sample recipes for missing diet types"""
        diet_types = ["Balanced", "Ketogenic", "Paleo", "Vegetarian", "Vegan", 
                     "Mediterranean", "Low Carb", "High Protein", "Gluten Free"]
        
        sample_recipes = {
            "Balanced": {
                "name": "Balanced Chicken and Rice Bowl",
                "calories": 450, "protein": 35, "carbs": 45, "fats": 12,
                "fiber": 4, "type": "balanced"
            },
            "Ketogenic": {
                "name": "Keto Avocado Fat Bomb",
                "calories": 320, "protein": 8, "carbs": 6, "fats": 30,
                "fiber": 8, "type": "keto"
            },
            "Paleo": {
                "name": "Paleo Grilled Salmon with Sweet Potato",
                "calories": 380, "protein": 32, "carbs": 25, "fats": 18,
                "fiber": 4, "type": "paleo"
            },
            "Vegetarian": {
                "name": "Vegetarian Quinoa Power Bowl",
                "calories": 420, "protein": 18, "carbs": 55, "fats": 14,
                "fiber": 8, "type": "vegetarian"
            },
            "Vegan": {
                "name": "Vegan Lentil Curry",
                "calories": 350, "protein": 16, "carbs": 48, "fats": 10,
                "fiber": 12, "type": "vegan"
            },
            "Mediterranean": {
                "name": "Mediterranean Olive Oil Herb Salad",
                "calories": 280, "protein": 8, "carbs": 20, "fats": 20,
                "fiber": 6, "type": "mediterranean"
            },
            "Low Carb": {
                "name": "Low Carb Zucchini Noodles with Pesto",
                "calories": 220, "protein": 12, "carbs": 8, "fats": 18,
                "fiber": 4, "type": "low-carb"
            },
            "High Protein": {
                "name": "High Protein Greek Yogurt Parfait",
                "calories": 380, "protein": 30, "carbs": 35, "fats": 12,
                "fiber": 5, "type": "high-protein"
            },
            "Gluten Free": {
                "name": "Gluten Free Rice Bowl with Vegetables",
                "calories": 340, "protein": 14, "carbs": 52, "fats": 10,
                "fiber": 6, "type": "gluten-free"
            }
        }
        
        created_count = 0
        for diet_type in diet_types:
            existing_recipes = Recipe.objects.filter(diet_types__icontains=diet_type)
            
            if existing_recipes.count() == 0:
                recipe_data = sample_recipes[diet_type]
                
                # Check if this exact recipe already exists
                if not Recipe.objects.filter(recipe_name=recipe_data["name"]).exists():
                    recipe = Recipe.objects.create(
                        recipe_name=recipe_data["name"],
                        calories=recipe_data["calories"],
                        protein=recipe_data["protein"],
                        carbohydrate=recipe_data["carbs"],  # Using correct field name
                        fat=recipe_data["fats"],  # Using correct field name
                        fiber=recipe_data["fiber"],
                        type=recipe_data["type"],
                        diet_types=diet_type,
                        ingredients=f"Sample ingredients for {diet_type.lower()} diet",
                        instructions=f"Sample instructions for preparing this {diet_type.lower()} recipe."
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Created sample recipe: {recipe.recipe_name}")
                    )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"\nCreated {created_count} sample recipes to ensure diet coverage!")
            )