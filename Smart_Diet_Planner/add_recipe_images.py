#!/usr/bin/env python
"""
Script to automatically add images to all recipes using AI-generated food images
This script will fetch appropriate food images for each recipe
"""
import os
import django
import sys
import requests
from urllib.parse import quote
import time

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

from recipes.models import Recipe
from django.core.files.base import ContentFile
from django.conf import settings

class RecipeImageManager:
    def __init__(self):
        self.unsplash_access_key = "YOUR_UNSPLASH_ACCESS_KEY"  # Replace with your key
        self.placeholder_service = "https://source.unsplash.com/400x300/?food,{}"
        
    def get_food_image_url(self, recipe_name, cuisine=None):
        """Generate food image URL based on recipe name and cuisine"""
        # Clean recipe name for search
        search_terms = recipe_name.lower().replace(' ', ',')
        if cuisine:
            search_terms += f",{cuisine.lower()}"
        
        # Use Unsplash for high-quality food images
        return f"https://source.unsplash.com/400x300/?{search_terms},food,meal"
    
    def download_image(self, url, recipe_name):
        """Download image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Create filename
            filename = f"{recipe_name.lower().replace(' ', '_')}.jpg"
            
            return ContentFile(response.content, name=filename)
            
        except Exception as e:
            print(f"❌ Error downloading image for {recipe_name}: {e}")
            return None
    
    def add_images_to_recipes(self):
        """Add images to all recipes that don't have them"""
        recipes_without_images = Recipe.objects.filter(image__isnull=True)
        total_recipes = recipes_without_images.count()
        
        print(f"🔍 Found {total_recipes} recipes without images")
        
        for i, recipe in enumerate(recipes_without_images, 1):
            print(f"📸 Processing {i}/{total_recipes}: {recipe.recipe_name}")
            
            # Get image URL
            image_url = self.get_food_image_url(recipe.recipe_name, recipe.cuisine)
            
            # Download and save image
            image_file = self.download_image(image_url, recipe.recipe_name)
            
            if image_file:
                recipe.image.save(
                    f"{recipe.recipe_name.lower().replace(' ', '_')}.jpg",
                    image_file,
                    save=True
                )
                print(f"✅ Added image to {recipe.recipe_name}")
            else:
                print(f"⚠️ Failed to add image to {recipe.recipe_name}")
            
            # Small delay to be respectful to the API
            time.sleep(1)
        
        print(f"🎉 Completed processing {total_recipes} recipes!")

def main():
    print("🚀 Starting Recipe Image Addition Process...")
    
    # Check if media directory exists
    media_root = settings.MEDIA_ROOT
    recipes_dir = os.path.join(media_root, 'recipes')
    
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir)
        print(f"📁 Created directory: {recipes_dir}")
    
    # Initialize image manager
    image_manager = RecipeImageManager()
    
    # Add images to recipes
    image_manager.add_images_to_recipes()
    
    print("✨ All done! Your recipes now have beautiful images!")

if __name__ == "__main__":
    main()