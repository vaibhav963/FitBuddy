from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Step 1
    age = models.PositiveIntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    height_unit = models.CharField(max_length=10, default="cm")  # cm or in
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")], null=True, blank=True)
    current_weight = models.FloatField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    weight_unit = models.CharField(max_length=10, default="kg")  # kg or lb

    # Step 2
    food_allergies = models.CharField(max_length=255, blank=True)  # Comma-separated values
    cooking_skill = models.CharField(max_length=20, choices=[
        ("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")
    ], null=True, blank=True)
    budget = models.CharField(max_length=30, choices=[
        ("Low", "Low"), ("Mid", "Mid"), ("No restrictions", "No restrictions")
    ], null=True, blank=True)
    physical_activity = models.CharField(max_length=20, choices=[
        ("Sedentary", "Sedentary"), ("Light", "Light"), ("Moderate", "Moderate"), ("Active", "Active")
    ], null=True, blank=True)
    include_exercise = models.BooleanField(default=False)

    # Step 3
    meal_prep_time = models.CharField(max_length=30, blank=True)
    meals_per_day = models.CharField(max_length=20, blank=True)
    cooking_frequency = models.CharField(max_length=50, blank=True)
    commitment_duration = models.CharField(max_length=100, blank=True)

    # Step 4
    additional_info = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"


class MealLog(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    date_logged = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    servings = models.FloatField(default=1.0)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_logged', '-created_at']
        unique_together = ['user', 'recipe', 'meal_type', 'date_logged']
    
    def __str__(self):
        return f"{self.user.username} - {self.recipe.recipe_name} ({self.meal_type}) on {self.date_logged}"
    
    def get_total_calories(self):
        """Calculate total calories based on servings"""
        if self.recipe.calories:
            return round(self.recipe.calories * self.servings, 1)
        return 0
    
    def get_total_protein(self):
        """Calculate total protein based on servings"""
        if self.recipe.protein:
            return round(self.recipe.protein * self.servings, 1)
        return 0
    
    def get_total_carbs(self):
        """Calculate total carbs based on servings"""
        if self.recipe.carbohydrate:
            return round(self.recipe.carbohydrate * self.servings, 1)
        return 0
    
    def get_total_fat(self):
        """Calculate total fat based on servings"""
        if self.recipe.fat:
            return round(self.recipe.fat * self.servings, 1)
        return 0


class DailyNutritionSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    total_calories = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.total_calories} cal)"
