from django.db import models
import ast

class Recipe(models.Model):
    recipe_name = models.CharField(max_length=255, null=False, blank=False)
    cook_time = models.DurationField(null=True, blank=True)
    prep_time = models.DurationField(null=True, blank=True)
    total_time = models.DurationField(null=True, blank=True)
    ingredients = models.TextField(null=True, blank=True)
    calories = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    saturated_fat = models.FloatField(null=True, blank=True)
    cholesterol = models.FloatField(null=True, blank=True)
    sodium = models.FloatField(null=True, blank=True)
    carbohydrate = models.FloatField(null=True, blank=True)
    fiber = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    cuisine = models.CharField(max_length=100, null=True, blank=True)
    diet_types = models.CharField(max_length=200, null=True, blank=True, help_text="Comma-separated diet types")
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)


    
    def get_instructions_list(self):
        try:
            if self.instructions.startswith("c("):  # R-style vector
                cleaned = self.instructions.replace('c(', '').rstrip(')').strip()
                return [i.strip('" ').strip() for i in cleaned.split('",')]
            return ast.literal_eval(self.instructions)  
        except Exception:
            return [self.instructions] if self.instructions else []


    def get_ingredients_list(self):
        if not self.ingredients:
            return []
        try:
            # converting to list
            cleaned = self.ingredients.strip()
            if cleaned.startswith("c("):
                cleaned = cleaned[2:-1]
            items = ast.literal_eval(f"[{cleaned}]")
            return [item.capitalize() for item in items]
        except Exception:
            return [self.ingredients]
    
    def get_diet_types_list(self):
        """Get list of diet types for this recipe"""
        if not self.diet_types:
            return []
        return [diet.strip() for diet in self.diet_types.split(',') if diet.strip()]
    
    def add_diet_type(self, diet_type):
        """Add a diet type to this recipe"""
        current_types = self.get_diet_types_list()
        if diet_type not in current_types:
            current_types.append(diet_type)
            self.diet_types = ', '.join(current_types)
    
    def is_diet_compatible(self, diet_type):
        """Check if recipe is compatible with a specific diet type"""
        return diet_type in self.get_diet_types_list()
    
    @classmethod
    def get_available_diet_types(cls):
        """Get all available diet types"""
        return [
            'Balanced',
            'Ketogenic (Keto)', 
            'Paleo',
            'Vegetarian',
            'Vegan',
            'Mediterranean',
            'Low Carb',
            'High Protein',
            'Gluten Free'
        ]
    
    def get_image_url(self):
        """Get image URL safely, returns None if no image"""
        try:
            if self.image:
                return self.image.url
        except ValueError:
            # Handle case where image field exists but file is missing
            pass
        return None
    
    def has_image(self):
        """Check if recipe has a valid image"""
        return self.get_image_url() is not None
    
    def __str__(self):
        return self.recipe_name