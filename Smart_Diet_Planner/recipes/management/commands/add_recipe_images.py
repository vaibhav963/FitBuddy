from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Recipe
from django.core.files.base import ContentFile
import requests
import time
import random
import os

class Command(BaseCommand):
    help = 'Add images to all recipes that don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--method',
            type=str,
            default='api',
            choices=['api', 'placeholder'],
            help='Method to use: api (download real images) or placeholder (generate custom images)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Replace existing images'
        )

    def handle(self, *args, **options):
        method = options['method']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting recipe image addition using {method} method...')
        )
        
        # Get recipes
        if force:
            recipes = Recipe.objects.all()
            self.stdout.write(f'📋 Processing ALL {recipes.count()} recipes (force mode)')
        else:
            recipes = Recipe.objects.filter(image__isnull=True)
            self.stdout.write(f'📋 Processing {recipes.count()} recipes without images')
        
        if not recipes.exists():
            self.stdout.write(self.style.WARNING('No recipes to process!'))
            return
        
        # Ensure media directory exists
        media_root = settings.MEDIA_ROOT
        recipes_dir = os.path.join(media_root, 'recipes')
        if not os.path.exists(recipes_dir):
            os.makedirs(recipes_dir)
            self.stdout.write(f'📁 Created directory: {recipes_dir}')
        
        # Process recipes based on method
        if method == 'api':
            self.add_api_images(recipes)
        else:
            self.add_placeholder_images(recipes)
        
        self.stdout.write(
            self.style.SUCCESS('✨ Recipe image addition completed!')
        )

    def add_api_images(self, recipes):
        """Add real food images from APIs"""
        success_count = 0
        total = recipes.count()
        
        for i, recipe in enumerate(recipes, 1):
            self.stdout.write(f'📥 [{i}/{total}] Processing: {recipe.recipe_name}')
            
            # Try to get a food image
            image_url = self.get_food_image_url(recipe)
            
            if image_url:
                image_file = self.download_image(image_url, recipe.recipe_name)
                if image_file:
                    try:
                        filename = f"{recipe.recipe_name.lower().replace(' ', '_')[:50]}.jpg"
                        recipe.image.save(filename, image_file, save=True)
                        self.stdout.write(f'   ✅ Added image successfully')
                        success_count += 1
                    except Exception as e:
                        self.stdout.write(f'   ❌ Error saving: {e}')
                else:
                    self.stdout.write(f'   ⚠️  Failed to download image')
            else:
                self.stdout.write(f'   ⚠️  No image URL found')
            
            # Small delay to be respectful to APIs
            time.sleep(1)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully added {success_count}/{total} images')
        )

    def get_food_image_url(self, recipe):
        """Get food image URL for recipe"""
        # Try different approaches
        urls_to_try = [
            f"https://source.unsplash.com/400x300/?{recipe.recipe_name.replace(' ', '%20')},food",
            f"https://source.unsplash.com/400x300/?food,meal,{random.randint(1,1000)}",
            "https://foodish-api.herokuapp.com/api/"
        ]
        
        for url in urls_to_try:
            if "foodish" in url:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('image')
                except:
                    continue
            else:
                return url
        
        return None

    def download_image(self, url, recipe_name):
        """Download image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                return None
            
            filename = f"{recipe_name.lower().replace(' ', '_')[:50]}.jpg"
            return ContentFile(response.content, name=filename)
            
        except Exception as e:
            self.stdout.write(f'   ❌ Download error: {e}')
            return None

    def add_placeholder_images(self, recipes):
        """Add custom generated placeholder images"""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            self.stdout.write(
                self.style.ERROR('❌ PIL (Pillow) not installed. Run: pip install Pillow')
            )
            return
        
        success_count = 0
        total = recipes.count()
        
        colors = [
            ('#FF6B6B', '#4ECDC4'),  # Red to Teal
            ('#A8E6CF', '#FFD93D'),  # Green to Yellow
            ('#FF8B94', '#FF3CAC'),  # Pink gradient
            ('#6C5CE7', '#A29BFE'),  # Purple gradient
        ]
        
        for i, recipe in enumerate(recipes, 1):
            self.stdout.write(f'🎨 [{i}/{total}] Creating image for: {recipe.recipe_name}')
            
            try:
                # Create image
                img = self.create_placeholder_image(recipe, colors)
                
                # Save to BytesIO
                from io import BytesIO
                img_buffer = BytesIO()
                img.save(img_buffer, format='JPEG', quality=90)
                img_buffer.seek(0)
                
                # Save to recipe
                filename = f"{recipe.recipe_name.lower().replace(' ', '_')[:50]}.jpg"
                django_file = ContentFile(img_buffer.read(), name=filename)
                
                recipe.image.save(filename, django_file, save=True)
                self.stdout.write(f'   ✅ Created custom image successfully')
                success_count += 1
                
            except Exception as e:
                self.stdout.write(f'   ❌ Error creating image: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully created {success_count}/{total} images')
        )

    def create_placeholder_image(self, recipe, colors):
        """Create a placeholder image for recipe"""
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        
        width, height = 400, 300
        color1, color2 = random.choice(colors)
        
        # Convert hex to RGB
        color1_rgb = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        color2_rgb = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        
        # Create gradient
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        for y in range(height):
            ratio = y / height
            r = int(color1_rgb[0] * (1 - ratio) + color2_rgb[0] * ratio)
            g = int(color1_rgb[1] * (1 - ratio) + color2_rgb[1] * ratio)
            b = int(color1_rgb[2] * (1 - ratio) + color2_rgb[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Add recipe name
        text = recipe.recipe_name
        if len(text) > 20:
            text = text[:20] + "..."
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Text shadow
        draw.text((x + 2, y + 2), text, font=font, fill='black')
        draw.text((x, y), text, font=font, fill='white')
        
        # Add emoji
        emoji = '🍽️'
        try:
            emoji_font = ImageFont.truetype("seguiemj.ttf", 36)
            draw.text((x, y - 50), emoji, font=emoji_font, fill='white')
        except:
            pass
        
        return img