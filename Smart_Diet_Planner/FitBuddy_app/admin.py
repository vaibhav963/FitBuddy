from django.contrib import admin
from .models import UserProfile, MealLog, DailyNutritionSummary

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = [
        'user', 'age', 'gender', 'current_weight', 'target_weight', 
        'height', 'physical_activity', 'cooking_skill'
    ]
    
    # Fields that can be used for filtering
    list_filter = [
        'gender', 'cooking_skill', 'budget', 'physical_activity', 
        'include_exercise', 'height_unit', 'weight_unit'
    ]
    
    # Fields that can be searched
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    
    # Organize fields into sections using fieldsets
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Basic Details', {
            'fields': (
                ('age', 'gender'),
                ('height', 'height_unit'),
                ('current_weight', 'target_weight', 'weight_unit'),
            ),
            'description': 'Basic physical information and measurements'
        }),
        ('Lifestyle & Preferences', {
            'fields': (
                ('cooking_skill', 'budget'),
                ('physical_activity', 'include_exercise'),
                'food_allergies',
            ),
            'description': 'Cooking preferences and activity level'
        }),
        ('Meal Planning', {
            'fields': (
                ('meal_prep_time', 'meals_per_day'),
                ('cooking_frequency', 'commitment_duration'),
            ),
            'description': 'Meal preparation and planning preferences'
        }),
        ('Additional Information', {
            'fields': ('additional_info',),
            'classes': ('collapse',),  # This section will be collapsible
            'description': 'Any additional notes or requirements'
        }),
    )
    
    # Make the form more readable
    radio_fields = {
        'gender': admin.HORIZONTAL,
        'cooking_skill': admin.HORIZONTAL,
        'budget': admin.HORIZONTAL,
        'physical_activity': admin.HORIZONTAL,
    }
    
    # Custom method to display weight info nicely
    def weight_info(self, obj):
        if obj.current_weight and obj.target_weight:
            return f"{obj.current_weight} → {obj.target_weight} {obj.weight_unit}"
        elif obj.current_weight:
            return f"{obj.current_weight} {obj.weight_unit}"
        return "Not specified"
    weight_info.short_description = "Weight Info"
    
    # Custom method to display height info
    def height_info(self, obj):
        if obj.height:
            return f"{obj.height} {obj.height_unit}"
        return "Not specified"
    height_info.short_description = "Height"
    
    # You can add these custom methods to list_display if desired
    # list_display = [..., 'weight_info', 'height_info']
    
    # Optional: Make the admin interface more user-friendly
    def get_readonly_fields(self, request, obj=None):
        # Make user field readonly when editing existing profiles
        if obj:  # editing an existing object
            return ['user']
        return []
    
    # Optional: Custom save behavior
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Add any custom save logic here if needed

# Alternative: If you want a more compact inline admin
# This would be useful if you're managing UserProfile from the User admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Basic Info', {
            'fields': (
                ('age', 'gender'),
                ('height', 'height_unit'),
                ('current_weight', 'target_weight', 'weight_unit'),
            )
        }),
        ('Preferences', {
            'fields': (
                ('cooking_skill', 'budget'),
                ('physical_activity', 'include_exercise'),
                'food_allergies'
            )
        }),
        ('Meal Planning', {
            'fields': (
                ('meal_prep_time', 'meals_per_day'),
                ('cooking_frequency', 'commitment_duration'),
            ),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('additional_info',),
            'classes': ('collapse',)
        })
    )


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'recipe', 'meal_type', 'date_logged', 
        'servings', 'get_total_calories', 'created_at'
    ]
    
    list_filter = [
        'meal_type', 'date_logged', 'created_at',
        'recipe__type', 'recipe__cuisine'
    ]
    
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'recipe__recipe_name', 'notes'
    ]
    
    date_hierarchy = 'date_logged'
    
    fieldsets = (
        ('Meal Information', {
            'fields': ('user', 'recipe', 'meal_type', 'date_logged')
        }),
        ('Serving Details', {
            'fields': ('servings', 'notes')
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_total_calories(self, obj):
        """Display total calories for this meal log entry"""
        return f"{obj.get_total_calories():.1f} cal"
    get_total_calories.short_description = "Total Calories"
    get_total_calories.admin_order_field = 'recipe__calories'


@admin.register(DailyNutritionSummary)
class DailyNutritionSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'date', 'total_calories', 'total_protein',
        'total_carbs', 'total_fat', 'updated_at'
    ]
    
    list_filter = ['date', 'created_at', 'updated_at']
    
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    
    date_hierarchy = 'date'
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Summary Information', {
            'fields': ('user', 'date')
        }),
        ('Nutrition Totals', {
            'fields': (
                ('total_calories', 'total_protein'),
                ('total_carbs', 'total_fat')
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )