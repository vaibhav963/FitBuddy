#!/usr/bin/env python
"""
Alternative script to generate beautiful placeholder images for recipes using PIL
This creates custom images with recipe names and cuisine types
"""
import os
import django
import sys
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

from recipes.models import Recipe
from django.core.files.base import ContentFile
from django.conf import settings

class PlaceholderImageGenerator:
    def __init__(self):
        self.image_size = (400, 300)
        self.colors = [
            ('#FF6B6B', '#4ECDC4'),  # Red to Teal
            ('#A8E6CF', '#FFD93D'),  # Green to Yellow
            ('#FF8B94', '#FF3CAC'),  # Pink gradient
            ('#6C5CE7', '#A29BFE'),  # Purple gradient
            ('#FD79A8', '#FDCB6E'),  # Pink to Orange
            ('#0984E3', '#00B894'),  # Blue to Green
            ('#E17055', '#FDCB6E'),  # Orange gradient
            ('#00CEC9', '#55A3FF'),  # Cyan to Blue
        ]
        
        self.food_emojis = ['🍽️', '🥘', '🍳', '🥗', '🍲', '🥙', '🍕', '🥞', '🍜', '🥖']
    
    def create_gradient_background(self, width, height, color1, color2):
        """Create a gradient background"""
        # Convert hex to RGB
        color1_rgb = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        color2_rgb = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        
        # Create gradient
        gradient = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(gradient)
        
        for y in range(height):
            # Calculate color for this row
            ratio = y / height
            r = int(color1_rgb[0] * (1 - ratio) + color2_rgb[0] * ratio)
            g = int(color1_rgb[1] * (1 - ratio) + color2_rgb[1] * ratio)
            b = int(color1_rgb[2] * (1 - ratio) + color2_rgb[2] * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return gradient
    
    def create_recipe_image(self, recipe_name, cuisine=None):
        """Create a beautiful placeholder image for a recipe"""
        width, height = self.image_size
        
        # Choose random color scheme
        color1, color2 = random.choice(self.colors)
        
        # Create gradient background
        img = self.create_gradient_background(width, height, color1, color2)
        draw = ImageDraw.Draw(img)
        
        # Add semi-transparent overlay
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 50))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Try to load a font (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            subtitle_font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
        
        # Add food emoji
        emoji = random.choice(self.food_emojis)
        try:
            emoji_font = ImageFont.truetype("seguiemj.ttf", 48)  # Windows emoji font
        except:
            emoji_font = ImageFont.load_default()
        
        # Calculate text positions
        emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
        emoji_width = emoji_bbox[2] - emoji_bbox[0]
        emoji_x = (width - emoji_width) // 2
        emoji_y = height // 4
        
        # Draw emoji
        draw.text((emoji_x, emoji_y), emoji, font=emoji_font, fill='white')
        
        # Draw recipe name (wrap if too long)
        words = recipe_name.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=title_font)
            if bbox[2] - bbox[0] < width - 40:  # 20px margin on each side
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw recipe name lines
        total_text_height = len(lines) * 30
        start_y = (height // 2) + 20
        
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            text_y = start_y + (i * 30)
            
            # Add text shadow
            draw.text((text_x + 2, text_y + 2), line, font=title_font, fill='black')
            draw.text((text_x, text_y), line, font=title_font, fill='white')
        
        # Draw cuisine if available
        if cuisine:
            cuisine_text = f"{cuisine} Cuisine"
            bbox = draw.textbbox((0, 0), cuisine_text, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            text_y = height - 40
            
            # Add text shadow
            draw.text((text_x + 1, text_y + 1), cuisine_text, font=subtitle_font, fill='black')
            draw.text((text_x, text_y), cuisine_text, font=subtitle_font, fill='white')
        
        return img
    
    def add_images_to_recipes(self):
        """Add placeholder images to all recipes that don't have them"""
        recipes_without_images = Recipe.objects.filter(image__isnull=True)
        total_recipes = recipes_without_images.count()
        
        print(f"🔍 Found {total_recipes} recipes without images")
        
        for i, recipe in enumerate(recipes_without_images, 1):
            print(f"🎨 Creating image {i}/{total_recipes}: {recipe.recipe_name}")
            
            # Create placeholder image
            img = self.create_recipe_image(recipe.recipe_name, recipe.cuisine)
            
            # Save to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG', quality=90)
            img_buffer.seek(0)
            
            # Create Django file
            filename = f"{recipe.recipe_name.lower().replace(' ', '_')}.jpg"
            django_file = ContentFile(img_buffer.read(), name=filename)
            
            # Save to recipe
            recipe.image.save(filename, django_file, save=True)
            print(f"✅ Added custom image to {recipe.recipe_name}")
        
        print(f"🎉 Created {total_recipes} beautiful recipe images!")

def main():
    print("🚀 Starting Custom Recipe Image Generation...")
    
    # Check if media directory exists
    media_root = settings.MEDIA_ROOT
    recipes_dir = os.path.join(media_root, 'recipes')
    
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir)
        print(f"📁 Created directory: {recipes_dir}")
    
    # Initialize image generator
    image_generator = PlaceholderImageGenerator()
    
    # Add images to recipes
    image_generator.add_images_to_recipes()
    
    print("✨ All done! Your recipes now have beautiful custom images!")

if __name__ == "__main__":
    main()