from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Recipe

def recipe_view(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_details.html', {'recipe': recipe})

def recipes_by_diet(request):
    """View to display recipes filtered by diet type"""
    diet_type = request.GET.get('diet', 'All')
    search_query = request.GET.get('search', '')
    
    # Get all available diet types
    diet_types = Recipe.get_available_diet_types()
    
    # Filter recipes
    recipes = Recipe.objects.all()
    
    if diet_type != 'All':
        recipes = recipes.filter(diet_types__icontains=diet_type)
    
    if search_query:
        recipes = recipes.filter(
            Q(recipe_name__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(type__icontains=search_query)
        )
    
    # Get recipe counts by diet type
    diet_counts = {}
    for dt in diet_types:
        diet_counts[dt] = Recipe.objects.filter(diet_types__icontains=dt).count()
    
    context = {
        'recipes': recipes.order_by('recipe_name'),
        'diet_types': diet_types,
        'selected_diet': diet_type,
        'search_query': search_query,
        'diet_counts': diet_counts,
        'total_recipes': Recipe.objects.count()
    }
    
    return render(request, 'recipes/recipes_by_diet.html', context)
