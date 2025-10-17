#!/usr/bin/env python
"""
Simple script to add real food images to recipes using free APIs
Uses Foodish API and other free food image services
"""
import os
import django
import sys
import requests
import time
import random

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

from recipes.models import Recipe
from django.core.files.base import ContentFile
from django.conf import settings

class FoodImageFetcher:
    def __init__(self):
        # Free food image APIs
        self.apis = [
            "https://foodish-api.herokuapp.com/api/",
            "https://source.unsplash.com/400x300/?food,meal",
            "https://picsum.photos/400/300",  # Random images as fallback
        ]
        
        # Specific food categories for better matching
        self.food_categories = {
            'chicken': 'https://foodish-api.herokuapp.com/api/images/chicken',
            'pizza': 'https://foodish-api.herokuapp.com/api/images/pizza',
            'burger': 'https://foodish-api.herokuapp.com/api/images/burger',
            'pasta': 'https://foodish-api.herokuapp.com/api/images/pasta',
            'rice': 'https://foodish-api.herokuapp.com/api/images/rice',
            'salad': 'https://source.unsplash.com/400x300/?salad,healthy',
            'soup': 'https://source.unsplash.com/400x300/?soup,bowl',
            'fish': 'https://source.unsplash.com/400x300/?fish,seafood',
            'meat': 'https://source.unsplash.com/400x300/?meat,steak',
            'vegetarian': 'https://source.unsplash.com/400x300/?vegetarian,vegetables',
            'dessert': 'https://source.unsplash.com/400x300/?dessert,cake',
            'breakfast': 'https://source.unsplash.com/400x300/?breakfast,morning',
        }
    
    def get_food_category_from_recipe(self, recipe_name, recipe_type=None, ingredients=None):
        """Determine food category from recipe details"""
        recipe_lower = recipe_name.lower()
        
        # Check recipe name for keywords
        for category, url in self.food_categories.items():
            if category in recipe_lower:
                return url
        
        # Check recipe type
        if recipe_type:
            type_lower = recipe_type.lower()
            for category, url in self.food_categories.items():
                if category in type_lower:
                    return url
        
        # Check ingredients
        if ingredients:
            ingredients_lower = ingredients.lower()
            for category, url in self.food_categories.items():
                if category in ingredients_lower:
                    return url
        
        # Default to general food image
        return f"https://source.unsplash.com/400x300/?{recipe_name.replace(' ', '%20')},food"
    
    def fetch_foodish_image(self):
        """Fetch random food image from Foodish API"""
        try:
            response = requests.get("https://foodish-api.herokuapp.com/api/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('image')
        except:
            pass
        return None
    
    def download_image(self, url, recipe_name):
        """Download image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Validate that it's an image
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                print(f"⚠️ Invalid content type for {recipe_name}: {content_type}")
                return None
            
            # Create filename
            filename = f"{recipe_name.lower().replace(' ', '_').replace('/', '_')[:50]}.jpg"
            
            return ContentFile(response.content, name=filename)
            
        except Exception as e:
            print(f"❌ Error downloading image for {recipe_name}: {e}")
            return None
    
    def add_images_to_recipes(self):
        """Add images to all recipes that don't have them"""
        recipes_without_images = Recipe.objects.filter(image__isnull=True)
        total_recipes = recipes_without_images.count()
        
        print(f"🔍 Found {total_recipes} recipes without images")
        print("📸 Starting image download process...")
        
        success_count = 0
        
        for i, recipe in enumerate(recipes_without_images, 1):
            print(f"\n📥 Processing {i}/{total_recipes}: {recipe.recipe_name}")
            
            # Try different image sources
            image_file = None
            
            # Method 1: Try category-specific URL
            category_url = self.get_food_category_from_recipe(
                recipe.recipe_name, 
                recipe.type, 
                recipe.ingredients
            )
            print(f"   🎯 Trying category-specific image...")
            image_file = self.download_image(category_url, recipe.recipe_name)
            
            # Method 2: Try Foodish API for random food image
            if not image_file:
                print(f"   🎲 Trying random food image...")
                foodish_url = self.fetch_foodish_image()
                if foodish_url:
                    image_file = self.download_image(foodish_url, recipe.recipe_name)
            
            # Method 3: Try general food search
            if not image_file:
                print(f"   🔍 Trying general food search...")
                general_url = f"https://source.unsplash.com/400x300/?food,meal,{random.randint(1,1000)}"
                image_file = self.download_image(general_url, recipe.recipe_name)
            
            # Save the image if we got one
            if image_file:
                try:
                    recipe.image.save(
                        f"{recipe.recipe_name.lower().replace(' ', '_')[:50]}.jpg",
                        image_file,
                        save=True
                    )
                    print(f"   ✅ Successfully added image to {recipe.recipe_name}")
                    success_count += 1
                except Exception as e:
                    print(f"   ❌ Error saving image for {recipe.recipe_name}: {e}")
            else:
                print(f"   ⚠️ Failed to get image for {recipe.recipe_name}")
            
            # Small delay to be respectful to APIs
            time.sleep(2)
        
        print(f"\n🎉 Process completed!")
        print(f"✅ Successfully added images to {success_count}/{total_recipes} recipes")

def main():
    print("🚀 Starting Food Image Download Process...")
    print("📊 This will add real food images to all your recipes!")
    
    # Check if media directory exists
    media_root = settings.MEDIA_ROOT
    recipes_dir = os.path.join(media_root, 'recipes')
    
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir)
        print(f"📁 Created directory: {recipes_dir}")
    
    # Show current status
    total_recipes = Recipe.objects.count()
    recipes_with_images = Recipe.objects.exclude(image__isnull=True).exclude(image__exact='').count()
    recipes_without_images = total_recipes - recipes_with_images
    
    print(f"📈 Current Status:")
    print(f"   Total Recipes: {total_recipes}")
    print(f"   With Images: {recipes_with_images}")
    print(f"   Without Images: {recipes_without_images}")
    
    if recipes_without_images == 0:
        print("🎉 All recipes already have images!")
        return
    
    # Ask for confirmation
    print(f"\n⚠️  This will download {recipes_without_images} images from the internet.")
    response = input("Continue? (y/N): ").lower().strip()
    
    if response != 'y':
        print("❌ Operation cancelled.")
        return
    
    # Initialize fetcher and start process
    fetcher = FoodImageFetcher()
    fetcher.add_images_to_recipes()
    
    print("\n✨ All done! Check your recipe detail pages to see the new images!")

if __name__ == "__main__":
    main()