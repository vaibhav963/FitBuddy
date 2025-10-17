"""
Fallback responses for the chatbot when AI is unavailable
"""

import random
from .models import Recipe

def get_fallback_response(query):
    """
    Provide a simple fallback response when AI is unavailable
    """
    query_lower = query.lower()
    
    # Recipe-related queries
    if any(word in query_lower for word in ['recipe', 'cook', 'make', 'prepare']):
        if any(word in query_lower for word in ['chicken', 'meat', 'protein']):
            return get_protein_recipe_suggestion()
        elif any(word in query_lower for word in ['vegetarian', 'vegan', 'plant']):
            return get_vegetarian_recipe_suggestion()
        elif any(word in query_lower for word in ['keto', 'low carb', 'ketogenic']):
            return get_keto_recipe_suggestion()
        else:
            return get_random_recipe_suggestion()
    
    # Diet-related queries
    elif any(word in query_lower for word in ['diet', 'nutrition', 'healthy', 'lose weight', 'gain weight']):
        return get_diet_advice()
    
    # Ingredient queries
    elif any(word in query_lower for word in ['ingredient', 'substitute', 'replace']):
        return get_ingredient_advice()
    
    # Default response
    else:
        return get_general_response()

def get_protein_recipe_suggestion():
    try:
        recipes = Recipe.objects.filter(diet_type__in=['High Protein', 'Balanced']).order_by('?')[:3]
        if recipes:
            recipe_list = "\n".join([f"• {recipe.recipe_name} ({recipe.calories} cal)" for recipe in recipes])
            return f"Here are some high-protein recipes you might enjoy:\n\n{recipe_list}\n\nVisit our recipe collection for detailed instructions!"
    except:
        pass
    
    return "For high-protein meals, try grilled chicken with vegetables, salmon with quinoa, or Greek yogurt with nuts. Check our recipe collection for detailed instructions!"

def get_vegetarian_recipe_suggestion():
    try:
        recipes = Recipe.objects.filter(diet_type__in=['Vegetarian', 'Vegan']).order_by('?')[:3]
        if recipes:
            recipe_list = "\n".join([f"• {recipe.recipe_name} ({recipe.calories} cal)" for recipe in recipes])
            return f"Here are some vegetarian recipes for you:\n\n{recipe_list}\n\nBrowse our recipe collection for more options!"
    except:
        pass
    
    return "Try vegetable stir-fry, lentil curry, or chickpea salad. Our recipe collection has many vegetarian options with full instructions!"

def get_keto_recipe_suggestion():
    try:
        recipes = Recipe.objects.filter(diet_type='Ketogenic (Keto)').order_by('?')[:3]
        if recipes:
            recipe_list = "\n".join([f"• {recipe.recipe_name} ({recipe.calories} cal)" for recipe in recipes])
            return f"Here are some keto-friendly recipes:\n\n{recipe_list}\n\nExplore our keto section for more low-carb options!"
    except:
        pass
    
    return "For keto meals, try avocado salad, grilled fish with vegetables, or cheese and nuts. Check our keto recipe collection!"

def get_random_recipe_suggestion():
    try:
        recipes = Recipe.objects.all().order_by('?')[:3]
        if recipes:
            recipe_list = "\n".join([f"• {recipe.recipe_name} ({recipe.calories} cal)" for recipe in recipes])
            return f"Here are some popular recipes:\n\n{recipe_list}\n\nVisit our recipe collection for the full instructions!"
    except:
        pass
    
    return "I'd love to suggest some recipes! Please browse our recipe collection where you'll find detailed instructions for hundreds of delicious meals."

def get_diet_advice():
    advice_options = [
        "For healthy eating, focus on balanced meals with vegetables, lean proteins, and whole grains. Our meal planner can help create personalized plans!",
        "A balanced diet includes variety, portion control, and regular meals. Check out our AI meal planner for customized recommendations!",
        "Remember to stay hydrated, eat plenty of vegetables, and choose whole foods over processed ones. Our recipe collection has many healthy options!"
    ]
    return random.choice(advice_options)

def get_ingredient_advice():
    return "For ingredient substitutions, try our recipe collection where many recipes include alternative ingredients. You can also use our recipe search to find meals with specific ingredients!"

def get_general_response():
    responses = [
        "I'm here to help with recipes and nutrition! Try asking about specific recipes, diet types, or cooking tips.",
        "Feel free to ask me about recipes, meal planning, or nutrition advice. I can also help you find recipes based on your dietary preferences!",
        "I'd be happy to help with your cooking and nutrition questions! Browse our recipe collection or try our AI meal planner for personalized suggestions."
    ]
    return random.choice(responses)